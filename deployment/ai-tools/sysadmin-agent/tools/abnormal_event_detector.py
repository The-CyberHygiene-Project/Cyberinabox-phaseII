"""
Automated Abnormal Event Detection

This module monitors system logs for security-relevant events that may indicate
unauthorized access attempts, data exfiltration, or policy violations.

Events monitored:
- Failed login attempts (SSH, PAM, Kerberos)
- Sensitive data transfers at unusual hours
- USBGuard policy violations and bypass attempts
- SELinux denials for security-sensitive operations

All detections include explainable AI elements:
- Confidence scores based on pattern severity
- Evidence from log entries
- Alternative hypotheses for benign explanations
- Recommended validation steps
"""

import re
import subprocess
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class EventSeverity(Enum):
    """Severity levels for detected events."""
    CRITICAL = "CRITICAL"   # Immediate attention required
    HIGH = "HIGH"           # Significant security concern
    MEDIUM = "MEDIUM"       # Notable but may be benign
    LOW = "LOW"             # Informational, likely benign
    INFO = "INFO"           # Normal activity logged for context


class EventCategory(Enum):
    """Categories of abnormal events."""
    FAILED_LOGIN = "failed_login"
    DATA_TRANSFER = "data_transfer"
    USB_VIOLATION = "usb_violation"
    SELINUX_SECURITY = "selinux_security"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    AFTER_HOURS_ACTIVITY = "after_hours_activity"


@dataclass
class AbnormalEvent:
    """Represents a detected abnormal event."""
    event_id: str
    timestamp: str
    category: EventCategory
    severity: EventSeverity
    summary: str
    details: str
    source_log: str
    raw_entries: List[str]

    # Explainable AI fields
    confidence_score: int  # 0-100
    evidence: List[str]
    alternative_hypotheses: List[str]
    validation_steps: List[str]
    recommended_action: str
    human_review_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "category": self.category.value,
            "severity": self.severity.value,
            "summary": self.summary,
            "details": self.details,
            "source_log": self.source_log,
            "raw_entries": self.raw_entries,
            "confidence_score": self.confidence_score,
            "evidence": self.evidence,
            "alternative_hypotheses": self.alternative_hypotheses,
            "validation_steps": self.validation_steps,
            "recommended_action": self.recommended_action,
            "human_review_required": self.human_review_required,
        }


def generate_event_id() -> str:
    """Generate a unique event ID."""
    import uuid
    return f"EVT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"


def is_after_hours(timestamp: datetime) -> bool:
    """
    Check if timestamp is outside normal business hours.
    Business hours: Mon-Fri, 7:00 AM - 6:00 PM
    """
    if timestamp.weekday() >= 5:  # Saturday or Sunday
        return True
    hour = timestamp.hour
    return hour < 7 or hour >= 18


def run_journalctl(
    unit: Optional[str] = None,
    since: str = "1 hour ago",
    grep: Optional[str] = None,
    priority: Optional[str] = None
) -> List[str]:
    """Run journalctl and return output lines."""
    cmd = ["journalctl", "--no-pager", "-o", "short-iso"]

    if unit:
        cmd.extend(["-u", unit])
    if since:
        cmd.extend(["--since", since])
    if priority:
        cmd.extend(["-p", priority])
    if grep:
        cmd.extend(["-g", grep])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception as e:
        return [f"Error running journalctl: {e}"]


def read_log_file(
    filepath: str,
    since_minutes: int = 60,
    grep_pattern: Optional[str] = None
) -> List[str]:
    """Read recent entries from a log file."""
    try:
        path = Path(filepath)
        if not path.exists():
            return []

        cutoff = datetime.now() - timedelta(minutes=since_minutes)
        lines = []

        with open(path, 'r', errors='ignore') as f:
            for line in f:
                # Try to extract timestamp from common log formats
                if grep_pattern and grep_pattern.lower() not in line.lower():
                    continue
                lines.append(line.strip())

        # Return last 500 lines max
        return lines[-500:]
    except Exception as e:
        return [f"Error reading {filepath}: {e}"]


