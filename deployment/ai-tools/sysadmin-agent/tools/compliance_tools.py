"""
Compliance Scanning Tools for SysAdmin Agent Dashboard
OpenSCAP integration for NIST 800-171 compliance scanning
Now with Wazuh integration for centralized compliance monitoring
"""

import subprocess
import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import (
    OPENSCAP_PROFILE,
    OPENSCAP_PROFILE_NAME,
    OPENSCAP_DATASTREAM,
    OPENSCAP_REPORTS_DIR,
    WORKSTATIONS,
)


def get_wazuh_compliance_data() -> Dict[str, Any]:
    """
    Get compliance scan results from Wazuh for all agents.
    Queries the OpenSCAP logs forwarded by agents.
    """
    result = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "agents": {},
        "summary": {
            "total_agents": 0,
            "compliant": 0,
            "warning": 0,
            "non_compliant": 0,
        },
        "error": None,
    }

    # Check if Wazuh manager is running
    try:
        wazuh_check = subprocess.run(
            ["systemctl", "is-active", "wazuh-manager"],
            capture_output=True, text=True, timeout=5
        )
        if wazuh_check.stdout.strip() != "active":
            result["error"] = "Wazuh manager is not running"
            result["status"] = "error"
            return result
    except Exception as e:
        result["error"] = f"Cannot check Wazuh status: {e}"
        result["status"] = "error"
        return result

    # Get list of connected agents
    try:
        agent_list = subprocess.run(
            ["/var/ossec/bin/agent_control", "-l"],
            capture_output=True, text=True, timeout=30
        )

        # Parse agent list
        agents = []
        for line in agent_list.stdout.split('\n'):
            # Format: "ID: 001, Name: labrat, IP: 192.168.1.115, Active/Disconnected"
            match = re.search(r'ID:\s*(\d+),\s*Name:\s*(\S+),\s*IP:\s*(\S+),\s*(Active|Disconnected)', line)
            if match:
                agents.append({
                    "id": match.group(1),
                    "name": match.group(2),
                    "ip": match.group(3),
                    "status": match.group(4),
                })

        result["summary"]["total_agents"] = len(agents)

        # For each agent, get the latest OpenSCAP scan result
        for agent in agents:
            agent_data = {
                "name": agent["name"],
                "ip": agent["ip"],
                "connected": agent["status"] == "Active",
                "last_scan": None,
                "score": None,
                "pass_count": None,
                "fail_count": None,
                "status": "unknown",
            }

            # Try to get scan results from Wazuh alerts
            # Look for openscap_cui events in alerts.json
            scan_result = _get_agent_openscap_result(agent["name"])
            if scan_result:
                agent_data.update(scan_result)

                # Categorize compliance status
                if agent_data["score"] is not None:
                    if agent_data["score"] >= 90:
                        agent_data["status"] = "compliant"
                        result["summary"]["compliant"] += 1
                    elif agent_data["score"] >= 70:
                        agent_data["status"] = "warning"
                        result["summary"]["warning"] += 1
                    else:
                        agent_data["status"] = "non_compliant"
                        result["summary"]["non_compliant"] += 1

            result["agents"][agent["name"]] = agent_data

    except subprocess.TimeoutExpired:
        result["error"] = "Timeout getting agent list"
    except Exception as e:
        result["error"] = f"Error getting agent data: {e}"

    return result


