# SYSTEM SECURITY PLAN
## SecureMac Reference System — diwai.org

**Document Control:**

| Field | Value |
|-------|-------|
| **System Name** | SecureMac — diwai.org CyberInABox Reference System #2 |
| **System Owner** | Donald Shannon |
| **Organization** | diwai.org (Do It With AI) |
| **Classification** | Controlled Unclassified Information (CUI) |
| **Version** | 1.2 |
| **Date** | April 23, 2026 |
| **SPRS Score** | 101 / 110 |
| **POA&M Reference** | SecureMac-POAM-v1.0 |
| **Compliance Framework** | NIST SP 800-171 Rev 2 / FIPS 140-2 |

---

## DOCUMENT REVISION HISTORY

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-10 | D. Shannon | Initial SSP. All core services operational: Apache, Postfix, Dovecot, 389-ds, OpenVPN, Suricata, Wazuh, Grafana, Prometheus, USBGuard. OpenSCAP 102/102 pass. Let's Encrypt auto-renewal configured. ClamAV risk accepted (FIPS incompatibility). Known gaps: MFA (3.5.3), formal risk assessment (3.11.1), IR tabletop exercise (3.6.3). |
| 1.1 | 2026-04-10 | D. Shannon | MFA deployed — YubiKey 5C Nano FIPS (FIDO2 ECDSA-SK, verify-required). POA&M-001 closed. SPRS 103 → 108/110. USB Guard UUID allowlist updated; guard enabled. |
| 1.2 | 2026-04-23 | D. Shannon | MFA re-documented after lockout incident (2026-04-14) and recovery (Time Machine rollback to 2026-04-12). v1.1 FIDO2-SK implementation lost in rollback. Re-implemented 2026-04-15 using native macOS CryptoTokenKit PIV (Slot 9C, ECDSA P-256, diwai.org Email CA). PIV operational for macOS local auth (screen lock, sudo). SSH to VM uses RSA key only post-rollback; smartcard enforcement not yet enabled pending Slot 9A regeneration. 3.5.3 revised to PARTIAL. SPRS adjusted 108 → 101/110. POA&M-009 opened. Break-glass sysadmin account documented. |

---

## EXECUTIVE SUMMARY

The SecureMac system is a single-appliance cybersecurity reference platform designed for Very Small Businesses (VSBs) with fewer than 15 users seeking NIST SP 800-171 compliance for government contracts. The system combines a network firewall/router, domain controller, email server, VPN endpoint, IDS/IPS, SIEM, and monitoring platform into a single Mac mini M4 Pro running a FIPS-validated Rocky Linux 9.7 service VM.

**SPRS Score: 101 / 110**

| Domain | Controls | Status |
|--------|----------|--------|
| Access Control (3.1) | 22 | Mostly MET — see 3.1 detail |
| Awareness and Training (3.2) | 3 | PARTIAL |
| Audit and Accountability (3.3) | 9 | MET |
| Configuration Management (3.4) | 9 | MET |
| Identification and Authentication (3.5) | 11 | PARTIAL — MFA operational for local macOS auth; enforcement and SSH MFA pending |
| Incident Response (3.6) | 3 | PARTIAL — no tabletop exercise |
| Maintenance (3.7) | 6 | PARTIAL — see 3.7.5 |
| Media Protection (3.8) | 9 | MET |
| Personnel Security (3.9) | 2 | MET |
| Physical Protection (3.10) | 6 | MET |
| Risk Assessment (3.11) | 3 | NOT MET — formal assessment pending |
| Security Assessment (3.12) | 4 | MET |
| System and Communications Protection (3.13) | 16 | MET |
| System and Information Integrity (3.14) | 7 | MET (ClamAV risk accepted) |

**Known SPRS Deficits:**

| Requirement | Description | Weight | Target Date |
|-------------|-------------|--------|-------------|
| 3.5.3 | MFA partial — PIV configured, enforcement not enabled; SSH to VM uses RSA key only | -5 | 2026-05-31 |
| 3.11.1 | Periodic risk assessment | -3 | 2026-07-01 |
| 3.6.3 | IR tabletop exercise | -1 | 2026-09-30 |
| 3.2.1/3.2.2 | Security awareness training | -3 | 2026-07-01 |
| **Total deficit** | | **-12** | |

---

## 1. SYSTEM DESCRIPTION

### 1.1 System Purpose and Scope

SecureMac is CyberInABox Reference System #2, a demonstration platform for Very Small Business (VSB) cybersecurity. It provides all core network security services for an organization of fewer than 15 users in a single physical appliance, enabling NIST SP 800-171 compliance at a cost accessible to small contractors pursuing government contracts.

**CUI Handling:** Administrative and configuration data only. No end-user CUI is processed in this reference deployment.

### 1.2 System Architecture

**Physical Host:**
- **Hardware:** Apple Mac mini M4 Pro (2024)
- **CPU:** 14-core Apple M4 Pro
- **RAM:** 64 GB unified memory
- **Storage:** 1.0 TB NVMe SSD (Apple Fabric, hardware encrypted)
- **OS:** macOS Tahoe 26.4 (Build 25E246)
- **Role:** Perimeter firewall/router, NAT gateway, USB security monitor, AI inference host (planned)

**Service VM:**
- **Hypervisor:** UTM (QEMU ARM64) on Mac mini
- **OS:** Rocky Linux 9.7 aarch64 (Blue Onyx)
- **Kernel:** 5.14.0-611.41.1.el9_7.aarch64
- **FIPS:** Enabled (fips=1, crypto-policy=FIPS)
- **SELinux:** Enforcing
- **Disk:** LUKS2 AES-256-XTS full-disk encryption
- **Role:** All application services (see §1.4)

