#!/usr/bin/env python3
"""
Daily AI Evaluation Script

This script runs as a scheduled task to:
1. Generate daily evaluation metrics
2. Check for model degradation
3. Send alerts if thresholds are exceeded
4. Archive reports for compliance

Run via systemd timer or cron for automated daily evaluation.
"""

import sys
import json
import smtplib
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.feedback_db import generate_daily_metrics, get_feedback_summary
from database.evaluation_reports import (
    get_performance_metrics,
    get_calibration_report,
    generate_compliance_report,
    export_report_markdown,
)

# Configuration
REPORTS_DIR = Path(__file__).parent.parent / "reports"
ALERT_THRESHOLDS = {
    "calibration_error_max": 25.0,      # Alert if calibration error > 25%
    "negative_rate_max": 40.0,          # Alert if negative feedback > 40%
    "feedback_rate_min": 5.0,           # Alert if feedback rate < 5%
}
ALERT_LOG = Path(__file__).parent.parent / "logs" / "evaluation_alerts.log"


def ensure_directories():
    """Ensure required directories exist."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)


def log_alert(message: str, severity: str = "WARNING"):
    """Log an alert to the alert log file."""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] [{severity}] {message}\n"

    with open(ALERT_LOG, "a") as f:
        f.write(log_entry)

    print(f"{severity}: {message}")


def check_thresholds(metrics) -> list:
    """Check metrics against alert thresholds."""
    alerts = []

    if metrics.calibration_error > ALERT_THRESHOLDS["calibration_error_max"]:
        alerts.append({
            "type": "CALIBRATION_ERROR",
            "severity": "HIGH",
            "message": f"Calibration error ({metrics.calibration_error}%) exceeds threshold ({ALERT_THRESHOLDS['calibration_error_max']}%)",
            "recommendation": "Review system prompt and confidence level guidelines",
        })

    if metrics.negative_rate > ALERT_THRESHOLDS["negative_rate_max"]:
        alerts.append({
            "type": "HIGH_NEGATIVE_FEEDBACK",
            "severity": "HIGH",
            "message": f"Negative feedback rate ({metrics.negative_rate}%) exceeds threshold ({ALERT_THRESHOLDS['negative_rate_max']}%)",
            "recommendation": "Analyze recent negative feedback for patterns",
        })

    if metrics.total_responses > 10 and metrics.feedback_rate < ALERT_THRESHOLDS["feedback_rate_min"]:
        alerts.append({
            "type": "LOW_FEEDBACK_RATE",
            "severity": "MEDIUM",
            "message": f"Feedback rate ({metrics.feedback_rate}%) below threshold ({ALERT_THRESHOLDS['feedback_rate_min']}%)",
            "recommendation": "Encourage users to provide feedback on AI responses",
        })

    return alerts


def generate_daily_report():
    """Generate and save the daily evaluation report."""
    today = datetime.now().strftime("%Y-%m-%d")

    print(f"Generating daily evaluation report for {today}...")

    # Generate daily metrics
    daily_metrics = generate_daily_metrics(today)
    print(f"  Daily metrics: {daily_metrics['total_responses']} responses, {daily_metrics['positive_feedback']} positive feedback")

    # Get 7-day performance metrics
    metrics = get_performance_metrics(days=7)

    # Check thresholds and log alerts
    alerts = check_thresholds(metrics)
    for alert in alerts:
        log_alert(f"{alert['type']}: {alert['message']}", alert['severity'])

    # Generate compliance report
    compliance_report = generate_compliance_report(days=7)

    # Add alerts to report
    if alerts:
        compliance_report["alerts"] = alerts

    # Save reports
    report_date = datetime.now().strftime("%Y%m%d")

    # Save JSON report
    json_path = REPORTS_DIR / f"evaluation_report_{report_date}.json"
    with open(json_path, "w") as f:
        json.dump(compliance_report, f, indent=2)
    print(f"  Saved JSON report: {json_path}")

    # Save Markdown report
    md_path = REPORTS_DIR / f"evaluation_report_{report_date}.md"
    md_content = export_report_markdown(compliance_report)

    # Add alerts section to markdown
    if alerts:
        alert_lines = ["\n## Alerts\n"]
        for alert in alerts:
            alert_lines.append(f"### {alert['severity']}: {alert['type']}")
            alert_lines.append(f"- {alert['message']}")
            alert_lines.append(f"- **Recommendation:** {alert['recommendation']}\n")
        md_content += "\n".join(alert_lines)

    with open(md_path, "w") as f:
        f.write(md_content)
    print(f"  Saved Markdown report: {md_path}")

    # Clean up old reports (keep last 90 days)
    cleanup_old_reports(90)

    return {
        "date": today,
        "metrics": metrics.to_dict(),
        "alerts": alerts,
        "reports": {
            "json": str(json_path),
            "markdown": str(md_path),
        }
    }


def cleanup_old_reports(keep_days: int = 90):
    """Remove reports older than keep_days."""
    cutoff = datetime.now() - timedelta(days=keep_days)

    for report_file in REPORTS_DIR.glob("evaluation_report_*.json"):
        try:
            # Extract date from filename
            date_str = report_file.stem.split("_")[-1]
            file_date = datetime.strptime(date_str, "%Y%m%d")
            if file_date < cutoff:
                report_file.unlink()
                # Also remove corresponding markdown
                md_file = report_file.with_suffix(".md")
                if md_file.exists():
                    md_file.unlink()
                print(f"  Cleaned up old report: {report_file.name}")
        except (ValueError, IndexError):
            continue


def get_trend_data(days: int = 30) -> dict:
    """Get trend data for dashboard visualization."""
    from database.feedback_db import get_metrics_history

    history = get_metrics_history(days=days)

    return {
        "dates": [h["metric_date"] for h in history],
        "response_counts": [h["total_responses"] for h in history],
        "positive_feedback": [h["positive_feedback_count"] for h in history],
        "negative_feedback": [h["negative_feedback_count"] for h in history],
        "calibration_errors": [h.get("confidence_calibration_error") for h in history],
        "avg_confidence": [h.get("avg_confidence_score") for h in history],
    }


def generate_weekly_summary():
    """Generate a weekly summary email (if configured)."""
    metrics = get_performance_metrics(days=7)
    calibration = get_calibration_report(days=7)

    summary = f"""
