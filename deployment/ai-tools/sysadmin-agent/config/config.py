"""
Configuration for SysAdmin Agent Dashboard
NIST 800-171 / CMMC Compliant Settings
"""

import os
from pathlib import Path

# =============================================================================
# LLM Configuration - Direct Ollama connection
# =============================================================================
LLM_BASE_URL = "http://192.168.1.7:11434/v1"  # Ollama server (Mac Mini M4 Pro)
LLM_MODEL = "default"
LLM_API_KEY = "ollama"  # Ollama doesn't require auth but ChatOpenAI needs a value
LLM_TEMPERATURE = 0.1  # Low temperature for consistent sysadmin responses
LLM_MAX_TOKENS = 4096

# =============================================================================
# Server Configuration
# =============================================================================
SERVER_HOSTNAME = "dc1.cyberinabox.net"
SERVER_IP = "192.168.1.10"

# =============================================================================
# Paths
# =============================================================================
BASE_DIR = Path("/data/ai-workspace/sysadmin-agent")
LOG_DIR = BASE_DIR / "logs"
AUDIT_LOG_FILE = LOG_DIR / "agent_audit.log"

# System log paths for monitoring
SYSTEM_LOGS = {
    "messages": "/var/log/messages",
    "secure": "/var/log/secure",
    "audit": "/var/log/audit/audit.log",
    "dnf": "/var/log/dnf.log",
    "wazuh_alerts": "/var/ossec/logs/alerts/alerts.json",
    "graylog": "/var/log/graylog-server/server.log",
}

# =============================================================================
# Security: Whitelisted Commands
# =============================================================================
# Only these commands (and their subcommands) are allowed for execution
ALLOWED_COMMANDS = [
    # System Information
    "uname", "hostname", "uptime", "date", "who", "w", "last", "id",
    # Process Management
    "ps", "top", "htop", "pgrep", "pidof",
    # Disk & Filesystem
    "df", "du", "lsblk", "mount", "findmnt", "stat",
    # Network
    "ip", "ss", "netstat", "ping", "traceroute", "dig", "nslookup", "curl",
    # Services (systemctl - read operations)
    "systemctl status", "systemctl list-units", "systemctl is-active", "systemctl is-enabled",
    # Logs (read-only)
    "journalctl", "tail", "head", "cat", "less", "grep", "awk",
    # Package Management (read operations)
    "dnf check-update", "dnf list", "dnf info", "rpm -qa", "rpm -qi",
    "sudo dnf check-update", "sudo dnf list", "sudo dnf info",
    # Security
    "firewall-cmd --list", "firewall-cmd --get", "sestatus", "getenforce",
    # Monitoring
    "free", "vmstat", "iostat", "sar",
    # YARA Malware Detection
    "yara", "yara -r", "yara -w", "yara -s",
    # USBGuard
    "usbguard list-devices", "usbguard list-rules",
    "usbguard allow-device", "usbguard block-device",
    # OpenSCAP
    "oscap", "oscap xccdf eval", "oscap-ssh",
    # Suricata IDS/IPS
    "suricata --build-info", "suricatasc",
    "systemctl status suricata",
    "cat /var/log/suricata/fast.log", "cat /var/log/suricata/eve.json",
    "tail /var/log/suricata/fast.log", "tail /var/log/suricata/eve.json",
    # Wazuh SIEM
    "/var/ossec/bin/agent_control", "/var/ossec/bin/ossec-control status",
    "/var/ossec/bin/wazuh-control status",
    "systemctl status wazuh-manager", "systemctl status wazuh-agent",
    "cat /var/ossec/logs/alerts/alerts.json", "tail /var/ossec/logs/alerts/alerts.json",
    "cat /var/ossec/logs/ossec.log", "tail /var/ossec/logs/ossec.log",
    # Graylog
    "systemctl status graylog-server",
    "cat /var/log/graylog-server/server.log", "tail /var/log/graylog-server/server.log",
    "curl -s http://localhost:9000/api/system/cluster/nodes",
    # Prometheus
    "systemctl status prometheus",
    "curl -s http://localhost:9090/api/v1/status/config",
    "curl -s http://localhost:9090/api/v1/targets",
    "curl -s http://localhost:9090/api/v1/alerts",
]

