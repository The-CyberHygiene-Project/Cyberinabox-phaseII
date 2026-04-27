#
# rocky9-fips.ks — Kickstart for SecureMac Rocky Linux 9 service VM
# diwai.org CyberInABox Reference System
# Created: 2026-04-08
#
# Architecture:
#   VM disk: 200 GB virtual (LVM on LUKS2 AES-256-XTS)
#   FIPS 140-2 enabled at boot via fips=1 kernel parameter
#   Partitioning follows NIST SP 800-171 / CIS Rocky Linux 9 Benchmark
#   SCAP profile: xccdf_org.ssgproject.content_profile_cui (NIST 800-171)
#   Separate partitions for /var, /var/log, /var/log/audit, /tmp, /home
#
# Credentials (store in password manager):
#   LUKS passphrase : REDACTED_SEE_SENSITIVE
#   root password   : Y9yXKC6C9Z4s0DuMUJ8S
#   dshannon pw     : hqJWVycXppiCiJ3QmX
#
# Usage:
#   1. On macOS: python3 -m http.server 8080 --bind 192.168.64.1 --directory /Users/dshannon/diwai
#   2. Boot Rocky Linux 9 aarch64 ISO in UTM VM
#   3. At GRUB menu press 'e', append to linux line:
#        inst.ks=http://192.168.64.1:8080/rocky9-fips.ks
#   4. Press Ctrl-x to boot — installation runs unattended
#

# ── Installation method ───────────────────────────────────────
url --mirrorlist=https://mirrors.rockylinux.org/mirrorlist?arch=aarch64&repo=BaseOS-9
repo --name=appstream --mirrorlist=https://mirrors.rockylinux.org/mirrorlist?arch=aarch64&repo=AppStream-9

# ── Locale / keyboard / timezone ─────────────────────────────
lang en_US.UTF-8
keyboard --vckeymap=us --xlayouts=us
timezone America/Denver --utc

# ── Network ───────────────────────────────────────────────────
# VM NIC gets DHCP from macOS LAN (10.10.1.x) during install
# Static IP configured post-install: 10.10.1.10/24 gw 10.10.1.1
network --bootproto=dhcp --device=eth0 --onboot=yes --hostname=services.diwai.org

# ── Security ──────────────────────────────────────────────────
# fips=1 in GRUB kernel line — required for FIPS 140-2 kernel mode
# audit=1 enables audit subsystem at boot
bootloader --location=mbr --append="fips=1 audit=1 audit_backlog_limit=8192"

# Root password — SHA-512 hashed
rootpw --iscrypted $6$hAtPvYU4ckNfjL48$4xxy0Ow/r8o5rlIAx7.KBLsoOqo/lWn18DPkH9bfQeGSFbh2Sm2QT8lfJtQacBG8PKlJ.cqVCBbeg8tmxdaTV0

# SELinux enforcing mode
selinux --enforcing

# Firewall — SSH only during build; tightened post-install
firewall --enabled --ssh

# ── Installation options ──────────────────────────────────────
text
skipx
firstboot --disabled
reboot

# ── Disk configuration ────────────────────────────────────────
# Target: first virtio block device from macOS Virtualization Framework
# Total: 200 GB virtual disk
zerombr
clearpart --all --initlabel --drives=vda

# /boot/efi and /boot UNENCRYPTED — required for GRUB/initramfs pre-LUKS
part /boot/efi --fstype=efi --size=600 --ondisk=vda --label=EFI
part /boot --fstype=xfs --size=1024 --ondisk=vda --label=boot

# LUKS2 encrypted physical volume — remainder of disk
part pv.01 --size=1 --grow --ondisk=vda --encrypted --luks-version=luks2 --cipher=aes-xts-plain64 --passphrase=REDACTED_SEE_SENSITIVE

# LVM volume group
volgroup vg0 pv.01

