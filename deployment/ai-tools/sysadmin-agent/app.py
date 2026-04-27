"""
SysAdmin Agent Dashboard
========================
A secure, local, production-grade dashboard for AI-assisted system administration.
Powered by LangGraph + Llama 3.3 70B Instruct.

NIST 800-171 / CMMC Compliant:
- Human-in-the-loop for all high-impact actions
- Full audit logging
- Least privilege command execution
- No cloud dependencies

Usage:
    streamlit run app.py --server.port 8501
"""

import streamlit as st
import json
import requests as _requests
from datetime import datetime
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import (
    APP_TITLE,
    APP_ICON,
    DASHBOARD_TILES,
    SERVER_HOSTNAME,
    AUDIT_LOG_FILE,
    LOG_DIR,
    WORKSTATIONS,
    OPENSCAP_PROFILE_NAME,
)
from tools.monitoring_tools import (
    get_system_health,
    get_disk_usage,
    get_running_services,
    get_recent_logs,
    get_network_status,
    get_firewall_status,
    get_security_summary,
)
from tools.security_tools import (
    get_wazuh_alerts,
    get_suricata_alerts,
    get_yara_status,
    get_virustotal_alerts,
    run_yara_scan,
    get_security_services_status,
    get_graylog_status,
    get_prometheus_status,
    get_usb_devices,
    allow_usb_device,
    block_usb_device,
    block_all_usb_storage,
)
from tools.compliance_tools import (
    get_compliance_status,
    get_wazuh_compliance_data,
    get_wazuh_sca_results,
    get_local_openscap_results,
    get_report_list,
)
from tools.shell_tool import execute_command, requires_approval, is_command_allowed
from tools.code_assistant import (
    check_aider_api_health,
    query_code,
    edit_file,
    architect_edit,
    execute_and_analyze,
    list_directory,
    read_file,
    set_audit_logger,
    ANALYSIS_COMMANDS,
    ALLOWED_DIRECTORIES,
    is_path_allowed,
)
from graphs.common import AgentState, create_initial_state, create_llm, get_system_prompt
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from models.explainable_response import (
    ExplainableResponse,
    parse_ai_response,
    format_explainable_response,
    ConfidenceLevel,
    HumanReviewLevel,
)
from database.feedback_db import (
    store_ai_response,
    store_feedback,
    get_feedback_summary,
    get_recent_responses,
    get_metrics_history,
    FeedbackRating,
    IssueCategory,
    ResponseFeedback,
)
from database.evaluation_reports import (
    get_performance_metrics,
    get_calibration_report,
    generate_compliance_report,
    export_report_markdown,
)
from tools.abnormal_event_detector import (
    run_full_detection,
    format_detection_report,
    EventSeverity,
    EventCategory,
)

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# Custom CSS
# =============================================================================
st.markdown("""
<style>
    /* ── Global font size: scale root so rem units follow ── */
    :root { font-size: 20px !important; }
    html  { font-size: 20px !important; }
    body  { font-size: 20px !important; }

    /* ── Core Streamlit containers ── */
    .stApp,
    .main, .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"] {
        font-size: 20px !important;
    }

    /* ── All plain text and paragraphs ── */
    p, span, li, td, th, div,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stText"],
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        font-size: 20px !important;
        line-height: 1.65 !important;
    }

    /* ── Headings ── */
    h1, [data-testid="stMarkdownContainer"] h1 { font-size: 34px !important; font-weight: 700 !important; }
    h2, [data-testid="stMarkdownContainer"] h2 { font-size: 28px !important; font-weight: 600 !important; }
    h3, [data-testid="stMarkdownContainer"] h3 { font-size: 24px !important; font-weight: 600 !important; }
    h4, [data-testid="stMarkdownContainer"] h4 { font-size: 22px !important; font-weight: 600 !important; }

    /* ── Labels (widget labels) ── */
    label,
    .stSelectbox label, .stMultiSelect label,
    .stTextInput label, .stTextArea label,
    .stCheckbox label, .stRadio label,
    .stSlider label, .stNumberInput label,
    [data-testid="stWidgetLabel"] {
        font-size: 20px !important;
        font-weight: 600 !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        font-size: 18px !important;
        line-height: 1.6 !important;
    }
    [data-testid="stSidebar"] h1 { font-size: 26px !important; }
    [data-testid="stSidebar"] h2 { font-size: 22px !important; }
    [data-testid="stSidebar"] h3 { font-size: 20px !important; }

    /* ── Buttons ── */
    .stButton button,
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-secondary"] {
        font-size: 18px !important;
        padding: 0.45rem 1.1rem !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetricValue"]  { font-size: 36px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"]  { font-size: 18px !important; }
    [data-testid="stMetricDelta"]  { font-size: 16px !important; }

    /* ── Expanders ── */
    .streamlit-expanderHeader,
    [data-testid="stExpander"] summary,
    details summary { font-size: 20px !important; font-weight: 600 !important; }

    /* ── Captions / help text ── */
    .stCaption, [data-testid="stCaptionContainer"],
    small, .st-emotion-cache-1629p8f { font-size: 16px !important; }

    /* ── Select / input widgets ── */
    .stSelectbox div[data-baseweb="select"],
    .stTextInput input, .stTextArea textarea,
    .stNumberInput input {
        font-size: 18px !important;
    }

    /* ── Tab labels ── */
    [data-testid="stTab"] button { font-size: 18px !important; }

    /* ── Tile styling ── */
    .tile-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        color: #ffffff;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        font-size: 1.05rem;
    }
    .tile-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    /* Darker tile variants for better text contrast */
    .tile-low      { background: linear-gradient(135deg, #0d7a5f 0%, #1db954 100%); color: #ffffff; }
    .tile-medium   { background: linear-gradient(135deg, #b35900 0%, #d4380d 100%); color: #ffffff; }
    .tile-high     { background: linear-gradient(135deg, #7b1fa2 0%, #c0392b 100%); color: #ffffff; }
    .tile-critical { background: linear-gradient(135deg, #4a0000 0%, #c0392b 100%); color: #ffcccc; }

    /* ── Status indicators (dark-background friendly) ── */
    .status-ok    { color: #4ade80; font-weight: bold; font-size: 1rem; }
    .status-warn  { color: #fbbf24; font-weight: bold; font-size: 1rem; }
    .status-error { color: #f87171; font-weight: bold; font-size: 1rem; }

    /* ── Chat styling (dark) ── */
    .chat-container {
        background: #1e2329;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        max-height: 500px;
        overflow-y: auto;
        font-size: 1rem;
        line-height: 1.6;
        color: #e8eaed;
    }

    /* ── Approval box ── */
    .approval-box {
        background: #2d2200;
        border: 2px solid #fbbf24;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        color: #ffe082;
        font-size: 1rem;
    }

    /* ── Command output ── */
    .command-output {
        background: #0d1117;
        color: #4ade80;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.95rem;
        line-height: 1.5;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #30363d;
        overflow-x: auto;
    }

    /* ── Header ── */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #ffffff;
        padding: 24px;
        border-radius: 10px;
        margin-bottom: 20px;
        font-size: 1.1rem;
    }
    .main-header h1 { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Session State Initialization
# =============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_state" not in st.session_state:
    st.session_state.agent_state = create_initial_state()

if "pending_command" not in st.session_state:
    st.session_state.pending_command = None

if "pending_command_context" not in st.session_state:
    st.session_state.pending_command_context = None

if "last_health_check" not in st.session_state:
    st.session_state.last_health_check = None

if "show_approval_dialog" not in st.session_state:
    st.session_state.show_approval_dialog = False

if "pending_timeout" not in st.session_state:
    st.session_state.pending_timeout = 60

if "show_alert_details" not in st.session_state:
    st.session_state.show_alert_details = False

if "show_feedback_form" not in st.session_state:
    st.session_state.show_feedback_form = None

if "show_evaluation_report" not in st.session_state:
    st.session_state.show_evaluation_report = False

if "export_compliance_report" not in st.session_state:
    st.session_state.export_compliance_report = False

# =============================================================================
# Helper Functions
# =============================================================================

def log_audit_event(event_type: str, details: str):
    """Log an audit event to file."""
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "details": details,
        "user": "admin",  # In production, get from auth
    }
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


# Connect Code Assistant audit logging to main audit system
set_audit_logger(log_audit_event)


def add_message(role: str, content: str, response_id: str = None):
    """Add a message to chat history."""
    msg = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    }
    if response_id:
        msg["response_id"] = response_id
    st.session_state.messages.append(msg)


def get_ai_response(prompt: str, query_type: str = "general") -> tuple:
    """Get a response from the AI for the given prompt.

    Returns:
        Tuple of (response_text, response_id) for feedback tracking
    """
    try:
        llm = create_llm()

        # Build context with system prompt and recent messages
        messages = [SystemMessage(content=get_system_prompt())]

        # Add recent conversation history (last 10 messages)
        for msg in st.session_state.messages[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Add current prompt
        messages.append(HumanMessage(content=prompt))

        # Get response
        response = llm.invoke(messages)
        raw_response = response.content

        # Parse into explainable structure and store for potential feedback
        parsed = parse_ai_response(raw_response, query_type=query_type, source_data=prompt[:200])

        # Store parsed response in session for feedback tracking
        if "ai_responses" not in st.session_state:
            st.session_state.ai_responses = []
        st.session_state.ai_responses.append(parsed.to_dict())

        # Store in feedback database for evaluation
        store_ai_response(parsed.to_dict())

        # Log the structured response
        log_audit_event("AI_RESPONSE", json.dumps({
            "response_id": parsed.response_id,
            "confidence": f"{parsed.confidence_level.value} ({parsed.confidence_score}%)",
            "human_review": parsed.human_review_level.value,
            "parsing_successful": parsed.parsing_successful,
        }))

        return raw_response, parsed.response_id

    except Exception as e:
        return f"Error connecting to AI: {str(e)}\n\nMake sure Ollama is running on 192.168.1.7 (HTTPS port 11443)", None


def get_ai_response_structured(prompt: str, query_type: str = "general") -> ExplainableResponse:
    """Get a structured explainable response from the AI."""
    try:
        llm = create_llm()

        # Build context with system prompt and recent messages
        messages = [SystemMessage(content=get_system_prompt())]

        # Add recent conversation history (last 10 messages)
        for msg in st.session_state.messages[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Add current prompt
        messages.append(HumanMessage(content=prompt))

        # Get response
        response = llm.invoke(messages)
        raw_response = response.content

        # Parse into explainable structure
        parsed = parse_ai_response(raw_response, query_type=query_type, source_data=prompt[:200])

        # Store parsed response in session for feedback tracking
        if "ai_responses" not in st.session_state:
            st.session_state.ai_responses = []
        st.session_state.ai_responses.append(parsed.to_dict())

        # Log the structured response
        log_audit_event("AI_RESPONSE_STRUCTURED", json.dumps({
            "response_id": parsed.response_id,
            "confidence": f"{parsed.confidence_level.value} ({parsed.confidence_score}%)",
            "human_review": parsed.human_review_level.value,
            "parsing_successful": parsed.parsing_successful,
        }))

        return parsed

    except Exception as e:
        error_response = ExplainableResponse(
            analysis=f"Error connecting to AI: {str(e)}\n\nMake sure Ollama is running on 192.168.1.7 (HTTPS port 11443)",
            confidence_level=ConfidenceLevel.UNKNOWN,
            human_review_level=HumanReviewLevel.REQUIRED,
        )
        return error_response


def display_explainable_response(response: ExplainableResponse):
    """Display an ExplainableResponse with structured formatting in Streamlit."""
    # Main analysis
    if response.analysis:
        st.markdown(response.analysis)

    # Create columns for structured sections
    st.markdown("---")

    # Confidence indicator
    confidence_colors = {
        ConfidenceLevel.HIGH: ("🟢", "green"),
        ConfidenceLevel.MEDIUM: ("🟡", "orange"),
        ConfidenceLevel.LOW: ("🔴", "red"),
        ConfidenceLevel.UNKNOWN: ("⚪", "gray"),
    }
    icon, color = confidence_colors.get(response.confidence_level, ("⚪", "gray"))

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"### {icon} Confidence: {response.confidence_level.value} ({response.confidence_score}%)")
        if response.confidence_justification:
            st.caption(response.confidence_justification)

    with col2:
        review_icons = {
            HumanReviewLevel.REQUIRED: "🔴",
            HumanReviewLevel.RECOMMENDED: "🟡",
            HumanReviewLevel.ROUTINE: "🟢",
            HumanReviewLevel.UNKNOWN: "⚪",
        }
        review_icon = review_icons.get(response.human_review_level, "⚪")
        st.markdown(f"### {review_icon} Human Review: {response.human_review_level.value}")
        if response.human_review_reason:
            st.caption(response.human_review_reason)

    # Evidence section
    if response.evidence:
        with st.expander("📋 Evidence", expanded=False):
            for i, item in enumerate(response.evidence, 1):
                st.markdown(f"{i}. {item}")

    # Alternative hypotheses section
    if response.alternative_hypotheses:
        with st.expander("🔀 Alternative Hypotheses", expanded=False):
            for i, item in enumerate(response.alternative_hypotheses, 1):
                st.markdown(f"{i}. {item}")

    # Validation steps section
    if response.validation_steps:
        with st.expander("✅ Validation Steps", expanded=True):
            for i, item in enumerate(response.validation_steps, 1):
                st.markdown(f"{i}. {item}")

    # Parsing status (for debugging)
    if not response.parsing_successful:
        st.warning(f"⚠️ Response parsing incomplete: {', '.join(response.parsing_errors)}")


def execute_with_approval(command: str, context: str = "") -> dict:
    """
    Execute a command, handling approval workflow if needed.

    Returns dict with: executed, output, needs_approval, error
    """
    # Check if command is allowed
    allowed, reason = is_command_allowed(command)

    if not allowed:
        return {
            "executed": False,
            "output": "",
            "needs_approval": False,
            "error": f"Command blocked: {reason}",
        }

    # Check if approval is required
    if requires_approval(command):
        return {
            "executed": False,
            "output": "",
            "needs_approval": True,
            "error": "",
            "command": command,
            "context": context,
        }

    # Execute the command
    result = execute_command(command, approval_granted=False)
    log_audit_event("COMMAND_EXECUTED", f"Command: {command}")

    return {
        "executed": result["success"],
        "output": result["output"],
        "needs_approval": False,
        "error": result["error"],
    }


def execute_approved_command(command: str, approved_by: str = "admin", timeout: int = 60) -> dict:
    """Execute a command that has been approved."""
    result = execute_command(command, approval_granted=True, approved_by=approved_by, timeout=timeout)
    log_audit_event("APPROVED_COMMAND_EXECUTED", f"Command: {command}, Approved by: {approved_by}")
    return result


# =============================================================================
# Tile Action Handlers
# =============================================================================

def handle_tile_action(tile_id: str):
    """Handle a tile button click."""
    log_audit_event("TILE_CLICKED", f"Tile: {tile_id}")

    if tile_id == "server_health":
        health = get_system_health()
        output = f"""## 🖥️ Server Health Report

**CPU:** {health['cpu']['percent']}% {health['cpu']['status']}
- Cores: {health['cpu']['count']}
- Load Average: {health['load_average']['1min']} / {health['load_average']['5min']} / {health['load_average']['15min']}

**Memory:** {health['memory']['percent']}% {health['memory']['status']}
- Used: {health['memory']['used_gb']} GB / {health['memory']['total_gb']} GB
- Available: {health['memory']['available_gb']} GB

**Swap:** {health['swap']['percent']}% used

**Uptime:** {health['uptime']['uptime_str']}

**Top Processes:**
"""
        for p in health['top_processes']:
            output += f"- {p['name']} (PID {p['pid']}): CPU {p['cpu_percent']}%, Mem {p['memory_percent']}%\n"

        add_message("assistant", output)
        st.session_state.last_health_check = health

    elif tile_id == "disk_usage":
        usage = get_disk_usage()
        output = "## 💾 Disk Usage Report\n\n"
        for part in usage['partitions']:
            output += f"**{part['mountpoint']}** ({part['device']})\n"
            output += f"- {part['used_gb']} GB / {part['total_gb']} GB ({part['percent']}%) {part['status']}\n\n"

        if usage['alerts']:
            output += "### ⚠️ Alerts\n"
            for alert in usage['alerts']:
                output += f"- {alert}\n"

        add_message("assistant", output)

    elif tile_id == "running_services":
        services = get_running_services()
        output = "## ⚙️ Service Status\n\n"
        for svc in services.get('services', []):
            output += f"{svc['status_icon']} **{svc['name']}**: {svc['status']}\n"

        if services.get('failed_services'):
            output += "\n### ⚠️ Failed Services\n"
            for svc in services['failed_services']:
                output += f"- {svc}\n"

        add_message("assistant", output)

    elif tile_id == "recent_logs":
        logs = get_recent_logs("messages", 30)
        output = f"""## 📋 Recent System Logs

**Errors found:** {logs.get('error_count', 0)}
**Warnings found:** {logs.get('warning_count', 0)}

### Recent Entries:
```
{logs.get('content', 'Unable to read logs')[-2000:]}
```
"""
        add_message("assistant", output)

    elif tile_id == "update_status":
        result = execute_command("sudo dnf check-update 2>/dev/null | head -50")
        if result['success'] or result['return_code'] == 100:  # 100 = updates available
            output = f"""## 🔄 Available Updates

```
{result['output'] if result['output'] else 'No updates available'}
```
"""
        else:
            output = f"## 🔄 Update Status\n\nError checking updates: {result['error']}"
        add_message("assistant", output)

    elif tile_id == "firewall_status":
        fw = get_firewall_status()
        output = f"""## 🔥 Firewall Status

**State:** {fw.get('status', 'Unknown')}

**Active Zones:**
```
{fw.get('active_zones', 'N/A')}
```

**Rules:**
```
{fw.get('default_zone_rules', 'N/A')}
```
"""
        add_message("assistant", output)

    elif tile_id == "network_test":
        network = get_network_status()
        output = "## 🌐 Network Status\n\n### Connectivity Tests\n"
        for test in network['connectivity']:
            output += f"{test['status']} {test['name']} ({test['host']})\n"

        output += "\n### Interfaces\n"
        for iface in network['interfaces']:
            if iface.get('ipv4'):
                output += f"- **{iface['name']}**: {iface.get('ipv4', 'N/A')}\n"

        add_message("assistant", output)

    elif tile_id == "security_scan":
        security = get_security_summary()
        output = f"""## 🔒 Security Summary

**Status:** {security.get('status', 'Unknown')}

**Failed SSH attempts (24h):** {security.get('failed_ssh_attempts_24h', 'N/A')}
**SELinux:** {security.get('selinux_status', 'N/A')}

**Recent root logins:**
```
{security.get('recent_root_logins', 'N/A')}
```
"""
        add_message("assistant", output)

    elif tile_id == "log_synopsis":
        add_message("user", "Please provide a synopsis of recent system logs, highlighting any errors or warnings.")
        with st.spinner("AI analyzing logs..."):
            logs = get_recent_logs("messages", 100)
            prompt = f"""Analyze these recent system logs and provide a brief synopsis.
Categorize findings as CRITICAL, WARNING, or INFORMATIONAL.

Analysis context for this hardened server:
- SELinux is enforcing. AVC denials for search/getattr on unrelated filesystems
  (e.g., mongod/ftdc probing NFS or proc paths) are normal probing behavior,
  not security incidents. Classify these as INFORMATIONAL.
- FIPS 140 mode is active. Crypto-related messages about FIPS are expected.
- setroubleshoot suggestions like audit2allow are generic and often inappropriate.
  Do not recommend audit2allow for probing denials. Use dontaudit rules instead.
- Wazuh and Suricata generate routine operational log entries.
- Do not recommend weakening security controls (disabling SELinux, opening
  firewall ports, disabling FIPS) to resolve log noise.

Focus on genuinely actionable items: service failures, disk space issues,
authentication failures from unexpected sources, and real security events.

Log content:
```
{logs.get('content', '')[-3000:]}
```

Errors found: {logs.get('error_count', 0)}
Warnings found: {logs.get('warning_count', 0)}

Remember to include the required Explainable AI sections: Confidence, Evidence, Alternative Hypotheses, Validation Steps, and Human Review.
"""
            response, response_id = get_ai_response(prompt, query_type="log_analysis")
            add_message("assistant", response, response_id=response_id)

    elif tile_id == "audit_report":
        add_message("user", "Generate an audit report of recent agent actions.")
        try:
            with open(AUDIT_LOG_FILE, "r") as f:
                recent_logs = f.readlines()[-50:]
            output = "## 📊 Audit Report\n\n### Recent Agent Actions:\n\n"
            for line in recent_logs:
                try:
                    event = json.loads(line)
                    output += f"- **{event['timestamp']}**: {event['event_type']} - {event['details'][:100]}\n"
                except:
                    continue
            add_message("assistant", output)
        except FileNotFoundError:
            add_message("assistant", "## 📊 Audit Report\n\nNo audit logs found yet.")

    # High-risk actions that require approval
    elif tile_id == "security_updates":
        st.session_state.pending_command = "sudo dnf update --security -y"
        st.session_state.pending_command_context = "Apply all security updates"
        st.session_state.show_approval_dialog = True

    elif tile_id == "full_update":
        st.session_state.pending_command = "sudo dnf update -y"
        st.session_state.pending_command_context = "Full system update (all packages)"
        st.session_state.show_approval_dialog = True

    elif tile_id == "backup_nas":
        st.session_state.pending_command = "sudo /usr/local/bin/backup-critical-files.sh"
        st.session_state.pending_command_context = "Backup critical files to NAS"
        st.session_state.show_approval_dialog = True

    elif tile_id == "restart_service":
        add_message("assistant", "Which service would you like to restart? Please type the service name in the chat.")

    elif tile_id == "cleanup":
        st.session_state.pending_command = "sudo journalctl --vacuum-time=2weeks && sudo dnf clean all"
        st.session_state.pending_command_context = "System cleanup (old logs and package cache)"
        st.session_state.show_approval_dialog = True

    elif tile_id == "reboot":
        st.session_state.pending_command = "sudo shutdown -r +1"
        st.session_state.pending_command_context = "⚠️ REBOOT SERVER in 1 minute"
        st.session_state.show_approval_dialog = True

    # Security tile handlers
    elif tile_id == "wazuh_alerts":
        with st.spinner("Fetching Wazuh alerts..."):
            alerts = get_wazuh_alerts(hours=24, max_alerts=25)
        output = f"""## 🛡️ Wazuh SIEM Alerts (Last 24h)

**Service Status:** {'🟢 Running' if alerts['service_running'] else '🔴 Stopped'}
**Total Alerts:** {alerts['alert_count']}

### Recent Alerts:
"""
        if alerts['alerts']:
            for alert in alerts['alerts'][:15]:
                level_icon = "🔴" if alert.get('rule_level', 0) >= 10 else "🟡" if alert.get('rule_level', 0) >= 5 else "🟢"
                output += f"\n{level_icon} **Level {alert.get('rule_level', 'N/A')}** | {alert.get('timestamp', 'N/A')[:19]}\n"
                output += f"   Rule {alert.get('rule_id', 'N/A')}: {alert.get('description', 'N/A')}\n"
                output += f"   Agent: {alert.get('agent', 'N/A')} | Location: {alert.get('location', 'N/A')}\n"
        else:
            output += "\nNo alerts found in the specified time period."

        if alerts.get('error'):
            output += f"\n\n⚠️ Note: {alerts['error']}"

        add_message("assistant", output)

    elif tile_id == "suricata_alerts":
        with st.spinner("Fetching Suricata alerts..."):
            alerts = get_suricata_alerts(hours=24, max_alerts=25)
        output = f"""## 🚨 Suricata IDS Alerts (Last 24h)

**Service Status:** {'🟢 Running' if alerts['service_running'] else '🔴 Stopped'}
**Total Alerts:** {alerts['alert_count']}

### Recent Alerts:
"""
        if alerts['alerts']:
            for alert in alerts['alerts'][:15]:
                if 'signature' in alert:
                    sev_icon = "🔴" if alert.get('severity', 0) <= 1 else "🟡" if alert.get('severity', 0) <= 2 else "🟢"
                    output += f"\n{sev_icon} **{alert.get('timestamp', 'N/A')[:19]}**\n"
                    output += f"   {alert.get('signature', 'N/A')}\n"
                    output += f"   {alert.get('src_ip', 'N/A')} → {alert.get('dest_ip', 'N/A')}\n"
                    output += f"   Category: {alert.get('category', 'N/A')}\n"
                else:
                    output += f"\n- {alert.get('raw', 'N/A')[:100]}\n"
        else:
            output += "\nNo alerts found in the specified time period."

        if alerts.get('error'):
            output += f"\n\n⚠️ Note: {alerts['error']}"

        add_message("assistant", output)

    elif tile_id == "yara_status":
        with st.spinner("Checking YARA status..."):
            status = get_yara_status()
        output = f"""## 🦠 YARA Malware Detection Status

**YARA Installed:** {'🟢 Yes' if status['yara_installed'] else '🔴 No'}
**Version:** {status.get('yara_version', 'N/A')}
**Rules Files:** {status['rules_count']}

"""
        if status['rules_files']:
            output += "**Active Rule Files:**\n"
            for rf in status['rules_files'][:10]:
                output += f"- {rf}\n"
            output += "\n"

        if status['recent_detections']:
            output += "### Recent Detections:\n"
            for det in status['recent_detections']:
                output += f"\n🚨 **{det.get('timestamp', 'N/A')[:19]}**\n"
                output += f"   Rule: {det.get('rule_id', 'N/A')} - {det.get('description', 'N/A')}\n"
                if det.get('file'):
                    output += f"   File: {det.get('file')}\n"
        else:
            output += "### Recent Detections:\nNo recent malware detections.\n"

        if status.get('error'):
            output += f"\n⚠️ Note: {status['error']}"

        add_message("assistant", output)

    elif tile_id == "yara_scan":
        st.session_state.pending_command = "sudo yara -r /var/ossec/ruleset/yara/rules/malware_rules.yar /tmp"
        st.session_state.pending_command_context = "Run YARA malware scan on /tmp directory"
        st.session_state.show_approval_dialog = True

    elif tile_id == "virustotal_status":
        with st.spinner("Fetching VirusTotal alerts..."):
            status = get_virustotal_alerts()
        output = f"""## 🔍 VirusTotal Scan Results

**Total Alerts:** {status['alert_count']}

"""
        if status['alerts']:
            output += "### Recent Scans:\n"
            for alert in status['alerts'][:10]:
                positives = alert.get('positives', 0)
                total = alert.get('total', 0)
                status_icon = "🔴" if positives > 5 else "🟡" if positives > 0 else "🟢"
                output += f"\n{status_icon} **{alert.get('timestamp', 'N/A')[:19]}**\n"
                output += f"   Detection: {positives}/{total} engines\n"
                output += f"   {alert.get('description', 'N/A')}\n"
                if alert.get('file'):
                    output += f"   File: {alert.get('file')}\n"
        else:
            output += "No recent VirusTotal scan results found.\n"

        if status.get('error'):
            output += f"\n⚠️ Note: {status['error']}"

        add_message("assistant", output)

    elif tile_id == "security_services":
        with st.spinner("Checking security services..."):
            status = get_security_services_status()
        output = f"""## 🔐 Security Services Status

**Timestamp:** {status['timestamp'][:19]}

| Service | Status | Enabled |
|---------|--------|---------|
"""
        for svc_name, svc_info in status['services'].items():
            status_icon = "🟢" if svc_info['status'] == 'active' else "🔴" if svc_info['status'] in ['inactive', 'failed'] else "🟡"
            enabled_icon = "✅" if svc_info['enabled'] else "❌"
            output += f"| {svc_info['name']} | {status_icon} {svc_info['status']} | {enabled_icon} |\n"

        add_message("assistant", output)

    elif tile_id == "graylog_status":
        with st.spinner("Fetching Graylog status..."):
            status = get_graylog_status()
        output = f"""## 📊 Graylog Log Management Status

**Service Status:** {'🟢 Running' if status['service_running'] else '🔴 Stopped'}

"""
        if status.get('cluster_info'):
            output += f"**Cluster Info:**\n```json\n{json.dumps(status['cluster_info'], indent=2)[:500]}\n```\n\n"

        if status.get('recent_logs'):
            output += "### Recent Server Logs:\n```\n"
            for log in status['recent_logs'][-10:]:
                output += f"{log[:150]}\n"
            output += "```\n"

        if status.get('error'):
            output += f"\n⚠️ Note: {status['error']}"

        add_message("assistant", output)

    elif tile_id == "prometheus_status":
        with st.spinner("Fetching Prometheus status..."):
            status = get_prometheus_status()
        output = f"""## 📈 Prometheus Monitoring Status

**Service Status:** {'🟢 Running' if status['service_running'] else '🔴 Stopped'}

"""
        if status.get('targets'):
            output += "### Scrape Targets:\n\n| Job | Instance | Health |\n|-----|----------|--------|\n"
            for target in status['targets'][:15]:
                health_icon = "🟢" if target['health'] == 'up' else "🔴"
                output += f"| {target['job']} | {target['instance']} | {health_icon} {target['health']} |\n"
            output += "\n"

        if status.get('alerts'):
            output += "### Active Alerts:\n\n"
            for alert in status['alerts']:
                sev_icon = "🔴" if alert.get('severity') == 'critical' else "🟡" if alert.get('severity') == 'warning' else "⚪"
                output += f"{sev_icon} **{alert.get('alertname', 'N/A')}** ({alert.get('state', 'N/A')})\n"
                output += f"   {alert.get('summary', 'No summary')[:100]}\n\n"
        else:
            output += "### Active Alerts:\nNo active alerts.\n"

        if status.get('error'):
            output += f"\n⚠️ Note: {status['error']}"

        add_message("assistant", output)

    elif tile_id == "usb_toggle":
        with st.spinner("Checking USB device status..."):
            usb_status = get_usb_devices()

        if usb_status.get('error'):
            add_message("assistant", f"## 🔌 USB Access Control\n\n⚠️ Error: {usb_status['error']}")
        else:
            output = f"""## 🔌 USB Access Control

**USBGuard Status:** {'🟢 Running' if usb_status['usbguard_running'] else '🔴 Stopped'}

### USB Storage Devices:
"""
            blocked = usb_status.get('blocked_storage', [])
            allowed = usb_status.get('allowed_storage', [])

            if blocked:
                output += "\n**🔒 Blocked Storage Devices:**\n"
                for dev in blocked:
                    output += f"- ID {dev['id']}: {dev.get('name', 'Unknown')} ({dev.get('usb_id', 'N/A')})\n"
                output += "\n*To enable a blocked device, type in chat: `enable usb <device_id>`*\n"

            if allowed:
                output += "\n**🔓 Allowed Storage Devices:**\n"
                for dev in allowed:
                    output += f"- ID {dev['id']}: {dev.get('name', 'Unknown')} ({dev.get('usb_id', 'N/A')})\n"
                output += "\n*To block all storage devices, type in chat: `block all usb`*\n"

            if not blocked and not allowed:
                output += "\nNo USB storage devices currently connected.\n"
                output += "\n*Insert a USB drive and click this tile again to see it.*\n"

            output += """
### Quick Commands:
- `enable usb <id>` - Allow a blocked USB storage device
- `block usb <id>` - Block an allowed USB storage device
- `block all usb` - Block all USB storage devices
- `usb status` - Refresh USB device list
"""
            add_message("assistant", output)

            # Store USB status in session for chat commands
            st.session_state.usb_devices = usb_status

    # Compliance tile handlers
    elif tile_id == "compliance_status":
        with st.spinner("Checking compliance status..."):
            status = get_compliance_status()

        # Get local scan results for dc1
        local_scan = status.get('local_scan', {})
        wazuh_data = status.get('wazuh_data', {})
        wazuh_summary = wazuh_data.get('summary', {})

        # Status icons
        def score_icon(score):
            if score is None:
                return "⚪"
            elif score >= 90:
                return "🟢"
            elif score >= 70:
                return "🟡"
            else:
                return "🔴"

        output = f"""## 📋 NIST 800-171 CUI Compliance Status

**OpenSCAP:** {'🟢 Installed' if status['oscap_installed'] else '🔴 Not Installed'} (v{status.get('oscap_version', 'N/A')})
**Profile:** {OPENSCAP_PROFILE_NAME}
**Wazuh Manager:** {'🟢 Running' if wazuh_data.get('status') == 'ok' else '🔴 ' + wazuh_data.get('error', 'Unknown')}

### Compliance Summary (Wazuh Agents)
| Metric | Count |
|--------|-------|
| Total Agents | {wazuh_summary.get('total_agents', 0)} |
| 🟢 Compliant (90%+) | {wazuh_summary.get('compliant', 0)} |
| 🟡 Warning (70-89%) | {wazuh_summary.get('warning', 0)} |
| 🔴 Non-Compliant (<70%) | {wazuh_summary.get('non_compliant', 0)} |

### DC1 Server (Local)
"""
        if local_scan.get('score') is not None:
            output += f"{score_icon(local_scan['score'])} **Score: {local_scan['score']}%** ({local_scan.get('pass_count', 0)} passed, {local_scan.get('fail_count', 0)} failed)\n"
            output += f"   Last Scan: {local_scan.get('last_scan', 'Unknown')}\n"
        else:
            output += "⚪ No scan results available\n"

        output += "\n### Workstation Status (via Wazuh)\n"
        output += "| System | Status | Score | Last Scan | Agent |\n"
        output += "|--------|--------|-------|-----------|-------|\n"

        for ws_id, ws_info in status.get('workstations', {}).items():
            score = ws_info.get('score')
            last_scan = ws_info.get('last_scan', 'Never')[:16] if ws_info.get('last_scan') else 'Never'
            connected = "🟢" if ws_info.get('connected') else "🔴"
            score_str = f"{score}%" if score is not None else "N/A"
            output += f"| {ws_info['display_name']} | {score_icon(score)} {ws_info.get('status', 'unknown')} | {score_str} | {last_scan} | {connected} |\n"

        output += """
### Scan Schedule
- **Automatic scans:** Every 12 hours via systemd timer
- **Results forwarded to:** Wazuh SIEM
- **Manual scans:** Use tiles below to trigger on-demand

"""
        if status.get('recent_reports'):
            output += "### Recent HTML Reports:\n"
            for report in status['recent_reports'][:5]:
                output += f"- [{report['filename']}]({report['url']}) - {report['date']}\n"
        else:
            output += "### Recent HTML Reports:\nNo reports found.\n"

        add_message("assistant", output)

    elif tile_id == "wazuh_sca":
        with st.spinner("Fetching Wazuh SCA results..."):
            sca_data = get_wazuh_sca_results()

        output = """## 🔐 Wazuh SCA - CIS Benchmark Results

**Note:** This shows CIS Benchmark compliance from Wazuh SCA (different from NIST 800-171 CUI profile).

"""
        if sca_data.get('error'):
            output += f"⚠️ Error: {sca_data['error']}\n"
        else:
            for agent_name, agent_data in sca_data.get('agents', {}).items():
                output += f"### {agent_name}\n"
                if agent_data.get('error'):
                    output += f"⚠️ Error: {agent_data['error']}\n\n"
                    continue

                scans = agent_data.get('scans', [])
                if scans:
                    output += "| Policy | Score | Pass | Fail | Last Scan |\n"
                    output += "|--------|-------|------|------|-----------|\n"
                    for scan in scans:
                        score = scan.get('score', 0)
                        score_icon = "🟢" if score >= 90 else "🟡" if score >= 70 else "🔴"
                        end_scan = scan.get('end_scan', 'N/A')
                        if end_scan and len(end_scan) > 16:
                            end_scan = end_scan[:16]
                        output += f"| {scan.get('name', 'Unknown')[:30]} | {score_icon} {score}% | {scan.get('pass', 0)} | {scan.get('fail', 0)} | {end_scan} |\n"
                    output += "\n"
                else:
                    output += "No SCA scans found.\n\n"

        output += """
### About SCA vs OpenSCAP CUI
- **Wazuh SCA (CIS):** Broader system hardening checks (more strict)
- **OpenSCAP CUI:** NIST 800-171 focused (required for CUI compliance)
- Use **CUI Compliance** tile for NIST 800-171 results
"""
        add_message("assistant", output)

    elif tile_id == "scan_dc1":
        st.session_state.pending_command = "sudo /usr/local/bin/openscap_cui_scan.sh"
        st.session_state.pending_command_context = "Run NIST 800-171 CUI compliance scan on DC1 server"
        st.session_state.pending_timeout = 600
        st.session_state.show_approval_dialog = True

    elif tile_id == "view_reports":
        reports = get_report_list()
        output = """## 📊 Compliance Reports

Click a report link to view in a new tab.

| Report | Workstation | Date | Size |
|--------|-------------|------|------|
"""
        if reports:
            for report in reports[:20]:
                output += f"| [{report['filename']}]({report['url']}) | {report['workstation']} | {report['date']} | {report['size']} |\n"
        else:
            output += "| *No reports found* | - | - | - |\n"

        output += f"\n\n**Reports URL:** https://cyberinabox.net/compliance-reports/"

        add_message("assistant", output)


# =============================================================================
# Main UI
# =============================================================================

# Header
st.markdown(f"""
<div class="main-header">
    <h1>{APP_ICON} {APP_TITLE}</h1>
    <p>Server: {SERVER_HOSTNAME} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Connection status — fast REST check, no model inference
    st.subheader("🔌 Connection Status")
    try:
        _r = _requests.get("http://192.168.1.7:11434/api/tags", timeout=3)
        _r.raise_for_status()
        st.success("✅ AI Connected (Llama 3.3 70B)")
    except Exception as e:
        st.error(f"❌ AI Offline: {str(e)[:50]}")

    st.divider()

    # Security Alerts Section
    st.subheader("🚨 Security Alerts")

    # Check for alerts on refresh or initial load
    if "last_alert_check" not in st.session_state:
        st.session_state.last_alert_check = None
        st.session_state.cached_alerts = None

    if st.button("🔍 Check for Alerts"):
        with st.spinner("Scanning for abnormal events..."):
            st.session_state.cached_alerts = run_full_detection(since_minutes=60)
            st.session_state.last_alert_check = datetime.now()

    if st.session_state.cached_alerts:
        alerts = st.session_state.cached_alerts
        summary = alerts["summary"]

        if summary["total_events"] > 0:
            # Show alert counts with severity colors
            if summary["critical_count"] > 0:
                st.error(f"🔴 {summary['critical_count']} CRITICAL")
            if summary["high_count"] > 0:
                st.warning(f"🟠 {summary['high_count']} HIGH")
            if summary["medium_count"] > 0:
                st.info(f"🟡 {summary['medium_count']} MEDIUM")
            if summary["low_count"] > 0:
                st.success(f"🟢 {summary['low_count']} LOW")

            if summary["human_review_required"] > 0:
                st.markdown(f"**⚠️ {summary['human_review_required']} require review**")

            # Button to view details in main area
            if st.button("📋 View Alert Details"):
                st.session_state.show_alert_details = True
        else:
            st.success("✅ No alerts")

        if st.session_state.last_alert_check:
            st.caption(f"Last check: {st.session_state.last_alert_check.strftime('%H:%M:%S')}")

    st.divider()

    # AI Evaluation Reports
    st.subheader("📊 AI Evaluation")

    # Quick feedback stats and alert check
    try:
        fb_summary = get_feedback_summary()
        if fb_summary["total_responses"] > 0:
            st.metric("Responses", fb_summary["total_responses"])
            pos_rate = (fb_summary["positive_feedback"] / fb_summary["total_feedback"] * 100) if fb_summary["total_feedback"] > 0 else 0
            st.metric("Positive Rate", f"{pos_rate:.0f}%")

            # Check for alerts
            metrics = get_performance_metrics(days=7)
            alert_count = 0
            if metrics.calibration_error > 25:
                alert_count += 1
            if metrics.negative_rate > 40:
                alert_count += 1
            if metrics.total_responses > 10 and metrics.feedback_rate < 5:
                alert_count += 1

            if alert_count > 0:
                st.warning(f"⚠️ {alert_count} evaluation alert(s)")
        else:
            st.caption("No AI responses yet")
    except:
        st.caption("Evaluation data loading...")

    if st.button("📈 View Evaluation Report"):
        st.session_state.show_evaluation_report = True

    if st.button("📄 Export Compliance Report"):
        st.session_state.export_compliance_report = True

    st.divider()

    # Quick stats
    if st.button("🔄 Refresh Stats"):
        st.session_state.last_health_check = get_system_health()

    if st.session_state.last_health_check:
        h = st.session_state.last_health_check
        st.metric("CPU", f"{h['cpu']['percent']}%")
        st.metric("Memory", f"{h['memory']['percent']}%")
        st.metric("Uptime", h['uptime']['uptime_str'])

    st.divider()

    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    # Download audit log
    if st.button("📥 Download Audit Log"):
        try:
            with open(AUDIT_LOG_FILE, "r") as f:
                audit_content = f.read()
            st.download_button(
                "Download",
                audit_content,
                file_name=f"audit_log_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        except:
            st.warning("No audit log available")


# =============================================================================
# Security Alert Details Display
# =============================================================================
if st.session_state.show_alert_details and st.session_state.cached_alerts:
    alerts = st.session_state.cached_alerts
    summary = alerts["summary"]

    st.markdown("---")
    st.header("🚨 Security Alert Details")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Critical", summary["critical_count"],
                  delta_color="inverse" if summary["critical_count"] > 0 else "off")
    with col2:
        st.metric("High", summary["high_count"],
                  delta_color="inverse" if summary["high_count"] > 0 else "off")
    with col3:
        st.metric("Medium", summary["medium_count"])
    with col4:
        st.metric("Low", summary["low_count"])

    st.caption(f"Scan period: Last {summary['period_minutes']} minutes | Scanned at: {summary['scan_timestamp'][:19]}")

    # Display each event
    for event in alerts["events"]:
        severity_colors = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢",
            "INFO": "ℹ️",
        }
        icon = severity_colors.get(event["severity"], "⚪")

        with st.expander(f"{icon} [{event['severity']}] {event['summary']}", expanded=event["severity"] in ["CRITICAL", "HIGH"]):
            st.markdown(f"**Category:** {event['category'].replace('_', ' ').title()}")
            st.markdown(f"**Confidence:** {event['confidence_score']}%")
            st.markdown(f"**Human Review:** {'⚠️ Required' if event['human_review_required'] else '✅ Routine'}")

            st.markdown("---")
            st.markdown(event["details"])

            if event["evidence"]:
                st.markdown("**Evidence:**")
                for i, e in enumerate(event["evidence"], 1):
                    st.markdown(f"{i}. {e}")

            if event["alternative_hypotheses"]:
                st.markdown("**Alternative Hypotheses:**")
                for i, h in enumerate(event["alternative_hypotheses"], 1):
                    st.markdown(f"{i}. {h}")

            if event["validation_steps"]:
                st.markdown("**Validation Steps:**")
                for i, s in enumerate(event["validation_steps"], 1):
                    st.code(s, language="bash") if s.strip().startswith("`") or ":" in s else st.markdown(f"{i}. {s}")

            st.markdown(f"**Recommended Action:** {event['recommended_action']}")

            if event["raw_entries"]:
                with st.expander("📜 Raw Log Entries"):
                    for entry in event["raw_entries"][:5]:
                        st.code(entry[:500], language="text")

    # Close button
    if st.button("✖️ Close Alert Details"):
        st.session_state.show_alert_details = False
        st.rerun()

    st.markdown("---")

