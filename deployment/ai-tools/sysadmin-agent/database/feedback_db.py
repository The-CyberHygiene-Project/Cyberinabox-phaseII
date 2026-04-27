"""
AI Response Feedback Database

This module provides persistent storage for AI response feedback,
enabling continuous model evaluation and improvement tracking
as required for CMMC compliance and AI governance.

Schema Design:
- ai_responses: Stores parsed AI response metadata for correlation
- feedback: User ratings and corrections for responses
- evaluation_metrics: Aggregated metrics for reporting
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


# Database location
DB_PATH = Path(__file__).parent / "feedback.db"


class FeedbackRating(Enum):
    """User feedback rating for AI responses."""
    POSITIVE = "positive"      # Thumbs up - response was helpful/accurate
    NEGATIVE = "negative"      # Thumbs down - response had issues
    NEUTRAL = "neutral"        # No strong opinion


class IssueCategory(Enum):
    """Categories of issues identified in AI responses."""
    FACTUAL_ERROR = "factual_error"           # Incorrect technical information
    SECURITY_CONCERN = "security_concern"      # Recommendation could weaken security
    OVERCONFIDENCE = "overconfidence"          # Confidence level was too high
    UNDERCONFIDENCE = "underconfidence"        # Confidence level was too low
    MISSING_CONTEXT = "missing_context"        # Failed to consider important factors
    WRONG_HYPOTHESIS = "wrong_hypothesis"      # Primary hypothesis was incorrect
    INCOMPLETE = "incomplete"                  # Response was incomplete
    FORMATTING = "formatting"                  # Parsing/display issues
    OTHER = "other"


@dataclass
class ResponseFeedback:
    """Represents user feedback for an AI response."""
    feedback_id: Optional[int]
    response_id: str
    user_id: str
    rating: FeedbackRating
    issue_categories: List[IssueCategory]
    correction_text: str
    actual_confidence_level: str  # What confidence SHOULD have been
    actual_outcome: str           # What actually happened
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedback_id": self.feedback_id,
            "response_id": self.response_id,
            "user_id": self.user_id,
            "rating": self.rating.value,
            "issue_categories": [c.value for c in self.issue_categories],
            "correction_text": self.correction_text,
            "actual_confidence_level": self.actual_confidence_level,
            "actual_outcome": self.actual_outcome,
            "timestamp": self.timestamp,
        }


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """Initialize the feedback database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # AI Responses table - stores metadata for correlation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id TEXT UNIQUE NOT NULL,
            timestamp TEXT NOT NULL,
            query_type TEXT,
            source_data_summary TEXT,
            confidence_level TEXT,
            confidence_score INTEGER,
            human_review_level TEXT,
            analysis_summary TEXT,
            evidence_count INTEGER,
            alternatives_count INTEGER,
            validation_steps_count INTEGER,
            parsing_successful INTEGER,
            raw_response_hash TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Feedback table - user ratings and corrections
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            rating TEXT NOT NULL,
            issue_categories TEXT,
            correction_text TEXT,
            actual_confidence_level TEXT,
            actual_outcome TEXT,
            timestamp TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (response_id) REFERENCES ai_responses(response_id)
        )
    """)

    # Evaluation metrics table - aggregated statistics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_date TEXT NOT NULL,
            total_responses INTEGER DEFAULT 0,
            positive_feedback_count INTEGER DEFAULT 0,
            negative_feedback_count INTEGER DEFAULT 0,
            avg_confidence_score REAL,
            confidence_calibration_error REAL,
            high_confidence_accuracy REAL,
            medium_confidence_accuracy REAL,
            low_confidence_accuracy REAL,
            common_issues TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(metric_date)
        )
    """)

    # Indexes for query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_responses_timestamp
        ON ai_responses(timestamp)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_feedback_response
        ON feedback(response_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_feedback_timestamp
        ON feedback(timestamp)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_metrics_date
        ON evaluation_metrics(metric_date)
    """)

    conn.commit()
    conn.close()


def store_ai_response(response_data: Dict[str, Any]) -> bool:
    """
    Store an AI response for later feedback correlation.

    Args:
        response_data: Dictionary from ExplainableResponse.to_dict()

    Returns:
        True if stored successfully
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Create a hash of the raw response for deduplication
        import hashlib
        raw_hash = hashlib.sha256(
            response_data.get("raw_response", "").encode()
        ).hexdigest()[:16]

        cursor.execute("""
            INSERT OR REPLACE INTO ai_responses (
                response_id, timestamp, query_type, source_data_summary,
                confidence_level, confidence_score, human_review_level,
                analysis_summary, evidence_count, alternatives_count,
                validation_steps_count, parsing_successful, raw_response_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            response_data.get("response_id"),
            response_data.get("timestamp"),
            response_data.get("query_type", ""),
            response_data.get("source_data", "")[:200],
            response_data.get("confidence_level"),
            response_data.get("confidence_score", 0),
            response_data.get("human_review_level"),
            response_data.get("analysis", "")[:500],
            len(response_data.get("evidence", [])),
            len(response_data.get("alternative_hypotheses", [])),
            len(response_data.get("validation_steps", [])),
            1 if response_data.get("parsing_successful") else 0,
            raw_hash,
        ))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error storing AI response: {e}")
        return False
    finally:
        conn.close()


def store_feedback(feedback: ResponseFeedback) -> int:
    """
    Store user feedback for an AI response.

    Args:
        feedback: ResponseFeedback object

    Returns:
        The feedback ID, or -1 on error
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO feedback (
                response_id, user_id, rating, issue_categories,
                correction_text, actual_confidence_level, actual_outcome,
                timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback.response_id,
            feedback.user_id,
            feedback.rating.value,
            json.dumps([c.value for c in feedback.issue_categories]),
            feedback.correction_text,
            feedback.actual_confidence_level,
            feedback.actual_outcome,
            feedback.timestamp,
        ))

        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error storing feedback: {e}")
        return -1
    finally:
        conn.close()


def get_response_feedback(response_id: str) -> List[ResponseFeedback]:
    """Get all feedback for a specific response."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM feedback WHERE response_id = ?
        ORDER BY timestamp DESC
    """, (response_id,))

    results = []
    for row in cursor.fetchall():
        categories = json.loads(row["issue_categories"] or "[]")
        results.append(ResponseFeedback(
            feedback_id=row["id"],
            response_id=row["response_id"],
            user_id=row["user_id"],
            rating=FeedbackRating(row["rating"]),
            issue_categories=[IssueCategory(c) for c in categories],
            correction_text=row["correction_text"] or "",
            actual_confidence_level=row["actual_confidence_level"] or "",
            actual_outcome=row["actual_outcome"] or "",
            timestamp=row["timestamp"],
        ))

    conn.close()
    return results


