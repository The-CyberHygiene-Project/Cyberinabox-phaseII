"""
Explainable AI Response Schema and Parsing Utilities

This module provides structured data types for AI responses that include
confidence levels, evidence, alternative hypotheses, and validation steps
as required for CMMC compliance and human oversight.
"""

import re
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence levels for AI assessments."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, value: str) -> "ConfidenceLevel":
        """Parse confidence level from string."""
        value_upper = value.upper().strip()
        if "HIGH" in value_upper:
            return cls.HIGH
        elif "MEDIUM" in value_upper or "MODERATE" in value_upper:
            return cls.MEDIUM
        elif "LOW" in value_upper:
            return cls.LOW
        return cls.UNKNOWN


class HumanReviewLevel(Enum):
    """Human review requirement levels."""
    REQUIRED = "REQUIRED"
    RECOMMENDED = "RECOMMENDED"
    ROUTINE = "ROUTINE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, value: str) -> "HumanReviewLevel":
        """Parse human review level from string."""
        value_upper = value.upper().strip()
        if "REQUIRED" in value_upper:
            return cls.REQUIRED
        elif "RECOMMENDED" in value_upper:
            return cls.RECOMMENDED
        elif "ROUTINE" in value_upper:
            return cls.ROUTINE
        return cls.UNKNOWN