# =============================================================================
# Feedback Form Dialog
# =============================================================================
if st.session_state.show_feedback_form:
    response_id = st.session_state.show_feedback_form

    st.markdown("---")
    st.header("📝 AI Response Feedback")
    st.markdown(f"**Response ID:** `{response_id}`")

    with st.form(key="feedback_form"):
        # Issue categories
        st.markdown("**What issues did you notice?** (select all that apply)")
        issue_cols = st.columns(2)
        issues = []
        with issue_cols[0]:
            if st.checkbox("Factual Error"):
                issues.append(IssueCategory.FACTUAL_ERROR)
            if st.checkbox("Security Concern"):
                issues.append(IssueCategory.SECURITY_CONCERN)
            if st.checkbox("Overconfident"):
                issues.append(IssueCategory.OVERCONFIDENCE)
            if st.checkbox("Underconfident"):
                issues.append(IssueCategory.UNDERCONFIDENCE)
        with issue_cols[1]:
            if st.checkbox("Missing Context"):
                issues.append(IssueCategory.MISSING_CONTEXT)
            if st.checkbox("Wrong Hypothesis"):
                issues.append(IssueCategory.WRONG_HYPOTHESIS)
            if st.checkbox("Incomplete"):
                issues.append(IssueCategory.INCOMPLETE)
            if st.checkbox("Other Issue"):
                issues.append(IssueCategory.OTHER)

        # Correction text
        correction = st.text_area(
            "Correction or additional context:",
            placeholder="Describe what was wrong or provide the correct information...",
            height=100
        )

        # What confidence should have been
        actual_confidence = st.select_slider(
            "What should the confidence level have been?",
            options=["LOW", "MEDIUM", "HIGH", "N/A"],
            value="N/A"
        )

        # What actually happened
        outcome = st.text_input(
            "What was the actual outcome?",
            placeholder="e.g., 'The issue was actually X, not Y'"
        )

        # Submit buttons
        submit_col1, submit_col2 = st.columns(2)
        with submit_col1:
            submitted = st.form_submit_button("Submit Feedback", type="primary")
        with submit_col2:
            cancel = st.form_submit_button("Cancel")

        if submitted:
            feedback = ResponseFeedback(
                feedback_id=None,
                response_id=response_id,
                user_id="admin",
                rating=FeedbackRating.NEGATIVE,
                issue_categories=issues,
                correction_text=correction,
                actual_confidence_level=actual_confidence if actual_confidence != "N/A" else "",
                actual_outcome=outcome,
                timestamp=datetime.now().isoformat(),
            )
            feedback_id = store_feedback(feedback)
            if feedback_id > 0:
                st.success(f"Feedback submitted (ID: {feedback_id}). Thank you!")
                log_audit_event("FEEDBACK_SUBMITTED", json.dumps({
                    "response_id": response_id,
                    "feedback_id": feedback_id,
                    "issues": [i.value for i in issues],
                }))
            else:
                st.error("Failed to submit feedback. Please try again.")
            st.session_state.show_feedback_form = None
            st.rerun()

        if cancel:
            st.session_state.show_feedback_form = None
            st.rerun()

    st.markdown("---")