# Logical volumes — all on one line (anaconda does not support \ continuation)
logvol / --vgname=vg0 --name=root --size=20480 --fstype=xfs
logvol /var --vgname=vg0 --name=var --size=25600 --fstype=xfs --fsoptions="nodev"
logvol /var/log --vgname=vg0 --name=var_log --size=10240 --fstype=xfs --fsoptions="nodev,nosuid"
logvol /var/log/audit --vgname=vg0 --name=var_log_audit --size=10240 --fstype=xfs --fsoptions="nodev,nosuid"
logvol /tmp --vgname=vg0 --name=tmp --size=5120 --fstype=xfs --fsoptions="nodev,nosuid,noexec"
logvol /home --vgname=vg0 --name=home --size=10240 --fstype=xfs --fsoptions="nodev,nosuid"
logvol /opt --vgname=vg0 --name=opt --size=51200 --fstype=xfs --fsoptions="nodev"
logvol swap --vgname=vg0 --name=swap --size=8192

# ── Package selection ─────────────────────────────────────────
%packages --ignoremissing
@^minimal-environment
@standard
# FIPS — must be installed for dracut FIPS initramfs
dracut-fips
dracut-fips-aesni
# SELinux
policycoreutils
policycoreutils-python-utils
setools-console
# Auditing
audit
audispd-plugins
# Cryptography
openssl
openssl-libs
nss
gnutls
# Admin
sudo
vim-minimal
curl
wget
tar
rsync
git
# Network
NetworkManager
firewalld
# Container runtime
podman
container-selinux
# OpenSCAP compliance scanning
openscap
openscap-scanner
scap-security-guide
# Time sync (required for Kerberos/audit timestamps)
chrony
%end

# ── Post-install ──────────────────────────────────────────────
%post --log=/root/ks-post.log

echo "=== SecureMac Rocky Linux 9 post-install ===" | tee /root/ks-post.log

# 1. FIPS mode — fips-mode-setup sets dracut + crypto-policies
#    bootloader --append already placed fips=1 in GRUB
echo "--- Enabling FIPS mode ---"
fips-mode-setup --enable
update-crypto-policies --set FIPS

# 2. Admin user
echo "--- Creating dshannon user ---"
useradd -m -G wheel dshannon
echo 'dshannon:$6$h3AS5vsQ3Nnd/JUF$BU0yYT24IDKS5iWGBOhxufZYq3GhiUGnoZBxZNsu8IXweEE9uWImlDB0R41LWtpELUwkJ3B4FN3tRofOA7zaa1' | chpasswd -e
echo "dshannon ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/dshannon
chmod 440 /etc/sudoers.d/dshannon

# SSH authorized key (RSA-4096, FIPS-compliant)
mkdir -p /home/dshannon/.ssh
chmod 700 /home/dshannon/.ssh
cat > /home/dshannon/.ssh/authorized_keys << 'EOF'
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC1LLmaJGPrR371ntQVXu+ouK5WMU6/CDX45B1+OACnk+gfx9DrNvKvOFy0+cgJklhsUAronPXPaxi3VfQWEizkAthLqpfzZsDTuVklqM3pLi55/kyeBN4x2s3uwDvpEshDQQyHtVoxY9byOkBWyH7/yN4FbiiS9KM0qXl5ECRtClTPEOV/1wUUnMD3rst2xicxeEFrm4rAY2eUOF1piBvC3EzN0o42KzXxbqgzbayDGJgNNE5ttOotdXHKsQltPxPDP5K/GHOgLXOm0A6MS5d0ljddkVmpRb17+LqiB3sCY06SVJwzJgfvSoEtRQ9CkqQqa1ft6Ns8NVpufJOwNTtYNPTdvwNQ5OOpPWxDZ0RYxehHbk3zWEYcEWq/LCchRkYKO1XzNEt7C0wC4X9OxAOu5yYq4AJjR1ZLbVmgkdSjernE4EjBr35Fgw2MY2cHHW5M2WtXWTlZ24hjRO7DwygTaUGSKgUQMOOWcc13SH5E62ZGfZEIN1td3RVOA7hq9YQHXSB08KUDZp7t589ezFFo86Kb7PqENWp/RdcRDbudDePNdn2IZ7yWJ9O/WWpcmH3L226gdWXAVegITQExeeYzG39zoVO0gUcbmgKxKzWnvq4+yWwEvksz5t8TcIJEk8337L5z1k7GzHV8QLtj17FKSCxZEhiL13V1oPWefCPpgw== dshannon@diwai.org
EOF
chmod 600 /home/dshannon/.ssh/authorized_keys
chown -R dshannon:dshannon /home/dshannon/.ssh

