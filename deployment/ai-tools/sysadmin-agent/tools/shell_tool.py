"""
Audited Shell Tool for SysAdmin Agent
NIST 800-171 / CMMC Compliant Command Execution

All commands are:
- Validated against whitelist
- Logged with full audit trail
- Require approval for high-risk operations
- Privileged commands routed through external sudo-proxy for HITL enforcement

CRITICAL: Commands requiring approval are routed through the sudo-proxy service
which runs OUTSIDE the agent's trust boundary. This ensures a compromised agent
cannot bypass approval requirements.
"""

import subprocess
import shlex
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from langchain_core.tools import tool

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import (
    ALLOWED_COMMANDS,
    APPROVAL_REQUIRED_COMMANDS,
    FORBIDDEN_COMMANDS,
    AUDIT_LOG_FILE,
    LOG_DIR,
)
from tools.sudo_proxy_client import (
    execute_via_proxy,
    should_use_proxy,
    is_proxy_available,
    get_proxy_status,
)

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure audit logging
audit_logger = logging.getLogger("sysadmin_audit")
audit_logger.setLevel(logging.INFO)

# File handler for audit log
if not audit_logger.handlers:
    file_handler = logging.FileHandler(AUDIT_LOG_FILE)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    )
    audit_logger.addHandler(file_handler)


def is_command_allowed(command: str) -> Tuple[bool, str]:
    """
    Check if a command is allowed to execute.

    Returns:
        Tuple of (is_allowed, reason)
    """
    command_lower = command.lower().strip()

    # Check forbidden commands first
    for forbidden in FORBIDDEN_COMMANDS:
        if forbidden.lower() in command_lower:
            return False, f"FORBIDDEN: Command contains dangerous pattern '{forbidden}'"

    # Check if command starts with an allowed prefix
    command_base = command_lower.split()[0] if command_lower else ""

    for allowed in ALLOWED_COMMANDS:
        if command_lower.startswith(allowed.lower()):
            return True, "ALLOWED"

    # Check if it's in the approval-required list
    for approval_cmd in APPROVAL_REQUIRED_COMMANDS:
        if command_lower.startswith(approval_cmd.lower()):
            return True, "REQUIRES_APPROVAL"

    return False, f"NOT_WHITELISTED: Command '{command_base}' is not in the allowed list"


def requires_approval(command: str) -> bool:
    """Check if a command requires human approval."""
    command_lower = command.lower().strip()

    for approval_cmd in APPROVAL_REQUIRED_COMMANDS:
        if command_lower.startswith(approval_cmd.lower()):
            return True
    return False


def log_audit_event(
    event_type: str,
    command: str,
    user: str = "system",
    result: str = "",
    approved: bool = False,
    approved_by: str = "",
    error: str = ""
):
    """Log an audit event for CMMC compliance."""
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "user": user,
        "command": command,
        "result_summary": result[:500] if result else "",  # Truncate long results
        "approved": approved,
        "approved_by": approved_by,
        "error": error,
    }

    audit_logger.info(json.dumps(event))
    return event