def _get_agent_openscap_result(agent_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the latest OpenSCAP scan result for a specific agent from Wazuh alerts.
    """
    try:
        # Search alerts.json for openscap_cui SCAN_COMPLETE events
        alerts_file = "/var/ossec/logs/alerts/alerts.json"
        if not os.path.exists(alerts_file):
            return None

        # Read last portion of alerts file (last 10MB to avoid memory issues)
        with open(alerts_file, 'rb') as f:
            f.seek(0, 2)  # Go to end
            file_size = f.tell()
            read_size = min(file_size, 10 * 1024 * 1024)  # Max 10MB
            f.seek(max(0, file_size - read_size))
            content = f.read().decode('utf-8', errors='ignore')

        # Parse each JSON line and find matching events
        latest_scan = None
        latest_timestamp = None
        agent_name_lower = agent_name.lower()

        for line in content.split('\n'):
            if not line.strip():
                continue
            try:
                alert = json.loads(line)
                full_log = alert.get('full_log', '')

                # Skip if not a real OpenSCAP SCAN_COMPLETE event
                # Must have both the openscap marker and SCAN_COMPLETE pattern
                decoder_name = alert.get('decoder', {}).get('name', '')
                if decoder_name != 'openscap_cui':
                    # Fallback: check for openscap pattern in full_log
                    if 'openscap_cui' not in full_log or 'SCAN_COMPLETE:' not in full_log:
                        continue

                # Match by agent name or data hostname
                alert_agent_name = alert.get('agent', {}).get('name', '').lower()
                data_hostname = alert.get('data', {}).get('hostname', '').lower()

                # Check if this alert matches our agent
                if (agent_name_lower in alert_agent_name or
                    alert_agent_name in agent_name_lower or
                    agent_name_lower in data_hostname or
                    data_hostname in agent_name_lower or
                    agent_name_lower in full_log.lower()):

                    timestamp_str = alert.get('timestamp', '')
                    if timestamp_str:
                        try:
                            # Fix timezone format for Python 3.9 (add colon: -0700 -> -07:00)
                            ts_fixed = timestamp_str.replace('Z', '+00:00')
                            # Handle offsets like -0700 -> -07:00
                            if len(ts_fixed) >= 5 and ts_fixed[-5] in '+-' and ':' not in ts_fixed[-5:]:
                                ts_fixed = ts_fixed[:-2] + ':' + ts_fixed[-2:]
                            timestamp = datetime.fromisoformat(ts_fixed)
                            if latest_timestamp is None or timestamp > latest_timestamp:
                                latest_timestamp = timestamp
                                # Use pre-parsed data from Wazuh if available
                                data = alert.get('data', {})
                                if data.get('score') is not None:
                                    latest_scan = {
                                        "last_scan": timestamp_str[:19],
                                        "score": int(str(data.get('score', 0))),
                                        "pass_count": int(str(data.get('pass_count', 0))),
                                        "fail_count": int(str(data.get('fail_count', 0))),
                                    }
                                else:
                                    # Fallback to parsing full_log
                                    latest_scan = _parse_scan_result(full_log, timestamp_str)
                        except Exception:
                            pass
            except json.JSONDecodeError:
                continue

        return latest_scan

    except Exception as e:
        return None


def _parse_scan_result(log_message: str, timestamp: str) -> Dict[str, Any]:
    """Parse OpenSCAP scan result from log message."""
    result = {
        "last_scan": timestamp[:19] if timestamp else None,
        "score": None,
        "pass_count": None,
        "fail_count": None,
    }

    # Try to parse the key-value format: hostname=X profile=Y pass=N fail=M score=P%
    match = re.search(r'pass=(\d+)\s+fail=(\d+)\s+score=(\d+)%', log_message)
    if match:
        result["pass_count"] = int(match.group(1))
        result["fail_count"] = int(match.group(2))
        result["score"] = int(match.group(3))
    else:
        # Try JSON format
        json_match = re.search(r'\{[^}]+\}', log_message)
        if json_match:
            try:
                data = json.loads(json_match.group())
                result["score"] = data.get("score")
                result["pass_count"] = data.get("pass")
                result["fail_count"] = data.get("fail")
            except:
                pass

    return result


def get_wazuh_sca_results() -> Dict[str, Any]:
    """
    Get Wazuh SCA (Security Configuration Assessment) results for all agents.
    This provides CIS benchmark compliance data.
    """
    result = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "agents": {},
        "error": None,
    }

    try:
        # Get SCA results from Wazuh API or local database
        # For now, we'll read from the SCA database files
        sca_dir = Path("/var/ossec/queue/db")

        if not sca_dir.exists():
            result["error"] = "SCA database directory not found"
            return result

        # List agent databases
        for db_file in sca_dir.glob("*.db"):
            agent_id = db_file.stem
            if agent_id == "global":
                continue

            try:
                # Query the SQLite database for SCA results
                import sqlite3
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()

                # Get agent name from global.db
                agent_name = f"Agent-{agent_id}"
                try:
                    global_conn = sqlite3.connect("/var/ossec/queue/db/global.db")
                    global_cursor = global_conn.cursor()
                    global_cursor.execute("SELECT name FROM agent WHERE id = ?", (agent_id,))
                    row = global_cursor.fetchone()
                    if row:
                        agent_name = row[0]
                    global_conn.close()
                except:
                    pass

                # Get SCA scan summary
                cursor.execute("""
                    SELECT policy_id, pass, fail, invalid, total_checks, score,
                           end_scan, hash_file, name, description
                    FROM sca_scan_info
                    ORDER BY end_scan DESC
                    LIMIT 5
                """)

                scans = []
                for row in cursor.fetchall():
                    scans.append({
                        "policy_id": row[0],
                        "pass": row[1],
                        "fail": row[2],
                        "invalid": row[3],
                        "total_checks": row[4],
                        "score": row[5],
                        "end_scan": row[6],
                        "name": row[8],
                        "description": row[9],
                    })

                result["agents"][agent_name] = {
                    "id": agent_id,
                    "scans": scans,
                }

                conn.close()

            except Exception as e:
                result["agents"][f"Agent-{agent_id}"] = {"error": str(e)}

    except Exception as e:
        result["error"] = f"Error reading SCA data: {e}"

    return result


def get_local_openscap_results() -> Dict[str, Any]:
    """
    Get OpenSCAP scan results from the local log file on dc1.
    """
    result = {
        "last_scan": None,
        "score": None,
        "pass_count": None,
        "fail_count": None,
        "status": "unknown",
        "error": None,
    }

    log_file = "/var/log/openscap/openscap_scan.log"

    try:
        if not os.path.exists(log_file):
            result["error"] = "OpenSCAP log file not found"
            return result

        # Read the last portion of the log file
        with open(log_file, 'r') as f:
            lines = f.readlines()

        # Find the most recent SCAN_COMPLETE line
        for line in reversed(lines):
            if 'SCAN_COMPLETE' in line:
                parsed = _parse_scan_result(line, None)
                result.update(parsed)

                # Extract timestamp from log line
                timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    result["last_scan"] = timestamp_match.group(1)

                # Set status
                if result["score"] is not None:
                    if result["score"] >= 90:
                        result["status"] = "compliant"
                    elif result["score"] >= 70:
                        result["status"] = "warning"
                    else:
                        result["status"] = "non_compliant"
                break

    except Exception as e:
        result["error"] = f"Error reading OpenSCAP log: {e}"

    return result


def get_compliance_status() -> Dict[str, Any]:
    """Get overall compliance scanning status and recent reports."""
    result = {
        "status": "ok",
        "oscap_installed": False,
        "oscap_version": None,
        "reports_dir": OPENSCAP_REPORTS_DIR,
        "wazuh_data": None,
        "local_scan": None,
        "workstations": {},
        "recent_reports": [],
        "error": None,
    }

    # Check if OpenSCAP is installed
    try:
        version_check = subprocess.run(
            ["oscap", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if version_check.returncode == 0:
            result["oscap_installed"] = True
            # Extract version from first line
            first_line = version_check.stdout.split('\n')[0]
            result["oscap_version"] = first_line.replace("OpenSCAP command line tool (oscap) ", "")
    except Exception as e:
        result["error"] = f"OpenSCAP not found: {e}"

    # Get Wazuh compliance data
    result["wazuh_data"] = get_wazuh_compliance_data()

    # Get local OpenSCAP results for dc1
    result["local_scan"] = get_local_openscap_results()

    # Get workstation status (combining Wazuh data with config)
    for ws_id, ws_info in WORKSTATIONS.items():
        ws_status = {
            "display_name": ws_info["display_name"],
            "hostname": ws_info["hostname"],
            "ip": ws_info["ip"],
            "last_scan": None,
            "score": None,
            "status": "unknown",
            "connected": False,
            "last_report": None,
        }

        # Try to get data from Wazuh
        wazuh_agents = result["wazuh_data"].get("agents", {})
        for agent_name, agent_data in wazuh_agents.items():
            if (ws_info["hostname"].split('.')[0].lower() in agent_name.lower() or
                ws_id.lower() in agent_name.lower()):
                ws_status["last_scan"] = agent_data.get("last_scan")
                ws_status["score"] = agent_data.get("score")
                ws_status["status"] = agent_data.get("status", "unknown")
                ws_status["connected"] = agent_data.get("connected", False)
                ws_status["pass_count"] = agent_data.get("pass_count")
                ws_status["fail_count"] = agent_data.get("fail_count")
                break

        # Check for existing HTML reports
        report_pattern = f"{ws_id}_*.html"
        reports_path = Path(OPENSCAP_REPORTS_DIR)
        if reports_path.exists():
            reports = sorted(reports_path.glob(report_pattern), reverse=True)
            if reports:
                latest = reports[0]
                ws_status["last_report"] = latest.name
                if not ws_status["last_scan"]:
                    ws_status["last_scan"] = datetime.fromtimestamp(
                        latest.stat().st_mtime
                    ).strftime("%Y-%m-%d %H:%M")

        result["workstations"][ws_id] = ws_status

    # Get recent reports (all workstations)
    reports_path = Path(OPENSCAP_REPORTS_DIR)
    if reports_path.exists():
        all_reports = sorted(reports_path.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True)
        for report in all_reports[:10]:
            result["recent_reports"].append({
                "filename": report.name,
                "date": datetime.fromtimestamp(report.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "size": f"{report.stat().st_size / 1024:.1f} KB",
                "url": f"https://cyberinabox.net/compliance-reports/{report.name}",
            })

    return result


def check_workstation_reachable(workstation_id: str) -> Dict[str, Any]:
    """Check if a workstation is reachable via SSH."""
    result = {
        "reachable": False,
        "workstation": workstation_id,
        "error": None,
    }

    if workstation_id not in WORKSTATIONS:
        result["error"] = f"Unknown workstation: {workstation_id}"
        return result

    ws = WORKSTATIONS[workstation_id]

    # Try to connect via SSH with a short timeout
    try:
        ssh_check = subprocess.run(
            [
                "ssh", "-o", "ConnectTimeout=5",
                "-o", "StrictHostKeyChecking=accept-new",
                "-o", "BatchMode=yes",
                f"{ws['ssh_user']}@{ws['ip']}",
                "echo ok"
            ],
            capture_output=True, text=True, timeout=15
        )

        if ssh_check.returncode == 0 and "ok" in ssh_check.stdout:
            result["reachable"] = True
        else:
            result["error"] = ssh_check.stderr.strip() or "SSH connection failed"

    except subprocess.TimeoutExpired:
        result["error"] = "SSH connection timed out"
    except Exception as e:
        result["error"] = f"SSH check failed: {e}"

    return result


def run_compliance_scan(workstation_id: str) -> Dict[str, Any]:
    """
    Run OpenSCAP compliance scan on a workstation.
    This should only be called after human approval.
    Returns scan results and report path.
    """
    result = {
        "success": False,
        "workstation": workstation_id,
        "report_file": None,
        "report_url": None,
        "scan_output": "",
        "error": None,
    }

    if workstation_id not in WORKSTATIONS:
        result["error"] = f"Unknown workstation: {workstation_id}"
        return result

    ws = WORKSTATIONS[workstation_id]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"{workstation_id}_{timestamp}.html"
    report_path = Path(OPENSCAP_REPORTS_DIR) / report_filename

    # Ensure reports directory exists
    Path(OPENSCAP_REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    # Run oscap-ssh scan
    try:
        scan_cmd = [
            "oscap-ssh",
            f"{ws['ssh_user']}@{ws['ip']}",
            "22",
            "xccdf", "eval",
            "--profile", OPENSCAP_PROFILE,
            "--report", str(report_path),
            OPENSCAP_DATASTREAM
        ]

        scan_result = subprocess.run(
            scan_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for full scan
        )

        result["scan_output"] = scan_result.stdout + scan_result.stderr

        # oscap returns 0 for pass, 2 for fail (some checks failed), 1 for error
        if scan_result.returncode in [0, 2]:
            result["success"] = True
            result["report_file"] = report_filename
            result["report_url"] = f"https://cyberinabox.net/compliance-reports/{report_filename}"

            # Extract summary from output
            if "Rule results:" in result["scan_output"]:
                summary_start = result["scan_output"].find("Rule results:")
                result["summary"] = result["scan_output"][summary_start:summary_start+200]
        else:
            result["error"] = f"Scan failed with code {scan_result.returncode}"

    except subprocess.TimeoutExpired:
        result["error"] = "Scan timed out after 10 minutes"
    except Exception as e:
        result["error"] = f"Scan failed: {e}"

    return result


def run_local_compliance_scan() -> Dict[str, Any]:
    """
    Run OpenSCAP compliance scan on the local server (dc1).
    Returns scan results and report path.
    """
    result = {
        "success": False,
        "workstation": "dc1",
        "report_file": None,
        "report_url": None,
        "scan_output": "",
        "error": None,
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"dc1_{timestamp}.html"
    report_path = Path(OPENSCAP_REPORTS_DIR) / report_filename

    # Ensure reports directory exists
    Path(OPENSCAP_REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    try:
        scan_cmd = [
            "oscap", "xccdf", "eval",
            "--profile", OPENSCAP_PROFILE,
            "--report", str(report_path),
            OPENSCAP_DATASTREAM
        ]

        scan_result = subprocess.run(
            scan_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        result["scan_output"] = scan_result.stdout + scan_result.stderr

        if scan_result.returncode in [0, 2]:
            result["success"] = True
            result["report_file"] = report_filename
            result["report_url"] = f"https://cyberinabox.net/compliance-reports/{report_filename}"
        else:
            result["error"] = f"Scan failed with code {scan_result.returncode}"

    except subprocess.TimeoutExpired:
        result["error"] = "Scan timed out after 10 minutes"
    except Exception as e:
        result["error"] = f"Scan failed: {e}"

    return result


def get_report_list() -> List[Dict[str, Any]]:
    """Get list of all compliance reports."""
    reports = []
    reports_path = Path(OPENSCAP_REPORTS_DIR)

    if not reports_path.exists():
        return reports

    for report in sorted(reports_path.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
        # Parse workstation from filename
        parts = report.stem.split("_")
        workstation = parts[0] if parts else "unknown"

        reports.append({
            "filename": report.name,
            "workstation": workstation,
            "date": datetime.fromtimestamp(report.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            "size": f"{report.stat().st_size / 1024:.1f} KB",
            "url": f"https://cyberinabox.net/compliance-reports/{report.name}",
        })

    return reports


def trigger_remote_scan(workstation_id: str) -> Dict[str, Any]:
    """
    Trigger an OpenSCAP scan on a remote workstation via its Wazuh agent.
    This runs the scan script on the workstation itself.
    """
    result = {
        "success": False,
        "workstation": workstation_id,
        "message": "",
        "error": None,
    }

    if workstation_id not in WORKSTATIONS:
        result["error"] = f"Unknown workstation: {workstation_id}"
        return result

    ws = WORKSTATIONS[workstation_id]

    try:
        # SSH to workstation and trigger the scan script
        ssh_cmd = [
            "ssh", "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=accept-new",
            f"{ws['ssh_user']}@{ws['ip']}",
            "sudo /usr/local/bin/openscap_cui_scan.sh"
        ]

        scan_result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if scan_result.returncode == 0:
            result["success"] = True
            result["message"] = scan_result.stdout
        else:
            result["error"] = scan_result.stderr or "Scan failed"
            result["message"] = scan_result.stdout

    except subprocess.TimeoutExpired:
        result["error"] = "Scan timed out"
    except Exception as e:
        result["error"] = f"Error triggering scan: {e}"

    return result
