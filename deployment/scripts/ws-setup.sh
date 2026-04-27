#!/bin/bash
###############################################################################
# ws-setup.sh — All-in-one workstation security setup for CMMC compliance
#
# Run this script as root on each workstation from the local console.
# It performs the following:
#   1. Installs dc1's SSH public key for remote administration
#   2. Enrolls the workstation in the FreeIPA domain (cyberinabox.net)
#   3. Installs and configures USBGuard (NIST 3.8.7)
#   4. Configures session lock at 15 minutes (NIST 3.1.10)
#   5. Deploys DoD-standard login banners (NIST 3.1.9)
#
# FreeIPA enrollment (step 2) may fail due to a KDC pre-auth issue on dc1.
# If it fails, skip it — the other 4 controls work independently.
# Host entries and DNS records have been pre-created on dc1.
#
# Download & run:
#   curl -ks https://dc1.cyberinabox.net/ws-setup.sh -o /root/ws-setup.sh
#   chmod +x /root/ws-setup.sh && /root/ws-setup.sh
#
# Created: 2026-02-15
# Author:  D. Shannon / TCC CMMC Remediation
###############################################################################

set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

IPA_SERVER="dc1.cyberinabox.net"
IPA_DOMAIN="cyberinabox.net"
IPA_REALM="CYBERINABOX.NET"

DSHANNON_PUBKEY="ecdsa-sha2-nistp521 AAAAE2VjZHNhLXNoYTItbmlzdHA1MjEAAAAIbmlzdHA1MjEAAACFBAAw+oq22GUp7YKneV/InxgnJVzHS3Tg5N+3fG1onxnxOO0oGNupLahtBrqj0oPQ7b+mVDe6L5RNELk3PA5SJ2Dp8QCErELlZMrU3VALemqJryi56dD4oLXXzWe2FrelVeiU9PNcf+zj3rpsygs4ZAc5OWZKx6fSQ7/5TkJgDGUfFNPeaA== dshannon@dc1.cyberinabox.net"

LOG="/var/log/ws-setup.log"

log()  { echo -e "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG"; }
ok()   { log "${GREEN}[OK]${NC} $1"; }
warn() { log "${YELLOW}[WARN]${NC} $1"; }
fail() { log "${RED}[FAIL]${NC} $1"; }

###############################################################################
# Pre-flight checks
###############################################################################
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root."
    exit 1
fi

log "=========================================="
log "Workstation Security Setup — $(hostname)"
log "=========================================="

# Verify network connectivity to dc1
if ! ping -c 1 -W 5 "$IPA_SERVER" > /dev/null 2>&1; then
    fail "Cannot reach $IPA_SERVER — check network."
    exit 1
fi
ok "Network connectivity to $IPA_SERVER verified"

###############################################################################
# 1. Install dshannon's SSH key + sudoers for remote administration
###############################################################################
log ""
log "--- Step 1: dshannon SSH Key and sudoers ---"

DSHANNON_HOME="/home/dshannon"
mkdir -p "${DSHANNON_HOME}/.ssh"
chmod 700 "${DSHANNON_HOME}/.ssh"
touch "${DSHANNON_HOME}/.ssh/authorized_keys"
chmod 600 "${DSHANNON_HOME}/.ssh/authorized_keys"

if grep -qF "dshannon@dc1.cyberinabox.net" "${DSHANNON_HOME}/.ssh/authorized_keys" 2>/dev/null; then
    ok "dshannon SSH key already installed"
else
    echo "$DSHANNON_PUBKEY" >> "${DSHANNON_HOME}/.ssh/authorized_keys"
    chown -R dshannon:dshannon "${DSHANNON_HOME}/.ssh"
    restorecon -Rv "${DSHANNON_HOME}/.ssh/" 2>/dev/null || true
    ok "dshannon ECDSA public key installed"
fi

# Configure sudoers for passwordless admin
printf '# Remote administration from dc1 via dshannon account\nDefaults:dshannon !requiretty\nDefaults:dshannon log_output\ndshannon ALL=(root) NOPASSWD: ALL\n' \
    > /etc/sudoers.d/dshannon-admin
chmod 440 /etc/sudoers.d/dshannon-admin
visudo -cf /etc/sudoers.d/dshannon-admin && ok "dshannon sudoers configured" || \
    { fail "sudoers error"; rm -f /etc/sudoers.d/dshannon-admin; }

# Ensure local sudoers files take precedence over SSSD
if grep -q 'sudoers:.*sss' /etc/nsswitch.conf 2>/dev/null; then
    sed -i 's/^sudoers:.*/sudoers:    files/' /etc/nsswitch.conf
    ok "Removed sss from sudoers NSS"
