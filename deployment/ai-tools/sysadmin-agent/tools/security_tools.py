"""
Security Tools for SysAdmin Agent Dashboard
Provides functions for Wazuh, Suricata, and ClamAV monitoring
NIST 800-171 / CMMC Compliant
"""

import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional


def get_wazuh_alerts(hours: int = 24, max_alerts: int = 50) -> Dict[str, Any]:
    """Get recent Wazuh SIEM alerts."""
    result = {
        "status": "unknown",
        "service_running": False,
        "alerts": [],
        "alert_count": 0,
        "error": None,
    }

    # Check if Wazuh manager is running
    try:
        svc_check = subprocess.run(
            ["systemctl", "is-active", "wazuh-manager"],
            capture_output=True, text=True, timeout=10
        )
        result["service_running"] = svc_check.stdout.strip() == "active"
    except Exception as e:
        result["error"] = f"Failed to check service: {e}"

    # Try to read recent alerts
    alerts_file = Path("/var/ossec/logs/alerts/alerts.json")
    if alerts_file.exists():
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            alerts = []

            # Read last 1000 lines to find recent alerts
            tail_result = subprocess.run(
                ["tail", "-n", "1000", str(alerts_file)],
                capture_output=True, text=True, timeout=30
            )

            for line in tail_result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    alert = json.loads(line)
                    # Parse timestamp
                    ts_str = alert.get("timestamp", "")
                    if ts_str:
                        alerts.append({
                            "timestamp": ts_str,
                            "rule_id": alert.get("rule", {}).get("id", ""),
                            "rule_level": alert.get("rule", {}).get("level", 0),
                            "description": alert.get("rule", {}).get("description", ""),
                            "agent": alert.get("agent", {}).get("name", ""),
                            "location": alert.get("location", ""),
                        })
                except json.JSONDecodeError:
                    continue

            # Sort by timestamp descending and limit
            alerts.sort(key=lambda x: x["timestamp"], reverse=True)
            result["alerts"] = alerts[:max_alerts]
            result["alert_count"] = len(alerts)
            result["status"] = "ok"

        except Exception as e:
            result["error"] = f"Failed to read alerts: {e}"
    else:
        result["error"] = "Alerts file not found"

    return result


def get_suricata_alerts(hours: int = 24, max_alerts: int = 50) -> Dict[str, Any]:
    """Get recent Suricata IDS alerts."""
    result = {
        "status": "unknown",
        "service_running": False,
        "alerts": [],
        "alert_count": 0,
        "error": None,
    }

    # Check if Suricata is running
    try:
        svc_check = subprocess.run(
            ["systemctl", "is-active", "suricata"],
            capture_output=True, text=True, timeout=10
        )
        result["service_running"] = svc_check.stdout.strip() == "active"
    except Exception as e:
        result["error"] = f"Failed to check service: {e}"

    # Try to read fast.log for quick alerts
    fast_log = Path("/var/log/suricata/fast.log")
    if fast_log.exists():
        try:
            tail_result = subprocess.run(
                ["tail", "-n", "200", str(fast_log)],
                capture_output=True, text=True, timeout=30
            )

            alerts = []
            for line in tail_result.stdout.strip().split('\n'):
                if not line:
                    continue
                alerts.append({"raw": line})

            alerts.reverse()  # Most recent first
            result["alerts"] = alerts[:max_alerts]
            result["alert_count"] = len(alerts)
            result["status"] = "ok"

        except Exception as e:
            result["error"] = f"Failed to read fast.log: {e}"

    # Also try eve.json for structured alerts
    eve_log = Path("/var/log/suricata/eve.json")
    if eve_log.exists() and not result["alerts"]:
        try:
            tail_result = subprocess.run(
                ["tail", "-n", "500", str(eve_log)],
                capture_output=True, text=True, timeout=30
            )

            alerts = []
            for line in tail_result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    if event.get("event_type") == "alert":
                        alerts.append({
                            "timestamp": event.get("timestamp", ""),
                            "src_ip": event.get("src_ip", ""),
                            "dest_ip": event.get("dest_ip", ""),
                            "signature": event.get("alert", {}).get("signature", ""),
                            "category": event.get("alert", {}).get("category", ""),
                            "severity": event.get("alert", {}).get("severity", 0),
                        })
                except json.JSONDecodeError:
                    continue

            alerts.sort(key=lambda x: x["timestamp"], reverse=True)
            result["alerts"] = alerts[:max_alerts]
            result["alert_count"] = len(alerts)
            result["status"] = "ok"

        except Exception as e:
            if not result["error"]:
                result["error"] = f"Failed to read eve.json: {e}"

    if not fast_log.exists() and not eve_log.exists():
        result["error"] = "No Suricata log files found"

    return result


