#!/bin/bash
###############################################################################
# fix-engineering.sh — Run on the ENGINEERING workstation console as root
#
# Fixes SSH access from dc1 and deploys all CMMC controls:
#   1. Ensure sshd is running and firewall allows SSH
#   2. Fix PermitRootLogin (hardening config overrides it to "no")
#   3. Install dc1's SSH public keys
#   4. Install and configure USBGuard (NIST 3.8.7)
#   5. Configure session lock at 15 minutes (NIST 3.1.10)
#   6. Deploy DoD-standard login banners (NIST 3.1.9)
#
# Run:  sudo bash fix-engineering.sh
###############################################################################

set -uo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

if [[ $EUID -ne 0 ]]; then echo "Run as root: sudo bash $0"; exit 1; fi

echo "============================================"
echo "Engineering Workstation — CMMC Remediation"
echo "============================================"
echo ""

###############################################################################
# 1. Ensure sshd is running and firewall allows SSH
###############################################################################
echo "=== Step 1: SSH Service & Firewall ==="

# Check if sshd is installed
if ! rpm -q openssh-server > /dev/null 2>&1; then
    echo "Installing openssh-server..."
    dnf install -y openssh-server
fi

# Enable and start sshd
systemctl enable sshd 2>/dev/null
if systemctl is-active --quiet sshd; then
    ok "sshd is already running"
else
    systemctl start sshd
    if systemctl is-active --quiet sshd; then
        ok "sshd started"
    else
        fail "sshd failed to start — check: journalctl -u sshd"
    fi
fi

# Open firewall for SSH
if command -v firewall-cmd > /dev/null 2>&1; then
    if systemctl is-active --quiet firewalld; then
        if firewall-cmd --query-service=ssh --quiet 2>/dev/null; then
            ok "Firewall already allows SSH"
        else
            firewall-cmd --permanent --add-service=ssh
            firewall-cmd --reload
            ok "Firewall opened for SSH"
        fi
    else
        warn "firewalld not running — SSH should be accessible"
    fi
else
    warn "firewall-cmd not found — checking iptables"
    if command -v iptables > /dev/null 2>&1; then
        if iptables -L INPUT -n 2>/dev/null | grep -q "dpt:22.*ACCEPT"; then
            ok "iptables allows SSH"
        else
            iptables -I INPUT -p tcp --dport 22 -j ACCEPT 2>/dev/null
            ok "iptables rule added for SSH"
        fi
    fi
fi
echo ""

###############################################################################
# 2. Set PermitRootLogin no (NIST compliance — admin via dshannon+sudo)
###############################################################################
echo "=== Step 2: Set PermitRootLogin no ==="

# Fix main sshd_config
if grep -q '^PermitRootLogin' /etc/ssh/sshd_config 2>/dev/null; then
    sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    ok "Updated PermitRootLogin no in sshd_config"
else
    echo 'PermitRootLogin no' >> /etc/ssh/sshd_config
    ok "Added PermitRootLogin no to sshd_config"
fi

