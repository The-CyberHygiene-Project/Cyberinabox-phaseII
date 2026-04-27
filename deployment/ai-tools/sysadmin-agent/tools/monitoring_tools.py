"""
System Monitoring Tools for SysAdmin Agent
Provides system health metrics, log analysis, and status information
"""

import psutil
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import SYSTEM_LOGS


def get_system_health() -> Dict:
    """
    Get comprehensive system health metrics.

    Returns:
        Dict with CPU, memory, disk, load, and uptime information
    """
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()

    # Memory
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Load average
    load_avg = psutil.getloadavg()

    # Boot time / uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time

    # Top processes by CPU
    processes = []
    for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                       key=lambda p: p.info.get('cpu_percent', 0) or 0, reverse=True)[:5]:
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu_percent': round(proc.info.get('cpu_percent', 0) or 0, 1),
                'memory_percent': round(proc.info.get('memory_percent', 0) or 0, 1),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": {
            "percent": cpu_percent,
            "count": cpu_count,
            "frequency_mhz": cpu_freq.current if cpu_freq else None,
            "status": "🟢 Normal" if cpu_percent < 80 else "🟡 High" if cpu_percent < 95 else "🔴 Critical",
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 1),
            "used_gb": round(memory.used / (1024**3), 1),
            "available_gb": round(memory.available / (1024**3), 1),
            "percent": memory.percent,
            "status": "🟢 Normal" if memory.percent < 80 else "🟡 High" if memory.percent < 95 else "🔴 Critical",
        },
        "swap": {
            "total_gb": round(swap.total / (1024**3), 1),
            "used_gb": round(swap.used / (1024**3), 1),
            "percent": swap.percent,
        },
        "load_average": {
            "1min": round(load_avg[0], 2),
            "5min": round(load_avg[1], 2),
            "15min": round(load_avg[2], 2),
            "status": "🟢 Normal" if load_avg[0] < cpu_count else "🟡 High" if load_avg[0] < cpu_count * 2 else "🔴 Critical",
        },
        "uptime": {
            "boot_time": boot_time.isoformat(),
            "uptime_days": uptime.days,
            "uptime_str": f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m",
        },
        "top_processes": processes,
    }


def get_disk_usage() -> Dict:
    """
    Get disk usage for all mounted partitions.

    Returns:
        Dict with partition information and alerts
    """
    partitions = []
    alerts = []

    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            part_info = {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total_gb": round(usage.total / (1024**3), 1),
                "used_gb": round(usage.used / (1024**3), 1),
                "free_gb": round(usage.free / (1024**3), 1),
                "percent": usage.percent,
            }

            # Set status
            if usage.percent >= 90:
                part_info["status"] = "🔴 Critical"
                alerts.append(f"CRITICAL: {partition.mountpoint} is {usage.percent}% full!")
            elif usage.percent >= 80:
                part_info["status"] = "🟡 Warning"
                alerts.append(f"WARNING: {partition.mountpoint} is {usage.percent}% full")
            else:
                part_info["status"] = "🟢 Normal"

            partitions.append(part_info)
        except (PermissionError, OSError):
            continue

    return {
        "timestamp": datetime.now().isoformat(),
        "partitions": partitions,
        "alerts": alerts,
        "total_partitions": len(partitions),
    }


def get_running_services() -> Dict:
    """
    Get status of running systemd services.

    Returns:
        Dict with service information
    """
    services = []
    failed_services = []

    # Key services to always check
    critical_services = [
        "sshd", "firewalld", "httpd", "named", "ipa", "krb5kdc",
        "wazuh-manager", "graylog-server", "mongod", "opensearch",
        "prometheus", "node_exporter", "grafana-server",
    ]

    try:
        # Get all active services
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager", "--no-legend"],
            capture_output=True, text=True, timeout=30
        )

        running_services = set()
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split()
                if parts:
                    service_name = parts[0].replace('.service', '')
                    running_services.add(service_name)

        # Check critical services
        for svc in critical_services:
            status_result = subprocess.run(
                ["systemctl", "is-active", f"{svc}.service"],
                capture_output=True, text=True, timeout=10
            )
            status = status_result.stdout.strip()

            service_info = {
                "name": svc,
                "status": status,
                "is_critical": True,
            }

            if status == "active":
                service_info["status_icon"] = "🟢"
            elif status == "inactive":
                service_info["status_icon"] = "⚪"
            else:
                service_info["status_icon"] = "🔴"
                failed_services.append(svc)

            services.append(service_info)

        return {
            "timestamp": datetime.now().isoformat(),
            "services": services,
            "running_count": len(running_services),
            "failed_services": failed_services,
            "alerts": [f"Service {svc} is not running!" for svc in failed_services],
        }

    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "services": [],
        }