def get_yara_status() -> Dict[str, Any]:
    """Get YARA malware detection status."""
    result = {
        "status": "unknown",
        "yara_installed": False,
        "yara_version": None,
        "rules_count": 0,
        "rules_files": [],
        "recent_detections": [],
        "error": None,
    }

    # Check if YARA is installed
    try:
        version_check = subprocess.run(
            ["yara", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if version_check.returncode == 0:
            result["yara_installed"] = True
            result["yara_version"] = version_check.stdout.strip()
    except Exception as e:
        result["error"] = f"YARA not found: {e}"

    # Check YARA rules directory
    rules_dirs = [
        Path("/var/ossec/ruleset/yara/rules"),
        Path("/etc/yara/rules"),
        Path("/usr/share/yara/rules"),
    ]

    for rules_dir in rules_dirs:
        if rules_dir.exists():
            try:
                rules_files = list(rules_dir.glob("*.yar")) + list(rules_dir.glob("*.yara"))
                result["rules_files"] = [str(f.name) for f in rules_files]
                result["rules_count"] = len(rules_files)
                break
            except Exception:
                pass

    # Check for recent YARA detections in Wazuh alerts
    alerts_file = Path("/var/ossec/logs/alerts/alerts.json")
    if alerts_file.exists():
        try:
            tail_result = subprocess.run(
                ["tail", "-n", "500", str(alerts_file)],
                capture_output=True, text=True, timeout=30
            )

            for line in tail_result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    alert = json.loads(line)
                    rule_desc = alert.get("rule", {}).get("description", "").lower()
                    if "yara" in rule_desc or "malware" in rule_desc:
                        result["recent_detections"].append({
                            "timestamp": alert.get("timestamp", ""),
                            "rule_id": alert.get("rule", {}).get("id", ""),
                            "description": alert.get("rule", {}).get("description", ""),
                            "file": alert.get("data", {}).get("file", ""),
                        })
                except json.JSONDecodeError:
                    continue

            result["recent_detections"] = result["recent_detections"][-10:]  # Last 10
            result["status"] = "ok"

        except Exception as e:
            if not result["error"]:
                result["error"] = f"Failed to read alerts: {e}"

    return result


def get_virustotal_alerts() -> Dict[str, Any]:
    """Get recent VirusTotal scan results from Wazuh alerts."""
    result = {
        "status": "unknown",
        "alerts": [],
        "alert_count": 0,
        "error": None,
    }

    # Check for VirusTotal alerts in Wazuh
    alerts_file = Path("/var/ossec/logs/alerts/alerts.json")
    try:
        if not alerts_file.exists():
            result["error"] = "Alerts file not found"
            return result

        tail_result = subprocess.run(
            ["tail", "-n", "1000", str(alerts_file)],
            capture_output=True, text=True, timeout=30
        )

        for line in tail_result.stdout.strip().split('\n'):
            if not line:
                continue
            try:
                alert = json.loads(line)
                rule_desc = alert.get("rule", {}).get("description", "").lower()
                # VirusTotal integration alerts
                if "virustotal" in rule_desc or alert.get("rule", {}).get("id", "").startswith("87"):
                    result["alerts"].append({
                        "timestamp": alert.get("timestamp", ""),
                        "rule_id": alert.get("rule", {}).get("id", ""),
                        "description": alert.get("rule", {}).get("description", ""),
                        "file": alert.get("data", {}).get("virustotal", {}).get("source", {}).get("file", ""),
                        "positives": alert.get("data", {}).get("virustotal", {}).get("positives", 0),
                        "total": alert.get("data", {}).get("virustotal", {}).get("total", 0),
                        "permalink": alert.get("data", {}).get("virustotal", {}).get("permalink", ""),
                    })
            except json.JSONDecodeError:
                continue

        result["alerts"] = result["alerts"][-20:]  # Last 20
        result["alert_count"] = len(result["alerts"])
        result["status"] = "ok"

    except PermissionError:
        result["error"] = "Permission denied accessing Wazuh alerts (run as root or add user to wazuh group)"
    except Exception as e:
        result["error"] = f"Failed to read alerts: {e}"

    return result


def run_yara_scan(path: str = "/tmp", rules_file: str = None) -> Dict[str, Any]:
    """
    Run YARA scan on specified path.
    This should only be called after human approval.
    """
    result = {
        "status": "unknown",
        "path": path,
        "matches": [],
        "files_scanned": 0,
        "error": None,
    }

    # Find rules file
    if not rules_file:
        rules_dirs = [
            Path("/var/ossec/ruleset/yara/rules"),
            Path("/etc/yara/rules"),
        ]
        for rules_dir in rules_dirs:
            if rules_dir.exists():
                rules_files = list(rules_dir.glob("*.yar")) + list(rules_dir.glob("*.yara"))
                if rules_files:
                    rules_file = str(rules_files[0])
                    break

    if not rules_file:
        result["error"] = "No YARA rules file found"
        result["status"] = "error"
        return result

    scan_path = Path(path)
    if not scan_path.exists():
        result["error"] = f"Path does not exist: {path}"
        result["status"] = "error"
        return result

    try:
        # Run YARA scan
        cmd = ["yara", "-r", rules_file, str(scan_path)]
        scan_result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=300  # 5 minute timeout
        )

        # Parse results
        for line in scan_result.stdout.strip().split('\n'):
            if line:
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    result["matches"].append({
                        "rule": parts[0],
                        "file": parts[1],
                    })

        result["status"] = "clean" if not result["matches"] else "detected"

    except subprocess.TimeoutExpired:
        result["error"] = "Scan timed out after 5 minutes"
        result["status"] = "timeout"
    except Exception as e:
        result["error"] = f"Scan failed: {e}"
        result["status"] = "error"

    return result


def get_security_services_status() -> Dict[str, Any]:
    """Get status of all security services."""
    services = {
        "wazuh-manager": {"name": "Wazuh Manager (SIEM)", "status": "unknown", "enabled": False},
        "wazuh-indexer": {"name": "Wazuh Indexer", "status": "unknown", "enabled": False},
        "wazuh-dashboard": {"name": "Wazuh Dashboard", "status": "unknown", "enabled": False},
        "suricata": {"name": "Suricata IDS", "status": "unknown", "enabled": False},
        "graylog-server": {"name": "Graylog Server", "status": "unknown", "enabled": False},
        "mongod": {"name": "MongoDB (Graylog)", "status": "unknown", "enabled": False},
        "elasticsearch": {"name": "Elasticsearch", "status": "unknown", "enabled": False},
        "prometheus": {"name": "Prometheus", "status": "unknown", "enabled": False},
        "grafana-server": {"name": "Grafana", "status": "unknown", "enabled": False},
    }

    for svc_name, svc_info in services.items():
        try:
            # Check if active
            active_check = subprocess.run(
                ["systemctl", "is-active", svc_name],
                capture_output=True, text=True, timeout=10
            )
            svc_info["status"] = active_check.stdout.strip()

            # Check if enabled
            enabled_check = subprocess.run(
                ["systemctl", "is-enabled", svc_name],
                capture_output=True, text=True, timeout=10
            )
            svc_info["enabled"] = enabled_check.stdout.strip() == "enabled"

        except Exception as e:
            svc_info["status"] = f"error: {e}"

    return {
        "services": services,
        "timestamp": datetime.now().isoformat(),
    }


def run_clamav_scan(path: str = "/tmp", options: str = "") -> Dict[str, Any]:
    """
    Run ClamAV scan on specified path.
    This should only be called after human approval.
    """
    result = {
        "status": "unknown",
        "path": path,
        "infected_files": 0,
        "scanned_files": 0,
        "output": "",
        "error": None,
    }

    # Validate path exists
    scan_path = Path(path)
    if not scan_path.exists():
        result["error"] = f"Path does not exist: {path}"
        result["status"] = "error"
        return result

    try:
        # Run clamscan with recursive flag
        cmd = ["clamscan", "-r", "--infected", "--suppress-ok-results", str(scan_path)]
        scan_result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=300  # 5 minute timeout
        )

        result["output"] = scan_result.stdout

        # Parse results
        for line in scan_result.stdout.split('\n'):
            if "Infected files:" in line:
                try:
                    result["infected_files"] = int(line.split(':')[1].strip())
                except:
                    pass
            elif "Scanned files:" in line:
                try:
                    result["scanned_files"] = int(line.split(':')[1].strip())
                except:
                    pass

        result["status"] = "clean" if result["infected_files"] == 0 else "infected"

    except subprocess.TimeoutExpired:
        result["error"] = "Scan timed out after 5 minutes"
        result["status"] = "timeout"
    except Exception as e:
        result["error"] = f"Scan failed: {e}"
        result["status"] = "error"

    return result