def detect_failed_logins(since_minutes: int = 60) -> List[AbnormalEvent]:
    """
    Detect failed login attempts from SSH, PAM, and authentication logs.

    Patterns detected:
    - SSH authentication failures
    - PAM authentication failures
    - Invalid user attempts
    - Brute force patterns (multiple failures from same source)
    """
    events = []

    # Get auth-related log entries
    auth_entries = run_journalctl(
        since=f"{since_minutes} minutes ago",
        grep="(Failed|failure|invalid|denied|authentication)"
    )

    # Track failed attempts by source IP
    failed_by_ip: Dict[str, List[str]] = {}
    failed_by_user: Dict[str, List[str]] = {}

    ssh_failure_pattern = re.compile(
        r'Failed (password|publickey) for (invalid user )?(\S+) from (\S+)'
    )
    pam_failure_pattern = re.compile(
        r'pam_unix.*authentication failure.*user=(\S+)'
    )

    for entry in auth_entries:
        if not entry or entry.startswith("Error"):
            continue

        # SSH failures
        ssh_match = ssh_failure_pattern.search(entry)
        if ssh_match:
            user = ssh_match.group(3)
            ip = ssh_match.group(4)

            if ip not in failed_by_ip:
                failed_by_ip[ip] = []
            failed_by_ip[ip].append(entry)

            if user not in failed_by_user:
                failed_by_user[user] = []
            failed_by_user[user].append(entry)

        # PAM failures
        pam_match = pam_failure_pattern.search(entry)
        if pam_match:
            user = pam_match.group(1)
            if user not in failed_by_user:
                failed_by_user[user] = []
            failed_by_user[user].append(entry)

    # Analyze patterns for brute force
    for ip, entries in failed_by_ip.items():
        if len(entries) >= 3:  # 3+ failures from same IP
            severity = EventSeverity.HIGH if len(entries) >= 10 else EventSeverity.MEDIUM
            confidence = min(90, 50 + len(entries) * 5)

            # Check if this is an internal IP (may be automated health checks)
            is_internal = ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172.")

            alt_hypotheses = [
                "Automated monitoring or health check with incorrect credentials" if is_internal else "Targeted brute force attack",
                "User mistyping password repeatedly",
                "Service account with expired credentials",
            ]

            if is_internal and len(entries) < 10:
                severity = EventSeverity.LOW
                confidence = max(30, confidence - 30)

            event = AbnormalEvent(
                event_id=generate_event_id(),
                timestamp=datetime.now().isoformat(),
                category=EventCategory.FAILED_LOGIN,
                severity=severity,
                summary=f"Multiple failed login attempts from {ip} ({len(entries)} failures)",
                details=f"Detected {len(entries)} failed authentication attempts from IP {ip} in the last {since_minutes} minutes. This pattern may indicate a brute force attack or misconfigured service.",
                source_log="journald/sshd",
                raw_entries=entries[:10],  # Limit to first 10
                confidence_score=confidence,
                evidence=[
                    f"{len(entries)} failed attempts from {ip}",
                    f"First attempt: {entries[0][:100]}...",
                    f"Internal IP: {is_internal}",
                ],
                alternative_hypotheses=alt_hypotheses,
                validation_steps=[
                    f"Check if {ip} is a known internal service: `host {ip}`",
                    f"Review full auth log: `journalctl -u sshd --since '{since_minutes} minutes ago' | grep {ip}`",
                    "Check if there's a service account that needs credential update",
                    "Verify firewall rules: `firewall-cmd --list-all`",
                ],
                recommended_action=f"Investigate source {ip} and consider blocking if malicious: `firewall-cmd --add-rich-rule='rule family=ipv4 source address={ip} reject'`" if not is_internal else "Review automated services for credential issues",
                human_review_required=severity in [EventSeverity.HIGH, EventSeverity.CRITICAL],
            )
            events.append(event)

    return events


