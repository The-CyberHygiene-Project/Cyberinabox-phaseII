#!/bin/bash
#
# OpenSCAP CUI Profile Scanner
# CyberHygiene Project - NIST 800-171 Compliance
#
# Runs OpenSCAP scan with the CUI profile and logs results for Wazuh ingestion
# Schedule: Run via cron every 12 hours
#
# Usage: sudo ./openscap_cui_scan.sh
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