# Commands requiring human approval before execution
APPROVAL_REQUIRED_COMMANDS = [
    # Service Management
    "systemctl start", "systemctl stop", "systemctl restart", "systemctl enable", "systemctl disable",
    "sudo systemctl start", "sudo systemctl stop", "sudo systemctl restart", "sudo systemctl enable", "sudo systemctl disable",
    # Package Management
    "dnf install", "dnf update", "dnf upgrade", "dnf remove",
    "sudo dnf install", "sudo dnf update", "sudo dnf upgrade", "sudo dnf remove", "sudo dnf clean",
    # System
    "reboot", "shutdown", "poweroff",
    "sudo reboot", "sudo shutdown", "sudo poweroff",
    # Firewall
    "firewall-cmd --add", "firewall-cmd --remove", "firewall-cmd --reload",
    # Backup
    "rsync", "tar", "cp -r",
    "/usr/local/bin/backup-critical-files.sh",
    "sudo /usr/local/bin/backup-critical-files.sh",
    # Security Services
    "systemctl start clamd@scan", "systemctl restart clamd@scan",
    "systemctl start suricata", "systemctl restart suricata",
    "systemctl start wazuh-manager", "systemctl restart wazuh-manager",
    "systemctl start wazuh-agent", "systemctl restart wazuh-agent",
    # Malware Scanning
    "clamscan -r", "clamdscan",
    "freshclam",  # Update virus definitions
    # Suricata rule updates
    "suricata-update",
    # Sudo versions for security tools
    "sudo yara", "sudo oscap", "sudo oscap-ssh",
    "sudo journalctl",
    # OpenSCAP local scan (DC1 only - workstations use Wazuh agents)
    "sudo /usr/local/bin/openscap_cui_scan.sh",
    "/usr/local/bin/openscap_cui_scan.sh",
]

# Absolutely forbidden commands (never execute)
FORBIDDEN_COMMANDS = [
    "rm -rf /", "rm -rf /*", "mkfs", "dd if=", "chmod -R 777",
    "> /dev/sda", ":(){ :|:& };:", "wget | sh", "curl | sh",
]

# =============================================================================
# Dashboard Tiles Configuration
# =============================================================================
DASHBOARD_TILES = {
    "monitoring": [
        {
            "id": "server_health",
            "title": "Check Server Health",
            "icon": "🖥️",
            "description": "CPU, memory, disk, load average",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "recent_logs",
            "title": "View Recent Logs",
            "icon": "📋",
            "description": "Last 100 lines from key logs",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "running_services",
            "title": "List Running Services",
            "icon": "⚙️",
            "description": "Active systemd services",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "disk_usage",
            "title": "Check Disk Usage",
            "icon": "💾",
            "description": "df -h + key partition status",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "update_status",
            "title": "System Update Status",
            "icon": "🔄",
            "description": "Available updates (no install)",
            "risk_level": "low",
            "requires_approval": False,
        },
    ],
    "maintenance": [
        {
            "id": "security_updates",
            "title": "Apply Security Updates",
            "icon": "🛡️",
            "description": "dnf update --security",
            "risk_level": "medium",
            "requires_approval": True,
        },
        {
            "id": "full_update",
            "title": "Full System Update",
            "icon": "📦",
            "description": "dnf update (all packages)",
            "risk_level": "high",
            "requires_approval": True,
        },
        {
            "id": "backup_nas",
            "title": "Backup to NAS",
            "icon": "💿",
            "description": "Rsync critical dirs to NAS",
            "risk_level": "medium",
            "requires_approval": True,
        },
        {
            "id": "restart_service",
            "title": "Restart Service",
            "icon": "🔁",
            "description": "Restart a specific service",
            "risk_level": "medium",
            "requires_approval": True,
        },
    ],
    "diagnostics": [
        {
            "id": "log_synopsis",
            "title": "Log Synopsis",
            "icon": "🔍",
            "description": "AI summary of log file",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "firewall_status",
            "title": "Firewall Status",
            "icon": "🔥",
            "description": "firewall-cmd rules summary",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "network_test",
            "title": "Network Test",
            "icon": "🌐",
            "description": "Ping/connectivity check",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "security_scan",
            "title": "Security Quick Scan",
            "icon": "🔒",
            "description": "Failed logins, suspicious activity",
            "risk_level": "low",
            "requires_approval": False,
        },
    ],
    "security": [
        {
            "id": "wazuh_alerts",
            "title": "Wazuh Alerts",
            "icon": "🛡️",
            "description": "Recent SIEM alerts and events",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "suricata_alerts",
            "title": "Suricata IDS Alerts",
            "icon": "🚨",
            "description": "Intrusion detection alerts",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "yara_status",
            "title": "YARA Malware Status",
            "icon": "🦠",
            "description": "YARA rules and recent detections",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "yara_scan",
            "title": "Run YARA Scan",
            "icon": "🔬",
            "description": "Scan directory with YARA rules",
            "risk_level": "medium",
            "requires_approval": True,
        },
        {
            "id": "virustotal_status",
            "title": "VirusTotal Alerts",
            "icon": "🔍",
            "description": "Recent VirusTotal scan results",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "security_services",
            "title": "Security Services Status",
            "icon": "🔐",
            "description": "Wazuh, Suricata, YARA status",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "graylog_status",
            "title": "Graylog Logs",
            "icon": "📊",
            "description": "Log management status and alerts",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "prometheus_status",
            "title": "Prometheus Metrics",
            "icon": "📈",
            "description": "Monitoring targets and alerts",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "usb_toggle",
            "title": "USB Access Control",
            "icon": "🔌",
            "description": "Enable/disable front USB ports",
            "risk_level": "medium",
            "requires_approval": True,
        },
    ],
    "compliance": [
        {
            "id": "compliance_status",
            "title": "CUI Compliance",
            "icon": "📋",
            "description": "NIST 800-171 CUI status from Wazuh agents",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "wazuh_sca",
            "title": "CIS Benchmark",
            "icon": "🔐",
            "description": "Wazuh SCA CIS benchmark results",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "scan_dc1",
            "title": "Scan DC1 (Local)",
            "icon": "🖥️",
            "description": "Run manual scan on this server",
            "risk_level": "medium",
            "requires_approval": True,
        },
        {
            "id": "view_reports",
            "title": "View Reports",
            "icon": "📊",
            "description": "Browse HTML compliance reports",
            "risk_level": "low",
            "requires_approval": False,
        },
    ],
    "dashboards": [
        {
            "id": "policy_index",
            "title": "Policy Index",
            "icon": "📜",
            "description": "SSP, policies, and compliance docs",
            "url": "https://cyberinabox.net/policy-index.html",
        },
        {
            "id": "grafana_node",
            "title": "Grafana Node Exporter",
            "icon": "📈",
            "description": "System metrics dashboard",
            "url": "https://grafana.cyberinabox.net/d/f24d133d-a42b-4a9d-8d19-85b1507b1f62/node-exporter-full?orgId=1&from=now-6h&to=now&timezone=browser&refresh=30s",
        },
        {
            "id": "monitoring_dashboard",
            "title": "Monitoring Dashboard",
            "icon": "🖥️",
            "description": "System monitoring overview",
            "url": "https://dc1.cyberinabox.net/dashboard/monitoring-dashboard.html",
        },
        {
            "id": "wazuh_dashboard",
            "title": "Wazuh SIEM",
            "icon": "🛡️",
            "description": "Security events and alerts",
            "url": "https://dc1.cyberinabox.net:5601",
        },
        {
            "id": "graylog_dashboard",
            "title": "Graylog Logs",
            "icon": "📊",
            "description": "Centralized log management",
            "url": "http://dc1.cyberinabox.net:9000",
        },
        {
            "id": "freeipa_dashboard",
            "title": "FreeIPA Admin",
            "icon": "👥",
            "description": "Identity management",
            "url": "https://dc1.cyberinabox.net/ipa/ui/",
        },
        {
            "id": "nextcloud_dashboard",
            "title": "NextCloud",
            "icon": "☁️",
            "description": "File sharing and collaboration",
            "url": "https://nextcloud.cyberinabox.net",
        },
        {
            "id": "cyberhygiene",
            "title": "CyberHygiene",
            "icon": "🌐",
            "description": "Main website",
            "url": "https://cyberinabox.net",
        },
    ],
    "advanced": [
        {
            "id": "audit_report",
            "title": "Generate Audit Report",
            "icon": "📊",
            "description": "Compliance report for POA&M",
            "risk_level": "low",
            "requires_approval": False,
        },
        {
            "id": "cleanup",
            "title": "System Cleanup",
            "icon": "🧹",
            "description": "Clear temp files, old logs",
            "risk_level": "medium",
            "requires_approval": True,
        },
        {
            "id": "reboot",
            "title": "Reboot Server",
            "icon": "⚠️",
            "description": "Emergency reboot",
            "risk_level": "critical",
            "requires_approval": True,
        },
    ],
}