def get_recent_responses(
    limit: int = 50,
    query_type: Optional[str] = None,
    has_feedback: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """
    Get recent AI responses with optional filtering.

    Args:
        limit: Maximum number of responses to return
        query_type: Filter by query type
        has_feedback: Filter by feedback status

    Returns:
        List of response dictionaries with feedback counts
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            r.*,
            COUNT(f.id) as feedback_count,
            SUM(CASE WHEN f.rating = 'positive' THEN 1 ELSE 0 END) as positive_count,
            SUM(CASE WHEN f.rating = 'negative' THEN 1 ELSE 0 END) as negative_count
        FROM ai_responses r
        LEFT JOIN feedback f ON r.response_id = f.response_id
    """

    conditions = []
    params = []

    if query_type:
        conditions.append("r.query_type = ?")
        params.append(query_type)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY r.response_id ORDER BY r.timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)

    results = []
    for row in cursor.fetchall():
        result = dict(row)
        if has_feedback is not None:
            if has_feedback and result["feedback_count"] == 0:
                continue
            if not has_feedback and result["feedback_count"] > 0:
                continue
        results.append(result)

    conn.close()
    return results


def calculate_confidence_calibration(
    days: int = 30
) -> Dict[str, Any]:
    """
    Calculate confidence calibration metrics.

    Compares AI confidence levels to actual accuracy based on feedback.
    A well-calibrated model should have:
    - HIGH confidence responses with ~80-100% positive feedback
    - MEDIUM confidence responses with ~50-79% positive feedback
    - LOW confidence responses with variable feedback

    Returns:
        Dictionary with calibration metrics
    """
    conn = get_connection()
    cursor = conn.cursor()

    since_date = (datetime.now() - timedelta(days=days)).isoformat()

    cursor.execute("""
        SELECT
            r.confidence_level,
            COUNT(DISTINCT r.response_id) as total_responses,
            COUNT(f.id) as feedback_count,
            SUM(CASE WHEN f.rating = 'positive' THEN 1 ELSE 0 END) as positive,
            SUM(CASE WHEN f.rating = 'negative' THEN 1 ELSE 0 END) as negative,
            AVG(r.confidence_score) as avg_confidence_score
        FROM ai_responses r
        LEFT JOIN feedback f ON r.response_id = f.response_id
        WHERE r.timestamp >= ?
        GROUP BY r.confidence_level
    """, (since_date,))

    results = {
        "period_days": days,
        "calculated_at": datetime.now().isoformat(),
        "by_confidence_level": {},
        "overall_calibration_error": 0.0,
    }

    total_error = 0.0
    level_count = 0

    for row in cursor.fetchall():
        level = row["confidence_level"] or "UNKNOWN"
        feedback_count = row["feedback_count"] or 0
        positive = row["positive"] or 0

        # Calculate accuracy rate from feedback
        accuracy = (positive / feedback_count * 100) if feedback_count > 0 else None

        # Expected accuracy based on confidence level
        expected = {"HIGH": 85, "MEDIUM": 65, "LOW": 35, "UNKNOWN": 50}
        expected_accuracy = expected.get(level, 50)

        # Calibration error (how far off is the confidence from actual accuracy)
        calibration_error = abs(accuracy - expected_accuracy) if accuracy else None

        if calibration_error is not None:
            total_error += calibration_error
            level_count += 1

        results["by_confidence_level"][level] = {
            "total_responses": row["total_responses"],
            "feedback_count": feedback_count,
            "positive_feedback": positive,
            "negative_feedback": row["negative"] or 0,
            "accuracy_rate": round(accuracy, 1) if accuracy else None,
            "expected_accuracy": expected_accuracy,
            "calibration_error": round(calibration_error, 1) if calibration_error else None,
            "avg_confidence_score": round(row["avg_confidence_score"], 1) if row["avg_confidence_score"] else None,
        }

    results["overall_calibration_error"] = round(total_error / level_count, 1) if level_count > 0 else None

    conn.close()
    return results