def execute_command(
    command: str,
    user: str = "agent",
    timeout: int = 60,
    approval_granted: bool = False,
    approved_by: str = "",
    reason: str = "SysAdmin Agent operation"
) -> dict:
    """
    Execute a shell command with full audit logging.

    CRITICAL: Commands requiring approval are routed through the external sudo-proxy.
    This ensures HITL enforcement cannot be bypassed by a compromised agent.

    Args:
        command: The command to execute
        user: User initiating the command
        timeout: Command timeout in seconds
        approval_granted: Whether human approval was given (legacy - ignored for proxy commands)
        approved_by: Who approved the command (legacy - ignored for proxy commands)
        reason: Reason for the command (shown to approver)

    Returns:
        dict with keys: success, output, error, requires_approval, audit_id
    """
    result = {
        "success": False,
        "output": "",
        "error": "",
        "requires_approval": False,
        "requires_proxy": False,
        "command": command,
        "timestamp": datetime.now().isoformat(),
    }

    # Validate command
    is_allowed, validation_reason = is_command_allowed(command)

    if not is_allowed:
        result["error"] = validation_reason
        log_audit_event("COMMAND_BLOCKED", command, user, error=validation_reason)
        return result

    # Check if this command should go through sudo-proxy (HITL enforcement)
    if requires_approval(command) or should_use_proxy(command):
        result["requires_proxy"] = True
        result["requires_approval"] = True

        # Verify sudo-proxy is available
        if not is_proxy_available():
            result["error"] = (
                "SECURITY: Sudo proxy unavailable. Privileged operations are disabled "
                "until the proxy is restored. This is a safety measure to ensure HITL compliance."
            )
            log_audit_event("PROXY_UNAVAILABLE", command, user, error="sudo-proxy not running")
            return result

        # Route through sudo-proxy for external HITL approval
        log_audit_event("ROUTING_TO_PROXY", command, user, error="Awaiting external HITL approval")

        proxy_result = execute_via_proxy(command, reason=reason, source=f"sysadmin-agent:{user}")

        # Map proxy result to our result format
        result["success"] = proxy_result.get("success", False)
        result["output"] = proxy_result.get("output", "")
        result["error"] = proxy_result.get("error", "")
        result["approved"] = proxy_result.get("approved", False)

        if result["approved"]:
            log_audit_event(
                "PROXY_APPROVED_EXECUTED" if result["success"] else "PROXY_APPROVED_FAILED",
                command,
                user,
                result=result["output"][:500],
                approved=True,
                approved_by="dashboard_operator",
                error=result["error"] if not result["success"] else ""
            )
        else:
            log_audit_event(
                "PROXY_DENIED",
                command,
                user,
                error=result["error"]
            )

        return result

    # Non-privileged command - execute directly
    try:
        log_audit_event("COMMAND_STARTED", command, user, approved=False, approved_by="")

        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        result["output"] = process.stdout
        result["error"] = process.stderr
        result["success"] = process.returncode == 0
        result["return_code"] = process.returncode

        log_audit_event(
            "COMMAND_COMPLETED" if result["success"] else "COMMAND_FAILED",
            command,
            user,
            result=process.stdout,
            approved=False,
            approved_by="",
            error=process.stderr if process.returncode != 0 else ""
        )

    except subprocess.TimeoutExpired:
        result["error"] = f"Command timed out after {timeout} seconds"
        log_audit_event("COMMAND_TIMEOUT", command, user, error=result["error"])

    except Exception as e:
        result["error"] = str(e)
        log_audit_event("COMMAND_ERROR", command, user, error=str(e))

    return result


@tool
def ShellTool(command: str) -> str:
    """
    Execute a shell command on the server.

    Only whitelisted commands are allowed. High-risk commands require human approval
    through the external sudo-proxy service (HITL enforcement).

    All commands are logged for audit compliance per NIST 800-171.

    Args:
        command: The shell command to execute

    Returns:
        Command output or error message
    """
    result = execute_command(command)

    # Command was routed through sudo-proxy
    if result.get("requires_proxy"):
        if result.get("approved"):
            if result["success"]:
                output = result["output"] if result["output"] else "(no output)"
                return f"✅ Approved and executed successfully:\n{output}"
            else:
                return f"⚠️ Approved but execution failed:\n{result['error']}"
        else:
            return f"❌ Request denied or timed out: {result['error']}"

    # Legacy approval flow (should not reach here with proxy integration)
    if result.get("requires_approval") and not result.get("requires_proxy"):
        return f"⚠️ APPROVAL REQUIRED: This command needs human approval.\nCommand: {command}"

    if not result["success"]:
        return f"❌ Error: {result['error']}"

    return result["output"] if result["output"] else "✅ Command completed successfully (no output)"


# Quick test functions
def test_shell_tool():
    """Test the shell tool with safe commands."""
    print("Testing shell tool...")

    # Test allowed command
    result = execute_command("uptime")
    print(f"uptime: {result}")

    # Test command requiring approval
    result = execute_command("systemctl restart httpd")
    print(f"restart (no approval): {result}")

    # Test forbidden command
    result = execute_command("rm -rf /")
    print(f"forbidden: {result}")


if __name__ == "__main__":
    test_shell_tool()
