"""
Database package for SysAdmin Agent Dashboard.
Contains feedback storage and evaluation metrics.
"""

from .feedback_db import (
    # Enums
    FeedbackRating,
    IssueCategory,
    # Data classes
    ResponseFeedback,
    # Core functions
    init_database,
    get_connection,
    store_ai_response,
    store_feedback,
    get_response_feedback,
    get_recent_responses,
    # Analytics
    calculate_confidence_calibration,
    get_common_issues,
    generate_daily_metrics,
    get_metrics_history,
    get_feedback_summary,
)

from .evaluation_reports import (
    # Data classes
    PerformanceMetrics,
    # Report functions
    get_performance_metrics,
    get_calibration_report,
    get_issue_trend_report,
    get_query_type_analysis,
    generate_compliance_report,
    # Export functions
    export_report_markdown,
    export_report_json,
)

__all__ = [
    # Feedback DB
    "FeedbackRating",
    "IssueCategory",
    "ResponseFeedback",
    "init_database",
    "get_connection",
    "store_ai_response",
    "store_feedback",
    "get_response_feedback",
    "get_recent_responses",
    "calculate_confidence_calibration",
    "get_common_issues",
    "generate_daily_metrics",
    "get_metrics_history",
    "get_feedback_summary",
    # Evaluation Reports
    "PerformanceMetrics",
    "get_performance_metrics",
    "get_calibration_report",
    "get_issue_trend_report",
    "get_query_type_analysis",
    "generate_compliance_report",
    "export_report_markdown",
    "export_report_json",
]