def get_common_issues(days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the most common issues identified in feedback.

    Returns:
        List of issue categories with counts
    """
    conn = get_connection()
    cursor = conn.cursor()

    since_date = (datetime.now() - timedelta(days=days)).isoformat()

    cursor.execute("""
        SELECT issue_categories FROM feedback
        WHERE timestamp >= ? AND issue_categories != '[]'
    """, (since_date,))

    issue_counts: Dict[str, int] = {}
    for row in cursor.fetchall():
        categories = json.loads(row["issue_categories"] or "[]")
        for category in categories:
            issue_counts[category] = issue_counts.get(category, 0) + 1

    conn.close()

    # Sort by count and return top issues
    sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
    return [
        {"category": cat, "count": count, "description": IssueCategory(cat).name.replace("_", " ").title()}
        for cat, count in sorted_issues[:limit]
    ]


def generate_daily_metrics(date: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate and store daily evaluation metrics.

    Args:
        date: Date string (YYYY-MM-DD), defaults to today

    Returns:
        Dictionary with the generated metrics
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    cursor = conn.cursor()

    # Get response counts for the day
    cursor.execute("""
        SELECT COUNT(*) as total FROM ai_responses
        WHERE DATE(timestamp) = ?
    """, (date,))
    total_responses = cursor.fetchone()["total"]

    # Get feedback counts
    cursor.execute("""
        SELECT
            SUM(CASE WHEN rating = 'positive' THEN 1 ELSE 0 END) as positive,
            SUM(CASE WHEN rating = 'negative' THEN 1 ELSE 0 END) as negative
        FROM feedback
        WHERE DATE(timestamp) = ?
    """, (date,))
    row = cursor.fetchone()
    positive_count = row["positive"] or 0
    negative_count = row["negative"] or 0

    # Get average confidence score
    cursor.execute("""
        SELECT AVG(confidence_score) as avg_score FROM ai_responses
        WHERE DATE(timestamp) = ?
    """, (date,))
    avg_confidence = cursor.fetchone()["avg_score"]

    # Get calibration data
    calibration = calculate_confidence_calibration(days=1)

    # Get common issues for the day
    common_issues = get_common_issues(days=1, limit=5)

    # Store metrics
    cursor.execute("""
        INSERT OR REPLACE INTO evaluation_metrics (
            metric_date, total_responses, positive_feedback_count,
            negative_feedback_count, avg_confidence_score,
            confidence_calibration_error, common_issues
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        date,
        total_responses,
        positive_count,
        negative_count,
        avg_confidence,
        calibration.get("overall_calibration_error"),
        json.dumps(common_issues),
    ))

    conn.commit()
    conn.close()

    return {
        "date": date,
        "total_responses": total_responses,
        "positive_feedback": positive_count,
        "negative_feedback": negative_count,
        "avg_confidence_score": round(avg_confidence, 1) if avg_confidence else None,
        "calibration_error": calibration.get("overall_calibration_error"),
        "common_issues": common_issues,
    }


