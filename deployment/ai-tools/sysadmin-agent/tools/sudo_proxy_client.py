"""
Sudo Proxy Client for SysAdmin Agent
Routes privileged commands through the external sudo-proxy for HITL approval.

NIST 800-171 Compliance:
- All privileged operations require human approval
- Cryptographically signed approval responses
- Complete audit trail
"""

import os
import json
import socket
import logging
from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List
from pathlib import Path

# Configure logging
logger = logging.getLogger("sudo_proxy_client")

# Sudo proxy socket path
SUDO_PROXY_SOCKET = '/run/sudo-proxy/sudo-proxy.sock'
SUDO_PROXY_TIMEOUT = 130  # Slightly longer than proxy's 120s timeout


# Mapping from raw shell commands to structured sudo-proxy command types
# This ensures only allowlisted operations go through
COMMAND_MAPPING = {
    # =========================================================================
    # Service management
    # =========================================================================
    'systemctl restart': ('systemctl_restart', lambda args: args[2:] if len(args) > 2 else []),
    'systemctl start': ('systemctl_start', lambda args: args[2:] if len(args) > 2 else []),
    'systemctl stop': ('systemctl_stop', lambda args: args[2:] if len(args) > 2 else []),
    'systemctl status': ('systemctl_status', lambda args: args[2:] if len(args) > 2 else []),
    'systemctl enable': ('systemctl_enable', lambda args: args[2:] if len(args) > 2 else []),
    'systemctl disable': ('systemctl_disable', lambda args: args[2:] if len(args) > 2 else []),
    'sudo systemctl restart': ('systemctl_restart', lambda args: args[3:] if len(args) > 3 else []),
    'sudo systemctl start': ('systemctl_start', lambda args: args[3:] if len(args) > 3 else []),
    'sudo systemctl stop': ('systemctl_stop', lambda args: args[3:] if len(args) > 3 else []),
    'sudo systemctl status': ('systemctl_status', lambda args: args[3:] if len(args) > 3 else []),
    'sudo systemctl enable': ('systemctl_enable', lambda args: args[3:] if len(args) > 3 else []),
    'sudo systemctl disable': ('systemctl_disable', lambda args: args[3:] if len(args) > 3 else []),

    # =========================================================================
    # FreeIPA
    # =========================================================================
    'ipactl status': ('ipactl_status', lambda args: []),
    'sudo ipactl status': ('ipactl_status', lambda args: []),
    'ipactl restart': ('ipactl_restart', lambda args: []),
    'sudo ipactl restart': ('ipactl_restart', lambda args: []),

    # =========================================================================
    # Firewall
    # =========================================================================
    'firewall-cmd --list-all': ('firewall_list', lambda args: []),
    'sudo firewall-cmd --list-all': ('firewall_list', lambda args: []),
    'firewall-cmd --reload': ('firewall_reload', lambda args: []),
    'sudo firewall-cmd --reload': ('firewall_reload', lambda args: []),

    # =========================================================================
    # System info (non-privileged, but routed for consistency)
    # =========================================================================
    'df -h': ('df', lambda args: []),
    'df': ('df', lambda args: []),
    'free -h': ('free', lambda args: []),
    'free': ('free', lambda args: []),
    'uptime': ('uptime', lambda args: []),

    # =========================================================================
    # Log viewing
    # =========================================================================
    'journalctl': ('journalctl', lambda args: args[1:] if len(args) > 1 else []),
    'sudo journalctl': ('journalctl', lambda args: args[2:] if len(args) > 2 else []),
    'tail': ('cat_log', lambda args: args[1:] if len(args) > 1 else []),
    'sudo tail': ('cat_log', lambda args: args[2:] if len(args) > 2 else []),

    # =========================================================================
    # Security scanning
    # =========================================================================
    'clamscan': ('clamscan', lambda args: args[1:] if len(args) > 1 else []),
    'sudo clamscan': ('clamscan', lambda args: args[2:] if len(args) > 2 else []),
    'clamdscan': ('clamscan', lambda args: args[1:] if len(args) > 1 else []),
    'freshclam': ('freshclam', lambda args: []),
    'sudo freshclam': ('freshclam', lambda args: []),
    'suricata-update': ('suricata_update', lambda args: []),
    'sudo suricata-update': ('suricata_update', lambda args: []),
    'sudo /usr/local/bin/openscap_cui_scan.sh': ('openscap_scan', lambda args: []),

    # =========================================================================
    # Package management
    # =========================================================================
    'dnf check-update': ('dnf_check_update', lambda args: []),
    'dnf update --security': ('dnf_update_security', lambda args: []),
    'sudo dnf update --security': ('dnf_update_security', lambda args: []),
}


