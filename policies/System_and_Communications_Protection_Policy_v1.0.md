# System and Communications Protection Policy

**Document ID:** DIWAI-SCP-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** CUI

---

## 1. Purpose

This policy establishes diwai.org (Do It With AI) requirements for protecting system boundaries and communications on the SecureMac Production Network (SPN). It ensures confidentiality, integrity, and availability of Controlled Unclassified Information (CUI) during storage and transmission, in compliance with NIST SP 800-171 Rev 2 (SC-1 through SC-28) and CMMC Level 2.

---

## 2. Scope

This policy applies to:

- **All SPN Systems:**
  - Mac mini M4 Pro (securemac.diwai.org) — macOS Tahoe host
    - pf firewall (perimeter boundary protection)
    - USB Guard daemon (media boundary)
    - en0 (WAN) / en6 (LAN, 10.10.1.0/24)
  - Rocky Linux 9.7 VM (services.diwai.org, 10.10.1.10)
    - All hosted services (LDAP, email, web, VPN)

- **All Communications:**
  - Network traffic (internal 10.10.1.0/24 and external)
  - Email communications (Postfix/Dovecot)
  - File transfers
  - Remote access connections (OpenVPN)
  - Administrative sessions (SSH)

- **All Data States:**
  - Data in transit (network communications)
  - Data at rest (LUKS-encrypted VM disk, FileVault macOS)

---

## 3. Policy Statements

### 3.1 Application Partitioning (SC-2)

**diwai.org shall:**

1. **Separate User from Management Functionality:**
   - SSH administrative interface separate from user-facing web/email services
   - SSH restricted to authorized source IPs (pf rules)
   - Web and email services on standard ports (HTTPS 443, IMAPS 993, SMTPS 587)

2. **Service Isolation:**
   - All services run in Rocky Linux VM (isolated from macOS host)
   - Services run with dedicated user accounts (postfix, dovecot, apache, dirsrv)
   - AI/ML inference (Ollama) runs on macOS host, isolated from VM services

### 3.2 Security Function Isolation (SC-3)

**diwai.org shall:**

1. **Security Functions Isolated:**
   - SELinux mandatory access control enforces isolation on Rocky Linux VM
   - pf firewall functions on macOS host (separate from VM)
   - Wazuh agent operates with dedicated user account

2. **Least Privilege for Security Components:**
   - Security services run with minimal required permissions
   - No direct user access to security component internals
   - auditd/Wazuh logs protected by SELinux type enforcement

### 3.3 Denial of Service Protection (SC-5)

**diwai.org shall protect against denial of service attacks:**

1. **Network-Level Protections (pf on macOS):**
   - Stateful packet inspection enabled
   - SYN flood protection via `scrub` rules
   - Connection rate limiting per source IP
   - Default-deny inbound policy

2. **Application-Level Protections:**
   - Apache MaxRequestWorkers limits (prevent resource exhaustion)
   - Email rate limiting (Postfix: connection limits per source)
   - SSH: `MaxStartups 10:30:60` (connection throttling)
   - Failed authentication lockout (5 attempts → 30-minute lockout via PAM faillock)

### 3.4 Boundary Protection (SC-7)

**diwai.org shall:**

1. **Managed Interfaces:**
   - pf firewall on macOS controls all external connections
   - Default-deny inbound on WAN (en0)
   - Explicit allow rules for required services only
   - LAN (en6, 10.10.1.0/24) is trusted zone

2. **External Connections:**
   - Internet connectivity via commercial ISP (en0 WAN)
   - Inbound services: HTTPS (443), IMAPS (993), SMTPS (587), OpenVPN (1194/UDP)
   - All other inbound blocked by default
   - Outbound allowed from LAN for updates and Let's Encrypt renewal

3. **Access Points:**
   - Single internet connection point (pf WAN interface)
   - UTM virtual network (192.168.64.0/24) — host-only, internal to macOS host

4. **pf Configuration (key rules):**
   ```
   # /etc/pf.conf — macOS Tahoe pf firewall
   set block-policy drop
   set skip on lo0
   
   # Scrub inbound for normalization
   scrub in all
   
   # Default deny
   block all
   
   # Allow established outbound
   pass out quick all keep state
   
   # Allow inbound services
   pass in on en0 proto tcp to any port {443, 993, 587} keep state
   pass in on en0 proto udp to any port 1194 keep state  # OpenVPN
   
   # Block RFC1918 on WAN
   block in on en0 from {10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16}
   ```

### 3.5 Split Tunneling Prevention (SC-7(4))

**diwai.org shall prevent split tunneling:**

- OpenVPN configured with `redirect-gateway def1` (all traffic through VPN)
- No local LAN breakout when VPN connected
- Verified in OpenVPN server config: `push "redirect-gateway def1 bypass-dhcp"`

### 3.6 Transmission Confidentiality and Integrity (SC-8, SC-8(1))

**diwai.org shall encrypt CUI in transit:**