fi

###############################################################################
# 2. FreeIPA Domain Enrollment
###############################################################################
log ""
log "--- Step 2: FreeIPA Domain Enrollment ---"

if ipa-client-install --version > /dev/null 2>&1; then
    ok "ipa-client package already installed"
else
    log "Installing ipa-client..."
    dnf install -y ipa-client >> "$LOG" 2>&1
    ok "ipa-client package installed"
fi

log ""
warn "NOTE: FreeIPA enrollment may fail due to a known KDC issue on dc1."
warn "If enrollment fails, the remaining controls (USBGuard, session lock,"
warn "login banners) will still be applied. Enrollment can be retried later."
log ""

# Pre-configured host enrollment passwords (one-time use)
# These were generated on dc1 and are unique per host.
declare -A HOST_OTP=(
    ["labrat"]="Enroll-labrat-2026"
    ["engineering"]="Enroll-engineering-2026"
    ["accounting"]="Enroll-accounting-2026"
)

MYHOSTNAME=$(hostname -s 2>/dev/null || hostname)
MY_OTP="${HOST_OTP[$MYHOSTNAME]:-}"

# Check if already enrolled
if [ -f /etc/ipa/default.conf ]; then
    warn "This system appears to already be enrolled in FreeIPA."
    read -rp "Re-enroll? (y/N): " REENROLL
    if [[ "$REENROLL" =~ ^[Yy] ]]; then
        log "Uninstalling previous enrollment..."
        ipa-client-install --uninstall --unattended >> "$LOG" 2>&1
    else
        ok "Keeping existing FreeIPA enrollment"
        IPA_SKIP=1
    fi
fi

if [ "${IPA_SKIP:-0}" -eq 0 ]; then
    log "Enrolling in FreeIPA domain $IPA_DOMAIN..."

    if [ -n "$MY_OTP" ]; then
        log "Using pre-configured enrollment password for $MYHOSTNAME"
        IPA_PW="$MY_OTP"
    else
        warn "No pre-configured password for hostname '$MYHOSTNAME'"
        echo ""
        read -rsp "Enter enrollment password (or FreeIPA admin password): " IPA_PW
        echo ""
    fi

    # Try host OTP enrollment first (no --principal needed)
    ipa-client-install \
        --server="$IPA_SERVER" \
        --domain="$IPA_DOMAIN" \
        --realm="$IPA_REALM" \
        --password="$IPA_PW" \
        --hostname="${MYHOSTNAME}.${IPA_DOMAIN}" \
        --mkhomedir \
        --enable-dns-updates \
        --no-ntp \
        --force-join \
        --unattended 2>&1 | tee -a "$LOG"

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        ok "FreeIPA enrollment successful"
    else
        warn "Host OTP enrollment failed — trying with admin principal..."
        echo ""
        read -rsp "Enter FreeIPA admin password: " ADMIN_PW
        echo ""
        ipa-client-install \
            --server="$IPA_SERVER" \
            --domain="$IPA_DOMAIN" \
            --realm="$IPA_REALM" \
            --principal=admin \
            --password="$ADMIN_PW" \
            --hostname="${MYHOSTNAME}.${IPA_DOMAIN}" \
            --mkhomedir \
            --enable-dns-updates \
            --no-ntp \
            --force-join \
            --unattended 2>&1 | tee -a "$LOG"

        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            ok "FreeIPA enrollment successful (admin)"
        else
            fail "FreeIPA enrollment failed — continuing with remaining controls"
            warn "Retry later: ipa-client-install --server=$IPA_SERVER --domain=$IPA_DOMAIN"
        fi
        unset ADMIN_PW
    fi
    unset IPA_PW
fi

###############################################################################
# 3. USBGuard (NIST SP 800-171 3.8.7 — Removable Media)
###############################################################################
log ""
log "--- Step 3: USBGuard (3.8.7 — Control Removable Media) ---"

if rpm -q usbguard > /dev/null 2>&1; then
    ok "USBGuard already installed: $(rpm -q usbguard)"
else
    log "Installing USBGuard..."
    dnf install -y usbguard >> "$LOG" 2>&1
    if [ $? -eq 0 ]; then
        ok "USBGuard installed"
    else
        fail "USBGuard installation failed"
    fi
fi