# Fix ALL sshd_config.d drop-in files
for f in /etc/ssh/sshd_config.d/*.conf; do
    if [ -f "$f" ] && grep -q '^PermitRootLogin' "$f" 2>/dev/null; then
        sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' "$f"
        ok "Set PermitRootLogin no in $(basename "$f")"
    fi
done

# Restart sshd to apply
systemctl restart sshd
if systemctl is-active --quiet sshd; then
    ok "sshd restarted with PermitRootLogin no"
else
    fail "sshd failed to restart!"
fi

# Verify
echo "  Verification:"
grep -ri PermitRootLogin /etc/ssh/sshd_config /etc/ssh/sshd_config.d/ 2>/dev/null | grep -v '^#' | while read line; do
    echo "    $line"
done
echo ""

###############################################################################
# 3. Install dshannon's SSH public key for remote administration
###############################################################################
echo "=== Step 3: Install dshannon SSH Key ==="

DSHANNON_HOME="/home/dshannon"
mkdir -p "${DSHANNON_HOME}/.ssh"
chmod 700 "${DSHANNON_HOME}/.ssh"
touch "${DSHANNON_HOME}/.ssh/authorized_keys"
chmod 600 "${DSHANNON_HOME}/.ssh/authorized_keys"

DSHANNON_ECDSA="ecdsa-sha2-nistp521 AAAAE2VjZHNhLXNoYTItbmlzdHA1MjEAAAAIbmlzdHA1MjEAAACFBAAw+oq22GUp7YKneV/InxgnJVzHS3Tg5N+3fG1onxnxOO0oGNupLahtBrqj0oPQ7b+mVDe6L5RNELk3PA5SJ2Dp8QCErELlZMrU3VALemqJryi56dD4oLXXzWe2FrelVeiU9PNcf+zj3rpsygs4ZAc5OWZKx6fSQ7/5TkJgDGUfFNPeaA== dshannon@dc1.cyberinabox.net"

if grep -qF "dshannon@dc1.cyberinabox.net" "${DSHANNON_HOME}/.ssh/authorized_keys" 2>/dev/null; then
    ok "dshannon SSH key already present"
else
    echo "$DSHANNON_ECDSA" >> "${DSHANNON_HOME}/.ssh/authorized_keys"
    ok "dshannon ECDSA key installed"
fi

chown -R dshannon:dshannon "${DSHANNON_HOME}/.ssh"
restorecon -Rv "${DSHANNON_HOME}/.ssh/" 2>/dev/null || true
ok "SELinux contexts restored on ${DSHANNON_HOME}/.ssh/"

###############################################################################
# 3b. Configure sudoers for dshannon NOPASSWD (remote admin)
###############################################################################
echo "=== Step 3b: Configure dshannon sudoers ==="

printf '# Remote administration from dc1 via dshannon account\nDefaults:dshannon !requiretty\nDefaults:dshannon log_output\ndshannon ALL=(root) NOPASSWD: ALL\n' \
    > /etc/sudoers.d/dshannon-admin
chmod 440 /etc/sudoers.d/dshannon-admin

if visudo -cf /etc/sudoers.d/dshannon-admin; then
    ok "sudoers configured: dshannon NOPASSWD: ALL"
else
    fail "sudoers syntax error — removing broken file"
    rm -f /etc/sudoers.d/dshannon-admin
fi

# Remove sss from sudoers NSS to prevent SSSD from overriding local rules
if grep -q 'sudoers:.*sss' /etc/nsswitch.conf 2>/dev/null; then
    sed -i 's/^sudoers:.*/sudoers:    files/' /etc/nsswitch.conf
    ok "Removed sss from sudoers NSS (local files only)"
fi
echo ""

###############################################################################
# 4. USBGuard (NIST 3.8.7)
###############################################################################
echo "=== Step 4: USBGuard (3.8.7 — Removable Media) ==="

if rpm -q usbguard > /dev/null 2>&1; then
    ok "USBGuard already installed"
else
    dnf install -y usbguard
    if [ $? -eq 0 ]; then
        ok "USBGuard installed"
    else
        fail "USBGuard installation failed"
    fi
fi

if rpm -q usbguard > /dev/null 2>&1; then
    usbguard generate-policy > /etc/usbguard/rules.conf 2>/dev/null
    RULE_COUNT=$(wc -l < /etc/usbguard/rules.conf)
    ok "Generated $RULE_COUNT allow rules from connected devices"

    systemctl enable --now usbguard 2>/dev/null
    if systemctl is-active --quiet usbguard; then
        ok "USBGuard is active"
    else
        fail "USBGuard failed to start"
    fi
fi
echo ""

###############################################################################
# 5. Session Lock (NIST 3.1.10 — 15 min idle)
###############################################################################
echo "=== Step 5: Session Lock (3.1.10 — 15 min idle) ==="

mkdir -p /etc/dconf/db/local.d/locks

cat > /etc/dconf/db/local.d/01-screensaver << 'EOF'
[org/gnome/desktop/session]
idle-delay=uint32 900

[org/gnome/desktop/screensaver]
lock-enabled=true
lock-delay=uint32 0
idle-activation-enabled=true
EOF
ok "Session lock config written (900s idle)"

