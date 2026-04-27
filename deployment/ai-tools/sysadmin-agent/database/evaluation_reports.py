"""
AI Evaluation Reporting Module

Provides comprehensive reporting functions for analyzing AI response quality,
confidence calibration, and continuous improvement tracking.

Reports generated:
- Performance summary (accuracy, feedback rates)
- Confidence calibration analysis
- Issue trend analysis
- Query type breakdown
- Exportable reports for compliance documentation
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from .feedback_db import (
    get_connection,
    get_feedback_summary,
    calculate_confidence_calibration,
    get_common_issues,
    get_recent_responses,
    get_metrics_history,
    generate_daily_metrics,
)


@dataclass
class PerformanceMetrics:
    """Container for AI performance metrics."""
    period_start: str
    period_end: str
    total_responses: int
    total_feedback: int
    feedback_rate: float
    positive_rate: float
    negative_rate: float
    avg_confidence_score: float
    calibration_error: float
    responses_by_confidence: Dict[str, int]
    responses_by_query_type: Dict[str, int]
    top_issues: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_start": self.period_start,
            "period_end": self.period_end,
            "total_responses": self.total_responses,
            "total_feedback": self.total_feedback,
            "feedback_rate": self.feedback_rate,
            "positive_rate": self.positive_rate,
            "negative_rate": self.negative_rate,
            "avg_confidence_score": self.avg_confidence_score,
            "calibration_error": self.calibration_error,
            "responses_by_confidence": self.responses_by_confidence,
            "responses_by_query_type": self.responses_by_query_type,
            "top_issues": self.top_issues,
        }


def get_performance_metrics(days: int = 30) -> PerformanceMetrics:
    """
    Calculate comprehensive performance metrics for the specified period.

    Args:
        days: Number of days to analyze

    Returns:
        PerformanceMetrics object with all calculated metrics
    """
    conn = get_connection()
    cursor = conn.cursor()

    period_end = datetime.now()
    period_start = period_end - timedelta(days=days)

    # Get total responses in period
    cursor.execute("""
        SELECT COUNT(*) as count, AVG(confidence_score) as avg_conf
        FROM ai_responses
        WHERE timestamp >= ?
    """, (period_start.isoformat(),))
    row = cursor.fetchone()
    total_responses = row["count"] or 0
    avg_confidence = row["avg_conf"] or 0

    # Get feedback counts
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN rating = 'positive' THEN 1 ELSE 0 END) as positive,
            SUM(CASE WHEN rating = 'negative' THEN 1 ELSE 0 END) as negative
        FROM feedback
        WHERE timestamp >= ?
    """, (period_start.isoformat(),))
    row = cursor.fetchone()
    total_feedback = row["total"] or 0
    positive_count = row["positive"] or 0
    negative_count = row["negative"] or 0

    # Calculate rates
    feedback_rate = (total_feedback / total_responses * 100) if total_responses > 0 else 0
    positive_rate = (positive_count / total_feedback * 100) if total_feedback > 0 else 0
    negative_rate = (negative_count / total_feedback * 100) if total_feedback > 0 else 0

    # Get responses by confidence level
    cursor.execute("""
        SELECT confidence_level, COUNT(*) as count
        FROM ai_responses
        WHERE timestamp >= ?
        GROUP BY confidence_level
    """, (period_start.isoformat(),))
    responses_by_confidence = {row["confidence_level"]: row["count"] for row in cursor.fetchall()}

    # Get responses by query type
    cursor.execute("""
        SELECT query_type, COUNT(*) as count
        FROM ai_responses
        WHERE timestamp >= ? AND query_type != ''
        GROUP BY query_type
    """, (period_start.isoformat(),))
    responses_by_query_type = {row["query_type"]: row["count"] for row in cursor.fetchall()}

    conn.close()

    # Get calibration and issues from existing functions
    calibration = calculate_confidence_calibration(days=days)
    top_issues = get_common_issues(days=days, limit=5)

    return PerformanceMetrics(
        period_start=period_start.isoformat(),
        period_end=period_end.isoformat(),
        total_responses=total_responses,
        total_feedback=total_feedback,
        feedback_rate=round(feedback_rate, 1),
        positive_rate=round(positive_rate, 1),
        negative_rate=round(negative_rate, 1),
        avg_confidence_score=round(avg_confidence, 1) if avg_confidence else 0,
        calibration_error=calibration.get("overall_calibration_error") or 0,
        responses_by_confidence=responses_by_confidence,
        responses_by_query_type=responses_by_query_type,
        top_issues=top_issues,
    )


