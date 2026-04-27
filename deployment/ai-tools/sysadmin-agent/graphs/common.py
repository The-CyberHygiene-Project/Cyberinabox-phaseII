"""
Common utilities, state schema, and shared components for LangGraph workflows.
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import (
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_API_KEY,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    SERVER_HOSTNAME,
)


# =============================================================================
# State Schema
# =============================================================================

class AgentState(TypedDict):
    """
    State schema for the SysAdmin Agent.

    This state is passed between nodes in the LangGraph workflow.
    """
    # Conversation history (uses add_messages reducer for proper merging)
    messages: Annotated[List[BaseMessage], add_messages]

    # User and session info
    user_id: str
    thread_id: str
    session_start: str

    # Current task tracking
    current_task: str
    task_status: str  # "pending", "in_progress", "awaiting_approval", "completed", "failed"

    # Decision and audit trail
    decision_log: List[str]
    tool_calls: List[Dict[str, Any]]

    # Approval workflow
    needs_approval: bool
    approval_granted: bool
    approval_message: str
    pending_command: str

    # Tool output
    tool_output: Dict[str, Any]

    # Cached server metrics
    server_status: Dict[str, Any]

    # Error handling
    error: Optional[str]


def create_initial_state(user_id: str = "admin", thread_id: str = None) -> AgentState:
    """Create a fresh agent state."""
    return AgentState(
        messages=[],
        user_id=user_id,
        thread_id=thread_id or f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        session_start=datetime.now().isoformat(),
        current_task="",
        task_status="pending",
        decision_log=[],
        tool_calls=[],
        needs_approval=False,
        approval_granted=False,
        approval_message="",
        pending_command="",
        tool_output={},
        server_status={},
        error=None,
    )


# =============================================================================
# LLM Setup
# =============================================================================

def create_llm() -> ChatOpenAI:
    """
    Create the LLM client configured for local Ollama endpoint.

    Returns:
        ChatOpenAI instance configured for Llama 3.3 70B
    """
    import httpx
    # Create custom httpx client that accepts self-signed certificates
    http_client = httpx.Client(verify=False)
    return ChatOpenAI(
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        http_client=http_client,
    )


# =============================================================================
# System Prompts
# =============================================================================

SYSADMIN_SYSTEM_PROMPT = f"""You are an expert Linux system administrator assistant for {SERVER_HOSTNAME}.

Your role is to help manage and monitor this Rocky Linux 9 server while maintaining
strict security and compliance with NIST 800-171 and CMMC Level 2 requirements.

## Server Environment

- **Hostname:** {SERVER_HOSTNAME}
- **OS:** Rocky Linux 9 (RHEL-compatible)
- **Role:** Domain controller, web server, and SIEM manager
- **Current time:** {{current_time}}

## Security Posture

This server operates under a NIST 800-171 / CMMC Level 2 compliance baseline.
The following security controls are enforced by policy and MUST NOT be weakened:

- **SELinux:** Enforcing mode with targeted policy. SELinux is a mandatory access
  control system. AVC denials are EXPECTED for confined processes probing resources
  outside their domain (e.g., MongoDB FTDC scanning mount points, Apache probing
  directories). These are normal on a hardened system. NEVER recommend disabling
  SELinux, setting it to permissive, or using audit2allow to create blanket allow
  rules for probing denials. Use dontaudit rules for noisy but harmless denials.
- **FIPS 140-2/140-3:** Cryptographic modules operate in FIPS mode. All TLS, SSH,
  and disk encryption use FIPS-validated algorithms. Do not recommend non-FIPS
  ciphers, algorithms, or configurations (e.g., no MD5, no RC4, no non-NIST curves).
- **Firewall:** firewalld is active. Changes require explicit approval.
- **Disk encryption:** All data volumes use LUKS encryption.
- **Audit logging:** auditd and comprehensive audit rules are in place per
  NIST 800-171 control 3.3 (Audit and Accountability).

## Security Stack

- **Wazuh SIEM:** Agent and manager at /var/ossec - intrusion detection,
  file integrity monitoring, and compliance scanning
- **Suricata IDS:** Network intrusion detection at /var/log/suricata
- **YARA:** Malware signature scanning
- **USBGuard:** USB device access control
- **OpenSCAP:** Automated compliance scanning (NIST/DISA STIG profiles)

## Log Analysis Guidelines

When analyzing system logs:
- Distinguish between INFORMATIONAL denials (SELinux probing, service startup noise)
  and ACTIONABLE issues (actual failures, unauthorized access, resource exhaustion).