# =============================================================================
# Evaluation Report Display
# =============================================================================
if st.session_state.show_evaluation_report:
    st.markdown("---")
    st.header("📊 AI Evaluation Report")

    # Period selector
    report_days = st.selectbox("Report Period", [7, 14, 30, 90], index=2, format_func=lambda x: f"Last {x} days")

    try:
        metrics = get_performance_metrics(days=report_days)
        calibration = get_calibration_report(days=report_days)

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Responses", metrics.total_responses)
        with col2:
            st.metric("Feedback Rate", f"{metrics.feedback_rate}%")
        with col3:
            st.metric("Positive Rate", f"{metrics.positive_rate}%")
        with col4:
            st.metric("Calibration Error", f"{metrics.calibration_error}%")

        st.markdown(f"**Calibration Assessment:** {calibration.get('overall_assessment', 'N/A')}")

        # Confidence level breakdown
        st.subheader("Confidence Level Analysis")
        conf_data = calibration.get("by_confidence_level", {})
        if conf_data:
            conf_cols = st.columns(len(conf_data))
            for i, (level, data) in enumerate(conf_data.items()):
                with conf_cols[i]:
                    icon = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(level, "⚪")
                    st.markdown(f"**{icon} {level}**")
                    st.caption(f"Responses: {data.get('total_responses', 0)}")
                    st.caption(f"Feedback: {data.get('feedback_count', 0)}")
                    if data.get("accuracy_rate") is not None:
                        st.caption(f"Accuracy: {data['accuracy_rate']}%")
                    if data.get("calibration_error") is not None:
                        st.caption(f"Cal. Error: {data['calibration_error']}%")

        # Query type breakdown
        if metrics.responses_by_query_type:
            st.subheader("Responses by Query Type")
            for qt, count in metrics.responses_by_query_type.items():
                st.progress(count / max(metrics.responses_by_query_type.values()), text=f"{qt}: {count}")

        # Top issues
        if metrics.top_issues:
            st.subheader("Top Issues Reported")
            for issue in metrics.top_issues:
                st.markdown(f"- **{issue['description']}**: {issue['count']} occurrences")

        # Interpretation
        if calibration.get("interpretation"):
            st.subheader("Calibration Interpretation")
            for interp in calibration["interpretation"]:
                st.markdown(f"- **{interp['level']}**: {interp['status']}{interp['direction']}")

        # Historical Trends
        st.subheader("📈 Historical Trends")
        try:
            history = get_metrics_history(days=report_days)
            if history and len(history) > 1:
                import pandas as pd

                # Prepare data for charts
                df = pd.DataFrame(history)
                df['metric_date'] = pd.to_datetime(df['metric_date'])
                df = df.sort_values('metric_date')

                # Response counts chart
                st.markdown("**Daily Response & Feedback Counts**")
                chart_data = df[['metric_date', 'total_responses', 'positive_feedback_count', 'negative_feedback_count']].copy()
                chart_data.columns = ['Date', 'Responses', 'Positive', 'Negative']
                chart_data = chart_data.set_index('Date')
                st.line_chart(chart_data)

                # Calibration error trend
                if 'confidence_calibration_error' in df.columns and df['confidence_calibration_error'].notna().any():
                    st.markdown("**Calibration Error Trend**")
                    cal_data = df[['metric_date', 'confidence_calibration_error']].copy()
                    cal_data.columns = ['Date', 'Calibration Error (%)']
                    cal_data = cal_data.set_index('Date')
                    st.line_chart(cal_data)

                # Average confidence trend
                if 'avg_confidence_score' in df.columns and df['avg_confidence_score'].notna().any():
                    st.markdown("**Average Confidence Score Trend**")
                    conf_data = df[['metric_date', 'avg_confidence_score']].copy()
                    conf_data.columns = ['Date', 'Avg Confidence (%)']
                    conf_data = conf_data.set_index('Date')
                    st.line_chart(conf_data)
            else:
                st.info("Not enough historical data for trends. Check back after a few days of usage.")
        except Exception as trend_err:
            st.caption(f"Trend data not available: {trend_err}")

        # Archived Reports
        st.subheader("📁 Archived Reports")
        reports_dir = Path("/data/ai-workspace/sysadmin-agent/reports")
        if reports_dir.exists():
            report_files = sorted(reports_dir.glob("evaluation_report_*.md"), reverse=True)[:10]
            if report_files:
                for rf in report_files:
                    date_str = rf.stem.split("_")[-1]
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text(f"Report: {date_str[:4]}-{date_str[4:6]}-{date_str[6:]}")
                    with col2:
                        with open(rf) as f:
                            st.download_button(
                                "📥",
                                f.read(),
                                file_name=rf.name,
                                mime="text/markdown",
                                key=f"dl_{rf.name}"
                            )
            else:
                st.caption("No archived reports yet. Reports are generated daily at 6 AM.")
        else:
            st.caption("Reports directory not found.")

    except Exception as e:
        st.error(f"Error generating report: {str(e)}")

    if st.button("✖️ Close Report"):
        st.session_state.show_evaluation_report = False
        st.rerun()

    st.markdown("---")

