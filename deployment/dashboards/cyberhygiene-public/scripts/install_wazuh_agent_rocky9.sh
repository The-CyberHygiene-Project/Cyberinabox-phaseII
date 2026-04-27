#!/bin/bash
#
# Wazuh Agent Installation Script for Rocky Linux 9
# CyberHygiene Project - NIST 800-171 Compliance
#
# Run this script on each Rocky Linux workstation to install and configure
# the Wazuh agent for Security Configuration Assessment (SCA) and
# OpenSCAP CUI profile compliance scanning.
#
# Usage: sudo ./install_wazuh_agent_rocky9.sh
#
# After installation:
#   - Wazuh SCA scans run automatically every 12 hours
#   - OpenSCAP CUI profile scans run every 12 hours
#   - Results appear in the Wazuh Dashboard
#

set -e

# Configuration
WAZUH_MANAGER="dc1.cyberinabox.net"
WAZUH_MANAGER_IP="192.168.1.10"
WAZUH_VERSION="4.9.2"
AGENT_NAME=$(hostname -s)

echo "=============================================="
echo "Wazuh Agent Installation - Rocky Linux 9"
echo "CyberHygiene Project"
echo "=============================================="
echo ""
echo "Manager: ${WAZUH_MANAGER}"
echo "Agent Name: ${AGENT_NAME}"
echo "Wazuh Version: ${WAZUH_VERSION}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root (use sudo)"
   exit 1
fi

# Check if agent is already installed
if rpm -q wazuh-agent &>/dev/null; then
    echo "Wazuh agent is already installed."
    systemctl status wazuh-agent --no-pager || true
    echo ""
    read -p "Do you want to reinstall? (y/N): " reinstall
    if [[ ! "$reinstall" =~ ^[Yy]$ ]]; then
        echo "Exiting without changes."
        exit 0
    fi
    echo "Stopping and removing existing agent..."
    systemctl stop wazuh-agent || true
    dnf remove -y wazuh-agent
fi

echo ""
echo "Step 1: Installing OpenSCAP and SCAP Security Guide..."
dnf install -y openscap-scanner scap-security-guide 2>/dev/null || yum install -y openscap-scanner scap-security-guide

# Verify SSG content is available
if [[ ! -f "/usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml" ]]; then
    echo "WARNING: SCAP Security Guide content not found. OpenSCAP scans may not work."
fi

echo ""
echo "Step 2: Setting up OpenSCAP CUI profile scan..."

# Create results directory
mkdir -p /var/log/openscap

# Create the OpenSCAP CUI scan script
cat > /usr/local/bin/openscap_cui_scan.sh << 'SCANEOF'
#!/bin/bash
#
# OpenSCAP CUI Profile Scanner
# CyberHygiene Project - NIST 800-171 Compliance
#
# Runs OpenSCAP scan with the CUI profile and logs results for Wazuh ingestion
# Schedule: Run via systemd timer every 12 hours
#

set -e

# Configuration
PROFILE="xccdf_org.ssgproject.content_profile_cui"
DATASTREAM="/usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml"
RESULTS_DIR="/var/log/openscap"
HOSTNAME=$(hostname -s)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="${RESULTS_DIR}/cui_results_${HOSTNAME}_${TIMESTAMP}.xml"
REPORT_FILE="${RESULTS_DIR}/cui_report_${HOSTNAME}_${TIMESTAMP}.html"
LOG_FILE="/var/log/openscap/openscap_scan.log"

# Ensure results directory exists
mkdir -p "${RESULTS_DIR}"

# Log function - outputs in format Wazuh can parse
log_event() {
    local level="$1"
    local message="$2"
    echo "$(date '+%Y-%m-%d %H:%M:%S') openscap_cui_scan[$$]: ${level}: ${message}" >> "${LOG_FILE}"
}

log_event "INFO" "Starting OpenSCAP CUI profile scan on ${HOSTNAME}"

# Check if OpenSCAP and SSG are installed
if ! command -v oscap &> /dev/null; then
    log_event "ERROR" "OpenSCAP scanner not installed"
    exit 1
fi

if [[ ! -f "${DATASTREAM}" ]]; then
    log_event "ERROR" "SCAP Security Guide datastream not found: ${DATASTREAM}"
    exit 1
fi

# Run the scan
log_event "INFO" "Executing scan with profile: ${PROFILE}"