def get_metrics_history(days: int = 30) -> List[Dict[str, Any]]:
    """Get historical evaluation metrics."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM evaluation_metrics
        ORDER BY metric_date DESC
        LIMIT ?
    """, (days,))

    results = []
    for row in cursor.fetchall():
        result = dict(row)
        result["common_issues"] = json.loads(result["common_issues"] or "[]")
        results.append(result)

    conn.close()
    return results


def get_feedback_summary() -> Dict[str, Any]:
    """Get overall feedback summary statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total counts
    cursor.execute("SELECT COUNT(*) as count FROM ai_responses")
    total_responses = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM feedback")
    total_feedback = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT
            SUM(CASE WHEN rating = 'positive' THEN 1 ELSE 0 END) as positive,
            SUM(CASE WHEN rating = 'negative' THEN 1 ELSE 0 END) as negative,
            SUM(CASE WHEN rating = 'neutral' THEN 1 ELSE 0 END) as neutral
        FROM feedback
    """)
    row = cursor.fetchone()

    # Responses needing feedback
    cursor.execute("""
        SELECT COUNT(DISTINCT r.response_id) as count
        FROM ai_responses r
        LEFT JOIN feedback f ON r.response_id = f.response_id
        WHERE f.id IS NULL
    """)
    needs_feedback = cursor.fetchone()["count"]

    conn.close()

    feedback_rate = (total_feedback / total_responses * 100) if total_responses > 0 else 0

    return {
        "total_responses": total_responses,
        "total_feedback": total_feedback,
        "feedback_rate": round(feedback_rate, 1),
        "positive_feedback": row["positive"] or 0,
        "negative_feedback": row["negative"] or 0,
        "neutral_feedback": row["neutral"] or 0,
        "responses_needing_feedback": needs_feedback,
    }


# Initialize database on module import
init_database()