def get_recent_logs(log_name: str = "messages", lines: int = 50) -> Dict:
    """
    Get recent lines from a system log.

    Args:
        log_name: Name of the log (messages, secure, audit, etc.)
        lines: Number of lines to retrieve

    Returns:
        Dict with log content and any errors/warnings found
    """
    log_path = SYSTEM_LOGS.get(log_name, f"/var/log/{log_name}")

    try:
        # Use journalctl for systemd logs, tail for others
        if log_name in ["messages", "secure"]:
            result = subprocess.run(
                ["journalctl", "-n", str(lines), "--no-pager"],
                capture_output=True, text=True, timeout=30
            )
            content = result.stdout
        else:
            result = subprocess.run(
                ["tail", "-n", str(lines), log_path],
                capture_output=True, text=True, timeout=30
            )
            content = result.stdout

        # Count errors and warnings
        lines_list = content.split('\n')
        errors = [l for l in lines_list if 'error' in l.lower() or 'fail' in l.lower()]
        warnings = [l for l in lines_list if 'warn' in l.lower()]

        return {
            "timestamp": datetime.now().isoformat(),
            "log_name": log_name,
            "log_path": log_path,
            "lines_requested": lines,
            "content": content,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "recent_errors": errors[-5:] if errors else [],
            "recent_warnings": warnings[-5:] if warnings else [],
        }

    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "log_name": log_name,
            "error": str(e),
        }


def get_network_status() -> Dict:
    """
    Get network interface and connectivity status.

    Returns:
        Dict with network information
    """
    interfaces = []

    # Get network interfaces
    net_io = psutil.net_io_counters(pernic=True)
    net_addrs = psutil.net_if_addrs()

    for iface, addrs in net_addrs.items():
        iface_info = {
            "name": iface,
            "addresses": [],
        }

        for addr in addrs:
            if addr.family.name == 'AF_INET':
                iface_info["ipv4"] = addr.address
            elif addr.family.name == 'AF_INET6':
                iface_info["ipv6"] = addr.address

        if iface in net_io:
            io = net_io[iface]
            iface_info["bytes_sent"] = io.bytes_sent
            iface_info["bytes_recv"] = io.bytes_recv
            iface_info["packets_sent"] = io.packets_sent
            iface_info["packets_recv"] = io.packets_recv

        interfaces.append(iface_info)

    # Test connectivity to key hosts
    connectivity = []
    test_hosts = [
        ("Gateway", "192.168.1.1"),
        ("AI Server", "192.168.1.7"),
        ("DNS", "8.8.8.8"),
    ]

    for name, host in test_hosts:
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", host],
                capture_output=True, text=True, timeout=5
            )
            connectivity.append({
                "name": name,
                "host": host,
                "reachable": result.returncode == 0,
                "status": "🟢 OK" if result.returncode == 0 else "🔴 Unreachable",
            })
        except Exception:
            connectivity.append({
                "name": name,
                "host": host,
                "reachable": False,
                "status": "🔴 Error",
            })

    return {
        "timestamp": datetime.now().isoformat(),
        "interfaces": interfaces,
        "connectivity": connectivity,
    }


def get_firewall_status() -> Dict:
    """Get firewall rules and status."""
    try:
        # Get firewall state (use systemctl - works without polkit agent)
        state_result = subprocess.run(
            ["systemctl", "is-active", "firewalld"],
            capture_output=True, text=True, timeout=10
        )

        # Get active zones
        zones_result = subprocess.run(
            ["firewall-cmd", "--get-active-zones"],
            capture_output=True, text=True, timeout=10
        )

        # Get default zone info
        zone_result = subprocess.run(
            ["firewall-cmd", "--list-all"],
            capture_output=True, text=True, timeout=10
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "state": state_result.stdout.strip(),
            "active_zones": zones_result.stdout.strip(),
            "default_zone_rules": zone_result.stdout,
            "status": "🟢 Running" if state_result.stdout.strip() == "active" else "🔴 Not Running",
        }

    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


def get_security_summary() -> Dict:
    """Get a quick security status summary."""
    try:
        # Failed login attempts (last 24h)
        failed_logins = subprocess.run(
            ["journalctl", "-u", "sshd", "--since", "24 hours ago", "--no-pager"],
            capture_output=True, text=True, timeout=30
        )
        failed_count = failed_logins.stdout.lower().count("failed")

        # SELinux status
        selinux = subprocess.run(
            ["getenforce"],
            capture_output=True, text=True, timeout=10
        )

        # Root logins
        root_logins = subprocess.run(
            ["last", "-n", "5", "root"],
            capture_output=True, text=True, timeout=10
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "failed_ssh_attempts_24h": failed_count,
            "selinux_status": selinux.stdout.strip(),
            "recent_root_logins": root_logins.stdout.strip(),
            "status": "🟢 Normal" if failed_count < 10 else "🟡 Elevated" if failed_count < 50 else "🔴 High Risk",
        }

    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