def update_clamav_signatures() -> Dict[str, Any]:
    """
    Update ClamAV virus definitions.
    This should only be called after human approval.
    """
    result = {
        "status": "unknown",
        "output": "",
        "error": None,
    }

    try:
        update_result = subprocess.run(
            ["freshclam"],
            capture_output=True, text=True, timeout=120  # 2 minute timeout
        )

        result["output"] = update_result.stdout + update_result.stderr
        result["status"] = "success" if update_result.returncode == 0 else "failed"

    except subprocess.TimeoutExpired:
        result["error"] = "Update timed out"
        result["status"] = "timeout"
    except Exception as e:
        result["error"] = f"Update failed: {e}"
        result["status"] = "error"

    return result


def get_graylog_status() -> Dict[str, Any]:
    """Get Graylog log management status."""
    result = {
        "status": "unknown",
        "service_running": False,
        "cluster_info": None,
        "recent_logs": [],
        "error": None,
    }

    # Check if Graylog is running
    try:
        svc_check = subprocess.run(
            ["systemctl", "is-active", "graylog-server"],
            capture_output=True, text=True, timeout=10
        )
        result["service_running"] = svc_check.stdout.strip() == "active"
    except Exception as e:
        result["error"] = f"Failed to check service: {e}"

    # Try to get cluster info from API
    if result["service_running"]:
        try:
            api_result = subprocess.run(
                ["curl", "-s", "http://localhost:9000/api/system/cluster/nodes"],
                capture_output=True, text=True, timeout=10
            )
            if api_result.returncode == 0 and api_result.stdout:
                try:
                    result["cluster_info"] = json.loads(api_result.stdout)
                except json.JSONDecodeError:
                    result["cluster_info"] = api_result.stdout[:500]
        except Exception:
            pass

    # Read recent server logs
    log_file = Path("/var/log/graylog-server/server.log")
    if log_file.exists():
        try:
            tail_result = subprocess.run(
                ["tail", "-n", "50", str(log_file)],
                capture_output=True, text=True, timeout=10
            )
            result["recent_logs"] = tail_result.stdout.strip().split('\n')[-20:]
            result["status"] = "ok"
        except Exception as e:
            if not result["error"]:
                result["error"] = f"Failed to read logs: {e}"
    else:
        if not result["error"]:
            result["error"] = "Log file not found"

    return result