@dataclass
class ExplainableResponse:
    """
    Structured representation of an explainable AI response.

    This schema captures the key elements required for transparent,
    auditable AI-assisted decision making in security contexts.
    """
    # Unique identifier for this response
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Timestamp when response was generated
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # The main analysis/response content
    analysis: str = ""

    # Confidence assessment
    confidence_level: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    confidence_score: int = 0  # 0-100 percentage
    confidence_justification: str = ""

    # Supporting evidence
    evidence: List[str] = field(default_factory=list)

    # Alternative explanations
    alternative_hypotheses: List[str] = field(default_factory=list)

    # Steps to verify the analysis
    validation_steps: List[str] = field(default_factory=list)

    # Human review requirement
    human_review_level: HumanReviewLevel = HumanReviewLevel.UNKNOWN
    human_review_reason: str = ""

    # Recommended action (if any)
    recommended_action: str = ""

    # Original raw response text
    raw_response: str = ""

    # Parsing metadata
    parsing_successful: bool = False
    parsing_errors: List[str] = field(default_factory=list)

    # Context information
    query_type: str = ""  # e.g., "log_analysis", "security_scan", "health_check"
    source_data: str = ""  # What data was analyzed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "response_id": self.response_id,
            "timestamp": self.timestamp,
            "analysis": self.analysis,
            "confidence_level": self.confidence_level.value,
            "confidence_score": self.confidence_score,
            "confidence_justification": self.confidence_justification,
            "evidence": self.evidence,
            "alternative_hypotheses": self.alternative_hypotheses,
            "validation_steps": self.validation_steps,
            "human_review_level": self.human_review_level.value,
            "human_review_reason": self.human_review_reason,
            "recommended_action": self.recommended_action,
            "raw_response": self.raw_response,
            "parsing_successful": self.parsing_successful,
            "parsing_errors": self.parsing_errors,
            "query_type": self.query_type,
            "source_data": self.source_data,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExplainableResponse":
        """Create from dictionary."""
        return cls(
            response_id=data.get("response_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            analysis=data.get("analysis", ""),
            confidence_level=ConfidenceLevel(data.get("confidence_level", "UNKNOWN")),
            confidence_score=data.get("confidence_score", 0),
            confidence_justification=data.get("confidence_justification", ""),
            evidence=data.get("evidence", []),
            alternative_hypotheses=data.get("alternative_hypotheses", []),
            validation_steps=data.get("validation_steps", []),
            human_review_level=HumanReviewLevel(data.get("human_review_level", "UNKNOWN")),
            human_review_reason=data.get("human_review_reason", ""),
            recommended_action=data.get("recommended_action", ""),
            raw_response=data.get("raw_response", ""),
            parsing_successful=data.get("parsing_successful", False),
            parsing_errors=data.get("parsing_errors", []),
            query_type=data.get("query_type", ""),
            source_data=data.get("source_data", ""),
        )

    def is_actionable(self) -> bool:
        """Check if response requires action."""
        return bool(self.recommended_action) and self.confidence_level != ConfidenceLevel.LOW

    def requires_human_review(self) -> bool:
        """Check if human review is required or recommended."""
        return self.human_review_level in [HumanReviewLevel.REQUIRED, HumanReviewLevel.RECOMMENDED]

    def get_summary(self) -> str:
        """Get a brief summary of the response for display."""
        return (
            f"[{self.confidence_level.value} {self.confidence_score}%] "
            f"{self.analysis[:100]}{'...' if len(self.analysis) > 100 else ''} "
            f"(Review: {self.human_review_level.value})"
        )


def parse_ai_response(
    raw_response: str,
    query_type: str = "",
    source_data: str = ""
) -> ExplainableResponse:
    """
    Parse an AI response text into a structured ExplainableResponse.

    This function extracts confidence levels, evidence, alternative hypotheses,
    validation steps, and human review requirements from the AI's text response.

    Args:
        raw_response: The raw text response from the AI
        query_type: Type of query (e.g., "log_analysis", "security_scan")
        source_data: Description of what data was analyzed

    Returns:
        ExplainableResponse with parsed fields
    """
    response = ExplainableResponse(
        raw_response=raw_response,
        query_type=query_type,
        source_data=source_data,
    )

    parsing_errors = []

    # Extract confidence level and score
    confidence_match = re.search(
        r'\*\*Confidence:\*\*\s*(\w+)\s*\((\d+)%?\)',
        raw_response,
        re.IGNORECASE
    )
    if confidence_match:
        response.confidence_level = ConfidenceLevel.from_string(confidence_match.group(1))
        response.confidence_score = int(confidence_match.group(2))

        # Extract justification (text after the percentage)
        justification_match = re.search(
            r'\*\*Confidence:\*\*\s*\w+\s*\(\d+%?\)\s*[-–—]?\s*(.+?)(?=\n\*\*|\n\n|$)',
            raw_response,
            re.IGNORECASE | re.DOTALL
        )
        if justification_match:
            response.confidence_justification = justification_match.group(1).strip()
    else:
        parsing_errors.append("Could not parse confidence level")

    # Extract evidence
    evidence_match = re.search(
        r'\*\*Evidence:\*\*\s*\n((?:\s*\d+\.\s*.+\n?)+)',
        raw_response,
        re.IGNORECASE
    )
    if evidence_match:
        evidence_text = evidence_match.group(1)
        evidence_items = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|\n\*\*|$)', evidence_text, re.DOTALL)
        response.evidence = [item.strip() for item in evidence_items if item.strip()]
    else:
        # Try bullet point format
        evidence_match = re.search(
            r'\*\*Evidence:\*\*\s*\n((?:\s*[-•]\s*.+\n?)+)',
            raw_response,
            re.IGNORECASE
        )
        if evidence_match:
            evidence_text = evidence_match.group(1)
            evidence_items = re.findall(r'[-•]\s*(.+?)(?=\n[-•]|\n\n|\n\*\*|$)', evidence_text, re.DOTALL)
            response.evidence = [item.strip() for item in evidence_items if item.strip()]
        else:
            parsing_errors.append("Could not parse evidence section")

    # Extract alternative hypotheses
    alt_match = re.search(
        r'\*\*Alternative Hypotheses:\*\*\s*\n((?:\s*\d+\.\s*.+\n?)+)',
        raw_response,
        re.IGNORECASE
    )
    if alt_match:
        alt_text = alt_match.group(1)
        alt_items = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|\n\*\*|$)', alt_text, re.DOTALL)
        response.alternative_hypotheses = [item.strip() for item in alt_items if item.strip()]
    else:
        # Check for "None identified" or similar
        none_match = re.search(
            r'\*\*Alternative Hypotheses:\*\*\s*[:\-]?\s*(None identified|N/A|None)',
            raw_response,
            re.IGNORECASE
        )
        if none_match:
            response.alternative_hypotheses = ["None identified"]
        else:
            parsing_errors.append("Could not parse alternative hypotheses section")

    # Extract validation steps
    validation_match = re.search(
        r'\*\*Validation Steps:\*\*\s*\n((?:\s*\d+\.\s*.+\n?)+)',
        raw_response,
        re.IGNORECASE
    )
    if validation_match:
        validation_text = validation_match.group(1)
        validation_items = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|\n\*\*|$)', validation_text, re.DOTALL)
        response.validation_steps = [item.strip() for item in validation_items if item.strip()]
    else:
        parsing_errors.append("Could not parse validation steps section")

    # Extract human review level
    review_match = re.search(
        r'\*\*Human Review:\*\*\s*(\w+)\s*[-–—]?\s*(.+?)(?=\n\*\*|\n\n|$)',
        raw_response,
        re.IGNORECASE
    )
    if review_match:
        response.human_review_level = HumanReviewLevel.from_string(review_match.group(1))
        response.human_review_reason = review_match.group(2).strip()
    else:
        parsing_errors.append("Could not parse human review section")

    # Extract main analysis (everything before the structured sections)
    analysis_match = re.search(
        r'^(.*?)(?=\*\*Confidence:\*\*|\*\*Evidence:\*\*)',
        raw_response,
        re.DOTALL | re.IGNORECASE
    )
    if analysis_match:
        response.analysis = analysis_match.group(1).strip()
    else:
        # If no structured sections found, use the whole response as analysis
        response.analysis = raw_response.strip()

    # Set parsing status
    response.parsing_errors = parsing_errors
    response.parsing_successful = len(parsing_errors) == 0

    return response