def get_calibration_report(days: int = 30) -> Dict[str, Any]:
    """
    Generate detailed confidence calibration report.

    This compares stated confidence levels to actual accuracy based on feedback.
    A well-calibrated model should have accuracy rates matching confidence levels.

    Returns:
        Dictionary with calibration analysis
    """
    calibration = calculate_confidence_calibration(days=days)

    # Add interpretation
    interpretation = []
    for level, data in calibration.get("by_confidence_level", {}).items():
        if data.get("calibration_error") is not None:
            error = data["calibration_error"]
            if error <= 10:
                status = "Well calibrated"
            elif error <= 20:
                status = "Slightly miscalibrated"
            else:
                status = "Significantly miscalibrated"

            direction = ""
            if data.get("accuracy_rate") is not None and data.get("expected_accuracy"):
                if data["accuracy_rate"] > data["expected_accuracy"]:
                    direction = " (underconfident - accuracy higher than stated)"
                elif data["accuracy_rate"] < data["expected_accuracy"]:
                    direction = " (overconfident - accuracy lower than stated)"

            interpretation.append({
                "level": level,
                "status": status,
                "direction": direction,
                "error": error,
            })

    calibration["interpretation"] = interpretation

    # Overall assessment
    overall_error = calibration.get("overall_calibration_error")
    if overall_error is not None:
        if overall_error <= 10:
            calibration["overall_assessment"] = "Model is well calibrated"
        elif overall_error <= 20:
            calibration["overall_assessment"] = "Model shows minor calibration issues"
        else:
            calibration["overall_assessment"] = "Model requires calibration adjustment"
    else:
        calibration["overall_assessment"] = "Insufficient feedback data for assessment"

    return calibration


def get_issue_trend_report(days: int = 30) -> Dict[str, Any]:
    """
    Analyze trends in reported issues over time.

    Returns:
        Dictionary with issue trends and patterns
    """
    conn = get_connection()
    cursor = conn.cursor()

    period_start = (datetime.now() - timedelta(days=days)).isoformat()

    # Get issues by week
    cursor.execute("""
        SELECT
            strftime('%Y-%W', timestamp) as week,
            issue_categories
        FROM feedback
        WHERE timestamp >= ? AND issue_categories != '[]'
        ORDER BY timestamp
    """, (period_start,))

    weekly_issues: Dict[str, Dict[str, int]] = {}
    for row in cursor.fetchall():
        week = row["week"]
        categories = json.loads(row["issue_categories"] or "[]")

        if week not in weekly_issues:
            weekly_issues[week] = {}

        for cat in categories:
            weekly_issues[week][cat] = weekly_issues[week].get(cat, 0) + 1

    conn.close()

    # Calculate trends
    all_issues = get_common_issues(days=days, limit=10)

    # Identify emerging vs declining issues
    weeks = sorted(weekly_issues.keys())
    if len(weeks) >= 2:
        recent_week = weeks[-1]
        earlier_week = weeks[0]

        emerging = []
        declining = []

        recent_issues = weekly_issues.get(recent_week, {})
        earlier_issues = weekly_issues.get(earlier_week, {})

        all_categories = set(recent_issues.keys()) | set(earlier_issues.keys())
        for cat in all_categories:
            recent_count = recent_issues.get(cat, 0)
            earlier_count = earlier_issues.get(cat, 0)

            if recent_count > earlier_count:
                emerging.append({"category": cat, "change": recent_count - earlier_count})
            elif recent_count < earlier_count:
                declining.append({"category": cat, "change": earlier_count - recent_count})

        emerging.sort(key=lambda x: x["change"], reverse=True)
        declining.sort(key=lambda x: x["change"], reverse=True)
    else:
        emerging = []
        declining = []

    return {
        "period_days": days,
        "generated_at": datetime.now().isoformat(),
        "top_issues": all_issues,
        "weekly_breakdown": weekly_issues,
        "emerging_issues": emerging[:5],
        "declining_issues": declining[:5],
    }


def get_query_type_analysis(days: int = 30) -> Dict[str, Any]:
    """
    Analyze AI performance broken down by query type.

    Returns:
        Dictionary with performance metrics per query type
    """
    conn = get_connection()
    cursor = conn.cursor()

    period_start = (datetime.now() - timedelta(days=days)).isoformat()

    cursor.execute("""
        SELECT
            r.query_type,
            COUNT(DISTINCT r.response_id) as total_responses,
            AVG(r.confidence_score) as avg_confidence,
            COUNT(f.id) as feedback_count,
            SUM(CASE WHEN f.rating = 'positive' THEN 1 ELSE 0 END) as positive,
            SUM(CASE WHEN f.rating = 'negative' THEN 1 ELSE 0 END) as negative
        FROM ai_responses r
        LEFT JOIN feedback f ON r.response_id = f.response_id
        WHERE r.timestamp >= ? AND r.query_type != ''
        GROUP BY r.query_type
    """, (period_start,))

    results = {}
    for row in cursor.fetchall():
        query_type = row["query_type"]
        feedback_count = row["feedback_count"] or 0
        positive = row["positive"] or 0

        accuracy = (positive / feedback_count * 100) if feedback_count > 0 else None

        results[query_type] = {
            "total_responses": row["total_responses"],
            "avg_confidence": round(row["avg_confidence"], 1) if row["avg_confidence"] else 0,
            "feedback_count": feedback_count,
            "positive_feedback": positive,
            "negative_feedback": row["negative"] or 0,
            "accuracy_rate": round(accuracy, 1) if accuracy else None,
        }

    conn.close()

    # Identify best and worst performing query types
    with_accuracy = [(qt, data) for qt, data in results.items() if data["accuracy_rate"] is not None]
    with_accuracy.sort(key=lambda x: x[1]["accuracy_rate"], reverse=True)

    return {
        "period_days": days,
        "generated_at": datetime.now().isoformat(),
        "by_query_type": results,
        "best_performing": with_accuracy[0] if with_accuracy else None,
        "worst_performing": with_accuracy[-1] if with_accuracy else None,
    }