def get_usb_devices() -> Dict[str, Any]:
    """Get current USB device status from USBGuard."""
    result = {
        "status": "unknown",
        "usbguard_running": False,
        "devices": [],
        "blocked_storage": [],
        "allowed_storage": [],
        "error": None,
    }

    # Check if USBGuard is running
    try:
        svc_check = subprocess.run(
            ["systemctl", "is-active", "usbguard"],
            capture_output=True, text=True, timeout=10
        )
        result["usbguard_running"] = svc_check.stdout.strip() == "active"
    except Exception as e:
        result["error"] = f"Failed to check USBGuard: {e}"
        return result

    if not result["usbguard_running"]:
        result["error"] = "USBGuard is not running"
        return result

    # List all USB devices
    try:
        list_result = subprocess.run(
            ["usbguard", "list-devices"],
            capture_output=True, text=True, timeout=10
        )

        for line in list_result.stdout.strip().split('\n'):
            if not line:
                continue

            # Parse device line: "ID: status id XXXX:XXXX ..."
            parts = line.split()
            if len(parts) < 4:
                continue

            device_id = parts[0].rstrip(':')
            status = parts[1]  # allow or block

            # Extract device info
            device_info = {
                "id": device_id,
                "status": status,
                "raw": line,
            }

            # Extract name if present
            if 'name "' in line:
                start = line.find('name "') + 6
                end = line.find('"', start)
                device_info["name"] = line[start:end]

            # Extract USB ID (vendor:product)
            if 'id ' in line:
                for part in parts:
                    if ':' in part and len(part) == 9:  # XXXX:XXXX format
                        device_info["usb_id"] = part
                        break

            # Check if it's a mass storage device (interface class 08)
            if 'with-interface' in line and '08:' in line:
                device_info["is_storage"] = True
                if status == "block":
                    result["blocked_storage"].append(device_info)
                else:
                    result["allowed_storage"].append(device_info)
            else:
                device_info["is_storage"] = False

            result["devices"].append(device_info)

        result["status"] = "ok"

    except Exception as e:
        result["error"] = f"Failed to list devices: {e}"

    return result