# =============================================================================
# Compliance Report Export
# =============================================================================
if st.session_state.export_compliance_report:
    st.markdown("---")
    st.header("📄 Export Compliance Report")

    export_days = st.selectbox("Report Period", [7, 14, 30, 90], index=2, format_func=lambda x: f"Last {x} days", key="export_period")

    try:
        compliance_report = generate_compliance_report(days=export_days)
        markdown_report = export_report_markdown(compliance_report)

        st.markdown("### Preview")
        with st.expander("View Report Content", expanded=True):
            st.markdown(markdown_report)

        # Download buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download Markdown",
                markdown_report,
                file_name=f"ai_compliance_report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
        with col2:
            import json as json_mod
            st.download_button(
                "📥 Download JSON",
                json_mod.dumps(compliance_report, indent=2),
                file_name=f"ai_compliance_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

        log_audit_event("COMPLIANCE_REPORT_GENERATED", f"Period: {export_days} days")

    except Exception as e:
        st.error(f"Error generating compliance report: {str(e)}")

    if st.button("✖️ Close Export"):
        st.session_state.export_compliance_report = False
        st.rerun()

    st.markdown("---")

# =============================================================================
# Approval Dialog
# =============================================================================
if st.session_state.show_approval_dialog and st.session_state.pending_command:
    st.warning("⚠️ **APPROVAL REQUIRED**")

    with st.container():
        st.markdown(f"""
### Command Requiring Approval

**Context:** {st.session_state.pending_command_context}

**Command to execute:**
```bash
{st.session_state.pending_command}
```

This action requires your explicit approval before execution.
""")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("✅ Approve & Execute", type="primary"):
                cmd = st.session_state.pending_command
                timeout = st.session_state.pending_timeout
                with st.spinner(f"Executing: {cmd}"):
                    result = execute_approved_command(cmd, timeout=timeout)

                # oscap returns 2 when some checks fail (normal for compliance scans)
                is_oscap = "oscap" in cmd
                scan_completed = is_oscap and result.get("return_code") == 2

                if result["success"] or scan_completed:
                    output_text = result['output'] if result['output'] else '(no output)'
                    msg = f"""## ✅ Command Executed Successfully

**Command:** `{cmd}`

**Output:**
```
{output_text[:2000]}
```
"""
                    # For compliance scans, add link to the generated report
                    if is_oscap and "--report" in cmd:
                        msg += "\n**Report generated.** View it from the **View Reports** tile or at https://cyberinabox.net/compliance-reports/\n"

                    add_message("assistant", msg)
                else:
                    add_message("assistant", f"""## ❌ Command Failed

**Command:** `{cmd}`

**Error:**
```
{result['error']}
```
""")

                st.session_state.pending_command = None
                st.session_state.pending_command_context = None
                st.session_state.pending_timeout = 60
                st.session_state.show_approval_dialog = False
                st.rerun()

        with col2:
            if st.button("❌ Cancel"):
                add_message("assistant", f"Command cancelled: `{st.session_state.pending_command}`")
                st.session_state.pending_command = None
                st.session_state.pending_command_context = None
                st.session_state.pending_timeout = 60
                st.session_state.show_approval_dialog = False
                st.rerun()

    st.divider()


# =============================================================================
# Dashboard Tiles
# =============================================================================

st.header("📊 Quick Actions")

# Monitoring tiles
st.subheader("🔍 Monitoring")
cols = st.columns(5)
for i, tile in enumerate(DASHBOARD_TILES["monitoring"]):
    with cols[i % 5]:
        if st.button(
            f"{tile['icon']} {tile['title']}",
            key=f"tile_{tile['id']}",
            help=tile['description'],
            use_container_width=True,
        ):
            handle_tile_action(tile['id'])
            st.rerun()

# Maintenance tiles
st.subheader("🔧 Maintenance")
cols = st.columns(4)
for i, tile in enumerate(DASHBOARD_TILES["maintenance"]):
    with cols[i % 4]:
        btn_type = "primary" if tile.get("requires_approval") else "secondary"
        if st.button(
            f"{tile['icon']} {tile['title']}",
            key=f"tile_{tile['id']}",
            help=tile['description'] + (" (requires approval)" if tile.get("requires_approval") else ""),
            use_container_width=True,
            type=btn_type,
        ):
            handle_tile_action(tile['id'])
            st.rerun()

# Diagnostics tiles
st.subheader("🔬 Diagnostics")
cols = st.columns(4)
for i, tile in enumerate(DASHBOARD_TILES["diagnostics"]):
    with cols[i % 4]:
        if st.button(
            f"{tile['icon']} {tile['title']}",
            key=f"tile_{tile['id']}",
            help=tile['description'],
            use_container_width=True,
        ):
            handle_tile_action(tile['id'])
            st.rerun()

# Security tiles
st.subheader("🛡️ Security")
cols = st.columns(6)
for i, tile in enumerate(DASHBOARD_TILES["security"]):
    with cols[i % 6]:
        btn_type = "primary" if tile.get("requires_approval") else "secondary"
        if st.button(
            f"{tile['icon']} {tile['title']}",
            key=f"tile_{tile['id']}",
            help=tile['description'] + (" (requires approval)" if tile.get("requires_approval") else ""),
            use_container_width=True,
            type=btn_type,
        ):
            handle_tile_action(tile['id'])
            st.rerun()

# Compliance tiles
st.subheader("📋 Compliance")
cols = st.columns(6)
for i, tile in enumerate(DASHBOARD_TILES["compliance"]):
    with cols[i % 6]:
        btn_type = "primary" if tile.get("requires_approval") else "secondary"
        if st.button(
            f"{tile['icon']} {tile['title']}",
            key=f"tile_{tile['id']}",
            help=tile['description'] + (" (requires approval)" if tile.get("requires_approval") else ""),
            use_container_width=True,
            type=btn_type,
        ):
            handle_tile_action(tile['id'])
            st.rerun()

# Dashboard links
st.subheader("🔗 Dashboards")
cols = st.columns(8)
for i, tile in enumerate(DASHBOARD_TILES["dashboards"]):
    with cols[i % 8]:
        st.link_button(
            f"{tile['icon']} {tile['title']}",
            url=tile['url'],
            help=tile['description'],
            use_container_width=True,
        )

# Advanced tiles
with st.expander("⚠️ Advanced Actions"):
    cols = st.columns(4)
    for i, tile in enumerate(DASHBOARD_TILES["advanced"]):
        with cols[i % 4]:
            btn_type = "primary" if tile['risk_level'] in ['high', 'critical'] else "secondary"
            if st.button(
                f"{tile['icon']} {tile['title']}",
                key=f"tile_{tile['id']}",
                help=tile['description'],
                use_container_width=True,
                type=btn_type,
            ):
                handle_tile_action(tile['id'])
                st.rerun()

st.divider()

# =============================================================================
# Code Assistant Section (Claude Code-like functionality)
# =============================================================================

with st.expander("🖥️ Code Assistant (Terminal AI Integration)", expanded=False):
    st.markdown("""
    **Claude Code-like functionality** powered by local Llama 3.3 70B.
    - **Read-only queries**: No approval needed (logged)
    - **File edits**: Require your explicit approval
    - **Command execution**: Require your explicit approval
    """)

    # Check Aider API status
    aider_status = check_aider_api_health()
    if aider_status["healthy"]:
        st.success("✅ Aider API Connected")
    else:
        st.error(f"❌ Aider API Offline: {aider_status.get('error', 'Unknown')}")
        st.info("Start the service: `sudo systemctl start aider-api`")

    # Initialize session state for code assistant
    if "code_assistant_files" not in st.session_state:
        st.session_state.code_assistant_files = []
    if "code_assistant_path" not in st.session_state:
        st.session_state.code_assistant_path = "/data/ai-workspace/sysadmin-agent"
    if "code_assistant_messages" not in st.session_state:
        st.session_state.code_assistant_messages = []
    if "pending_edit" not in st.session_state:
        st.session_state.pending_edit = None

    # Tabs for different functions
    code_tab1, code_tab2, code_tab3, code_tab4 = st.tabs([
        "💬 Ask About Code",
        "📁 Browse Files",
        "📊 Analyze Logs",
        "✏️ Edit Files"
    ])

    # Tab 1: Ask About Code
    with code_tab1:
        st.subheader("Ask Questions About Code")
        st.caption("Read-only - no approval required (all queries logged)")

        # File selector for context
        selected_files = st.multiselect(
            "Select files for context (optional):",
            st.session_state.code_assistant_files,
            help="The AI will read these files to provide better answers"
        )

        # Query input
        code_query = st.text_area(
            "Your question:",
            placeholder="e.g., How does the authentication work in this file?",
            height=100,
            key="code_query_input"
        )

        if st.button("🔍 Ask AI", key="ask_code_btn", disabled=not aider_status["healthy"]):
            if code_query:
                log_audit_event("CODE_ASSISTANT_QUERY", f"Query: {code_query[:100]}...")
                with st.spinner("AI is analyzing..."):
                    result = query_code(code_query, selected_files if selected_files else None)

                if result["success"]:
                    st.markdown("### AI Response:")
                    st.markdown(result["output"])
                else:
                    st.error(f"Error: {result['error']}")
            else:
                st.warning("Please enter a question")

    # Tab 2: Browse Files
    with code_tab2:
        st.subheader("Browse Files")
        st.caption("Navigate allowed directories and select files")

        # Directory selector
        col1, col2 = st.columns([3, 1])
        with col1:
            new_path = st.text_input(
                "Current path:",
                value=st.session_state.code_assistant_path,
                key="browse_path"
            )
        with col2:
            if st.button("📂 Go", key="browse_go"):
                if is_path_allowed(new_path):
                    st.session_state.code_assistant_path = new_path
                    st.rerun()
                else:
                    st.error("Path not in allowed directories")

        # Quick directory buttons
        st.caption("Quick access:")
        quick_cols = st.columns(4)
        quick_dirs = [
            ("/data/ai-workspace/sysadmin-agent", "SysAdmin Agent"),
            ("/etc/fapolicyd", "fapolicyd"),
            ("/etc/yara", "YARA"),
            ("/var/www", "Web Root"),
        ]
        for i, (path, name) in enumerate(quick_dirs):
            with quick_cols[i]:
                if st.button(name, key=f"quick_{i}"):
                    st.session_state.code_assistant_path = path
                    st.rerun()

        # List directory contents
        dir_contents = list_directory(st.session_state.code_assistant_path)
        if dir_contents["error"]:
            st.error(dir_contents["error"])
        else:
            # Show parent directory link
            parent = str(Path(st.session_state.code_assistant_path).parent)
            if is_path_allowed(parent) and parent != st.session_state.code_assistant_path:
                if st.button("⬆️ Parent Directory"):
                    st.session_state.code_assistant_path = parent
                    st.rerun()

            # Show directories
            for d in dir_contents["directories"]:
                if st.button(f"📁 {d['name']}", key=f"dir_{d['name']}"):
                    st.session_state.code_assistant_path = d["path"]
                    st.rerun()

            # Show files with selection
            st.markdown("---")
            for f in dir_contents["files"]:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    icon = "📄" if f["editable"] else "📋"
                    st.text(f"{icon} {f['name']} ({f['size']} bytes)")
                with col2:
                    if st.button("👁️", key=f"view_{f['name']}", help="View file"):
                        file_content = read_file(f["path"])
                        if file_content["error"]:
                            st.error(file_content["error"])
                        else:
                            st.session_state.viewing_file = {
                                "path": f["path"],
                                "content": file_content["content"],
                                "lines": file_content["lines"]
                            }
                with col3:
                    if f["editable"]:
                        selected = f["path"] in st.session_state.code_assistant_files
                        if st.checkbox("📎", value=selected, key=f"sel_{f['name']}", help="Select for AI context"):
                            if f["path"] not in st.session_state.code_assistant_files:
                                st.session_state.code_assistant_files.append(f["path"])
                        else:
                            if f["path"] in st.session_state.code_assistant_files:
                                st.session_state.code_assistant_files.remove(f["path"])

            # Show file viewer if a file is being viewed
            if "viewing_file" in st.session_state and st.session_state.viewing_file:
                st.markdown("---")
                st.markdown(f"**Viewing:** `{st.session_state.viewing_file['path']}`")
                st.code(st.session_state.viewing_file["content"], language="python")
                if st.button("Close viewer"):
                    st.session_state.viewing_file = None
                    st.rerun()

    # Tab 3: Analyze Logs
    with code_tab3:
        st.subheader("AI Log Analysis")
        st.caption("Execute whitelisted commands and get AI analysis")
        st.warning("⚠️ Command execution requires approval")

        # Command selector
        command_key = st.selectbox(
            "Select analysis type:",
            list(ANALYSIS_COMMANDS.keys()),
            format_func=lambda x: f"{x}: {ANALYSIS_COMMANDS[x]}"
        )

        analysis_prompt = st.text_input(
            "What should the AI look for?",
            value="Analyze this output and highlight any issues, warnings, or security concerns.",
            key="analysis_prompt"
        )

        if st.button("🔍 Analyze", key="analyze_btn", type="primary"):
            # Set up approval workflow
            st.session_state.pending_code_action = {
                "type": "analyze",
                "command_key": command_key,
                "analysis_prompt": analysis_prompt
            }
            st.session_state.show_code_approval = True
            st.rerun()

    # Tab 4: Edit Files
    with code_tab4:
        st.subheader("AI-Powered File Editing")
        st.caption("Have AI edit files based on your instructions")
        st.error("⚠️ ALL FILE EDITS REQUIRE YOUR EXPLICIT APPROVAL")

        # Edit Mode Selector
        edit_mode = st.radio(
            "Edit Mode:",
            ["Standard", "Architect"],
            horizontal=True,
            help="Standard: Fast edits with CodeLlama. Architect: Complex changes using Llama 3.3 70B for planning + CodeLlama for implementation."
        )

        if edit_mode == "Architect":
            st.info("🏛️ **Architect Mode:** Uses Llama 3.3 70B for high-level planning and CodeLlama for implementation. Best for complex refactoring, architecture changes, or multi-step modifications. Takes longer but produces better results for complex tasks.")

        # Show selected files
        if st.session_state.code_assistant_files:
            st.markdown("**Selected files for editing:**")
            for f in st.session_state.code_assistant_files:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"📄 {f}")
                with col2:
                    if st.button("❌", key=f"remove_{f}"):
                        st.session_state.code_assistant_files.remove(f)
                        st.rerun()
        else:
            st.info("No files selected. Use the Browse tab to select files.")

        # Edit instruction
        edit_instruction = st.text_area(
            "Edit instruction:",
            placeholder="e.g., Add error handling to the main function",
            height=100,
            key="edit_instruction"
        )

        button_label = "🏛️ Request Architect Edit" if edit_mode == "Architect" else "✏️ Request Edit"
        if st.button(button_label, key="edit_btn", type="primary",
                     disabled=not st.session_state.code_assistant_files or not edit_instruction):
            # Set up approval workflow
            st.session_state.pending_code_action = {
                "type": "architect" if edit_mode == "Architect" else "edit",
                "files": st.session_state.code_assistant_files.copy(),
                "instruction": edit_instruction
            }
            st.session_state.show_code_approval = True
            st.rerun()

    # Approval Dialog for Code Assistant Actions
    if st.session_state.get("show_code_approval") and st.session_state.get("pending_code_action"):
        st.markdown("---")
        st.warning("⚠️ **APPROVAL REQUIRED FOR CODE ASSISTANT ACTION**")

        action = st.session_state.pending_code_action

        if action["type"] == "analyze":
            st.markdown(f"""
### Command Execution Request

**Analysis Type:** {action['command_key']}
**Description:** {ANALYSIS_COMMANDS.get(action['command_key'], 'Unknown')}
**AI Prompt:** {action['analysis_prompt']}

This will execute a whitelisted command and send the output to the AI for analysis.
            """)
        elif action["type"] == "edit":
            st.markdown(f"""
### File Edit Request (Standard Mode)

**Files to modify:**
{chr(10).join(f'- `{f}`' for f in action['files'])}

**Edit instruction:** {action['instruction']}

⚠️ **This will modify the above files!**
            """)
        elif action["type"] == "architect":
            st.markdown(f"""
### File Edit Request (🏛️ Architect Mode)

**Files to modify:**
{chr(10).join(f'- `{f}`' for f in action['files'])}

**Edit instruction:** {action['instruction']}

🏛️ **Architect Mode:** Uses Llama 3.3 70B for planning + CodeLlama for implementation.
This mode is best for complex refactoring and takes longer (up to 5 minutes).

⚠️ **This will modify the above files!**
            """)

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("✅ Approve", key="approve_code_action", type="primary"):
                log_audit_event("CODE_ASSISTANT_APPROVED", f"Action: {action['type']}")

                if action["type"] == "analyze":
                    with st.spinner("Executing and analyzing..."):
                        result = execute_and_analyze(
                            action["command_key"],
                            action["analysis_prompt"],
                            approved_by="admin"
                        )
                    if result["success"]:
                        st.markdown("### Command Output:")
                        st.code(result["command_output"][:3000])
                        st.markdown("### AI Analysis:")
                        st.markdown(result["ai_analysis"])
                    else:
                        st.error(f"Error: {result['error']}")

                elif action["type"] == "edit":
                    with st.spinner("AI is editing files..."):
                        result = edit_file(
                            action["instruction"],
                            action["files"],
                            auto_commit=False,
                            approved_by="admin"
                        )
                    if result["success"]:
                        st.success("✅ Files edited successfully!")
                        st.markdown("### Edit Output:")
                        st.code(result["output"])
                        log_audit_event("CODE_ASSISTANT_EDIT_COMPLETE", f"Files: {action['files']}")
                    else:
                        st.error(f"Error: {result['error']}")

                elif action["type"] == "architect":
                    with st.spinner("🏛️ Architect mode: Planning and implementing (this may take up to 5 minutes)..."):
                        result = architect_edit(
                            action["instruction"],
                            action["files"],
                            auto_commit=False,
                            approved_by="admin"
                        )
                    if result["success"]:
                        st.success("✅ Architect edit completed successfully!")
                        st.markdown("### Architect Output:")
                        st.code(result["output"])
                        log_audit_event("CODE_ASSISTANT_ARCHITECT_COMPLETE", f"Files: {action['files']}")
                    else:
                        st.error(f"Error: {result['error']}")

                st.session_state.pending_code_action = None
                st.session_state.show_code_approval = False

        with col2:
            if st.button("❌ Reject", key="reject_code_action"):
                log_audit_event("CODE_ASSISTANT_REJECTED", f"Action: {action['type']}")
                st.session_state.pending_code_action = None
                st.session_state.show_code_approval = False
                st.info("Action cancelled")
                st.rerun()

