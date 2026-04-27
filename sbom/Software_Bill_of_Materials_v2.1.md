# SOFTWARE BILL OF MATERIALS (SBOM) — SecureMac Reference System

**System:** SecureMac — CyberInABox Reference System #2  
**Organization:** diwai.org (Do It With AI)  
**Classification:** Controlled Unclassified Information (CUI)  
**Version:** 2.1  
**Date Generated:** 2026-04-26  
**Scope:** 2 systems (1 combined firewall/DC/mail/SIEM server + 1 macOS host)  
**Architectures:** ARM64 (Apple Silicon — both systems)  

---

## EXECUTIVE SUMMARY

### System Inventory

| Hostname | IP | Platform | Architecture | Packages | Role |
|----------|----|----------|--------------|----------|------|
| **services.diwai.org** | 10.10.1.10 | Rocky Linux 9.7 (Blue Onyx) | aarch64 | ~817 RPM | Domain Controller, Mail, VPN, IDS, SIEM, Monitoring |
| **Mac mini (host)** | 10.10.1.1 (LAN) / 71.39.182.149 (WAN) | macOS Tahoe 26.4.1 | ARM64 (M4 Pro) | macOS native + Homebrew | Firewall/Router, AI Inference host |

**Total Systems:** 2  
**Architecture:** ARM64 (Apple Silicon) throughout — no x86_64  
**Compliance Target:** NIST SP 800-171 R2 / FIPS 140-2  

### Platform Distribution

- **Rocky Linux 9.7 (aarch64):** 1 system — FIPS 140-2 mode enabled, SELinux enforcing
- **macOS Tahoe 26.4 (ARM64):** 1 system — M4 Pro hardware encryption, pf firewall

---

## PURPOSE

This Software Bill of Materials (SBOM) provides a comprehensive inventory of all software components installed on the SecureMac reference system. This SBOM supports:

- **Supply chain security assessment** per NIST 800-171 SR-2
- **Vulnerability management** and patch tracking
- **Software licensing compliance** (Rocky Linux, macOS, open source)
- **System security auditing** and configuration management (CM-8)
- **Incident response and forensics** capabilities
- **CMMC Level 2 compliance** (Component Inventory requirements)

---

## DOCUMENT CLASSIFICATION

**Classification:** CUI (Controlled Unclassified Information)  
**Distribution:** Owner/ISSO, Authorized Auditors, C3PAO Assessors  
**Retention:** Maintain current version + 3 years historical  
**Review Schedule:** Quarterly (with each SSP review)  

---

## VERSION HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-10 | D. Shannon | Initial SBOM for SecureMac Reference System. All core services operational: Apache, Postfix, Dovecot, 389-ds, OpenVPN, Suricata, Wazuh, Grafana, Prometheus, ClamAV, USBGuard. OpenSCAP 102/102 pass. Let's Encrypt auto-renewal configured. |
| 2.0 | 2026-04-23 | D. Shannon | Verified all package versions against installed state. Updates: kernel 611.41→611.45, php-fpm 8.0→8.2 (Remi), roundcubemail 1.5.14→1.5.15, grafana 12.4.2→13.0.1, python3 minor rev, node-exporter 1.11.1 (proper package name), OpenSCAP/SSG versions added. macOS updated to 26.4.1 (25E253). Added Homebrew YubiKey tools (ykman 5.9.0, yubico-piv-tool 2.7.3, libfido2 1.16.0, openssh 10.3p1) and YubiKey PIV hardware to macOS section. Auth section updated to reflect PIV smartcard. |
| 2.1 | 2026-04-26 | D. Shannon | Ollama AI inference confirmed deployed (v0.21.2 via Homebrew, Metal GPU). Models installed: codestral:latest (12 GB), mistral:latest (4.4 GB), nomic-embed-text:latest (274 MB), all-minilm:latest (45 MB). Open Web UI confirmed deployed (pip venv, /opt/local/open-webui-venv/, port 3000, since 2026-04-14). POA&M-007 closed. OpenSCAP quarterly scan updated: 102/102 pass, 2026-04-24. AI Governance section updated from planned to operational. |

---

## SYSTEM 1: services.diwai.org (Rocky Linux 9.7 Service VM)