### 1.3 Network Architecture

| Interface | Device | Address | Role |
|-----------|--------|---------|------|
| en0 | Mac mini (WAN) | 71.39.182.149/29 primary; .145 web; .146 VPN; .147 mail | WAN — CenturyLink fiber |
| en6 | Mac mini (LAN) | 10.10.1.1/24 | LAN — service VM network |
| en1 | Mac mini (MGMT) | 10.0.0.152 | Management — never blocked |
| eth0/enp0s1 | Rocky Linux VM | 10.10.1.10/24 | All services |

**ISP Block:** 71.39.182.144/29 · Gateway: 71.39.182.150  
**DNS:** Cloudflare authoritative for diwai.org; Unbound local resolver on VM  

### 1.4 Services Inventory

| Service | Software | Port(s) | Status |
|---------|---------|---------|--------|
| LDAP Directory | 389-ds-base 2.7.0 | 389/636 | Running |
| Web Server | Apache httpd 2.4.62 | 443 (TLS) | Running |
| Webmail | Roundcubemail 1.5.14 | HTTPS proxy | Running |
| SMTP | Postfix 3.5.25 | 25, 465, 587 | Running |
| IMAP/POP3 | Dovecot 2.3.16 | 993 (IMAPS) | Running |
| Database | MariaDB 10.5.29 | 3306 (local) | Running |
| VPN | OpenVPN 2.5.11 | UDP 1194 | Running |
| DNS Resolver | Unbound 1.16.2 | 53 (local) | Running |
| Network IDS | Suricata 7.0.13 | AF_PACKET | Running |
| SIEM | Wazuh 4.14.4 | 1514/1515 | Running |
| Metrics | Grafana 12.4.2 + Prometheus 3.10.0 | 3000/9090 (LAN) | Running |
| Antivirus | ClamAV 1.4.3 | — | Partial (DB pending) |
| USB Control | USBGuard 1.0.0 | — | Running |
| Cert Renewal | Certbot 3.1.0 | — | Running (timer) |
| Firewall | pf (macOS) | All | Active |
| Firewall | firewalld (VM) | All | Active |

### 1.5 TLS Certificate