def allow_usb_device(device_id: str) -> Dict[str, Any]:
    """
    Allow a USB device by its USBGuard device ID.
    Requires approval before execution.
    """
    result = {
        "success": False,
        "device_id": device_id,
        "output": "",
        "error": None,
    }

    try:
        allow_result = subprocess.run(
            ["usbguard", "allow-device", str(device_id)],
            capture_output=True, text=True, timeout=10
        )

        if allow_result.returncode == 0:
            result["success"] = True
            result["output"] = f"Device {device_id} allowed"
        else:
            result["error"] = allow_result.stderr.strip() or "Unknown error"

    except Exception as e:
        result["error"] = f"Failed to allow device: {e}"

    return result


def block_usb_device(device_id: str) -> Dict[str, Any]:
    """
    Block a USB device by its USBGuard device ID.
    """
    result = {
        "success": False,
        "device_id": device_id,
        "output": "",
        "error": None,
    }

    try:
        block_result = subprocess.run(
            ["usbguard", "block-device", str(device_id)],
            capture_output=True, text=True, timeout=10
        )

        if block_result.returncode == 0:
            result["success"] = True
            result["output"] = f"Device {device_id} blocked"
        else:
            result["error"] = block_result.stderr.strip() or "Unknown error"

    except Exception as e:
        result["error"] = f"Failed to block device: {e}"

    return result


def block_all_usb_storage() -> Dict[str, Any]:
    """
    Block all currently allowed USB storage devices.
    """
    result = {
        "success": True,
        "blocked_count": 0,
        "errors": [],
    }

    devices = get_usb_devices()
    if devices.get("error"):
        result["success"] = False
        result["errors"].append(devices["error"])
        return result

    for device in devices.get("allowed_storage", []):
        block_result = block_usb_device(device["id"])
        if block_result["success"]:
            result["blocked_count"] += 1
        else:
            result["errors"].append(f"Device {device['id']}: {block_result.get('error')}")

    if result["errors"]:
        result["success"] = False

    return result


def get_prometheus_status() -> Dict[str, Any]:
    """Get Prometheus monitoring status."""
    result = {
        "status": "unknown",
        "service_running": False,
        "targets": [],
        "alerts": [],
        "config": None,
        "error": None,
    }

    # Check if Prometheus is running
    try:
        svc_check = subprocess.run(
            ["systemctl", "is-active", "prometheus"],
            capture_output=True, text=True, timeout=10
        )
        result["service_running"] = svc_check.stdout.strip() == "active"
    except Exception as e:
        result["error"] = f"Failed to check service: {e}"

    # Get targets from Prometheus API
    if result["service_running"]:
        try:
            targets_result = subprocess.run(
                ["curl", "-s", "http://localhost:9090/api/v1/targets"],
                capture_output=True, text=True, timeout=10
            )
            if targets_result.returncode == 0 and targets_result.stdout:
                try:
                    data = json.loads(targets_result.stdout)
                    if data.get("status") == "success":
                        active_targets = data.get("data", {}).get("activeTargets", [])
                        result["targets"] = [
                            {
                                "job": t.get("labels", {}).get("job", ""),
                                "instance": t.get("labels", {}).get("instance", ""),
                                "health": t.get("health", "unknown"),
                                "lastScrape": t.get("lastScrape", ""),
                            }
                            for t in active_targets[:20]  # Limit to 20 targets
                        ]
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

        # Get alerts from Prometheus API
        try:
            alerts_result = subprocess.run(
                ["curl", "-s", "http://localhost:9090/api/v1/alerts"],
                capture_output=True, text=True, timeout=10
            )
            if alerts_result.returncode == 0 and alerts_result.stdout:
                try:
                    data = json.loads(alerts_result.stdout)
                    if data.get("status") == "success":
                        alerts = data.get("data", {}).get("alerts", [])
                        result["alerts"] = [
                            {
                                "alertname": a.get("labels", {}).get("alertname", ""),
                                "state": a.get("state", ""),
                                "severity": a.get("labels", {}).get("severity", ""),
                                "summary": a.get("annotations", {}).get("summary", ""),
                            }
                            for a in alerts[:20]  # Limit to 20 alerts
                        ]
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

        result["status"] = "ok"

    return result