**Platform:** Rocky Linux 9.7 (Blue Onyx)  
**Kernel:** 5.14.0-611.45.1.el9_7.aarch64  
**Architecture:** aarch64 (ARM64)  
**Hypervisor:** UTM (QEMU ARM64) on Mac mini M4 Pro  
**FIPS Mode:** Enabled (fips=1 kernel parameter, crypto-policy=FIPS)  
**SELinux:** Enforcing  
**Total Packages:** ~817 RPM  
**IP Address:** 10.10.1.10/24 (LAN)  
**Role:** Domain Controller, Mail Server, VPN Endpoint, IDS, SIEM, Web, Webmail, Monitoring  

### Disk Configuration

- **Full-disk encryption:** LUKS2 AES-256-XTS on vda3 (198.4 GB)
- **Volume manager:** LVM on LUKS
- **Partitions:** /boot/efi (EFI), /boot (XFS), / (20GB), /var (25GB, nodev), /var/log (10GB), /var/log/audit (10GB), /tmp (5GB, noexec,nosuid), /home (10GB), /opt (50GB), swap (8GB)
- **GRUB2:** Password protected

---

### Critical Security Software

#### Identity & Access Management

| Package | Version | Purpose |
|---------|---------|---------|
| **389-ds-base** | 2.7.0-12.el9_7.aarch64 | LDAP Directory Server — dc=diwai,dc=org |
| **sssd** | (system) | System Security Services Daemon |

**LDAP Structure:**
- Base DN: `dc=diwai,dc=org`
- OUs: people, groups, permissions, services
- Auth backends: Dovecot IMAP, Postfix SASL, system PAM

#### Web Services

| Package | Version | Purpose |
|---------|---------|---------|
| **httpd** | 2.4.62-7.el9_7.3.aarch64 | Apache HTTP Server |
| **mod_ssl** | 2.4.62-7.el9_7.3.aarch64 | TLS module for Apache |
| **php-fpm** | 8.2.30-1.module_php.8.2.el9.remi.aarch64 | PHP FastCGI Process Manager (Roundcube) — Remi repo |
| **roundcubemail** | 1.5.15-1.el9.noarch | Webmail interface |

**Virtual Hosts:** diwai.org, webmail.diwai.org, ldap.diwai.org (LAN), monitor.diwai.org (LAN), wazuh.diwai.org (LAN)

#### Email Services

| Package | Version | Purpose |
|---------|---------|---------|
| **postfix** | 3.5.25-1.el9.aarch64 | SMTP Mail Transfer Agent (ports 25, 465, 587) |
| **dovecot** | 2.3.16-15.el9.aarch64 | IMAP/POP3 Mail Server (port 993 IMAPS) |
| **mariadb-server** | 10.5.29-3.el9_7.aarch64 | MariaDB database (Roundcube backend) |

**Mail Auth:** SASL via Dovecot → LDAP  
**Mail Storage:** Maildir format in user home directories  

#### VPN

| Package | Version | Purpose |
|---------|---------|---------|
| **openvpn** | 2.5.11-1.el9.aarch64 | OpenVPN server (UDP 1194) |
| **easy-rsa** | 3.2.1-2.el9.noarch | RSA PKI management |

**VPN Config:** AES-256-GCM, TLS 1.2+, RSA-4096 keys, tunnel 10.8.0.0/24

#### Security & Monitoring

| Package | Version | Purpose |
|---------|---------|---------|
| **suricata** | 7.0.13-1.el9.aarch64 | Network IDS (AF_PACKET, enp0s1) |
| **wazuh-manager** | 4.14.4-1.aarch64 | SIEM — log collection, FIM, rootcheck |
| **grafana** | 13.0.1-1.aarch64 | Metrics visualization dashboard |
| **prometheus** | 3.10.0-1.el9.aarch64 | Time-series metrics collection |
| **node-exporter** | 1.11.1-1.el9.aarch64 | Host metrics for Prometheus |
| **audit** | 3.1.5-7.el9.aarch64 | Linux kernel audit subsystem |
| **usbguard** | 1.0.0-16.el9.aarch64 | USB device access control |

**Suricata Rules:** Emerging Threats ruleset (~49,521 rules)  
**Wazuh Integrations:** syslog, auditd, httpd access logs, OpenVPN, Suricata EVE JSON  

#### Antivirus

| Package | Version | Purpose |
|---------|---------|---------|
| **clamav** | 1.4.3-3.el9.aarch64 | ClamAV antivirus engine |
| **clamd** | 1.4.3-3.el9.aarch64 | ClamAV daemon |

**Status:** freshclam running; databases pending download (CDN rate limit — auto-resolves 2026-04-11); clamd enabled, starts automatically when databases present  
**Note:** Bytecode database disabled (FIPS/OpenSSL algorithm compatibility)