def generate_compliance_report(days: int = 30) -> Dict[str, Any]:
    """
    Generate a compliance-focused report suitable for CMMC/NIST documentation.

    This report provides evidence of AI oversight and continuous evaluation
    as required for CMMC Level 2 compliance.

    Returns:
        Dictionary with compliance-relevant metrics and evidence
    """
    metrics = get_performance_metrics(days=days)
    calibration = get_calibration_report(days=days)
    issues = get_issue_trend_report(days=days)

    conn = get_connection()
    cursor = conn.cursor()

    period_start = (datetime.now() - timedelta(days=days)).isoformat()

    # Get human review statistics
    cursor.execute("""
        SELECT
            human_review_level,
            COUNT(*) as count
        FROM ai_responses
        WHERE timestamp >= ?
        GROUP BY human_review_level
    """, (period_start,))
    review_stats = {row["human_review_level"]: row["count"] for row in cursor.fetchall()}

    # Get responses that had feedback corrections
    cursor.execute("""
        SELECT COUNT(DISTINCT f.response_id) as count
        FROM feedback f
        WHERE f.timestamp >= ? AND f.correction_text != ''
    """, (period_start,))
    corrected_responses = cursor.fetchone()["count"]

    conn.close()

    return {
        "report_type": "AI Oversight Compliance Report",
        "generated_at": datetime.now().isoformat(),
        "period": {
            "start": metrics.period_start,
            "end": metrics.period_end,
            "days": days,
        },
        "executive_summary": {
            "total_ai_responses": metrics.total_responses,
            "human_feedback_rate": f"{metrics.feedback_rate}%",
            "positive_feedback_rate": f"{metrics.positive_rate}%",
            "responses_corrected": corrected_responses,
            "calibration_status": calibration.get("overall_assessment", "Unknown"),
        },
        "human_oversight_evidence": {
            "responses_requiring_review": review_stats.get("REQUIRED", 0),
            "responses_recommended_review": review_stats.get("RECOMMENDED", 0),
            "responses_routine": review_stats.get("ROUTINE", 0),
            "feedback_submissions": metrics.total_feedback,
            "corrections_provided": corrected_responses,
        },
        "model_performance": {
            "average_confidence_score": metrics.avg_confidence_score,
            "calibration_error": metrics.calibration_error,
            "calibration_assessment": calibration.get("overall_assessment"),
            "by_confidence_level": calibration.get("by_confidence_level", {}),
        },
        "issue_tracking": {
            "top_issues": metrics.top_issues,
            "emerging_concerns": issues.get("emerging_issues", []),
        },
        "recommendations": _generate_recommendations(metrics, calibration, issues),
        "compliance_notes": [
            "This report demonstrates continuous AI oversight per NIST 800-171 control 3.3",
            "Human-in-the-loop feedback collection provides evidence of AI accountability",
            "Confidence calibration tracking ensures AI transparency requirements are met",
            "Issue trending enables proactive identification of model degradation",
        ],
    }