- **Certificate:** `*.diwai.org` + `diwai.org` (Let's Encrypt R12, wildcard)
- **Expiry:** 2026-07-09
- **Auto-renewal:** certbot-renew.timer (nightly, DNS-01 via Cloudflare)
- **Deploy hook:** Copies to `/etc/pki/tls/`, restores SELinux context, restarts services

---

## 2. SECURITY CONTROLS

### 3.1 — ACCESS CONTROL (AC)

#### 3.1.1 — Limit System Access to Authorized Users
**Status:** MET  
User accounts managed via 389 Directory Server (LDAP). Only `dshannon` has system access. Remote access requires SSH public key (`~/.ssh/diwai_rsa`, RSA-4096). Password authentication disabled in sshd_config.

#### 3.1.2 — Limit System Access to Authorized Transactions
**Status:** MET  
- Apache: LAN-only vhosts (`ldap.diwai.org`, `monitor.diwai.org`, `wazuh.diwai.org`) restricted to `Require ip 10.10.1.0/24 127.0.0.1`
- MariaDB: binds to localhost only
- Grafana/Prometheus: proxied through Apache, LAN-restricted
- LDAP: firewalld restricts external LDAP access

#### 3.1.3 — Control CUI Flows
**Status:** MET  
- pf firewall enforces default-deny on all WAN inbound
- Only explicitly permitted services pass through
- LAN segment (10.10.1.x) isolated from WAN via pf NAT/RDR
- VPN (TLS 1.2+, AES-256-GCM) for remote administrative access

#### 3.1.4 — Separate Duties
**Status:** MET (VSB context)  
Single-administrator deployment appropriate for <15 user VSB. System Owner = System Administrator = Security Officer (D. Shannon). Documented as accepted single-person-shop configuration.

#### 3.1.5 — Least Privilege
**Status:** MET  
- Services run as unprivileged users (apache, postfix, dovecot, suricata, clamupdate, prometheus, grafana)
- SELinux enforcing mode provides mandatory access control confinement
- `dshannon` has sudo access; root direct login disabled via sshd_config (`PermitRootLogin no`)

#### 3.1.6 — Non-Privileged Accounts for Non-Security Functions
**Status:** MET  
Administrative shell access via `dshannon` (non-root). Root elevation via sudo with logging.

#### 3.1.7 — Prevent Non-Privileged Users from Executing Privileged Functions
**Status:** MET  
SELinux type enforcement. Sudo configured in `/etc/sudoers.d/dshannon`.

#### 3.1.8 — Limit Unsuccessful Logon Attempts
**Status:** MET  
sshd_config: `MaxAuthTries 3`, `LoginGraceTime 60`. SSH key-only authentication eliminates brute-force password risk.

#### 3.1.9 — Privacy and Security Notices
**Status:** MET  
Login banner at `/etc/issue.net` and `/etc/issue` (NIST AC-8 compliant): "AUTHORIZED USE ONLY — diwai.org SecureMac Reference System. Access is monitored and recorded."

#### 3.1.10 — Session Lock
**Status:** MET  
SSH: `ClientAliveInterval 300`, `ClientAliveCountMax 0` (5-minute idle timeout, disconnect).

#### 3.1.11 — Terminate Sessions After Period of Inactivity
**Status:** MET  
SSH idle timeout enforced (see 3.1.10). Web sessions managed by Roundcube session timeout.

#### 3.1.12 — Monitor and Control Remote Access Sessions
**Status:** MET  
All SSH sessions logged by auditd and Wazuh. Remote access exclusively via VPN (OpenVPN) + SSH key, or direct SSH to WAN IP.

#### 3.1.13 — Employ Cryptographic Mechanisms for Remote Access
**Status:** MET  
- SSH: FIPS-compliant algorithms (ECDHE, AES-CTR/GCM, HMAC-SHA256/512)
- VPN: AES-256-GCM, TLS 1.2+, RSA-4096 PKI

#### 3.1.14 — Route Remote Access Via Managed Access Control Points
**Status:** MET  
All remote access enters through pf firewall on Mac mini. VPN terminates at VM (10.10.1.10). No split-tunneling for admin sessions.

#### 3.1.15 — Authorize Remote Execution of Privileged Commands
**Status:** MET  
Administrative commands executed via SSH only. Documented in system configuration.

#### 3.1.16 — Authorize Wireless Access
**Status:** MET  
Wi-Fi (en1) is management-only interface. No production services on Wi-Fi. pf rules ensure MGMT traffic cannot be used to bypass production access controls.

#### 3.1.17 — Protect Wireless Access Using Authentication and Encryption
**Status:** MET  
WPA2/WPA3 on cassinet network. MGMT interface only; no CUI.

#### 3.1.18 — Control Connection of Mobile Devices
**Status:** MET  
Mobile device access via VPN only (AES-256-GCM). No direct LAN access for mobile devices.

#### 3.1.19 — Encrypt CUI on Mobile Devices
**Status:** MET  
VPN enforced for all remote/mobile access. No CUI stored on mobile devices.

#### 3.1.20 — Verify and Control External System Connections
**Status:** MET  
pf default-deny. Only explicitly defined inbound services permitted.

#### 3.1.21 — Limit Use of Portable Storage Devices
**Status:** MET  
- VM: USBGuard 1.0.0 — ImplicitPolicyTarget=block. Toggle: `sudo usb-guard on|off`
- Mac: Custom LaunchDaemon (`org.diwai.usb-guard`) auto-ejects USB storage when mode=on. Toggle: `sudo usb-guard on|off`
- Audit log: `/var/log/usb-guard.log`

#### 3.1.22 — Control CUI Posted to Publicly Accessible Systems
**Status:** MET  
Public-facing website (`diwai.org`) contains no CUI. Webmail and admin interfaces require authentication.

---

### 3.2 — AWARENESS AND TRAINING (AT)

#### 3.2.1 — Security Awareness Activities
**Status:** PARTIAL  
**SPRS Impact:** -3  
Security awareness training not yet formally documented or scheduled for end users. System is currently a single-administrator reference build. Formal training program will be developed prior to VSB customer deployment.  
**POA&M:** SecureMac-POAM-003 — Target: 2026-07-01

#### 3.2.2 — Training for Privileged Users
**Status:** PARTIAL  
Administrator (D. Shannon) has practical security knowledge demonstrated through system build. Formal training completion records not yet documented.  
**POA&M:** SecureMac-POAM-003 — Target: 2026-07-01

#### 3.2.3 — Insider Threat Awareness
**Status:** MET  
Wazuh SIEM monitors for anomalous user behavior, unauthorized access attempts, and suspicious file modifications. Auditd logs all privileged operations.

---

### 3.3 — AUDIT AND ACCOUNTABILITY (AU)

#### 3.3.1 — Create and Retain System Audit Logs
**Status:** MET  
auditd running with comprehensive rules. Wazuh log collector ingests: `/var/log/messages`, `/var/log/secure`, `/var/log/audit/audit.log`, `/var/log/maillog`, `/var/log/httpd/*.log`, `/var/log/suricata/eve.json`, `/var/log/openvpn/*.log`.

#### 3.3.2 — Ensure Actions Can Be Traced to Individual Users
**Status:** MET  
All SSH sessions, sudo operations, and authentication events logged with timestamps and user IDs via auditd.

#### 3.3.3 — Review and Update Logged Events
**Status:** MET  
Wazuh analysisd continuously reviews logs. Alert rules configured for failed logins, privilege escalation, file integrity violations.

#### 3.3.4 — Alert on Audit Failure
**Status:** MET  
Auditd configured with `audit_backlog_limit=8192`. Wazuh monitors auditd process health.

#### 3.3.5 — Correlate Audit Review Processes
**Status:** MET  
Wazuh SIEM provides centralized log correlation across syslog, auditd, Suricata IDS, httpd, and mail logs.

#### 3.3.6 — Provide Audit Reduction and Report Generation
**Status:** MET  
Grafana dashboards for metrics visualization. Wazuh provides security event reporting. Prometheus + node_exporter for system health.

#### 3.3.7 — Provide System Capability That Compares and Synchronizes Clocks
**Status:** MET  
chronyd time synchronization running. Pool: `pool.ntp.org iburst`. `rtcsync` enabled.

#### 3.3.8 — Protect Audit Information
**Status:** MET  
`/var/log/audit` mounted with `noexec,nosuid` (separate LUKS-encrypted LV). Wazuh logs stored in `/var/ossec/logs/` on encrypted storage.

#### 3.3.9 — Limit Audit Log Management to Subset of Privileged Users
**Status:** MET  
Audit logs owned by root/auditd. Only dshannon (sudo) can manage. SELinux `auditd_t` context enforced.

---

### 3.4 — CONFIGURATION MANAGEMENT (CM)

#### 3.4.1 — Establish and Maintain Baseline Configurations
**Status:** MET  
Kickstart file (`~/diwai/rocky9-fips.ks`) documents the complete baseline configuration. SYSTEM-STATE document maintained. SBOM v1.0 documents all software.

#### 3.4.2 — Establish Configuration Settings
**Status:** MET  
OpenSCAP CUI profile applied. 102/102 checks passing (2026-04-09). FIPS crypto-policy enforced. SELinux enforcing. SSH hardened.

#### 3.4.3 — Track, Review, and Log Changes
**Status:** MET  
Wazuh syscheck (FIM) monitors `/etc`, `/usr/bin`, `/usr/sbin`, `/bin`, `/sbin`, `/boot`. Configuration changes logged.

#### 3.4.4 — Analyze Security Impact of Changes
**Status:** MET  
All changes reviewed by system administrator before implementation. OpenSCAP re-scan following significant changes.

#### 3.4.5 — Define, Document, Approve Changes
**Status:** MET  
Changes documented in system state file and SSP revision history. Single-administrator VSB environment.

#### 3.4.6 — Employ Least Functionality
**Status:** MET  
Minimal package installation (Rocky Linux minimal + required services only). Unnecessary services disabled (kdump, avahi, cups, bluetooth). `/tmp` mounted `noexec,nosuid`.

#### 3.4.7 — Restrict, Disable, Prevent Use of Nonessential Programs
**Status:** MET  
Only required services enabled and started. firewalld default-drop zone.

#### 3.4.8 — Apply Deny-by-Exception Policy
**Status:** MET  
pf firewall: `block all` default, explicit permit rules only. firewalld: default-drop zone with explicit service allowances.

#### 3.4.9 — Control and Monitor User-Installed Software
**Status:** MET  
dnf package management with GPG signature verification. No unauthorized software installed. SBOM maintained.

---

### 3.5 — IDENTIFICATION AND AUTHENTICATION (IA)

#### 3.5.1 — Identify System Users, Processes, and Devices
**Status:** MET  
389 Directory Server provides centralized identity. LDAP: `dc=diwai,dc=org`, `ou=people`. SSH RSA-4096 key pairs for system authentication.

#### 3.5.2 — Authenticate Users, Processes, and Devices
**Status:** MET  
SSH: RSA-4096 public key authentication only. LDAP: SSHA512 password hashing. Mail: Dovecot SASL → LDAP.

#### 3.5.3 — Multi-Factor Authentication for Local and Network Access
**Status:** PARTIAL — **POA&M-009 OPEN**  
**SPRS Impact:** -5 (deficit reinstated pending enforcement and SSH MFA)  

MFA is implemented using YubiKey 5C Nano FIPS (PIV smartcard) via native macOS CryptoTokenKit. No third-party PAM modules are used. The current implementation provides MFA for local macOS authentication only.

**Implementation (as of 2026-04-15):**
- **Mechanism:** PIV smartcard — Slot 9C, ECDSA P-256, cert issued by diwai.org Email CA
- **Factor 1 (have):** YubiKey 5C Nano FIPS hardware token (serial 34246645, FIPS 140-2 Level 1)
- **Factor 2 (know):** PIV PIN (PIN:ONCE policy — cached per session)
- **Cert hash:** `3CE899BDDF09EA91986C3DB41BC24DA030EB2159` — paired to `dshannon` via `sc_auth`
- **Cert validity:** 2026-04-13 → 2028-04-12

**Coverage:**

| Auth Path | MFA Status | Notes |
|-----------|-----------|-------|
| macOS screen lock/unlock | ✅ MFA active | PIV PIN required |
| macOS sudo | ✅ MFA active | pam_smartcard.so, PIN cached per ONCE policy |
| SSH to services.diwai.org | ⚠ RSA key only | FIDO2-SK key lost in Time Machine rollback (2026-04-14) |
| macOS login enforcement | ⚠ Not enforced | Password fallback active pending Slot 9A regeneration |

**Gaps and remediation path:**
1. Regenerate Slot 9A with correct policies (`--pin-policy once --touch-policy never`) — requires diwai.org CA online
2. Re-pair `dshannon` to Slot 9A cert; unpair Slot 9C
3. Restore SSH MFA to services.diwai.org (recover FIDO2-SK via `ssh-keygen -K`)
4. Enable enforcement: `sudo defaults write /Library/Preferences/com.apple.security.smartcard enforceSmartCard -bool true`

**Break-glass account:** `sysadmin` — strong 16-char password in sealed envelope, locked cabinet. No smartcard paired (intentional emergency access). Will receive Slot 9A cert when regenerated.

**Evidence:** `~/Documents/SecureMac Project Docs/Evidence/MFA_YubiKey_Deployment.md` (DIWAI-EV-MFA-001 v2.0)

**Background — lockout incident (2026-04-14):** Initial MFA deployment (v1.1, FIDO2-SK via third-party PAM) caused a total lockout when pam_yubico/pam_u2f was set as `required` with a VM network dependency. The VM does not autostart; when unreachable, authentication failed completely. Recovered via Recovery Mode + Time Machine rollback to 2026-04-12. Re-implemented using native CryptoTokenKit (zero network dependency).

#### 3.5.4 — Employ Replay-Resistant Authentication Mechanisms
**Status:** MET  
SSH public key with challenge-response. OpenVPN TLS 1.2+ with TLS-auth HMAC. FIPS cipher suite throughout.

#### 3.5.5 — Prohibit Reuse of Identifiers
**Status:** MET  
LDAP user accounts assigned unique UIDs. No shared accounts.

#### 3.5.6 — Disable Identifiers After Defined Inactivity Period
**Status:** MET  
LDAP accounts managed by administrator. Inactive accounts disabled manually upon user departure.

#### 3.5.7 — Enforce Minimum Password Complexity
**Status:** MET  
PAM password quality configured. LDAP SSHA512 hashing. SSH key-only eliminates password-based remote access.

#### 3.5.8 — Prohibit Password Reuse
**Status:** MET  
PAM pam_pwhistory configured. LDAP password policy enforces history.

#### 3.5.9 — Temporary Passwords
**Status:** MET  
Temporary passwords set to require change on first use via LDAP password policy.

#### 3.5.10 — Store and Transmit Only Cryptographically Protected Passwords
**Status:** MET  
LDAP: SSHA512 hashing. Transmission: LDAPS (TLS 1.2+) or SASL authenticated channel. No plaintext password storage.

#### 3.5.11 — Obscure Feedback of Authentication Information
**Status:** MET  
PAM pam_pwfeedback disabled. Password characters not echoed.

---

### 3.6 — INCIDENT RESPONSE (IR)

#### 3.6.1 — Establish Operational Incident Handling Capability
**Status:** MET  
Incident response procedures documented in CyberHygiene documentation repository. Wazuh SIEM provides alerting. Administrator contact and escalation path defined.

#### 3.6.2 — Track, Document, and Report Incidents
**Status:** MET  
Wazuh alert logs provide incident timeline. auditd provides forensic evidence trail. Incident documentation procedures in place.

#### 3.6.3 — Test Incident Response Capability
**Status:** NOT MET  
**SPRS Impact:** -1  
No formal tabletop exercise has been conducted.  
**POA&M:** SecureMac-POAM-004 — Target: 2026-09-30

---

### 3.7 — MAINTENANCE (MA)

#### 3.7.1 — Perform Maintenance on Organizational Systems
**Status:** MET  
`dnf update` performed regularly. certbot-renew.timer automated. Wazuh and Suricata rules auto-updated.

#### 3.7.2 — Provide Controls on Tools Used for Maintenance
**Status:** MET  
Maintenance performed via SSH (encrypted, authenticated). No third-party remote access tools.

#### 3.7.3 — Ensure Equipment Removed for Maintenance is Sanitized
**Status:** MET  
LUKS2 full-disk encryption on VM. Mac mini hardware encryption via M4 Secure Enclave. Drive removal requires cryptographic key for data access.

#### 3.7.4 — Check Media Containing Diagnostic Programs for Malicious Code
**Status:** MET  
USBGuard blocks unauthorized USB media. ClamAV scanning (when operational) for media content.

#### 3.7.5 — Require MFA for Remote Maintenance Sessions
**Status:** PARTIAL (follows 3.5.3)  
PIV MFA is operational for local macOS maintenance (console access, sudo). Remote maintenance via SSH to services.diwai.org uses RSA key only post-rollback. Full MFA for remote maintenance sessions will be restored as part of POA&M-009 (Slot 9A regeneration + SSH MFA). See 3.5.3.

#### 3.7.6 — Supervise Maintenance Activities
**Status:** MET  
All maintenance performed by system owner (D. Shannon). auditd logs all privileged operations.

---

### 3.8 — MEDIA PROTECTION (MP)

#### 3.8.1 — Protect System Media
**Status:** MET  
VM disk: LUKS2 AES-256-XTS. Mac: M4 Secure Enclave hardware encryption. Backup drives: APFS encrypted or stored on encrypted NAS.

#### 3.8.2 — Limit Access to CUI on System Media
**Status:** MET  
LUKS encryption requires passphrase for any offline media access. System access requires SSH key authentication.

#### 3.8.3 — Sanitize or Destroy Media Before Disposal
**Status:** MET  
LUKS encryption ensures that media disposal without key destruction results in unreadable data. Procedure: destroy LUKS header to sanitize.

#### 3.8.4 — Mark Media with CUI Markings
**Status:** MET  
Backup media labeled "SecureMac Back-up" and "SecureMac" on NAS. System state documents classified as CUI.

#### 3.8.5 — Control Access to Media with CUI
**Status:** MET  
USB storage blocked by default (USBGuard + macOS daemon). Manual toggle required for authorized transfers. All toggle events logged.

#### 3.8.6 — Implement Cryptographic Mechanisms for CUI on Portable Storage
**Status:** MET  
LUKS2 encryption on VM. M4 Secure Enclave encryption on Mac. Kingston IronKey hardware AES-256 encryption for portable key/config vault (planned).

#### 3.8.7 — Control Use of Removable Media
**Status:** MET  
See 3.1.21. USB guard enforced on both Mac host and Rocky Linux VM.

#### 3.8.8 — Prohibit Use of Portable Storage Without Identifiable Owner
**Status:** MET  
Only administrator-controlled storage permitted. USBGuard blocks unknown devices by default.

#### 3.8.9 — Protect Backups Containing CUI
**Status:** MET  
VM backup (diwai-services.utm) stored on encrypted NAS shares (DataStore, Shannon_Home). LUKS encryption protects VM disk image content.

---

### 3.9 — PERSONNEL SECURITY (PS)

#### 3.9.1 — Screen Individuals Before Authorizing Access
**Status:** MET  
Single-administrator deployment (D. Shannon). No additional personnel with system access at this time.

#### 3.9.2 — Ensure CUI is Protected During and After Personnel Actions
**Status:** MET  
Account deprovisioning procedures defined. LDAP account disable + SSH key revocation process documented.

---

### 3.10 — PHYSICAL PROTECTION (PE)

#### 3.10.1 — Limit Physical Access to Systems
**Status:** MET  
Mac mini located in controlled office environment. Physical access limited to system owner.

#### 3.10.2 — Protect and Monitor Physical Facility
**Status:** MET  
Office/home facility with standard physical security. Appropriate for VSB single-office deployment.

#### 3.10.3 — Escort Visitors and Monitor Activity
**Status:** MET  
System owner present when any visitor accesses the facility.

#### 3.10.4 — Maintain Audit Logs of Physical Access
**Status:** MET  
Physical access log maintained manually. Electronic entry to hosting facility documented.

#### 3.10.5 — Control and Manage Physical Access Devices
**Status:** MET  
Key/access control to facility managed by system owner.

#### 3.10.6 — Enforce Safeguarding Measures for CUI at Alternate Work Sites
**Status:** MET  
Remote access only via VPN (AES-256-GCM). No CUI transported to alternate locations without encryption.

---

### 3.11 — RISK ASSESSMENT (RA)

#### 3.11.1 — Periodically Assess Risk
**Status:** NOT MET  
**SPRS Impact:** -3  
Formal risk assessment has not been conducted. This SSP documents the security posture; a formal risk assessment will be conducted in Q2 2026.  
**POA&M:** SecureMac-POAM-002 — Target: 2026-07-01

#### 3.11.2 — Scan for Vulnerabilities
**Status:** MET  
OpenSCAP quarterly scans. Wazuh vulnerability detection module. Weekly `dnf check-update` for available patches.

#### 3.11.3 — Remediate Vulnerabilities
**Status:** MET  
Critical patches applied within 30 days. OpenSCAP findings remediated as identified. Current status: 102/102 checks passing.

---

### 3.12 — SECURITY ASSESSMENT (CA)

#### 3.12.1 — Periodically Assess Security Controls
**Status:** MET  
OpenSCAP CUI profile scan completed 2026-04-09: 102/102 pass. Quarterly review schedule established.

#### 3.12.2 — Develop and Implement Plans of Action
**Status:** MET  
POA&M maintained (this document). Known gaps tracked with target dates.

#### 3.12.3 — Monitor Security Controls on Ongoing Basis
**Status:** MET  
Wazuh SIEM continuous monitoring. Suricata IDS continuous packet inspection. Grafana/Prometheus system health monitoring.

#### 3.12.4 — Develop, Document, and Periodically Update System Security Plans
**Status:** MET  
This document (SSP v1.0, 2026-04-10). Quarterly review scheduled.

---

### 3.13 — SYSTEM AND COMMUNICATIONS PROTECTION (SC)

#### 3.13.1 — Monitor, Control, and Protect Communications at External Boundaries
**Status:** MET  
pf firewall on Mac mini: default-deny, explicit inbound rules for web (80/443), VPN (UDP 1194), mail (25/465/587/993/995), SSH (22), ICMP echo. NAT for LAN clients.

#### 3.13.2 — Employ Architectural Designs and Implementation Principles
**Status:** MET  
Network segmentation: WAN (71.39.182.x), LAN (10.10.1.x), MGMT (10.0.0.x). VM isolated on LAN segment. VPN tunnel (10.8.0.x) separate from LAN.

#### 3.13.3 — Separate User Functionality from System Management Functionality
**Status:** MET  
Admin access via SSH only. User-facing services (webmail, web) on separate vhosts with distinct access controls. Admin interfaces (LDAP, monitor, Wazuh dashboards) LAN-restricted.

#### 3.13.4 — Prevent Unauthorized and Unintended Information Transfer
**Status:** MET  
pf rules prevent unauthorized outbound connections. SELinux policy restricts service communication paths. USBGuard prevents unauthorized data exfiltration via removable media.

#### 3.13.5 — Implement Subnetworks for Publicly Accessible System Components
**Status:** MET  
Separate WAN IPs for web (.145), VPN (.146), mail (.147). pf RDR forwards only specific ports to VM. No direct VM exposure to internet.

#### 3.13.6 — Deny Network Communications Traffic by Default
**Status:** MET  
pf: `block all` default. firewalld: default-drop zone. Explicit permit rules only.

#### 3.13.7 — Prevent Remote Devices from Simultaneously Connecting to the System
**Status:** MET  
VPN: `redirect-gateway def1` pushes all client traffic through VPN tunnel. Split-tunneling not permitted for administrative sessions.

#### 3.13.8 — Implement Cryptographic Mechanisms for CUI During Transmission
**Status:** MET  
All services use TLS 1.2+ with FIPS-approved cipher suite. SSH FIPS-compliant algorithms. VPN AES-256-GCM. Mail: STARTTLS/SMTPS.

#### 3.13.9 — Terminate Network Connections After Defined Period
**Status:** MET  
SSH: `ClientAliveInterval 300`, `ClientAliveCountMax 0`. Firewall state table timeouts configured in pf.

#### 3.13.10 — Establish and Manage Cryptographic Keys
**Status:** MET  
- TLS: Let's Encrypt (auto-renewed), stored `/etc/pki/tls/`
- VPN PKI: easy-rsa 3.2.1, RSA-4096, stored `/etc/openvpn/server/pki/`
- SSH: RSA-4096 key pair, stored `~/.ssh/diwai_rsa`
- LUKS: Passphrase stored in secure location, backed up to IronKey vault (planned)
- Cloudflare API token: `/etc/letsencrypt/cloudflare.ini` (mode 600, root only)

#### 3.13.11 — Employ FIPS-Validated Cryptography
**Status:** MET  
FIPS 140-2 enabled system-wide on Rocky Linux VM (fips=1 kernel parameter, crypto-policy=FIPS). OpenSSL 3.5.1 FIPS provider. GnuTLS 3.8.3 FIPS validated. Mac mini: M4 Secure Enclave (FIPS 140-3 equivalent hardware security).

#### 3.13.12 — Prohibit Remote Activation of Collaborative Computing Devices
**Status:** MET  
No cameras, microphones, or collaborative devices attached to server systems.

#### 3.13.13 — Control and Monitor Use of Mobile Code
**Status:** MET  
No mobile code execution on server systems. Web content served statically or through PHP-FPM with SELinux confinement.

#### 3.13.14 — Control and Monitor Use of VoIP Technologies
**Status:** MET  
No VoIP services deployed or planned.

#### 3.13.15 — Protect Authenticity of Communications Sessions
**Status:** MET  
TLS session authentication for all web/mail services. SSH session integrity via HMAC. VPN TLS-auth HMAC (`ta.key`) prevents session replay.

#### 3.13.16 — Protect CUI at Rest
**Status:** MET  
VM: LUKS2 AES-256-XTS full-disk encryption. Mac: M4 Secure Enclave hardware encryption. NAS backups: stored on encrypted volumes.

---

### 3.14 — SYSTEM AND INFORMATION INTEGRITY (SI)

#### 3.14.1 — Identify, Report, and Correct System Flaws
**Status:** MET  
Weekly `dnf check-update`. Critical patches applied within 30 days. Wazuh vulnerability module. OpenSCAP quarterly scans.

#### 3.14.2 — Provide Protection from Malicious Code at Appropriate Locations
**Status:** PARTIAL (Risk Accepted)  
See §3 — Risk Acceptance. ClamAV 1.4.3 deployed but non-functional due to FIPS/OpenSSL incompatibility. Compensating controls in place (Suricata IDS, Wazuh FIM, SELinux, USBGuard).

#### 3.14.3 — Monitor System Security Alerts
**Status:** MET  
Wazuh SIEM with real-time alerting. Suricata EVE JSON ingested into Wazuh. Grafana/Prometheus system health alerts.

#### 3.14.4 — Update Malicious Code Protection Mechanisms
**Status:** PARTIAL (Risk Accepted)  
ClamAV freshclam daemon configured for 24 checks/day. Database download blocked by FIPS/OpenSSL incompatibility (bytecode verification). Daily/main databases will auto-download when CDN cooldown expires (2026-04-11). Suricata Emerging Threats rules updated daily.

#### 3.14.5 — Perform Periodic Scans
**Status:** MET  
OpenSCAP quarterly. Wazuh continuous FIM. Suricata continuous network scan. ClamAV on-demand scanning when databases are available.

#### 3.14.6 — Monitor Organizational Systems to Detect Attacks
**Status:** MET  
Suricata 7.0.13 with 49,521 Emerging Threats rules. Wazuh analysisd with PAM/auth/rootcheck rules. auditd continuous event monitoring.

#### 3.14.7 — Identify Unauthorized Use
**Status:** MET  
Wazuh rootcheck module. auditd syscall monitoring. Suricata anomaly detection. Login banner establishes legal basis for monitoring.

---

## 3. COMPLIANCE SCAN RESULTS

### 3.1 — Rocky Linux VM: OpenSCAP Compliance Scan

**System:** services.diwai.org (Rocky Linux 9.7 FIPS VM)  
**Tool:** OpenSCAP 1.3.13 / SCAP Security Guide 0.1.80  
**Profile:** `xccdf_org.ssgproject.content_profile_cui` (NIST SP 800-171)  
**Scan Date:** 2026-04-24  
**Kernel:** 5.14.0-611.45.1.el9_7.aarch64  

| Result | Count |
|--------|-------|
| Pass | 102 |
| Fail | 0 |
| Error | 0 |
| **Status** | **FULLY COMPLIANT** |

**Report:** `~/Documents/SecureMac Project Docs/Evidence/oscap-20260424.html`  
**Evidence ID:** DIWAI-EV-SCAP-001 v2.0  
**Next scan:** July 2026 (quarterly)

---

### 3.2 — macOS Host: mSCP Compliance Scan

**System:** securemac.diwai.org (macOS Tahoe 26.4.1, M4 Pro)  
**Tool:** macOS Security Compliance Project (mSCP) — Tahoe Guidance Rev 2.0  
**Baseline:** `diwai_phase1` (custom NIST 800-171 / CMMC Level 2 profile)  
**Scan Date:** 2026-04-24 16:38 MDT  

| Result | Count |
|--------|-------|
| Pass | 127 |
| Fail | 8 |
| **Compliance Rate** | **94.1%** |

**Report:** `~/Documents/SecureMac Project Docs/Evidence/mscp-20260424.html`  
**Spreadsheet:** `~/Documents/SecureMac Project Docs/Evidence/mscp-20260424.xlsx`

**Remediation applied this session:**
- Fix script resolved 39 items (122 → 83 failures)
- 19 mSCP configuration profiles installed via System Settings → General → Device Management
- macOS application firewall enabled with stealth mode
- Bluetooth disabled (wired USB keyboard/mouse required — see deployment note below)
- Screensaver timeout and password configured

**Remaining 8 failures — disposition:**

| Rule | Count | Disposition | POA&M |
|------|-------|-------------|-------|
| `os_recovery_lock_enable` | 1 | Open — MDM required for Apple Silicon Recovery Lock | POAM-010 |
| `os_firewall_default_deny_require` | 1 | Risk Accepted — pf default-deny is compensating control | POAM-011 |
| `os_gatekeeper_enable` / `system_settings_gatekeeper_*` | 2 | Risk Accepted — Gatekeeper confirmed enabled; MDM verification gap only | POAM-012 |
| Screensaver enforcement (4 rules) | 4 | Deferred — dependent on YubiKey enforcement (POAM-009) | POAM-013 |

**Deployment note — Bluetooth:**  
Disabling Bluetooth on a rack-mounted Mac mini requires wired USB keyboard and mouse to be physically connected before applying the setting. Loss of Bluetooth with only wireless peripherals results in immediate loss of input. The Logitech USB keyboard and mouse on the Thunderbolt port expander (en6) satisfy this requirement. **VSBs replicating this reference system must ensure wired input devices are present before disabling Bluetooth.**

---

## 4. RISK ACCEPTANCE DOCUMENTATION

### 4.1 — ClamAV Antivirus FIPS Mode Incompatibility

**Risk:** ClamAV 1.4.3 cannot verify database signatures under OpenSSL 3 FIPS mode ("Can't allocate memory" — a misleading error masking a cryptographic algorithm incompatibility).

**Decision:** ACCEPT risk with compensating controls  
**Risk Level:** MEDIUM (with compensating controls: LOW)  
**SPRS Impact:** 0 (compensating controls adequately mitigate SI-3)

**Compensating Controls:**
| Control | Implementation |
|---------|---------------|
| Network IDS | Suricata 7.0.13 — 49,521 ET rules, real-time traffic inspection |
| File Integrity Monitoring | Wazuh syscheck on /etc, /bin, /sbin, /usr/bin, /usr/sbin, /boot |
| SELinux | Enforcing mode — prevents unauthorized code execution |
| USBGuard | Blocks unauthorized USB media on both Mac and VM |
| Audit Logging | auditd + Wazuh — detects anomalous process execution |
| Patch Management | Weekly updates eliminate known-vulnerable packages |

**Resolution Path:** Evaluate FIPS-compatible commercial AV in FY2026 budget cycle. Reassess if ClamAV releases a FIPS-compatible version.

**Review Date:** 2026-10-01

---

## 5. PLAN OF ACTION AND MILESTONES (POA&M)

The POA&M is maintained as a standalone document:

**`~/Documents/SecureMac Project Docs/SecureMac_POAM_v1.0.md`**

| Field | Value |
|-------|-------|
| Document | SecureMac_POAM_v1.0.md |
| Version | 1.0 |
| Date | 2026-04-24 |
| Open Items | 6 (POAM-002, 003, 004, 006, 007, 009) |
| Closed | 1 (POAM-001) |
| Risk Accepted | 1 (POAM-005) |
| Deferred | 1 (POAM-008) |
| SPRS technical deficit | -9 (3.5.3: -5, 3.11.1: -3, 3.6.3: -1) |

Refer to the POA&M document for full item detail, remediation steps, and milestone tracking.

---

## 6. SPRS SCORECARD

**Maximum Score:** 110  
**Current Score:** 101  
**Deficit:** -9 (technical gaps assessed below; training gaps additional)

| Requirement | Weight | Status | Score |
|-------------|--------|--------|-------|
| 3.5.3 | -5 | PARTIAL (POA&M-009 open) | -5 |
| 3.11.1 | -3 | NOT MET (POA&M-002 open) | -3 |
| 3.6.3 | -1 | NOT MET (POA&M-004 open) | -1 |
| All other requirements | — | MET | 0 |
| **SPRS Total** | | | **101** |

> Note: Training gaps (3.2.1/3.2.2) carry an additional -2 bringing adjusted score to **99/110** pending formal training documentation. Score path to recovery: +5 upon POA&M-009 close (3.5.3 fully MET) → 106; +3 upon formal risk assessment (3.11.1) → 109; +1 upon IR tabletop exercise (3.6.3) → **110/110**.

---

## 7. DOCUMENT CONTROL

**Classification:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)  
**Distribution:** Official Use Only — Need to Know Basis  
**Retention:** Current + 3 years  
**Next Review:** 2026-07-01 (Quarterly)  
**Local Copy:** `~/Documents/SecureMac Project Docs/System_Security_Plan_v1.0.md`  
**System State Reference:** `~/diwai/SYSTEM-STATE-2026-04-15.md`  
**NAS Copy:** `DataStore:/Cyberinabox/Secure_Mac/`  

---

**END OF SSP v1.0**

*This System Security Plan supports NIST SP 800-171 Rev 2 compliance for the SecureMac Reference System (diwai.org). SPRS score: 101/110 (adjusted 99/110 pending training documentation). POA&M-009 (MFA partial — Slot 9A regeneration + enforcement) open, target 2026-05-31.*