# 3. Static IP post-install
#    VM NIC: eth0 → 10.10.1.10/24, gateway 10.10.1.1, DNS 10.10.1.1
nmcli con mod "Wired connection 1" \
    ipv4.method manual \
    ipv4.addresses 10.10.1.10/24 \
    ipv4.gateway 10.10.1.1 \
    ipv4.dns "10.10.1.1 1.1.1.1" \
    connection.autoconnect yes 2>/dev/null || \
nmcli con mod eth0 \
    ipv4.method manual \
    ipv4.addresses 10.10.1.10/24 \
    ipv4.gateway 10.10.1.1 \
    ipv4.dns "10.10.1.1 1.1.1.1" \
    connection.autoconnect yes 2>/dev/null || true

# 4. Disable unnecessary services
echo "--- Disabling unused services ---"
for svc in kdump avahi-daemon cups bluetooth; do
    systemctl disable --now $svc 2>/dev/null || true
done

# 5. Enable required services
systemctl enable auditd
systemctl enable chronyd
systemctl enable firewalld

# 6. chrony — use pool.ntp.org (replace with internal NTP post-install if needed)
cat > /etc/chrony.conf << 'EOF'
pool pool.ntp.org iburst
driftfile /var/lib/chrony/drift
makestep 1.0 3
rtcsync
logdir /var/log/chrony
EOF

# 7. SSH hardening — FIPS-compliant algorithms only
cat >> /etc/ssh/sshd_config << 'EOF'

# FIPS 140-2 / NIST 800-171 SSH hardening — SecureMac
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
MaxAuthTries 3
LoginGraceTime 60
ClientAliveInterval 300
ClientAliveCountMax 0
KexAlgorithms ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256
Ciphers aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-256,hmac-sha2-512,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com
Banner /etc/issue.net
EOF

# 8. Login banner (NIST AC-8)
cat > /etc/issue.net << 'EOF'
************************************************************************
*  AUTHORIZED USE ONLY — diwai.org SecureMac Reference System         *
*  Access is monitored and recorded. Unauthorized access is            *
*  prohibited and subject to criminal and civil penalties.             *
*  By logging in you consent to monitoring per diwai.org policy.      *
************************************************************************
EOF
cp /etc/issue.net /etc/issue

# 9. Firewall — open only SSH during build phase
firewall-cmd --permanent --set-default-zone=drop
firewall-cmd --permanent --zone=drop --add-service=ssh
firewall-cmd --reload 2>/dev/null || true

# 10. Set hostname
hostnamectl set-hostname services.diwai.org

# 11. OpenSCAP — apply NIST 800-171 CUI profile post-install
#     SSG is now installed, so this will succeed
echo "--- Running OpenSCAP CUI baseline remediation ---"
oscap xccdf eval \
    --remediate \
    --profile xccdf_org.ssgproject.content_profile_cui \
    --results /root/oscap-ks-results.xml \
    --report /root/oscap-ks-report.html \
    /usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml \
    >> /root/ks-post.log 2>&1 || true
echo "OpenSCAP remediation complete (see /root/oscap-ks-report.html)"

echo "=== Post-install complete. Rebooting. ===" >> /root/ks-post.log
%end
