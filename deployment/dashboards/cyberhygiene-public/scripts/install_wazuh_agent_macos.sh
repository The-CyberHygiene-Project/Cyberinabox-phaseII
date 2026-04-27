#!/bin/bash
#
# Wazuh Agent Installation Script for macOS
# CyberHygiene Project - NIST 800-171 Compliance
#
# Run this script on the Mac Mini (ai.cyberinabox.net) to install and configure
# the Wazuh agent for Security Configuration Assessment (SCA).
#
# Usage: sudo ./install_wazuh_agent_macos.sh
#
# After installation, compliance scans will run automatically every 12 hours
# and results will appear in the Wazuh Dashboard.
#

set -e

# Configuration
WAZUH_MANAGER="dc1.cyberinabox.net"
WAZUH_MANAGER_IP="192.168.1.10"
WAZUH_VERSION="4.9.2"
AGENT_NAME=$(hostname -s)

echo "=============================================="
echo "Wazuh Agent Installation - macOS"
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

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    PKG_ARCH="arm64"
    echo "Detected: Apple Silicon (ARM64)"
else
    PKG_ARCH="intel64"
    echo "Detected: Intel x86_64"
fi

# Check if agent is already installed
if [[ -d "/Library/Ossec" ]]; then
    echo ""
    echo "Wazuh agent appears to be already installed."
    /Library/Ossec/bin/wazuh-control status 2>/dev/null || true
    echo ""
    read -p "Do you want to reinstall? (y/N): " reinstall
    if [[ ! "$reinstall" =~ ^[Yy]$ ]]; then
        echo "Exiting without changes."
        exit 0
    fi
    echo "Stopping existing agent..."
    /Library/Ossec/bin/wazuh-control stop 2>/dev/null || true
fi

echo ""
echo "Step 1: Downloading Wazuh agent package..."
PKG_URL="https://packages.wazuh.com/4.x/macos/wazuh-agent-${WAZUH_VERSION}-1.${PKG_ARCH}.pkg"
PKG_FILE="/tmp/wazuh-agent.pkg"

curl -L -o "${PKG_FILE}" "${PKG_URL}"

if [[ ! -f "${PKG_FILE}" ]]; then
    echo "ERROR: Failed to download package"
    exit 1
fi

echo ""
echo "Step 2: Installing Wazuh agent..."
installer -pkg "${PKG_FILE}" -target /

echo ""
echo "Step 3: Configuring agent connection..."
# Backup original config
cp /Library/Ossec/etc/ossec.conf /Library/Ossec/etc/ossec.conf.bak

# Update manager address
sed -i '' "s/<address>.*<\/address>/<address>${WAZUH_MANAGER}<\/address>/" /Library/Ossec/etc/ossec.conf

# Ensure SCA is enabled with macOS policy
cat > /Library/Ossec/etc/shared/agent.conf << 'AGENTCONF'
<agent_config os="Darwin">
  <!-- Security Configuration Assessment for macOS -->
  <sca>
    <enabled>yes</enabled>
    <scan_on_start>yes</scan_on_start>
    <interval>12h</interval>
    <skip_nfs>yes</skip_nfs>
  </sca>
</agent_config>
AGENTCONF

echo ""
echo "Step 4: Registering agent with manager..."
/Library/Ossec/bin/agent-auth -m ${WAZUH_MANAGER}

echo ""
echo "Step 5: Starting Wazuh agent..."
/Library/Ossec/bin/wazuh-control start

echo ""
echo "Step 6: Verifying agent status..."
sleep 5
/Library/Ossec/bin/wazuh-control status

echo ""
echo "Step 7: Enabling agent to start at boot..."
# Create LaunchDaemon if it doesn't exist
if [[ ! -f "/Library/LaunchDaemons/com.wazuh.agent.plist" ]]; then
    cat > /Library/LaunchDaemons/com.wazuh.agent.plist << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.wazuh.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Library/Ossec/bin/wazuh-control</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
PLIST
    launchctl load /Library/LaunchDaemons/com.wazuh.agent.plist
fi

# Check if connected
sleep 3
if grep -q "Connected" /Library/Ossec/logs/ossec.log 2>/dev/null; then
    echo ""
    echo "SUCCESS: Agent connected to manager!"
else
    echo ""
    echo "NOTE: Check /Library/Ossec/logs/ossec.log for connection status."
fi

# Cleanup
rm -f "${PKG_FILE}"

echo ""
echo "=============================================="
echo "Installation Complete!"
echo "=============================================="
echo ""
echo "Agent Name: ${AGENT_NAME}"
echo "Manager: ${WAZUH_MANAGER}"
echo ""
echo "SCA (Security Configuration Assessment) is enabled."
echo "Compliance scans will run:"
echo "  - Immediately on agent start"
echo "  - Every 12 hours thereafter"
echo ""
echo "macOS CIS Benchmark policies are available for:"
echo "  - macOS 10.15 Catalina through macOS 15 Sequoia"
echo ""
echo "View results in Wazuh Dashboard:"
echo "  https://dc1.cyberinabox.net:5601"
echo "  Navigate to: Agents > ${AGENT_NAME} > Security Configuration Assessment"
echo ""
echo "Useful commands:"
echo "  Check status:  sudo /Library/Ossec/bin/wazuh-control status"
echo "  View logs:     sudo tail -f /Library/Ossec/logs/ossec.log"
echo "  Restart:       sudo /Library/Ossec/bin/wazuh-control restart"
echo ""
