"""
Code Assistant Tools for SysAdmin Agent Dashboard
Integrates with local Aider API for Claude Code-like functionality.

NIST 800-171 Compliance Features:
- All file modifications require human approval
- All actions are logged to audit trail
- Read-only operations logged but don't require approval
- Restricted to allowed directories only

Provides:
- AI-powered code queries
- Direct file editing with approval
- Command execution with AI analysis
"""

import requests
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Audit logging callback - set by the main app
_audit_logger: Optional[Callable[[str, str], None]] = None


def set_audit_logger(logger_func: Callable[[str, str], None]):
    """Set the audit logging function from main app."""
    global _audit_logger
    _audit_logger = logger_func


def log_audit(event_type: str, details: str):
    """Log an event to the audit trail."""
    if _audit_logger:
        _audit_logger(f"CODE_ASSISTANT_{event_type}", details)
    logger.info(f"[AUDIT] {event_type}: {details}")

# Aider API Configuration
AIDER_API_URL = "http://127.0.0.1:5001"

# Safe directories for browsing/editing
ALLOWED_DIRECTORIES = [
    "/data/ai-workspace",
    "/etc/fapolicyd",
    "/etc/usbguard",
    "/etc/yara",
    "/etc/httpd/conf.d",
    "/var/www",
    "/opt/aider-api",
    "/home",
    "/root",
    "/tmp",
]

# File extensions we can work with
ALLOWED_EXTENSIONS = [
    ".py", ".sh", ".bash", ".yml", ".yaml", ".json", ".conf", ".cfg",
    ".md", ".txt", ".html", ".css", ".js", ".xml", ".ini", ".rules",
    ".service", ".timer", ".socket", ".yar", ".yara",
]


def is_path_allowed(path: str) -> bool:
    """Check if a path is within allowed directories."""
    abs_path = os.path.abspath(path)
    return any(abs_path.startswith(allowed) for allowed in ALLOWED_DIRECTORIES)