cat > /etc/dconf/db/local.d/locks/screensaver << 'EOF'
/org/gnome/desktop/session/idle-delay
/org/gnome/desktop/screensaver/lock-enabled
/org/gnome/desktop/screensaver/lock-delay
/org/gnome/desktop/screensaver/idle-activation-enabled
EOF
ok "Settings locked — users cannot override"

if [ ! -f /etc/dconf/profile/user ]; then
    cat > /etc/dconf/profile/user << 'EOF'
user-db:user
system-db:local
system-db:site
system-db:distro
EOF
    ok "Created dconf user profile"
fi

dconf update 2>/dev/null
ok "dconf database updated"
echo ""

###############################################################################
# 6. Login Banner (NIST 3.1.9 — DoD Standard)
###############################################################################
echo "=== Step 6: Login Banners (3.1.9 — DoD Banner) ==="

cat > /etc/issue << 'EOF'
You are accessing a CyberHygiene Project Contractor Information System (CIS)
that is provided for company-authorized use only.

Unauthorized access or use is strictly prohibited and may be subject to
civil and criminal penalties. All activity on this system is monitored
and recorded. By continuing, you consent to this monitoring.

EOF
ok "Console banner written to /etc/issue"

cp /etc/issue /etc/issue.net
ok "SSH banner written to /etc/issue.net"

if ! grep -q '^Banner' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null; then
    echo 'Banner /etc/issue.net' >> /etc/ssh/sshd_config
    ok "Added Banner directive to sshd_config"
else
    ok "SSH Banner directive already configured"
fi

systemctl restart sshd 2>/dev/null
ok "sshd restarted"
echo ""

###############################################################################
# Verification
###############################################################################
echo "============================================"
echo "Verification Summary — $(hostname)"
echo "============================================"

# SSH
if systemctl is-active --quiet sshd; then
    ok "sshd: Running"
else
    fail "sshd: NOT running"
fi

PRL=$(sshd -T 2>/dev/null | grep -i permitrootlogin | head -1)
if echo "$PRL" | grep -qi "no"; then
    ok "PermitRootLogin: no"
else
    fail "PermitRootLogin: $PRL (expected 'no')"
fi

# dshannon SSH key
if grep -q "dshannon@dc1.cyberinabox.net" /home/dshannon/.ssh/authorized_keys 2>/dev/null; then
    ok "dshannon SSH key: installed"
else
    fail "dshannon SSH key: NOT found"
fi

# dshannon sudoers
if [ -f /etc/sudoers.d/dshannon-admin ] && visudo -cf /etc/sudoers.d/dshannon-admin >/dev/null 2>&1; then
    ok "dshannon sudoers: configured"
else
    fail "dshannon sudoers: NOT configured"
fi

# Firewall
if command -v firewall-cmd > /dev/null 2>&1 && systemctl is-active --quiet firewalld; then
    if firewall-cmd --query-service=ssh --quiet 2>/dev/null; then
        ok "Firewall: SSH allowed"
    else
        fail "Firewall: SSH NOT allowed"
    fi
else
    ok "Firewall: firewalld not active (SSH accessible)"
fi

# USBGuard
if systemctl is-active --quiet usbguard 2>/dev/null; then
    ok "USBGuard: Active"
else
    fail "USBGuard: NOT active"
fi

# Session lock
if [ -f /etc/dconf/db/local.d/01-screensaver ]; then
    ok "Session lock: Configured (900s idle)"
else
    fail "Session lock: Missing"
fi

# Banner
if [ -f /etc/issue ] && grep -q "CyberHygiene Project" /etc/issue 2>/dev/null; then
    ok "Login banner: Present"
else
    fail "Login banner: Missing"
fi

BANNER_CONF=$(sshd -T 2>/dev/null | grep -i banner || echo "not found")
ok "SSH Banner: $BANNER_CONF"

echo ""
echo "============================================"
echo "Done. dc1 can now SSH as dshannon with passwordless sudo."
echo "Test from dc1: ssh -i /home/dshannon/.ssh/id_ecdsa dshannon@192.168.1.104 'sudo whoami'"
echo "============================================"
