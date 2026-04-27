#!/bin/bash
# Deploy USBGuard, session lock, and login banners to ws1-ws3
# Background watcher — polls every 60s, deploys when host comes online
# Created: 2026-02-15

LOG="/var/log/ws-deploy.log"
POLL_INTERVAL=60
HOSTS=("192.168.1.115" "192.168.1.104" "192.168.1.113")
NAMES=("labrat" "engineering" "accounting")
DEPLOYED_FILE="/root/.ws-deploy-done"
SSH_USER="dshannon"
SSH_KEY="/home/dshannon/.ssh/id_ecdsa"
SSH_OPTS="-o IdentitiesOnly=yes -i ${SSH_KEY}"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG"; }

deploy_host() {
    local ip="$1"
    local name="$2"

    log "[$name] Deploying controls to $ip..."

    # --- USBGuard ---
    log "[$name] Installing USBGuard..."
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" \
        "sudo sh -c 'rpm -q usbguard >/dev/null 2>&1 || dnf install -y usbguard'" >> "$LOG" 2>&1
    if [ $? -ne 0 ]; then
        log "[$name] ERROR: USBGuard install failed"
        return 1
    fi

    log "[$name] Generating USBGuard device policy..."
    ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" \
        "sudo sh -c 'usbguard generate-policy > /etc/usbguard/rules.conf && systemctl enable --now usbguard'" >> "$LOG" 2>&1
    if [ $? -ne 0 ]; then
        log "[$name] ERROR: USBGuard config failed"
        return 1
    fi

    log "[$name] Verifying USBGuard..."
    ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" "sudo usbguard list-devices" >> "$LOG" 2>&1

    # --- Session Lock (dconf) ---
    log "[$name] Configuring session lock..."
    ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" "sudo mkdir -p /etc/dconf/db/local.d/locks" >> "$LOG" 2>&1

    ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" \
        'printf "[org/gnome/desktop/session]\nidle-delay=uint32 900\n\n[org/gnome/desktop/screensaver]\nlock-enabled=true\nlock-delay=uint32 0\nidle-activation-enabled=true\n" | sudo tee /etc/dconf/db/local.d/01-screensaver' >> "$LOG" 2>&1

    ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" \
        'printf "/org/gnome/desktop/session/idle-delay\n/org/gnome/desktop/screensaver/lock-enabled\n/org/gnome/desktop/screensaver/lock-delay\n/org/gnome/desktop/screensaver/idle-activation-enabled\n" | sudo tee /etc/dconf/db/local.d/locks/screensaver' >> "$LOG" 2>&1

    ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" "sudo dconf update" >> "$LOG" 2>&1

    # --- Ensure dconf profile exists ---
    ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" \
        'test -f /etc/dconf/profile/user || printf "user-db:user\nsystem-db:local\nsystem-db:site\nsystem-db:distro\n" | sudo tee /etc/dconf/profile/user' >> "$LOG" 2>&1

    # --- Login Banners ---
    log "[$name] Deploying login banners..."
    cat /etc/issue | ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" "sudo tee /etc/issue" >> "$LOG" 2>&1
    cat /etc/issue.net | ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" "sudo tee /etc/issue.net" >> "$LOG" 2>&1

    # Ensure SSH Banner is set
    ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" "
        if ! grep -q '^Banner' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null; then
            echo 'Banner /etc/issue.net' | sudo tee -a /etc/ssh/sshd_config
        fi
        sudo systemctl restart sshd
    " >> "$LOG" 2>&1

    log "[$name] Verifying banner..."
    ssh -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" "sudo sshd -T 2>/dev/null | grep banner" >> "$LOG" 2>&1

    log "[$name] ALL CONTROLS DEPLOYED SUCCESSFULLY"
    return 0
}

# Track which hosts are done
touch "$DEPLOYED_FILE"

log "=== Workstation deployment watcher started ==="
log "Monitoring: ${HOSTS[*]}"
log "Poll interval: ${POLL_INTERVAL}s"

while true; do
    all_done=true
    for i in "${!HOSTS[@]}"; do
        ip="${HOSTS[$i]}"
        name="${NAMES[$i]}"

        # Skip if already deployed
        if grep -q "$name" "$DEPLOYED_FILE" 2>/dev/null; then
            continue
        fi

        all_done=false

        # Check if host is reachable
        if ping -c 1 -W 3 "$ip" > /dev/null 2>&1; then
            log "[$name] Host $ip is ONLINE — starting deployment"

            # Wait a few seconds for SSH to be ready
            sleep 5

            # Verify SSH is reachable
            if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 ${SSH_OPTS} "${SSH_USER}@$ip" "hostname" >> "$LOG" 2>&1; then
                deploy_host "$ip" "$name"
                if [ $? -eq 0 ]; then
                    echo "$name" >> "$DEPLOYED_FILE"
                    log "[$name] Marked as deployed"
                else
                    log "[$name] Deployment failed — will retry next cycle"
                fi
            else
                log "[$name] Host pingable but SSH not ready — will retry"
            fi
        fi
    done

    if $all_done; then
        log "=== All workstations deployed! Watcher exiting. ==="
        exit 0
    fi

    sleep "$POLL_INTERVAL"
done