oscap xccdf eval \
    --profile "${PROFILE}" \
    --results "${RESULTS_FILE}" \
    --report "${REPORT_FILE}" \
    "${DATASTREAM}" 2>&1 | while read line; do
        # Log each result line for Wazuh to parse
        if [[ "$line" =~ ^Title ]]; then
            log_event "INFO" "CHECK: $line"
        elif [[ "$line" =~ ^Result ]]; then
            result=$(echo "$line" | awk '{print $2}')
            if [[ "$result" == "fail" ]]; then
                log_event "WARNING" "RESULT: $line"
            else
                log_event "INFO" "RESULT: $line"
            fi
        fi
    done

# Parse results for summary
if [[ -f "${RESULTS_FILE}" ]]; then
    PASS_COUNT=$(grep -c '<result>pass</result>' "${RESULTS_FILE}" 2>/dev/null | tr -d '\n' || echo 0)
    FAIL_COUNT=$(grep -c '<result>fail</result>' "${RESULTS_FILE}" 2>/dev/null | tr -d '\n' || echo 0)
    NOTAPPLICABLE=$(grep -c '<result>notapplicable</result>' "${RESULTS_FILE}" 2>/dev/null | tr -d '\n' || echo 0)
    # Ensure numeric values
    PASS_COUNT=${PASS_COUNT:-0}
    FAIL_COUNT=${FAIL_COUNT:-0}
    TOTAL=$((PASS_COUNT + FAIL_COUNT))

    if [[ $TOTAL -gt 0 ]]; then
        SCORE=$((PASS_COUNT * 100 / TOTAL))
    else
        SCORE=0
    fi

    # Log summary in JSON format for Wazuh
    log_event "INFO" "SCAN_COMPLETE: {\"hostname\":\"${HOSTNAME}\",\"profile\":\"CUI\",\"pass\":${PASS_COUNT},\"fail\":${FAIL_COUNT},\"notapplicable\":${NOTAPPLICABLE},\"score\":${SCORE},\"report\":\"${REPORT_FILE}\"}"

    # Also log to syslog for Wazuh agent to pick up
    logger -t openscap_cui "SCAN_COMPLETE: hostname=${HOSTNAME} profile=CUI pass=${PASS_COUNT} fail=${FAIL_COUNT} score=${SCORE}%"

    echo ""
    echo "======================================"
    echo "OpenSCAP CUI Profile Scan Complete"
    echo "======================================"
    echo "Hostname: ${HOSTNAME}"
    echo "Profile:  NIST 800-171 CUI"
    echo "Passed:   ${PASS_COUNT}"
    echo "Failed:   ${FAIL_COUNT}"
    echo "Score:    ${SCORE}%"
    echo ""
    echo "Results:  ${RESULTS_FILE}"
    echo "Report:   ${REPORT_FILE}"
    echo "======================================"
else
    log_event "ERROR" "Results file not created: ${RESULTS_FILE}"
    exit 1
fi

# Cleanup old results (keep last 30 days)
find "${RESULTS_DIR}" -name "cui_results_*.xml" -mtime +30 -delete 2>/dev/null || true
find "${RESULTS_DIR}" -name "cui_report_*.html" -mtime +30 -delete 2>/dev/null || true

log_event "INFO" "Scan completed successfully. Score: ${SCORE}%"
SCANEOF

chmod +x /usr/local/bin/openscap_cui_scan.sh

echo ""
echo "Step 3: Creating systemd timer for scheduled scans..."

# Create systemd service for OpenSCAP scan
cat > /etc/systemd/system/openscap-cui-scan.service << 'SVCEOF'
[Unit]
Description=OpenSCAP CUI Compliance Scan
Documentation=man:oscap(8)
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/openscap_cui_scan.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

# Create systemd timer
cat > /etc/systemd/system/openscap-cui-scan.timer << 'TMREOF'
[Unit]
Description=Run OpenSCAP CUI scan every 12 hours
Documentation=man:oscap(8)

[Timer]
OnBootSec=15min
OnUnitActiveSec=12h
Persistent=true

[Install]
WantedBy=timers.target
TMREOF

# Enable and start the timer
systemctl daemon-reload
systemctl enable openscap-cui-scan.timer
systemctl start openscap-cui-scan.timer

echo ""
echo "Step 4: Adding Wazuh repository..."
rpm --import https://packages.wazuh.com/key/GPG-KEY-WAZUH