def parse_command(command: str) -> Tuple[Optional[str], List[str]]:
    """
    Parse a shell command and map to sudo-proxy command type.

    Returns:
        Tuple of (command_type, args) or (None, []) if not mappable
    """
    parts = command.strip().split()
    if not parts:
        return (None, [])

    # Try to find the longest matching prefix
    for prefix_len in range(len(parts), 0, -1):
        prefix = ' '.join(parts[:prefix_len])
        if prefix in COMMAND_MAPPING:
            cmd_type, args_extractor = COMMAND_MAPPING[prefix]
            args = args_extractor(parts)
            return (cmd_type, args)

    return (None, [])


def is_proxy_available() -> bool:
    """Check if sudo-proxy socket exists and is accessible."""
    return os.path.exists(SUDO_PROXY_SOCKET)


def execute_via_proxy(
    command: str,
    reason: str = "SysAdmin Agent operation",
    source: str = "sysadmin-agent"
) -> Dict[str, Any]:
    """
    Execute a command through the sudo-proxy with HITL approval.

    Args:
        command: The shell command to execute
        reason: Reason for the command (shown to approver)
        source: Source identifier

    Returns:
        Dict with keys: success, output, error, approved, requires_proxy
    """
    result = {
        'success': False,
        'output': '',
        'error': '',
        'approved': False,
        'requires_proxy': True,
        'command': command,
        'timestamp': datetime.now().isoformat()
    }

    # Parse command to structured format
    command_type, args = parse_command(command)

    if command_type is None:
        result['error'] = f"Command not supported by sudo-proxy: {command}"
        result['requires_proxy'] = False
        logger.warning(f"Unmapped command: {command}")
        return result

    # Check proxy availability
    if not is_proxy_available():
        result['error'] = "Sudo proxy not available - privileged operations disabled"
        logger.error("Sudo proxy socket not found")
        return result

    # Build request
    request = {
        'type': 'approval_request',
        'command_type': command_type,
        'args': args,
        'reason': reason,
        'source': source,
        'timestamp': datetime.now().isoformat()
    }

    logger.info(f"Sending to sudo-proxy: {command_type} {args}")

    try:
        # Connect to sudo proxy
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(SUDO_PROXY_TIMEOUT)
        sock.connect(SUDO_PROXY_SOCKET)

        # Send request
        sock.sendall(json.dumps(request).encode() + b'\n')

        # Wait for response
        response_data = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response_data += chunk
            if b'\n' in response_data:
                break

        sock.close()

        # Parse response
        response = json.loads(response_data.decode().strip())

        result['approved'] = response.get('approved', False)

        if result['approved']:
            result['success'] = response.get('success', False)
            result['output'] = response.get('result', '')
        else:
            result['error'] = response.get('error', 'Request denied')

        logger.info(f"Proxy response: approved={result['approved']}, success={result['success']}")

    except socket.timeout:
        result['error'] = "Sudo proxy request timed out - approval window expired"
        logger.error("Sudo proxy timeout")
    except ConnectionRefusedError:
        result['error'] = "Sudo proxy connection refused - service may be down"
        logger.error("Sudo proxy connection refused")
    except Exception as e:
        result['error'] = f"Sudo proxy error: {str(e)}"
        logger.error(f"Sudo proxy error: {e}")

    return result


def should_use_proxy(command: str) -> bool:
    """
    Determine if a command should be routed through the sudo-proxy.

    Returns True for any command that:
    1. Contains 'sudo'
    2. Is in APPROVAL_REQUIRED_COMMANDS
    3. Modifies system state (restart, start, stop services, etc.)
    """
    command_lower = command.lower().strip()

    # Keywords that indicate privileged operations
    privileged_keywords = [
        'sudo', 'systemctl restart', 'systemctl start', 'systemctl stop',
        'systemctl enable', 'systemctl disable', 'reboot', 'shutdown',
        'dnf install', 'dnf update', 'dnf remove', 'firewall-cmd --add',
        'firewall-cmd --remove', 'ipactl', 'kadmin'
    ]

    for keyword in privileged_keywords:
        if keyword in command_lower:
            return True

    return False


def get_proxy_status() -> Dict[str, Any]:
    """Get sudo-proxy status information."""
    return {
        'available': is_proxy_available(),
        'socket_path': SUDO_PROXY_SOCKET,
        'timeout_seconds': SUDO_PROXY_TIMEOUT
    }
