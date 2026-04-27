#!/bin/bash
# SysAdmin Agent Dashboard Startup Script
# NIST 800-171 / CMMC Compliant

cd /data/ai-workspace/sysadmin-agent

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Installing Streamlit..."
    pip3 install streamlit
fi

# Start the dashboard
echo "Starting SysAdmin Agent Dashboard..."
echo "URL: http://dc1.cyberinabox.net:8501"
echo "Press Ctrl+C to stop"

streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --theme.base dark \
    --theme.primaryColor "#667eea"