cat > /etc/yum.repos.d/wazuh.repo << 'EOF'
[wazuh]
gpgcheck=1
gpgkey=https://packages.wazuh.com/key/GPG-KEY-WAZUH
enabled=1
name=EL-$releasever - Wazuh
baseurl=https://packages.wazuh.com/4.x/yum/
protect=1
EOF

echo ""
echo "Step 5: Installing Wazuh agent..."
WAZUH_MANAGER="${WAZUH_MANAGER}" WAZUH_AGENT_NAME="${AGENT_NAME}" dnf install -y wazuh-agent

echo ""
echo "Step 6: Configuring agent connection..."
# Backup original config
cp /var/ossec/etc/ossec.conf /var/ossec/etc/ossec.conf.bak

# Update manager address in ossec.conf
sed -i "s/<address>.*<\/address>/<address>${WAZUH_MANAGER}<\/address>/" /var/ossec/etc/ossec.conf

# Ensure SCA is enabled
if ! grep -q "<sca>" /var/ossec/etc/ossec.conf; then
    # Add SCA configuration before </ossec_config>
    sed -i '/<\/ossec_config>/i \
  <!-- Security Configuration Assessment -->\
  <sca>\
    <enabled>yes</enabled>\
    <scan_on_start>yes</scan_on_start>\
    <interval>12h</interval>\
    <skip_nfs>yes</skip_nfs>\
  </sca>' /var/ossec/etc/ossec.conf
fi

# Add OpenSCAP log file monitoring for Wazuh
if ! grep -q "openscap_scan.log" /var/ossec/etc/ossec.conf; then
    sed -i '/<\/ossec_config>/i \
  <!-- OpenSCAP CUI Compliance Log -->\
  <localfile>\
    <log_format>syslog</log_format>\
    <location>/var/log/openscap/openscap_scan.log</location>\
  </localfile>' /var/ossec/etc/ossec.conf
fi

echo ""
echo "Step 7: Configuring firewall..."
# Allow Wazuh agent communication
firewall-cmd --permanent --add-port=1514/tcp 2>/dev/null || true
firewall-cmd --permanent --add-port=1515/tcp 2>/dev/null || true
firewall-cmd --reload 2>/dev/null || true

echo ""
echo "Step 8: Starting and enabling Wazuh agent..."
systemctl daemon-reload
systemctl enable wazuh-agent
systemctl start wazuh-agent

echo ""
echo "Step 9: Verifying agent status..."
sleep 5
systemctl status wazuh-agent --no-pager

echo ""
echo "Step 10: Checking agent connection..."
/var/ossec/bin/agent-auth -m ${WAZUH_MANAGER} 2>/dev/null || echo "Agent may need manual registration"

# Check if connected
sleep 3
if grep -q "Connected to the manager" /var/ossec/logs/ossec.log 2>/dev/null; then
    echo ""
    echo "SUCCESS: Agent connected to manager!"
else
    echo ""
    echo "NOTE: Agent installed. Check /var/ossec/logs/ossec.log for connection status."
fi

echo ""
echo "Step 11: Running initial OpenSCAP scan..."
echo "(This may take a few minutes...)"
/usr/local/bin/openscap_cui_scan.sh || echo "Initial scan completed (check results above)"

echo ""
echo "=============================================="
echo "Installation Complete!"
echo "=============================================="
echo ""
echo "Agent Name: ${AGENT_NAME}"
echo "Manager: ${WAZUH_MANAGER}"
echo ""
echo "Compliance scanning is configured:"
echo "  - Wazuh SCA: Runs on start + every 12 hours"
echo "  - OpenSCAP CUI: Runs on boot + every 12 hours"
echo ""
echo "OpenSCAP Results:"
echo "  - XML Results: /var/log/openscap/cui_results_*.xml"
echo "  - HTML Reports: /var/log/openscap/cui_report_*.html"
echo "  - Scan Log: /var/log/openscap/openscap_scan.log"
echo ""
echo "View results in Wazuh Dashboard:"
echo "  https://dc1.cyberinabox.net:5601"
echo "  Navigate to: Agents > ${AGENT_NAME} > Security Configuration Assessment"
echo ""
echo "Useful commands:"
echo "  Check Wazuh status:     systemctl status wazuh-agent"
echo "  View Wazuh logs:        tail -f /var/ossec/logs/ossec.log"
echo "  Check scan timer:       systemctl list-timers openscap-cui-scan.timer"
echo "  Run manual scan:        sudo /usr/local/bin/openscap_cui_scan.sh"
echo "  Restart Wazuh:          systemctl restart wazuh-agent"
echo ""