st.divider()

# =============================================================================
# Chat Interface
# =============================================================================

st.header("💬 AI Assistant")

# Display chat history
chat_container = st.container()
with chat_container:
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Add feedback buttons for assistant messages with response_id
            if message["role"] == "assistant" and message.get("response_id"):
                resp_id = message["response_id"]
                fb_cols = st.columns([1, 1, 1, 5])
                with fb_cols[0]:
                    if st.button("👍", key=f"hist_pos_{idx}_{resp_id[:8]}", help="Helpful"):
                        feedback = ResponseFeedback(
                            feedback_id=None,
                            response_id=resp_id,
                            user_id="admin",
                            rating=FeedbackRating.POSITIVE,
                            issue_categories=[],
                            correction_text="",
                            actual_confidence_level="",
                            actual_outcome="Positive feedback from history",
                            timestamp=datetime.now().isoformat(),
                        )
                        store_feedback(feedback)
                        st.toast("Thanks for your feedback!")
                with fb_cols[1]:
                    if st.button("👎", key=f"hist_neg_{idx}_{resp_id[:8]}", help="Issues"):
                        st.session_state.show_feedback_form = resp_id
                        st.rerun()
                with fb_cols[2]:
                    if st.button("📝", key=f"hist_corr_{idx}_{resp_id[:8]}", help="Correct"):
                        st.session_state.show_feedback_form = resp_id
                        st.rerun()

