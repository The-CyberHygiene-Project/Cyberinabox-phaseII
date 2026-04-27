#!/bin/bash
# fix_macmini.sh
# Fixes DHCP networking broken by NIST 800-171 hardening
# Run with: sudo bash fix_macmini.sh

echo "============================================"
echo " Mac Mini Hardening Fix Script"
echo " $(date)"
echo "============================================"
echo ""

# ── STEP 1: Fix file permissions ──────────────────────────────────────────────
echo "[1/6] Removing write protection from firewall anchor file..."
sudo chflags noschg /etc/pf.anchors/800_171_cyberhygiene_pf_anchors
sudo chmod 644 /etc/pf.anchors/800_171_cyberhygiene_pf_anchors
echo "      Done."
echo ""

# ── STEP 2: Rewrite the firewall anchor with DHCP exception ───────────────────
echo "[2/6] Writing corrected firewall rules (adding DHCP exception)..."
sudo tee /etc/pf.anchors/800_171_cyberhygiene_pf_anchors > /dev/null << 'EOF'
# CyberHygiene mSCP 800-171 pf anchor
# Applied: 2026-03-30
# Purpose: Default deny inbound (satisfies os_firewall_default_deny_require)

# Allow loopback
pass quick on lo0 all

# Allow established/related (stateful)
pass out all keep state

# Allow SSH inbound (air-gapped admin access)
pass in proto tcp to any port 22 keep state

# Allow DHCP inbound (required for network connectivity)
pass in proto udp from any to any port 68 keep state

# Block inbound insecure/unused services
block drop in proto tcp to any port {548, 1900, 79, 20, 21, 80, 143, 993, 3689}

# Default deny all other inbound
block drop in all
EOF
echo "      Done."
echo ""

# ── STEP 3: Reload firewall ────────────────────────────────────────────────────
echo "[3/6] Reloading firewall..."
sudo pfctl -f /etc/pf.conf 2>&1 | grep -v "ALTQ"
echo "      Done."
echo ""

# ── STEP 4: Renew DHCP lease ──────────────────────────────────────────────────
echo "[4/6] Requesting new IP address from router..."
sudo ipconfig set en0 DHCP
sleep 5
echo "      Done."
echo ""

# ── STEP 5: Verify networking ─────────────────────────────────────────────────
echo "[5/6] Checking network status..."
IP=$(ipconfig getifaddr en0)
if [ -z "$IP" ]; then
    echo "      WARNING: No IP address assigned yet. Waiting a few more seconds..."
    sleep 5
    IP=$(ipconfig getifaddr en0)
fi

if [ -z "$IP" ]; then
    echo "      FAIL: Still no IP address. DHCP may need more time or there is another issue."
else
    echo "      IP Address: $IP"
    if [[ "$IP" == 169.254.* ]]; then
        echo "      FAIL: Still getting a 169.254.x.x address - DHCP not working yet."
    else
        echo "      SUCCESS: Valid IP address obtained!"
        # Test internet connectivity
        echo "      Testing internet connectivity..."
        if ping -c 2 -W 3 8.8.8.8 > /dev/null 2>&1; then
            echo "      SUCCESS: Internet is reachable!"
        else
            echo "      WARNING: IP looks good but internet ping failed (may be blocked by firewall - this can be normal)."
        fi
    fi
fi
echo ""

# ── STEP 6: Verify sudo ────────────────────────────────────────────────────────
echo "[6/6] Verifying sudo and pam.d/sudo config..."
cat /etc/pam.d/sudo
echo ""
SUDO_TEST=$(sudo -n whoami 2>/dev/null)
if [ "$SUDO_TEST" = "root" ]; then
    echo "      SUCCESS: sudo is working correctly."
else
    echo "      sudo requires password (this is normal and correct)."
fi
echo ""

# ── Final Report ───────────────────────────────────────────────────────────────
echo "============================================"
echo " Final Report"
echo "============================================"
echo " IP Address : $(ipconfig getifaddr en0 || echo 'None assigned')"
echo " Router     : $(netstat -rn | grep default | awk '{print $2}' | head -1 || echo 'None')"
echo " DNS        : $(cat /etc/resolv.conf 2>/dev/null | grep nameserver | head -1 || echo 'Unknown')"
echo " sudo PAM   : $(grep pam_deny /etc/pam.d/sudo | grep '^auth' || echo 'No auth deny found - looks good')"
echo "============================================"
echo " Script complete. $(date)"
echo "============================================"