# =============================================================================
# OpenSCAP Workstation Configuration
# =============================================================================
OPENSCAP_PROFILE = "xccdf_org.ssgproject.content_profile_cui"
OPENSCAP_PROFILE_NAME = "NIST 800-171 CUI"
OPENSCAP_DATASTREAM = "/usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml"
OPENSCAP_REPORTS_DIR = "/var/www/cyberhygiene/compliance-reports"

# Workstations to scan (name: hostname or IP)
# Update these with actual IPs/hostnames once configured
WORKSTATIONS = {
    "labrat": {
        "display_name": "Lab Rat",
        "hostname": "labrat.cyberinabox.net",
        "ip": "192.168.1.115",
        "ssh_user": "root",
    },
    "accounting": {
        "display_name": "Accounting",
        "hostname": "accounting.cyberinabox.net",
        "ip": "192.168.1.113",
        "ssh_user": "root",
    },
    "engineering": {
        "display_name": "Engineering",
        "hostname": "engineering.cyberinabox.net",
        "ip": "192.168.1.104",
        "ssh_user": "root",
    },
}

# All systems for compliance monitoring (including server and AI server)
ALL_SYSTEMS = {
    "dc1": {
        "display_name": "DC1 Server",
        "hostname": "dc1.cyberinabox.net",
        "ip": "192.168.1.10",
        "is_local": True,
    },
    "aiserver": {
        "display_name": "AI Server (Mac Mini)",
        "hostname": "AIserver.local",
        "ip": "192.168.1.7",
        "is_local": False,
        "os": "macOS",
    },
    **WORKSTATIONS,
}

# =============================================================================
# Audit Settings
# =============================================================================
AUDIT_ENABLED = True
AUDIT_RETENTION_DAYS = 90  # Keep audit logs for 90 days

# =============================================================================
# UI Settings
# =============================================================================
APP_TITLE = "SysAdmin Agent Dashboard"
APP_ICON = "🖥️"
REFRESH_INTERVAL = 30  # seconds for auto-refresh metrics