AI Evaluation Weekly Summary
============================
Period: Last 7 days
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Performance Metrics
-------------------
Total Responses: {metrics.total_responses}
Feedback Rate: {metrics.feedback_rate}%
Positive Feedback: {metrics.positive_rate}%
Negative Feedback: {metrics.negative_rate}%

Calibration Status
------------------
Average Confidence: {metrics.avg_confidence_score}%
Calibration Error: {metrics.calibration_error}%
Assessment: {calibration.get('overall_assessment', 'N/A')}

Top Issues
----------
"""
    for issue in metrics.top_issues[:5]:
        summary += f"- {issue['description']}: {issue['count']} occurrences\n"

    alerts = check_thresholds(metrics)
    if alerts:
        summary += "\nAlerts\n------\n"
        for alert in alerts:
            summary += f"[{alert['severity']}] {alert['message']}\n"

    return summary


if __name__ == "__main__":
    ensure_directories()

    print("=" * 60)
    print("AI Evaluation Daily Report Generator")
    print("=" * 60)

    result = generate_daily_report()

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Date: {result['date']}")
    print(f"Total Responses (7-day): {result['metrics']['total_responses']}")
    print(f"Feedback Rate: {result['metrics']['feedback_rate']}%")
    print(f"Calibration Error: {result['metrics']['calibration_error']}%")

    if result['alerts']:
        print(f"\n⚠️  {len(result['alerts'])} alert(s) generated")
        for alert in result['alerts']:
            print(f"  [{alert['severity']}] {alert['type']}")
    else:
        print("\n✅ No alerts - all metrics within thresholds")

    print(f"\nReports saved to: {REPORTS_DIR}")