1. **Required Encryption:**
   - **TLS 1.2 or higher** for all web services (HTTPS)
   - **SSH** (OpenSSH — ECDSA-521 host key) for all administrative access
   - **IMAPS (993)** and **SMTPS (587)** with TLS for email
   - **OpenVPN** with TLS + AES-256-GCM for remote access

2. **Certificate Management:**
   - Let's Encrypt wildcard certificate (*.diwai.org)
   - Issued via certbot + Cloudflare DNS-01 challenge
   - Auto-renewal: certbot-renew.timer (nightly)
   - Current expiry: 2026-07-09
   - Deployed to: `/etc/pki/tls/certs/diwai.org.crt`, `/etc/pki/tls/private/diwai.org.key`

3. **Prohibited Clear-Text Protocols:**
   - ❌ HTTP (redirected to HTTPS)
   - ❌ Telnet (SSH only)
   - ❌ FTP (SFTP only)
   - ❌ SMTP without TLS
   - ❌ IMAP/POP3 without TLS

4. **Cryptographic Standards (FIPS 140-2 compliant):**
   - AES-256 for symmetric encryption
   - ECDSA P-521 for asymmetric
   - SHA-256 or stronger for hashing
   - Perfect Forward Secrecy (ECDHE key exchange)

### 3.7 Network Disconnect (SC-10)

**Session timeout controls:**
- SSH: `ClientAliveInterval 300`, `ClientAliveCountMax 0` (disconnect after 5 min idle)
- macOS screen lock: 15-minute timeout
- Web sessions (Roundcube): 15-minute session timeout
- OpenVPN: `keepalive 10 60` with inactive session cleanup

### 3.8 Cryptographic Key Management (SC-12, SC-13)

1. **FIPS 140-2 Cryptographic Protection (SC-13):**
   - FIPS mode enabled on Rocky Linux VM
   - Verification: `fips-mode-setup --check`
   - Only FIPS-approved algorithms permitted on VM