def _generate_recommendations(
    metrics: PerformanceMetrics,
    calibration: Dict[str, Any],
    issues: Dict[str, Any]
) -> List[str]:
    """Generate actionable recommendations based on metrics."""
    recommendations = []

    # Feedback rate recommendations
    if metrics.feedback_rate < 10:
        recommendations.append(
            "Low feedback rate ({:.1f}%). Consider encouraging users to provide "
            "more feedback on AI responses for better evaluation.".format(metrics.feedback_rate)
        )

    # Calibration recommendations
    if metrics.calibration_error > 20:
        recommendations.append(
            "Significant calibration error ({:.1f}%). Review system prompt to "
            "improve confidence level accuracy.".format(metrics.calibration_error)
        )

    # Check for overconfidence
    for level, data in calibration.get("by_confidence_level", {}).items():
        if level == "HIGH" and data.get("accuracy_rate") and data["accuracy_rate"] < 70:
            recommendations.append(
                f"HIGH confidence responses show only {data['accuracy_rate']}% accuracy. "
                "Model may be overconfident - consider adjusting confidence thresholds."
            )

    # Issue-based recommendations
    for issue in metrics.top_issues[:3]:
        if issue["count"] >= 5:
            recommendations.append(
                f"Recurring issue: {issue['description']} ({issue['count']} occurrences). "
                "Consider targeted prompt improvements."
            )

    # Emerging issues
    for emerging in issues.get("emerging_issues", [])[:2]:
        recommendations.append(
            f"Emerging issue trend: {emerging['category'].replace('_', ' ').title()}. "
            "Monitor closely for potential model degradation."
        )

    if not recommendations:
        recommendations.append("No immediate concerns identified. Continue monitoring.")

    return recommendations


def export_report_markdown(report: Dict[str, Any]) -> str:
    """
    Export a compliance report as markdown for documentation.

    Args:
        report: Report dictionary from generate_compliance_report()

    Returns:
        Markdown formatted string
    """
    lines = [
        f"# {report['report_type']}",
        "",
        f"**Generated:** {report['generated_at'][:19]}",
        f"**Period:** {report['period']['start'][:10]} to {report['period']['end'][:10]} ({report['period']['days']} days)",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
    ]

    summary = report["executive_summary"]
    lines.extend([
        f"- **Total AI Responses:** {summary['total_ai_responses']}",
        f"- **Human Feedback Rate:** {summary['human_feedback_rate']}",
        f"- **Positive Feedback Rate:** {summary['positive_feedback_rate']}",
        f"- **Responses Corrected:** {summary['responses_corrected']}",
        f"- **Calibration Status:** {summary['calibration_status']}",
        "",
        "## Human Oversight Evidence",
        "",
    ])

    oversight = report["human_oversight_evidence"]
    lines.extend([
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Responses Requiring Review | {oversight['responses_requiring_review']} |",
        f"| Responses Recommended Review | {oversight['responses_recommended_review']} |",
        f"| Responses Routine | {oversight['responses_routine']} |",
        f"| Feedback Submissions | {oversight['feedback_submissions']} |",
        f"| Corrections Provided | {oversight['corrections_provided']} |",
        "",
        "## Model Performance",
        "",
    ])

    perf = report["model_performance"]
    lines.extend([
        f"- **Average Confidence Score:** {perf['average_confidence_score']}%",
        f"- **Calibration Error:** {perf['calibration_error']}%",
        f"- **Assessment:** {perf['calibration_assessment']}",
        "",
    ])

    if perf.get("by_confidence_level"):
        lines.extend([
            "### Confidence Level Breakdown",
            "",
            "| Level | Responses | Feedback | Accuracy | Expected | Error |",
            "|-------|-----------|----------|----------|----------|-------|",
        ])
        for level, data in perf["by_confidence_level"].items():
            lines.append(
                f"| {level} | {data.get('total_responses', 0)} | "
                f"{data.get('feedback_count', 0)} | "
                f"{data.get('accuracy_rate', 'N/A')}% | "
                f"{data.get('expected_accuracy', 'N/A')}% | "
                f"{data.get('calibration_error', 'N/A')}% |"
            )
        lines.append("")

    if report.get("issue_tracking", {}).get("top_issues"):
        lines.extend([
            "## Issue Tracking",
            "",
            "### Top Issues",
            "",
        ])
        for issue in report["issue_tracking"]["top_issues"]:
            lines.append(f"- {issue['description']}: {issue['count']} occurrences")
        lines.append("")

    if report.get("recommendations"):
        lines.extend([
            "## Recommendations",
            "",
        ])
        for i, rec in enumerate(report["recommendations"], 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    if report.get("compliance_notes"):
        lines.extend([
            "## Compliance Notes",
            "",
        ])
        for note in report["compliance_notes"]:
            lines.append(f"- {note}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "*This report was automatically generated by the SysAdmin Agent AI Evaluation System.*",
    ])

    return "\n".join(lines)


def export_report_json(report: Dict[str, Any]) -> str:
    """Export report as JSON for programmatic access."""
    return json.dumps(report, indent=2)


if __name__ == "__main__":
    # Test report generation
    print("Generating evaluation reports...")

    print("\n=== Performance Metrics ===")
    metrics = get_performance_metrics(days=7)
    print(json.dumps(metrics.to_dict(), indent=2))

    print("\n=== Calibration Report ===")
    calibration = get_calibration_report(days=7)
    print(json.dumps(calibration, indent=2))

    print("\n=== Compliance Report (Markdown) ===")
    compliance = generate_compliance_report(days=7)
    print(export_report_markdown(compliance))