def create_explainable_response(
    analysis: str,
    confidence_level: str,
    confidence_score: int,
    evidence: List[str],
    alternative_hypotheses: List[str],
    validation_steps: List[str],
    human_review_level: str,
    query_type: str = "",
    source_data: str = "",
    recommended_action: str = "",
) -> ExplainableResponse:
    """
    Create an ExplainableResponse from individual components.

    Use this when programmatically creating responses rather than parsing AI text.
    """
    return ExplainableResponse(
        analysis=analysis,
        confidence_level=ConfidenceLevel.from_string(confidence_level),
        confidence_score=confidence_score,
        confidence_justification="",
        evidence=evidence,
        alternative_hypotheses=alternative_hypotheses,
        validation_steps=validation_steps,
        human_review_level=HumanReviewLevel.from_string(human_review_level),
        recommended_action=recommended_action,
        query_type=query_type,
        source_data=source_data,
        parsing_successful=True,
    )


def format_explainable_response(response: ExplainableResponse) -> str:
    """
    Format an ExplainableResponse as a human-readable markdown string.

    This is useful for displaying structured responses in the UI.
    """
    output = []

    # Main analysis
    if response.analysis:
        output.append(response.analysis)
        output.append("")

    # Confidence
    confidence_color = {
        ConfidenceLevel.HIGH: "🟢",
        ConfidenceLevel.MEDIUM: "🟡",
        ConfidenceLevel.LOW: "🔴",
        ConfidenceLevel.UNKNOWN: "⚪",
    }
    icon = confidence_color.get(response.confidence_level, "⚪")
    output.append(f"**Confidence:** {icon} {response.confidence_level.value} ({response.confidence_score}%)")
    if response.confidence_justification:
        output.append(f"  _{response.confidence_justification}_")
    output.append("")

    # Evidence
    if response.evidence:
        output.append("**Evidence:**")
        for i, item in enumerate(response.evidence, 1):
            output.append(f"{i}. {item}")
        output.append("")

    # Alternative hypotheses
    if response.alternative_hypotheses:
        output.append("**Alternative Hypotheses:**")
        for i, item in enumerate(response.alternative_hypotheses, 1):
            output.append(f"{i}. {item}")
        output.append("")

    # Validation steps
    if response.validation_steps:
        output.append("**Validation Steps:**")
        for i, item in enumerate(response.validation_steps, 1):
            output.append(f"{i}. {item}")
        output.append("")

    # Human review
    review_icon = {
        HumanReviewLevel.REQUIRED: "🔴",
        HumanReviewLevel.RECOMMENDED: "🟡",
        HumanReviewLevel.ROUTINE: "🟢",
        HumanReviewLevel.UNKNOWN: "⚪",
    }
    icon = review_icon.get(response.human_review_level, "⚪")
    output.append(f"**Human Review:** {icon} {response.human_review_level.value}")
    if response.human_review_reason:
        output.append(f"  _{response.human_review_reason}_")

    return "\n".join(output)