# Chat input
if prompt := st.chat_input("Ask me anything about this server..."):
    # Add user message
    add_message("user", prompt)
    log_audit_event("USER_QUERY", prompt[:200])

    with st.chat_message("user"):
        st.markdown(prompt)

    # Handle USB commands directly
    prompt_lower = prompt.lower().strip()
    usb_command_handled = False

    if prompt_lower == "usb status":
        usb_status = get_usb_devices()
        if usb_status.get('error'):
            response = f"## 🔌 USB Status\n\n⚠️ Error: {usb_status['error']}"
        else:
            response = f"## 🔌 USB Status\n\n**USBGuard:** {'🟢 Running' if usb_status['usbguard_running'] else '🔴 Stopped'}\n\n"
            blocked = usb_status.get('blocked_storage', [])
            allowed = usb_status.get('allowed_storage', [])
            if blocked:
                response += "**🔒 Blocked Storage:**\n"
                for dev in blocked:
                    response += f"- ID {dev['id']}: {dev.get('name', 'Unknown')}\n"
            if allowed:
                response += "**🔓 Allowed Storage:**\n"
                for dev in allowed:
                    response += f"- ID {dev['id']}: {dev.get('name', 'Unknown')}\n"
            if not blocked and not allowed:
                response += "No USB storage devices connected.\n"
        add_message("assistant", response)
        usb_command_handled = True

    elif prompt_lower.startswith("enable usb "):
        device_id = prompt_lower.replace("enable usb ", "").strip()
        st.session_state.pending_command = f"usbguard allow-device {device_id}"
        st.session_state.pending_command_context = f"Enable USB storage device ID {device_id}"
        st.session_state.show_approval_dialog = True
        usb_command_handled = True

    elif prompt_lower.startswith("block usb "):
        device_id = prompt_lower.replace("block usb ", "").strip()
        result = block_usb_device(device_id)
        if result["success"]:
            response = f"## 🔌 USB Blocked\n\n✅ Device {device_id} has been blocked."
        else:
            response = f"## 🔌 USB Block Failed\n\n❌ Error: {result.get('error', 'Unknown error')}"
        add_message("assistant", response)
        log_audit_event("USB_BLOCKED", f"Device {device_id}")
        usb_command_handled = True

    elif prompt_lower == "block all usb":
        result = block_all_usb_storage()
        if result["success"]:
            response = f"## 🔌 All USB Storage Blocked\n\n✅ Blocked {result['blocked_count']} storage device(s)."
        else:
            response = f"## 🔌 USB Block Status\n\nBlocked {result['blocked_count']} device(s).\n\n⚠️ Errors: {', '.join(result['errors'])}"
        add_message("assistant", response)
        log_audit_event("USB_ALL_BLOCKED", f"Blocked {result['blocked_count']} devices")
        usb_command_handled = True

    if usb_command_handled:
        st.rerun()

    # Check if user is requesting a command execution
    command_keywords = ["run", "execute", "restart", "start", "stop", "install", "update"]
    is_command_request = any(kw in prompt.lower() for kw in command_keywords)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Determine query type based on content
            query_type = "general"
            prompt_lower = prompt.lower()
            if any(kw in prompt_lower for kw in ["log", "error", "warning", "message"]):
                query_type = "log_analysis"
            elif any(kw in prompt_lower for kw in ["security", "alert", "threat", "attack", "ssh", "login"]):
                query_type = "security_scan"
            elif any(kw in prompt_lower for kw in ["health", "cpu", "memory", "disk", "performance"]):
                query_type = "health_check"

            # Get AI response
            response, response_id = get_ai_response(prompt, query_type=query_type)

            # Check if AI suggested a command
            if "```" in response and is_command_request:
                # Extract command from code block
                import re
                code_blocks = re.findall(r'```(?:bash|sh)?\n?(.*?)\n?```', response, re.DOTALL)
                if code_blocks:
                    suggested_cmd = code_blocks[0].strip()
                    if suggested_cmd and not suggested_cmd.startswith('#'):
                        # Check if it requires approval
                        if requires_approval(suggested_cmd):
                            st.session_state.pending_command = suggested_cmd
                            st.session_state.pending_command_context = f"AI suggested: {prompt}"
                            st.session_state.show_approval_dialog = True

            # Display the response
            st.markdown(response)
            add_message("assistant", response, response_id=response_id)

            # Show explainability summary if structured sections were detected
            if st.session_state.get("ai_responses"):
                latest = st.session_state.ai_responses[-1]
                if latest.get("parsing_successful"):
                    with st.expander("📊 AI Explainability Details", expanded=False):
                        conf_icons = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴", "UNKNOWN": "⚪"}
                        review_icons = {"REQUIRED": "🔴", "RECOMMENDED": "🟡", "ROUTINE": "🟢", "UNKNOWN": "⚪"}

                        col1, col2 = st.columns(2)
                        with col1:
                            conf_level = latest.get("confidence_level", "UNKNOWN")
                            conf_score = latest.get("confidence_score", 0)
                            st.metric(
                                "Confidence",
                                f"{conf_icons.get(conf_level, '⚪')} {conf_level}",
                                f"{conf_score}%"
                            )
                        with col2:
                            review_level = latest.get("human_review_level", "UNKNOWN")
                            st.metric(
                                "Human Review",
                                f"{review_icons.get(review_level, '⚪')} {review_level}"
                            )

                        if latest.get("evidence"):
                            st.markdown("**Evidence:**")
                            for i, e in enumerate(latest["evidence"][:3], 1):
                                st.markdown(f"{i}. {e[:100]}{'...' if len(e) > 100 else ''}")

                        if latest.get("validation_steps"):
                            st.markdown("**Validation Steps:**")
                            for i, v in enumerate(latest["validation_steps"][:3], 1):
                                st.markdown(f"{i}. {v[:100]}{'...' if len(v) > 100 else ''}")

                        # Feedback buttons
                        st.markdown("---")
                        st.markdown("**Rate this response:**")
                        fb_col1, fb_col2, fb_col3 = st.columns(3)
                        with fb_col1:
                            if st.button("👍 Helpful", key=f"fb_pos_{response_id}"):
                                feedback = ResponseFeedback(
                                    feedback_id=None,
                                    response_id=response_id,
                                    user_id="admin",
                                    rating=FeedbackRating.POSITIVE,
                                    issue_categories=[],
                                    correction_text="",
                                    actual_confidence_level="",
                                    actual_outcome="Positive feedback",
                                    timestamp=datetime.now().isoformat(),
                                )
                                store_feedback(feedback)
                                st.success("Thanks for your feedback!")
                        with fb_col2:
                            if st.button("👎 Issues", key=f"fb_neg_{response_id}"):
                                st.session_state.show_feedback_form = response_id
                        with fb_col3:
                            if st.button("📝 Correct", key=f"fb_corr_{response_id}"):
                                st.session_state.show_feedback_form = response_id

    st.rerun()

# =============================================================================
# Footer
# =============================================================================
st.divider()
st.caption(f"""
{APP_TITLE} | Server: {SERVER_HOSTNAME} | NIST 800-171 / CMMC Compliant
All actions are logged for audit compliance. High-risk operations require human approval.
""")