2. **Key Management (SC-12):**

   **SSH Host Keys:**
   - ECDSA-521 generated at VM initial setup
   - Stored in `/etc/ssh/` (mode 600)
   - Backup stored in KeePass vault

   **TLS Certificates (Let's Encrypt):**
   - Private key: ECDSA-384 (certbot default)
   - Stored: `/etc/pki/tls/private/diwai.org.key` (mode 600)
   - Cloudflare API token: `/etc/letsencrypt/cloudflare.ini` (mode 600)
   - Auto-renewed via certbot-renew.timer

   **LUKS Encryption Keys:**
   - AES-256-XTS cipher
   - Passphrase: REDACTED_SEE_SENSITIVE (primary), additional key slot for recovery
   - Scratch codes: Stored in KeePass vault (Passwords.kdbx)

   **KeePass Vault:**
   - Location: `~/Documents/SecureMac Project Docs/` (macOS)
   - Protected with strong master password + key file
   - Backed up to DataStore NAS (encrypted location)

### 3.9 Cryptographic Protection Table (SC-13)

| Data State | Protection Method | Algorithm |
|------------|-------------------|-----------|
| VM disk (at rest) | LUKS full-disk encryption | AES-256-XTS |
| macOS disk (at rest) | FileVault + M4 Secure Enclave | AES-256-XTS |
| Web traffic (transit) | TLS 1.2+ (Let's Encrypt cert) | AES-256-GCM, ECDHE |
| SSH admin sessions | OpenSSH | ECDSA-521, AES-256-CTR |
| Email (transit) | STARTTLS / SMTPS / IMAPS | AES-256-GCM |
| VPN (remote access) | OpenVPN | AES-256-GCM |
| Key storage | KeePass AES-256 | AES-256-CBC |

### 3.10 Secure Name/Address Resolution (SC-20, SC-21)

**DNS Security:**
- Authoritative DNS for diwai.org: Cloudflare (external)
- Internal DNS: macOS host provides DNS for 10.10.1.0/24 via dnsmasq or split-horizon
- services.diwai.org → 10.10.1.10 (internal A record)
- DNSSEC enabled on Cloudflare for diwai.org zone
- Let's Encrypt DNS-01 validation via Cloudflare API token

### 3.11 Session Authenticity (SC-23)

**Session Protection:**
- SSH sessions: unique keys per connection, HMAC integrity
- TLS sessions: random session IDs, PFS enabled
- HTTP cookies: Secure flag, HttpOnly flag
- OpenVPN: TLS + HMAC-SHA256 for session authenticity

### 3.12 Protection of Information at Rest (SC-28, SC-28(1))

1. **Full-Disk Encryption:**
   - Rocky Linux VM: LUKS AES-256-XTS (all partitions)
   - macOS host: FileVault with M4 Secure Enclave

2. **Verification Commands:**
   ```bash
   # Rocky Linux VM
   cryptsetup status | grep cipher  # Expected: aes-xts-plain64
   lsblk -f | grep crypto_LUKS      # All partitions LUKS

   # macOS host
   fdesetup status  # Expected: FileVault is On
   ```

3. **Removable Media:**
   - USB drives encrypted with LUKS or VeraCrypt before CUI storage
   - USB Guard daemon enforces authorization (macOS host)

---

## 4. Roles and Responsibilities

### 4.1 System Owner / ISSO (Donald E. Shannon)

- Define and maintain security architecture and boundary protections
- Configure and maintain pf firewall rules
- Manage cryptographic key lifecycle (certificates, SSH keys, LUKS)
- Monitor network security controls
- Approve encryption implementations
- Conduct annual security architecture review

---

## 5. Implementation Details

### 5.1 Apache HTTPS Configuration

```apache
# /etc/httpd/conf.d/ssl.conf
SSLEngine on
SSLProtocol -all +TLSv1.2 +TLSv1.3
SSLCipherSuite HIGH:!aNULL:!MD5:!3DES
SSLHonorCipherOrder on
SSLCompression off
SSLSessionTickets off
Header always set Strict-Transport-Security "max-age=31536000"
SSLCertificateFile /etc/pki/tls/certs/diwai.org.crt
SSLCertificateKeyFile /etc/pki/tls/private/diwai.org.key
```

### 5.2 SSH Hardening (/etc/ssh/sshd_config)

```
Port 22
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding no
Ciphers aes256-ctr,aes192-ctr,aes128-ctr
MACs hmac-sha2-512,hmac-sha2-256
KexAlgorithms ecdh-sha2-nistp521,ecdh-sha2-nistp384
ClientAliveInterval 300
ClientAliveCountMax 0
```

**Note:** When MFA deployed (POA&M-001), add:
```
AuthenticationMethods publickey,keyboard-interactive
KbdInteractiveAuthentication yes
```

### 5.3 Postfix TLS Configuration

```
# Outbound TLS
smtp_tls_security_level = may
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_cert_file = /etc/pki/tls/certs/diwai.org.crt
smtp_tls_key_file = /etc/pki/tls/private/diwai.org.key

# Inbound TLS
smtpd_tls_security_level = may
smtpd_tls_auth_only = yes
smtpd_tls_cert_file = /etc/pki/tls/certs/diwai.org.crt
smtpd_tls_key_file = /etc/pki/tls/private/diwai.org.key
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
```

### 5.4 Monthly Security Checks

| Check | Command | Expected Result |
|-------|---------|----------------|
| FIPS mode | `fips-mode-setup --check` | FIPS mode is enabled |
| LUKS encryption | `lsblk -f | grep crypto` | crypto_LUKS on partitions |
| FileVault | `fdesetup status` | FileVault is On |
| pf status | `sudo pfctl -si | head` | Enabled: YES |
| Rocky firewall | `sudo firewall-cmd --state` | running |
| TLS cert expiry | `openssl x509 -in /etc/pki/tls/certs/diwai.org.crt -noout -dates` | Valid, not expired |
| SSH config | `sudo sshd -T | grep PasswordAuthentication` | no |
| SELinux | `getenforce` | Enforcing |

---

## 6. Compliance Mapping

| NIST SP 800-171 Control | Implementation |
|-------------------------|----------------|
| **SC-1** Policy and Procedures | This document |
| **SC-2** Application Partitioning | Section 3.1 |
| **SC-3** Security Function Isolation | Section 3.2 |
| **SC-5** Denial of Service Protection | Section 3.3 |
| **SC-7** Boundary Protection | Section 3.4 |
| **SC-7(4)** Split Tunneling | Section 3.5 |
| **SC-8** Transmission Confidentiality/Integrity | Section 3.6 |
| **SC-8(1)** Cryptographic Protection | Section 3.6.4 |
| **SC-10** Network Disconnect | Section 3.7 |
| **SC-12** Cryptographic Key Management | Section 3.8 |
| **SC-13** Cryptographic Protection | Section 3.9 |
| **SC-20** Secure Name Resolution (authoritative) | Section 3.10 |
| **SC-21** Secure Name Resolution (recursive) | Section 3.10 |
| **SC-23** Session Authenticity | Section 3.11 |
| **SC-28** Protection of Information at Rest | Section 3.12 |
| **SC-28(1)** Cryptographic Protection (at rest) | Section 3.12.1 |

---

## 7. Policy Review and Updates

- **Review Frequency:** Annually or upon significant security events
- **Update Triggers:** New NIST cryptographic guidance; TLS/SSL vulnerabilities; new certificate or key infrastructure changes; VPN changes

- **Approval Authority:** System Owner / ISSO (Donald E. Shannon)

---

## 8. Approval Signatures

**Prepared By:**
Name: Donald E. Shannon, System Administrator
Signature: /s/ Donald E. Shannon                Date: April 10, 2026

**Reviewed By:**
Name: Donald E. Shannon, Information System Security Officer
Signature: /s/ Donald E. Shannon                Date: April 10, 2026

**Approved By:**
Name: Donald E. Shannon, System Owner
Signature: /s/ Donald E. Shannon                Date: April 10, 2026

---

**CLASSIFICATION:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)
**DISTRIBUTION:** Official Use Only - Need to Know Basis
**STATUS:** APPROVED

---

**END OF DOCUMENT**