if rpm -q usbguard > /dev/null 2>&1; then
    log "Generating device-specific policy from currently connected devices..."
    usbguard generate-policy > /etc/usbguard/rules.conf 2>> "$LOG"
    RULE_COUNT=$(wc -l < /etc/usbguard/rules.conf)
    ok "Generated $RULE_COUNT device-specific allow rules"

    log "Enabling and starting USBGuard..."
    systemctl enable --now usbguard >> "$LOG" 2>&1
    if systemctl is-active --quiet usbguard; then
        ok "USBGuard is active — unrecognized USB devices will be blocked"
    else
        fail "USBGuard failed to start — check: journalctl -u usbguard"
    fi

    log "Current device list:"
    usbguard list-devices 2>&1 | tee -a "$LOG"
fi

###############################################################################
# 4. Session Lock (NIST SP 800-171 3.1.10 — 15-minute idle timeout)
###############################################################################
log ""
log "--- Step 4: Session Lock (3.1.10 — Idle Lock at 15 min) ---"

mkdir -p /etc/dconf/db/local.d/locks

cat > /etc/dconf/db/local.d/01-screensaver << 'DCONF'
[org/gnome/desktop/session]
idle-delay=uint32 900

[org/gnome/desktop/screensaver]
lock-enabled=true
lock-delay=uint32 0
idle-activation-enabled=true
DCONF
ok "Session lock config written (idle-delay=900s, lock-enabled=true)"

cat > /etc/dconf/db/local.d/locks/screensaver << 'LOCKS'
/org/gnome/desktop/session/idle-delay
/org/gnome/desktop/screensaver/lock-enabled
/org/gnome/desktop/screensaver/lock-delay
/org/gnome/desktop/screensaver/idle-activation-enabled
LOCKS
ok "Settings locked — users cannot override"

# Ensure dconf profile exists
if [ ! -f /etc/dconf/profile/user ]; then
    cat > /etc/dconf/profile/user << 'PROF'
user-db:user
system-db:local
system-db:site
system-db:distro
PROF
    ok "Created dconf user profile"
fi

dconf update 2>> "$LOG"
ok "dconf database updated"

###############################################################################
# 5. Login Banners (NIST SP 800-171 3.1.9 — DoD Standard)
###############################################################################
log ""
log "--- Step 5: Login Banners (3.1.9 — Company Access Notice) ---"

cat > /etc/issue << 'BANNER'
You are accessing a CyberHygiene Project Contractor Information System (CIS)
that is provided for company-authorized use only.

Unauthorized access or use is strictly prohibited and may be subject to
civil and criminal penalties. All activity on this system is monitored
and recorded. By continuing, you consent to this monitoring.

BANNER
ok "Console banner written to /etc/issue"

cp /etc/issue /etc/issue.net
ok "SSH banner written to /etc/issue.net"

# Configure SSH Banner directive
if ! grep -q '^Banner' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null; then
    echo 'Banner /etc/issue.net' >> /etc/ssh/sshd_config
    ok "Added Banner directive to sshd_config"
else
    ok "SSH Banner directive already configured"
fi

systemctl restart sshd >> "$LOG" 2>&1
ok "sshd restarted"

# Verify
BANNER_CONF=$(sshd -T 2>/dev/null | grep -i banner || echo "not found")
log "SSH Banner setting: $BANNER_CONF"

###############################################################################
# 6. Verify and Report
###############################################################################
log ""
log "=========================================="
log "Verification Summary — $(hostname)"
log "=========================================="

# SSH key
if grep -q "root@dc1.cyberinabox.net" /root/.ssh/authorized_keys 2>/dev/null; then
    ok "SSH key: dc1 key present"
else
    fail "SSH key: dc1 key NOT found"
fi

# FreeIPA
if [ -f /etc/ipa/default.conf ]; then
    ok "FreeIPA: Enrolled in $(grep -oP 'domain\s*=\s*\K.*' /etc/ipa/default.conf)"
else
    fail "FreeIPA: NOT enrolled"
fi

# USBGuard
if systemctl is-active --quiet usbguard 2>/dev/null; then
    ok "USBGuard: Active — $(usbguard list-rules 2>/dev/null | wc -l) rules"
else
    fail "USBGuard: NOT active"
fi

# Session lock
if [ -f /etc/dconf/db/local.d/01-screensaver ]; then
    ok "Session lock: Configured (900s idle, lock enforced)"
else
    fail "Session lock: Config file missing"
fi

# Banners
if [ -f /etc/issue ] && grep -q "CyberHygiene Project" /etc/issue 2>/dev/null; then
    ok "Login banner: CyberHygiene Project access notice present"
else
    fail "Login banner: Missing or incorrect"
fi

log ""
log "Setup complete. Log saved to $LOG"
log "dc1 can now remotely manage this workstation via SSH."
log ""
log "If FreeIPA enrollment failed, you can retry manually:"
log "  ipa-client-install --server=$IPA_SERVER --domain=$IPA_DOMAIN --principal=admin"
log ""