def detect_usb_violations(since_minutes: int = 60) -> List[AbnormalEvent]:
    """
    Detect USBGuard policy violations and potential bypass attempts.

    Patterns detected:
    - Blocked USB device insertions
    - Policy modification attempts
    - Unauthorized device allow requests
    """
    events = []

    # Check USBGuard logs
    usbguard_entries = run_journalctl(
        unit="usbguard",
        since=f"{since_minutes} minutes ago"
    )

    blocked_devices = []
    policy_changes = []

    for entry in usbguard_entries:
        if not entry or entry.startswith("Error"):
            continue

        if "block" in entry.lower() or "denied" in entry.lower():
            blocked_devices.append(entry)
        elif "policy" in entry.lower() or "allow" in entry.lower():
            policy_changes.append(entry)

    if blocked_devices:
        # Check for after-hours attempts
        after_hours_attempts = []
        for entry in blocked_devices:
            # Parse timestamp if possible
            try:
                ts_match = re.match(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', entry)
                if ts_match:
                    ts = datetime.fromisoformat(ts_match.group(1))
                    if is_after_hours(ts):
                        after_hours_attempts.append(entry)
            except:
                pass

        severity = EventSeverity.HIGH if after_hours_attempts else EventSeverity.MEDIUM
        confidence = 70 if after_hours_attempts else 50

        event = AbnormalEvent(
            event_id=generate_event_id(),
            timestamp=datetime.now().isoformat(),
            category=EventCategory.USB_VIOLATION,
            severity=severity,
            summary=f"USB device(s) blocked by USBGuard ({len(blocked_devices)} events)",
            details=f"USBGuard blocked {len(blocked_devices)} USB device insertion(s). {len(after_hours_attempts)} occurred outside business hours.",
            source_log="journald/usbguard",
            raw_entries=blocked_devices[:5],
            confidence_score=confidence,
            evidence=[
                f"{len(blocked_devices)} blocked device events",
                f"{len(after_hours_attempts)} after-hours attempts" if after_hours_attempts else "All during business hours",
                f"Sample: {blocked_devices[0][:100]}..." if blocked_devices else "No samples",
            ],
            alternative_hypotheses=[
                "User attempting to use authorized device not yet in policy",
                "New hardware requiring policy update",
                "Accidental insertion of personal device",
            ] if not after_hours_attempts else [
                "Legitimate after-hours work requiring USB device",
                "Attempted data exfiltration via removable media",
                "Hardware testing or maintenance",
            ],
            validation_steps=[
                "Review blocked device details: `usbguard list-devices`",
                "Check who was logged in: `last -a | head -20`",
                "Review device hash against known-good inventory",
                "Check physical access logs if available",
            ],
            recommended_action="Review blocked devices with `usbguard list-devices` and update policy if legitimate",
            human_review_required=after_hours_attempts or len(blocked_devices) >= 5,
        )
        events.append(event)

    return events


def detect_data_transfers(since_minutes: int = 60) -> List[AbnormalEvent]:
    """
    Detect potential sensitive data transfers to external destinations.

    Patterns detected:
    - Large outbound transfers via scp/rsync/curl/wget
    - Connections to external IPs during off-hours
    - Transfers involving sensitive file patterns
    """
    events = []

    # Check for network transfer tools in audit logs
    audit_entries = run_journalctl(
        since=f"{since_minutes} minutes ago",
        grep="(scp|rsync|curl|wget|nc|netcat)"
    )

    # Also check Suricata for large outbound flows
    suricata_log = Path("/var/log/suricata/eve.json")
    suricata_alerts = []

    if suricata_log.exists():
        try:
            with open(suricata_log, 'r') as f:
                # Read last 1000 lines
                lines = f.readlines()[-1000:]
                cutoff = datetime.now() - timedelta(minutes=since_minutes)

                for line in lines:
                    try:
                        entry = json.loads(line)
                        if entry.get("event_type") == "alert":
                            suricata_alerts.append(entry)
                        elif entry.get("event_type") == "flow":
                            # Check for large outbound flows
                            bytes_out = entry.get("flow", {}).get("bytes_toserver", 0)
                            if bytes_out > 100_000_000:  # 100MB+
                                suricata_alerts.append({
                                    "type": "large_transfer",
                                    "bytes": bytes_out,
                                    "dest_ip": entry.get("dest_ip"),
                                    "raw": line[:200],
                                })
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            pass

    suspicious_transfers = []
    for entry in audit_entries:
        if not entry or entry.startswith("Error"):
            continue
        # Look for external IP patterns
        external_ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', entry)
        if external_ip_match:
            ip = external_ip_match.group(1)
            if not (ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172.") or ip == "127.0.0.1"):
                suspicious_transfers.append(entry)

    if suspicious_transfers or suricata_alerts:
        # Check for after-hours
        after_hours = is_after_hours(datetime.now())
        severity = EventSeverity.HIGH if after_hours else EventSeverity.MEDIUM
        confidence = 60 if after_hours else 40

        total_events = len(suspicious_transfers) + len(suricata_alerts)

        event = AbnormalEvent(
            event_id=generate_event_id(),
            timestamp=datetime.now().isoformat(),
            category=EventCategory.DATA_TRANSFER,
            severity=severity,
            summary=f"Potential sensitive data transfer detected ({total_events} events)",
            details=f"Detected {len(suspicious_transfers)} suspicious transfer commands and {len(suricata_alerts)} network alerts. {'Activity occurred outside business hours.' if after_hours else 'Activity during business hours.'}",
            source_log="journald + suricata",
            raw_entries=suspicious_transfers[:5] + [str(a)[:200] for a in suricata_alerts[:5]],
            confidence_score=confidence,
            evidence=[
                f"{len(suspicious_transfers)} external transfer commands",
                f"{len(suricata_alerts)} Suricata alerts/flows",
                f"After hours: {after_hours}",
            ],
            alternative_hypotheses=[
                "Legitimate backup or synchronization to cloud services",
                "Software updates or package downloads",
                "Approved file sharing with external partners",
                "Developer uploading to remote repository",
            ],
            validation_steps=[
                "Review user activity: `last -a` to see who was logged in",
                "Check command history for the user in question",
                "Review Suricata logs: `tail -100 /var/log/suricata/eve.json | jq 'select(.event_type==\"alert\")'`",
                "Check if destination IPs are approved external services",
            ],
            recommended_action="Review transfer destinations and verify with data owner if legitimate",
            human_review_required=after_hours or total_events >= 5,
        )
        events.append(event)

    return events


def detect_selinux_security_events(since_minutes: int = 60) -> List[AbnormalEvent]:
    """
    Detect SELinux denials that may indicate security issues.

    Focus on security-sensitive denials, not routine probing:
    - Privilege escalation attempts
    - Access to sensitive files (/etc/shadow, keys, etc.)
    - Unusual process behaviors
    """
    events = []

    # Get SELinux denials
    audit_entries = run_journalctl(
        since=f"{since_minutes} minutes ago",
        grep="avc:.*denied"
    )

    # Patterns for security-sensitive denials
    sensitive_patterns = [
        (r'/etc/shadow', "shadow file access", EventSeverity.CRITICAL),
        (r'/etc/passwd', "passwd file modification", EventSeverity.HIGH),
        (r'\.ssh/', "SSH key access", EventSeverity.HIGH),
        (r'/etc/sudoers', "sudoers access", EventSeverity.CRITICAL),
        (r'execute.*stack', "stack execution", EventSeverity.CRITICAL),
        (r'ptrace', "process tracing", EventSeverity.HIGH),
        (r'rawip_socket', "raw socket access", EventSeverity.HIGH),
        (r'/var/log/audit', "audit log access", EventSeverity.HIGH),
    ]

    security_denials = []

    for entry in audit_entries:
        if not entry or entry.startswith("Error"):
            continue

        for pattern, description, severity in sensitive_patterns:
            if re.search(pattern, entry, re.IGNORECASE):
                security_denials.append({
                    "entry": entry,
                    "pattern": description,
                    "severity": severity,
                })
                break

    if security_denials:
        # Group by severity
        critical_count = sum(1 for d in security_denials if d["severity"] == EventSeverity.CRITICAL)
        high_count = sum(1 for d in security_denials if d["severity"] == EventSeverity.HIGH)

        overall_severity = EventSeverity.CRITICAL if critical_count > 0 else EventSeverity.HIGH
        confidence = 80 if critical_count > 0 else 65

        event = AbnormalEvent(
            event_id=generate_event_id(),
            timestamp=datetime.now().isoformat(),
            category=EventCategory.SELINUX_SECURITY,
            severity=overall_severity,
            summary=f"Security-sensitive SELinux denials ({len(security_denials)} events)",
            details=f"Detected {len(security_denials)} SELinux denials involving security-sensitive resources. {critical_count} CRITICAL, {high_count} HIGH severity.",
            source_log="journald/audit",
            raw_entries=[d["entry"][:200] for d in security_denials[:5]],
            confidence_score=confidence,
            evidence=[
                f"{critical_count} critical-level denials",
                f"{high_count} high-level denials",
                f"Patterns matched: {', '.join(set(d['pattern'] for d in security_denials[:5]))}",
            ],
            alternative_hypotheses=[
                "Legitimate administrative tool probing system capabilities",
                "Security scanning tool (e.g., OpenSCAP) performing audit",
                "Misconfigured application attempting unauthorized access",
            ],
            validation_steps=[
                "Review full audit log: `ausearch -m AVC -ts recent`",
                "Identify the source process: look for 'scontext' in denial",
                "Check if this correlates with scheduled security scans",
                "Verify no successful access occurred despite denial",
            ],
            recommended_action="Investigate source process immediately if denial appears to be exploitation attempt",
            human_review_required=True,
        )
        events.append(event)

    return events


def run_full_detection(since_minutes: int = 60) -> Dict[str, Any]:
    """
    Run all detection modules and compile results.

    Returns:
        Dictionary with all detected events and summary statistics
    """
    all_events = []

    # Run all detectors
    all_events.extend(detect_failed_logins(since_minutes))
    all_events.extend(detect_usb_violations(since_minutes))
    all_events.extend(detect_data_transfers(since_minutes))
    all_events.extend(detect_selinux_security_events(since_minutes))

    # Sort by severity
    severity_order = {
        EventSeverity.CRITICAL: 0,
        EventSeverity.HIGH: 1,
        EventSeverity.MEDIUM: 2,
        EventSeverity.LOW: 3,
        EventSeverity.INFO: 4,
    }
    all_events.sort(key=lambda e: severity_order[e.severity])

    # Compile summary
    summary = {
        "scan_timestamp": datetime.now().isoformat(),
        "period_minutes": since_minutes,
        "total_events": len(all_events),
        "critical_count": sum(1 for e in all_events if e.severity == EventSeverity.CRITICAL),
        "high_count": sum(1 for e in all_events if e.severity == EventSeverity.HIGH),
        "medium_count": sum(1 for e in all_events if e.severity == EventSeverity.MEDIUM),
        "low_count": sum(1 for e in all_events if e.severity == EventSeverity.LOW),
        "human_review_required": sum(1 for e in all_events if e.human_review_required),
        "events_by_category": {},
    }

    for cat in EventCategory:
        count = sum(1 for e in all_events if e.category == cat)
        if count > 0:
            summary["events_by_category"][cat.value] = count

    return {
        "summary": summary,
        "events": [e.to_dict() for e in all_events],
    }


def format_detection_report(results: Dict[str, Any]) -> str:
    """Format detection results as a human-readable report."""
    summary = results["summary"]
    events = results["events"]

    lines = [
        "# Abnormal Event Detection Report",
        "",
        f"**Scan Time:** {summary['scan_timestamp']}",
        f"**Period:** Last {summary['period_minutes']} minutes",
        "",
        "## Summary",
        "",
        f"- **Total Events:** {summary['total_events']}",
        f"- **Critical:** {summary['critical_count']}",
        f"- **High:** {summary['high_count']}",
        f"- **Medium:** {summary['medium_count']}",
        f"- **Low:** {summary['low_count']}",
        f"- **Requires Human Review:** {summary['human_review_required']}",
        "",
    ]

    if summary["events_by_category"]:
        lines.append("### Events by Category")
        lines.append("")
        for cat, count in summary["events_by_category"].items():
            lines.append(f"- {cat.replace('_', ' ').title()}: {count}")
        lines.append("")

    if events:
        lines.append("## Detected Events")
        lines.append("")

        for event in events:
            icon = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🟢",
                "INFO": "ℹ️",
            }.get(event["severity"], "⚪")

            lines.append(f"### {icon} [{event['severity']}] {event['summary']}")
            lines.append("")
            lines.append(f"**Category:** {event['category'].replace('_', ' ').title()}")
            lines.append(f"**Confidence:** {event['confidence_score']}%")
            lines.append(f"**Human Review:** {'Required' if event['human_review_required'] else 'Routine'}")
            lines.append("")
            lines.append(event["details"])
            lines.append("")

            if event["evidence"]:
                lines.append("**Evidence:**")
                for i, e in enumerate(event["evidence"], 1):
                    lines.append(f"{i}. {e}")
                lines.append("")

            if event["alternative_hypotheses"]:
                lines.append("**Alternative Hypotheses:**")
                for i, h in enumerate(event["alternative_hypotheses"], 1):
                    lines.append(f"{i}. {h}")
                lines.append("")

            if event["validation_steps"]:
                lines.append("**Validation Steps:**")
                for i, s in enumerate(event["validation_steps"], 1):
                    lines.append(f"{i}. {s}")
                lines.append("")

            lines.append(f"**Recommended Action:** {event['recommended_action']}")
            lines.append("")
            lines.append("---")
            lines.append("")
    else:
        lines.append("## No Abnormal Events Detected")
        lines.append("")
        lines.append("No security-relevant events detected in the specified time period.")

    return "\n".join(lines)


if __name__ == "__main__":
    # Test the detection
    print("Running abnormal event detection...")
    results = run_full_detection(since_minutes=60)
    print(format_detection_report(results))