#### DNS

| Package | Version | Purpose |
|---------|---------|---------|
| **unbound** | 1.16.2-21.el9.aarch64 | Recursive DNS resolver (local) |

#### Certificate Management

| Package | Version | Purpose |
|---------|---------|---------|
| **certbot** | 3.1.0-1.el9.noarch | Let's Encrypt ACME client |
| **python3-certbot-dns-cloudflare** | 3.1.0-1.el9.noarch | Cloudflare DNS-01 plugin |

**Certificate:** `*.diwai.org` + `diwai.org` wildcard (Let's Encrypt R12)  
**Expiry:** 2026-07-09  
**Auto-renewal:** `certbot-renew.timer` nightly; deploys via hook, restarts all TLS services  

#### Encryption & FIPS

| Package | Version | Purpose |
|---------|---------|---------|
| **openssl** | 3.5.1-7.el9_7.aarch64 | FIPS-validated TLS/crypto library |
| **openssl-libs** | 3.5.1-7.el9_7.aarch64 | OpenSSL shared libraries |
| **gnutls** | 3.8.3-10.el9_7.aarch64 | FIPS-validated TLS library |
| **cryptsetup-libs** | 2.7.2-4.el9.aarch64 | LUKS/dm-crypt support |

#### Container Runtime

| Package | Version | Purpose |
|---------|---------|---------|
| **podman** | 5.6.0-14.el9_7.aarch64 | Container runtime (available, not in use) |

#### Development & Admin Tools

| Package | Version | Purpose |
|---------|---------|---------|
| **python3** | 3.9.25-3.el9_7.2.aarch64 | Python 3 runtime |
| **git** | (system) | Version control |

#### Compliance

| Package | Version | Purpose |
|---------|---------|---------|
| **openscap** | 1.3.13-1.el9_7.rocky.0.1.aarch64 | SCAP compliance scanner |
| **openscap-scanner** | 1.3.13-1.el9_7.rocky.0.1.aarch64 | oscap CLI tool |
| **scap-security-guide** | 0.1.80-1.el9_7.rocky.1.2.noarch | NIST 800-171 CUI content |

**Last Scan Result:** 102 pass / 0 fail / 0 errors (2026-04-24 — quarterly scan, post-PIV)  
**Profile:** `xccdf_org.ssgproject.content_profile_cui`

---

## SYSTEM 2: Mac mini Host (macOS Tahoe 26.4)

**Platform:** macOS Tahoe 26.4.1 (Build 25E253)  
**Hardware:** Apple Mac mini (M4 Pro, 2024)  
**Chip:** Apple M4 Pro — 14-core CPU, 20-core GPU, 16-core Neural Engine  
**Architecture:** ARM64 (Apple Silicon)  
**RAM:** 64 GB unified memory  
**Storage:** 1.0 TB NVMe SSD (Apple Fabric)  
**Total Packages:** macOS native  
**Role:** Network Firewall/Router, AI Inference Host  

### macOS System Software

#### Operating System

- **macOS Tahoe** 26.4.1 (Build 25E253) — Apple Unix-based OS
- **XNU Kernel** — Darwin kernel ARM64
- **System Integrity Protection (SIP)** — Enabled
- **Gatekeeper** — Enabled (code signing enforcement)

#### Security & Encryption

- **M4 Secure Enclave** — Hardware encryption, key storage
- **Secure Boot** — Boot integrity verification
- **XProtect** — Built-in malware protection
- **pf (Packet Filter)** — BSD firewall, NAT/RDR rules (config: `/etc/pf.conf`)
- **FileVault** — Full-disk encryption (APFS encryption via M4 Secure Enclave)

#### Network / Firewall

| Component | Version | Purpose |
|-----------|---------|---------|
| **pf** | macOS built-in | Stateful packet filter, NAT, port forwarding |
| **Cloudflare DNS** | — | Authoritative DNS for diwai.org zone |

**pf Rules:**
- NAT: LAN (10.10.1.0/24) → WAN (71.39.182.149)
- RDR: UDP 71.39.182.146:1194 → VM 10.10.1.10:1194 (VPN)
- Inbound allowed: TCP 22 (SSH), TCP 80/443 (.145), UDP 1194 (.146), TCP 25/465/587/993/995/4190 (.147), ICMP echo

#### USB Security

| Component | Location | Purpose |
|-----------|----------|---------|
| **usb-guard** | `/usr/local/sbin/usb-guard` | USB block/allow toggle script |
| **usb-guard-monitor** | `/usr/local/sbin/usb-guard-monitor` | LaunchDaemon polling monitor |
| **org.diwai.usb-guard** | `/Library/LaunchDaemons/` | LaunchDaemon (runs at boot) |

**State file:** `/var/lib/usb-guard/mode` (`on`/`off`)  
**Audit log:** `/var/log/usb-guard.log`

#### AI Inference

| Component | Version | Purpose |
|-----------|---------|---------|
| **Ollama** | 0.21.2 (Homebrew) | LLM inference engine — Metal GPU acceleration, localhost:11434 |
| **Open Web UI** | current (pip venv) | Web UI for Ollama — `/opt/local/open-webui-venv/`, port 3000, deployed 2026-04-14 |
| **codestral:latest** | — | Mistral AI code generation model (12 GB) |
| **mistral:latest** | — | Mistral 7B general-purpose model (4.4 GB) |
| **nomic-embed-text:latest** | — | Text embedding model (274 MB) |
| **all-minilm:latest** | — | Sentence embedding model (45 MB) |

**Status:** Operational — Ollama running as Homebrew service; Open Web UI serving on port 3000  
**Platform:** Metal Performance Shaders (MPS) on M4 Pro 20-core GPU  
**Network:** Ollama bound to 127.0.0.1:11434 (LAN-isolated); Open Web UI bound to 0.0.0.0:3000 (LAN-accessible)  
**Data isolation:** No CUI processed by AI; inference separate from compliance data stores  

#### YubiKey Hardware

| Component | Detail | Purpose |
|-----------|--------|---------|
| **YubiKey 5C Nano FIPS** | Serial: 34246645 · Firmware: 5.4.3 · Form: Nano USB-C | PIV smartcard MFA — permanently installed |
| **FIPS Validation** | FIPS 140-2 Level 1 (YubiKey 5 FIPS Series) | Hardware security key |

**Active PIV configuration:**
- Slot 9C: ECDSA P-256 cert (diwai.org Email CA) — paired to `dshannon` via `sc_auth`
- Slot 9A: Present but incorrect policies — pending regeneration

#### Homebrew Packages (YubiKey / SSH)

| Package | Version | Source | Purpose |
|---------|---------|--------|---------|
| **ykman** | 5.9.0 | Homebrew | YubiKey Manager — PIN management, device config |
| **yubico-piv-tool** | 2.7.3 | Homebrew | PIV tool — certificate operations |
| **libfido2** | 1.16.0_2 | Homebrew | FIDO2 library — dependency for Homebrew OpenSSH |
| **openssh** | 10.3p1 | Homebrew | OpenSSH compiled with libfido2 support (required for FIDO2-SK key ops) |

**Note:** macOS system OpenSSH (10.2p1/LibreSSL) does not include libfido2. Homebrew OpenSSH is required for any FIDO2-SK key generation or recovery (`ssh-keygen -K`). Current admin SSH to VM uses system or Homebrew SSH with RSA-4096 key.

#### Admin Tools

| Component | Purpose |
|-----------|---------|
| **SSH** (built-in + Homebrew 10.3p1) | Remote access to VM (`~/.ssh/diwai_rsa`); Homebrew SSH required for FIDO2-SK ops |
| **SuperDuper! 3.20-beta.8** | Bootable clone (blocked by Tahoe beta bug — deferred) |
| **Tunnelblick / OpenVPN Connect** | VPN client for `dshannon-diwai.ovpn` |

---

## CROSS-SYSTEM SECURITY CONTROLS

### Encryption

| Control | Implementation |
|---------|---------------|
| Disk encryption (VM) | LUKS2 AES-256-XTS on all CUI partitions |
| Disk encryption (Mac) | M4 Secure Enclave / APFS native |
| TLS in transit | TLS 1.2+ minimum, FIPS cipher suite |
| FIPS 140-2 (VM) | Enabled system-wide; kernel + OpenSSL + GnuTLS |

### Authentication

| Control | Implementation |
|---------|---------------|
| Centralized auth | 389 Directory Server (LDAP), dc=diwai,dc=org |
| Mail auth | Dovecot SASL → LDAP |
| Web auth | Apache + Roundcube → LDAP |
| Admin SSH (VM) | RSA-4096 key pair only; password auth disabled |
| macOS local auth | YubiKey 5C Nano FIPS PIV (Slot 9C, ECDSA P-256) via CryptoTokenKit — screen lock + sudo |
| macOS enforcement | Not yet enabled (pending Slot 9A regeneration — see POA&M-009) |
| GRUB/LUKS | Passphrase protected |

### Monitoring

| Control | Implementation |
|---------|---------------|
| SIEM | Wazuh 4.14.4 (log collection, FIM, rootcheck) |
| Network IDS | Suricata 7.0.13 (Emerging Threats rules) |
| Metrics | Grafana 13.0.1 + Prometheus 3.10.0 + node-exporter 1.11.1 |
| Audit | auditd with comprehensive rules |
| Antivirus | ClamAV 1.4.3 (databases pending) |
| USB control | USBGuard (VM) + custom daemon (Mac) |

### Network Security

| Control | Implementation |
|---------|---------------|
| Perimeter firewall | pf on macOS (NAT, RDR, default drop) |
| VM firewall | firewalld (default drop zone) |
| SSH hardening | FIPS ciphers, no root login, key-only |
| DNS | Unbound local resolver; Cloudflare authoritative |

---

## BACKUP & RECOVERY

| Asset | Backup Method | Location | Date |
|-------|--------------|----------|------|
| Rocky Linux VM | UTM bundle copy | DataStore NAS: `/home/Backup/SecureMac/diwai-services.utm` | 2026-04-10 |
| Rocky Linux VM | UTM bundle copy | Shannon_Home NAS: `/VM/SecureMac-Backups/diwai-services.utm` | 2026-04-10 |
| Config files | File copy | DataStore NAS: `/Cyberinabox/Secure_Mac/` | 2026-04-10 |
| Mac bootable clone | SuperDuper! | Deferred (Tahoe beta bug) | — |

---

## AI GOVERNANCE

### Local AI Inference

**Purpose:** Administrative assistance for VSB operators; no CUI processed by AI  
**Status:** Operational as of 2026-04-26 (Ollama v0.21.2 + Open Web UI deployed)

| Control | Implementation |
|---------|---------------|
| Model hosting | Local only — Ollama on Mac mini (no external API calls); bound to 127.0.0.1:11434 |
| Web interface | Open Web UI (port 3000) — LAN-accessible, localhost only from WAN |
| GPU acceleration | Apple M4 Pro Metal — 20-core GPU |
| Data isolation | AI inference separate from compliance data; no CUI in prompt context |
| Human oversight | All AI-assisted actions require admin confirmation |
| Models installed | codestral (12 GB), mistral (4.4 GB), nomic-embed-text (274 MB), all-minilm (45 MB) |

---

## VULNERABILITY MANAGEMENT

### Patch Management

**Rocky Linux VM:**
- Security updates via `dnf` from Rocky Linux official repositories
- Critical patches applied within 30 days
- Quarterly OpenSCAP compliance verification

**macOS Host:**
- Automatic security updates enabled
- macOS Tahoe updates via Apple Software Update
- Certbot renewal automated (nightly timer)

### Current Vulnerability Status (2026-04-23)

- OpenSCAP: **102/102 checks passed** — zero failures (quarterly scan 2026-04-24)
- All packages current from official repositories
- No known critical vulnerabilities (CVSS >7.0)
- Let's Encrypt cert: valid, auto-renews before 2026-07-09

---

## LICENSE COMPLIANCE

### Open Source Licenses

| Software | License | Notes |
|---------|---------|-------|
| Rocky Linux 9.7 | GPL, BSD, Apache 2.0 (various) | Community enterprise Linux |
| Apache httpd | Apache 2.0 | Web server |
| 389 Directory Server | GPL v3 | LDAP server |
| Postfix | IBM Public License + EPL | MTA |
| Dovecot | MIT + LGPL | IMAP/POP3 |
| Roundcubemail | GPL v3 | Webmail |
| MariaDB | GPL v2 | Database |
| OpenVPN | GPL v2 | VPN |
| Suricata | GPL v2 | IDS |
| Wazuh | GPL v2 | SIEM |
| Grafana | AGPLv3 | Dashboards |
| Prometheus | Apache 2.0 | Metrics |
| ClamAV | GPL v2 | Antivirus |
| Unbound | BSD | DNS resolver |
| USBGuard | GPL v2 | USB control |
| Certbot | Apache 2.0 | ACME client |
| OpenSSL | Apache 2.0 | Cryptography |
| OpenSCAP | LGPL | Compliance scanning |
| Ollama 0.21.2 | MIT | LLM inference engine |
| Open Web UI | MIT | Web interface for Ollama |
| macOS Tahoe | Proprietary Apple EULA | Included with hardware |

### Commercial Licenses

- **macOS Tahoe:** Included with Mac mini hardware purchase
- **Let's Encrypt wildcard cert:** Free (ISRG) — automated renewal
- All other software: Open source

### No PRC-Origin Software

All software sourced from US/European open source projects. No software of PRC origin is installed or planned. This is a hard requirement for Federal contract compliance.

---

## SUPPLY CHAIN SECURITY

### Software Sources

**Rocky Linux Packages:**
- Primary: Rocky Linux official repositories (HTTPS, GPG verified)
- EPEL: Extra Packages for Enterprise Linux (certbot, etc.)
- Wazuh: Official Wazuh repository (GPG verified)
- Grafana: Official Grafana repository (GPG verified)
- Prometheus: Official release (GPG verified)
- Integrity: SHA-256 checksums verified by dnf

**macOS Software:**
- Primary: Apple Software Update (signed by Apple)
- Third-party: Gatekeeper / notarization required
- pf rules: Local configuration, no external downloads

**DNS:**
- Cloudflare DNS API (Cloudflare, Inc., US) for diwai.org zone management

### Supply Chain Risk Mitigation

- Software obtained only from official upstream sources
- GPG signature verification mandatory (dnf)
- No software from unknown or untrusted sources
- No PRC-origin software (Federal hard requirement)
- Regular security updates from official channels only

---

## COMPLIANCE MAPPING

### NIST SP 800-171 Controls

| Control | Requirement | Implementation |
|---------|-------------|---------------|
| **CM-8** | Component inventory | This SBOM |
| **SR-2** | Supply chain risk | Verified sources, GPG checks |
| **SI-2** | Flaw remediation | dnf updates, OpenSCAP, Wazuh |
| **AC-17** | Remote access | OpenVPN AES-256-GCM, RSA-4096 |
| **AC-19** | Mobile/removable media | USBGuard (VM) + usb-guard daemon (Mac) |
| **IA-2** | Identification/Auth | 389-ds LDAP, SSH key-only |
| **SC-8** | Transmission confidentiality | TLS 1.2+, FIPS ciphers throughout |
| **SC-28** | Protection at rest | LUKS2 (VM), M4 Secure Enclave (Mac) |
| **AU-2** | Audit events | auditd + Wazuh SIEM |
| **SI-3** | Malware protection | ClamAV (pending DB), Suricata IDS |

### OpenSCAP Compliance

- **Profile:** `xccdf_org.ssgproject.content_profile_cui` (NIST 800-171)
- **Last result:** 102 pass / 0 fail / 0 errors (2026-04-09)
- **Report:** `/root/oscap-report.html` (on VM); local copy at `~/diwai/oscap-report-2.html`
- **Next scheduled:** Quarterly (by 2026-07-01)

---

## MAINTENANCE SCHEDULE

### SBOM Update Triggers

**Quarterly Reviews:**
- Scheduled review aligned with SSP updates (June 30, September 30, December 31, March 31)
- Full package inventory refresh
- Verification of new software installations

**Event-Driven Updates:**
- New service added or removed
- Major package version updates
- Platform upgrades (Rocky Linux 9.7 → 9.8, macOS updates)
- AI model additions (Ollama/Mistral deployment)
- After security incidents

---

## POINT OF CONTACT

**SBOM Owner:** Donald Shannon  
**Title:** System Administrator / Security Officer  
**Organization:** diwai.org — Do It With AI  
**Domain:** diwai.org  

**For Questions Regarding:**
- Software inventory accuracy
- Vulnerability management
- License compliance
- Supply chain security

---

## DOCUMENT CONTROL

**Classification:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)  
**Distribution:** Official Use Only — Need to Know Basis  
**Retention:** Current + 3 years  
**Next Review:** 2026-07-01  
**Local Copy:** `~/Documents/SecureMac Project Docs/Software_Bill_of_Materials.md`  
**NAS Copy:** `DataStore:/Cyberinabox/Secure_Mac/`  
**GitHub:** `The-CyberHygiene-Project/cyberhygiene-documentation`  

---

**END OF SBOM v2.1**

*This document supports NIST SP 800-171 CM-8, SR-2, and CMMC Level 2 compliance requirements for the SecureMac Reference System (diwai.org).*
