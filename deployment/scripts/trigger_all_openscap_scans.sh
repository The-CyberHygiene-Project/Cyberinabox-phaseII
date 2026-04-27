#!/bin/bash
#
# Trigger OpenSCAP CUI Scans on All Workstations
# CyberHygiene Project - NIST 800-171 Compliance
#
# Runs OpenSCAP scans on all configured workstations via SSH
# Results are forwarded to Wazuh via each workstation's agent
#

set -e

WORKSTATIONS="labrat engineering accounting"
SCAN_SCRIPT="/usr/local/bin/openscap_cui_scan.sh"
SSH_USER="dshannon"
SSH_KEY="/home/dshannon/.ssh/id_ecdsa"
SSH_OPTS="-o ConnectTimeout=10 -o BatchMode=yes -o IdentitiesOnly=yes -i ${SSH_KEY}"

echo "========================================"
echo "Triggering OpenSCAP CUI Scans"
echo "========================================"
echo ""

# Also run local scan on dc1
echo "[dc1] Running local scan..."
if [[ -x "${SCAN_SCRIPT}" ]]; then
    ${SCAN_SCRIPT}
    echo "[dc1] Scan complete."
else
    echo "[dc1] WARNING: Scan script not found at ${SCAN_SCRIPT}"
fi
echo ""

# Trigger scans on workstations
for ws in ${WORKSTATIONS}; do
    echo "[${ws}] Triggering scan..."

    if ssh ${SSH_OPTS} ${SSH_USER}@${ws}.cyberinabox.net "sudo test -x ${SCAN_SCRIPT}" 2>/dev/null; then
        ssh ${SSH_OPTS} ${SSH_USER}@${ws}.cyberinabox.net "sudo ${SCAN_SCRIPT}" &
        echo "[${ws}] Scan started in background."
    else
        echo "[${ws}] WARNING: Cannot connect or scan script not found."
    fi
done

# Wait for all background jobs
echo ""
echo "Waiting for all scans to complete..."
wait

echo ""
echo "========================================"
echo "All scans triggered. Check Wazuh dashboard"
echo "for results or use 'CUI Compliance' tile."
echo "========================================"