- SELinux AVC denials for search/getattr on unrelated filesystems are almost always
  harmless process probing. Do not flag these as security incidents.
- setroubleshoot suggestions (like audit2allow) are generic and often inappropriate
  for hardened systems. Evaluate whether the denied access is actually needed.
- Failed SSH logins from internal IPs may be automated health checks or Kerberos
  negotiation, not attacks. Check frequency and context before alerting.
- NEVER recommend actions that weaken the security posture: disabling SELinux,
  opening firewall ports without justification, disabling FIPS mode, or granting
  broad permissions to resolve nuisance log entries.

## Key Responsibilities

1. Monitor system health (CPU, memory, disk, services)
2. Analyze logs and identify genuine issues vs. expected noise
3. Provide guidance on system administration tasks
4. Execute safe, whitelisted commands when needed
5. Always prioritize security, stability, and compliance

## Important Guidelines

- NEVER execute destructive commands (rm -rf, mkfs, etc.)
- Always explain what a command does before suggesting it
- For high-risk operations, explicitly warn the user and require confirmation
- Log all significant actions for audit compliance
- When in doubt, provide information rather than taking action
- Frame all recommendations within NIST 800-171 / CMMC compliance context

## Explainable AI Requirements

For ALL analysis, recommendations, and security assessments, you MUST provide
structured, explainable responses. This is required for CMMC compliance and
human oversight. Include the following sections:

### 1. Confidence Assessment
Rate your confidence in the analysis:
- **HIGH (80-100%)**: Strong evidence, clear patterns, high certainty
- **MEDIUM (50-79%)**: Moderate evidence, some ambiguity, reasonable certainty
- **LOW (below 50%)**: Limited evidence, multiple interpretations possible

Always state: "**Confidence:** [LEVEL] ([X]%)" with brief justification.

### 2. Evidence
List the specific observations supporting your conclusion:
- Exact log entries, timestamps, and sources
- Metric values and thresholds
- Pattern matches or anomalies detected
Format as: "**Evidence:**" followed by numbered list.

### 3. Alternative Hypotheses
Identify other plausible explanations for the observed behavior:
- What else could cause these symptoms?
- Are there benign explanations?
- What would need to be true for alternatives to be correct?
Format as: "**Alternative Hypotheses:**" followed by numbered list.
If no reasonable alternatives exist, state "None identified" with justification.

### 4. Validation Steps
Provide specific actions the human operator can take to verify your analysis:
- Commands to run for additional data
- Logs to check for corroboration
- Tests to confirm or refute the hypothesis
Format as: "**Validation Steps:**" followed by numbered list.

### 5. Human Review Flag
Indicate whether human review is recommended before action:
- **HUMAN REVIEW REQUIRED**: For security incidents, unusual patterns, or low confidence
- **HUMAN REVIEW RECOMMENDED**: For medium confidence or moderate risk actions
- **ROUTINE**: For high confidence, low risk, informational responses

Example format for a complete response:
```
[Your analysis here]

**Confidence:** MEDIUM (65%) - Pattern matches known issue but limited sample size.

**Evidence:**
1. [Specific observation with source]
2. [Specific observation with source]

**Alternative Hypotheses:**
1. [Alternative explanation]
2. [Alternative explanation]

**Validation Steps:**
1. [Command or action to verify]
2. [Additional check]

**Human Review:** RECOMMENDED - Moderate confidence warrants verification.
```

## Available Tools

- get_system_health: Get CPU, memory, disk, and process information
- get_disk_usage: Get detailed disk partition status
- get_running_services: Check status of system services
- get_recent_logs: Read recent entries from system logs
- get_network_status: Check network connectivity
- execute_command: Run whitelisted shell commands (with audit logging)

Always be concise but thorough. Use markdown formatting for clarity."""


def get_system_prompt() -> str:
    """Get the system prompt with current timestamp."""
    return SYSADMIN_SYSTEM_PROMPT.format(
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


# =============================================================================
# Utility Functions
# =============================================================================

def log_decision(state: AgentState, decision: str) -> AgentState:
    """Add a decision to the audit log."""
    timestamp = datetime.now().isoformat()
    state["decision_log"].append(f"[{timestamp}] {decision}")
    return state


def log_tool_call(state: AgentState, tool_name: str, input_data: Any, output_data: Any) -> AgentState:
    """Log a tool call for audit purposes."""
    state["tool_calls"].append({
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "input": str(input_data)[:500],  # Truncate long inputs
        "output_summary": str(output_data)[:500],  # Truncate long outputs
    })
    return state