def is_file_editable(path: str) -> bool:
    """Check if a file can be edited (allowed path and extension)."""
    if not is_path_allowed(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    return ext in ALLOWED_EXTENSIONS or ext == ""


def check_aider_api_health() -> Dict[str, Any]:
    """Check if Aider API is running and responsive."""
    try:
        response = requests.get(f"{AIDER_API_URL}/health", timeout=5)
        if response.status_code == 200:
            return {"healthy": True, "status": response.json()}
        return {"healthy": False, "error": f"HTTP {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"healthy": False, "error": "Cannot connect to Aider API (port 5001)"}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


def query_code(prompt: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Ask a coding question, optionally with file context.
    This is a READ-ONLY operation - no approval required but is logged.

    Args:
        prompt: The question or request
        files: Optional list of file paths for context

    Returns:
        Dict with success, output, and error fields
    """
    # Audit log the query (read-only, no approval needed)
    log_audit("QUERY", f"Prompt: {prompt[:100]}... Files: {files or 'none'}")

    try:
        # Validate files if provided
        if files:
            for f in files:
                if not os.path.exists(f):
                    log_audit("QUERY_BLOCKED", f"File not found: {f}")
                    return {"success": False, "output": "", "error": f"File not found: {f}"}
                if not is_path_allowed(f):
                    log_audit("QUERY_BLOCKED", f"Path not allowed: {f}")
                    return {"success": False, "output": "", "error": f"Path not allowed: {f}"}

        payload = {
            "prompt": prompt,
            "files": files or [],
            "read_only": True
        }

        response = requests.post(
            f"{AIDER_API_URL}/api/aider/query",
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "success": result.get("success", False),
                "output": result.get("output", ""),
                "error": result.get("error", "")
            }
        else:
            return {
                "success": False,
                "output": "",
                "error": f"API error: HTTP {response.status_code}"
            }

    except requests.exceptions.Timeout:
        return {"success": False, "output": "", "error": "Request timed out"}
    except Exception as e:
        logger.error(f"Error in query_code: {e}")
        return {"success": False, "output": "", "error": str(e)}


def edit_file(prompt: str, files: List[str], auto_commit: bool = False, approved_by: str = "unknown") -> Dict[str, Any]:
    """
    Have AI edit files based on the prompt.
    REQUIRES HUMAN APPROVAL - This modifies files!

    Args:
        prompt: The edit instruction
        files: List of file paths to edit
        auto_commit: Whether to auto-commit changes (default False)
        approved_by: Username of person who approved (for audit)

    Returns:
        Dict with success, output, modified_files, and error fields
    """
    # Audit log the edit request
    log_audit("EDIT_APPROVED", f"Approved by: {approved_by}, Files: {files}, Prompt: {prompt[:100]}...")

    try:
        # Validate files
        for f in files:
            if not os.path.exists(f):
                log_audit("EDIT_BLOCKED", f"File not found: {f}")
                return {"success": False, "output": "", "error": f"File not found: {f}"}
            if not is_file_editable(f):
                log_audit("EDIT_BLOCKED", f"Cannot edit (restricted): {f}")
                return {"success": False, "output": "", "error": f"Cannot edit: {f}"}
            if not os.access(f, os.W_OK):
                log_audit("EDIT_BLOCKED", f"No write permission: {f}")
                return {"success": False, "output": "", "error": f"No write permission: {f}"}

        payload = {
            "prompt": prompt,
            "files": files,
            "auto_commit": auto_commit
        }

        response = requests.post(
            f"{AIDER_API_URL}/api/aider/edit",
            json=payload,
            timeout=180
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "success": result.get("success", False),
                "output": result.get("output", ""),
                "modified_files": result.get("modified_files", []),
                "error": result.get("error", "")
            }
        else:
            return {
                "success": False,
                "output": "",
                "modified_files": [],
                "error": f"API error: HTTP {response.status_code}"
            }

    except requests.exceptions.Timeout:
        return {"success": False, "output": "", "modified_files": [], "error": "Request timed out"}
    except Exception as e:
        logger.error(f"Error in edit_file: {e}")
        return {"success": False, "output": "", "modified_files": [], "error": str(e)}


def architect_edit(prompt: str, files: List[str], auto_commit: bool = False, approved_by: str = "unknown") -> Dict[str, Any]:
    """
    Have AI architect and implement complex changes using two-model approach.
    Uses Llama 3.3 70B for planning and CodeLlama for implementation.
    REQUIRES HUMAN APPROVAL - This modifies files!

    Args:
        prompt: The edit instruction (complex changes work best)
        files: List of file paths to edit
        auto_commit: Whether to auto-commit changes (default False)
        approved_by: Username of person who approved (for audit)

    Returns:
        Dict with success, output, modified_files, and error fields
    """
    # Audit log the architect edit request
    log_audit("ARCHITECT_APPROVED", f"Approved by: {approved_by}, Files: {files}, Prompt: {prompt[:100]}...")

    try:
        # Validate files
        for f in files:
            if not os.path.exists(f):
                log_audit("ARCHITECT_BLOCKED", f"File not found: {f}")
                return {"success": False, "output": "", "error": f"File not found: {f}"}
            if not is_file_editable(f):
                log_audit("ARCHITECT_BLOCKED", f"Cannot edit (restricted): {f}")
                return {"success": False, "output": "", "error": f"Cannot edit: {f}"}
            if not os.access(f, os.W_OK):
                log_audit("ARCHITECT_BLOCKED", f"No write permission: {f}")
                return {"success": False, "output": "", "error": f"No write permission: {f}"}

        payload = {
            "prompt": prompt,
            "files": files,
            "auto_commit": auto_commit
        }

        response = requests.post(
            f"{AIDER_API_URL}/api/aider/architect",
            json=payload,
            timeout=330  # 5.5 min to allow for architect's 5 min timeout
        )

        if response.status_code == 200:
            result = response.json()
            log_audit("ARCHITECT_COMPLETE", f"Files modified: {result.get('modified_files', [])}")
            return {
                "success": result.get("success", False),
                "output": result.get("output", ""),
                "modified_files": result.get("modified_files", []),
                "mode": "architect",
                "error": result.get("error", "")
            }
        else:
            return {
                "success": False,
                "output": "",
                "modified_files": [],
                "mode": "architect",
                "error": f"API error: HTTP {response.status_code}"
            }

    except requests.exceptions.Timeout:
        return {"success": False, "output": "", "modified_files": [], "mode": "architect", "error": "Request timed out"}
    except Exception as e:
        logger.error(f"Error in architect_edit: {e}")
        return {"success": False, "output": "", "modified_files": [], "mode": "architect", "error": str(e)}


def execute_and_analyze(command_key: str, analysis_prompt: str, approved_by: str = "unknown") -> Dict[str, Any]:
    """
    Execute a whitelisted command and get AI analysis.
    REQUIRES HUMAN APPROVAL for command execution.

    Args:
        command_key: Key from the ALLOWED_COMMANDS in aider_service.py
        analysis_prompt: What to ask the AI about the output
        approved_by: Username of person who approved (for audit)

    Returns:
        Dict with success, command_output, ai_analysis, and error fields
    """
    # Audit log the execution
    log_audit("EXECUTE_APPROVED", f"Approved by: {approved_by}, Command: {command_key}, Analysis: {analysis_prompt[:50]}...")

    try:
        payload = {
            "command_key": command_key,
            "analysis_prompt": analysis_prompt,
            "system_prompt": "You are a helpful Linux system administrator assistant. Provide concise, actionable analysis."
        }

        response = requests.post(
            f"{AIDER_API_URL}/api/execute-and-analyze",
            json=payload,
            timeout=150
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "success": result.get("success", False),
                "command_output": result.get("command_output", ""),
                "ai_analysis": result.get("ai_analysis", ""),
                "command_executed": result.get("command_executed", ""),
                "error": ""
            }
        elif response.status_code == 403:
            return {
                "success": False,
                "command_output": "",
                "ai_analysis": "",
                "error": f"Command not in whitelist: {command_key}"
            }
        else:
            return {
                "success": False,
                "command_output": "",
                "ai_analysis": "",
                "error": f"API error: HTTP {response.status_code}"
            }

    except Exception as e:
        logger.error(f"Error in execute_and_analyze: {e}")
        return {"success": False, "command_output": "", "ai_analysis": "", "error": str(e)}


def list_directory(path: str) -> Dict[str, Any]:
    """
    List contents of a directory for file browsing.

    Args:
        path: Directory path to list

    Returns:
        Dict with files, directories, and error fields
    """
    try:
        if not is_path_allowed(path):
            return {"files": [], "directories": [], "error": f"Path not allowed: {path}"}

        if not os.path.isdir(path):
            return {"files": [], "directories": [], "error": f"Not a directory: {path}"}

        files = []
        directories = []

        for entry in sorted(os.listdir(path)):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                directories.append({
                    "name": entry,
                    "path": full_path,
                    "type": "directory"
                })
            else:
                ext = os.path.splitext(entry)[1].lower()
                size = os.path.getsize(full_path)
                files.append({
                    "name": entry,
                    "path": full_path,
                    "type": "file",
                    "extension": ext,
                    "size": size,
                    "editable": ext in ALLOWED_EXTENSIONS
                })

        return {
            "files": files,
            "directories": directories,
            "current_path": path,
            "error": ""
        }

    except PermissionError:
        return {"files": [], "directories": [], "error": f"Permission denied: {path}"}
    except Exception as e:
        return {"files": [], "directories": [], "error": str(e)}


def read_file(path: str, max_lines: int = 500) -> Dict[str, Any]:
    """
    Read contents of a file.
    READ-ONLY operation - logged but no approval required.

    Args:
        path: File path to read
        max_lines: Maximum number of lines to return

    Returns:
        Dict with content, lines, and error fields
    """
    # Audit log file read (read-only, no approval needed)
    log_audit("FILE_READ", f"Path: {path}")

    try:
        if not is_path_allowed(path):
            log_audit("FILE_READ_BLOCKED", f"Path not allowed: {path}")
            return {"content": "", "lines": 0, "error": f"Path not allowed: {path}"}

        if not os.path.isfile(path):
            return {"content": "", "lines": 0, "error": f"Not a file: {path}"}

        with open(path, 'r', errors='replace') as f:
            lines = f.readlines()

        total_lines = len(lines)
        if total_lines > max_lines:
            content = ''.join(lines[:max_lines])
            content += f"\n... (truncated, showing {max_lines} of {total_lines} lines)"
        else:
            content = ''.join(lines)

        return {
            "content": content,
            "lines": total_lines,
            "truncated": total_lines > max_lines,
            "error": ""
        }

    except PermissionError:
        return {"content": "", "lines": 0, "error": f"Permission denied: {path}"}
    except Exception as e:
        return {"content": "", "lines": 0, "error": str(e)}


# Available analysis commands (must match keys in aider_service.py)
ANALYSIS_COMMANDS = {
    "wazuh_alerts": "Analyze Wazuh security alerts",
    "secure_logs": "Analyze authentication logs",
    "audit_logs": "Analyze audit logs",
    "system_messages": "Analyze system messages for errors",
    "apache_errors": "Analyze Apache error logs",
    "journal_errors": "Analyze recent journal errors",
    "top_processes": "Analyze top processes",
    "disk_usage": "Analyze disk usage",
    "disk_usage_var": "Analyze /var disk usage",
    "memory_usage": "Analyze memory usage",
    "cpu_usage": "Analyze CPU usage",
    "system_status": "Analyze overall system status",
    "failed_logins": "Analyze failed login attempts",
    "ipa_status": "Analyze FreeIPA status",
    "firewall_status": "Analyze firewall configuration",
    "dns_check": "Analyze DNS configuration",
}
