# Configuration Management Policy

**Document ID:** DIWAI-CMP-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** CUI

---

## 1. Purpose

This policy establishes diwai.org (Do It With AI) requirements for configuration management on the SecureMac Production Network (SPN). It ensures systems are configured securely, changes are controlled, and baseline configurations are maintained to protect Controlled Unclassified Information (CUI) in compliance with NIST SP 800-171 Rev 2 (CM-1 through CM-11) and CMMC Level 2.

---

## 2. Scope

This policy applies to:

- **All SPN Systems:**
  - Mac mini M4 Pro running macOS Tahoe — gateway appliance (securemac.diwai.org)
    - pf firewall (built-in macOS)
    - USB Guard daemon (`/usr/local/sbin/usb-guard-monitor`)
    - FileVault full-disk encryption
  - Rocky Linux 9.7 VM — diwai-services UTM (services.diwai.org, 10.10.1.10)
    - 389 Directory Server (LDAP identity)
    - Postfix / Dovecot (email)
    - Apache HTTPD (web / Roundcube)
    - OpenVPN (remote access)
    - Wazuh agent
    - ClamAV
    - LUKS AES-256 encryption
    - FIPS 140-2 mode
    - SELinux enforcing

- **Configuration Items:** Operating systems, applications, network configuration, security tools, pf rules, baseline configurations

- **All Personnel:** Donald E. Shannon (System Owner/ISSO) and any contractors with administrative access

---

## 3. Policy Statements

### 3.1 Baseline Configurations (CM-2, CM-6)

**diwai.org shall:**

1. **Establish Security Baselines (CM-2):**
   - Maintain documented baseline configurations for each system type
   - Baselines based on industry standards:
     - **Rocky Linux 9.7 VM:** NIST 800-171 CUI profile (SCAP/OpenSCAP)
     - **macOS Tahoe:** CIS Apple macOS Benchmark (applicable controls)
   - Document deviations from baseline with security justification

2. **Configuration Settings (CM-6):**
   - FIPS 140-2 cryptographic mode enabled (Rocky Linux VM)
   - SELinux enforcing mode (Rocky Linux VM)
   - LUKS AES-256-XTS full-disk encryption (Rocky Linux VM)
   - FileVault with M4 Secure Enclave (macOS host)
   - USB Guard daemon active when in "on" mode
   - Automatic updates disabled (manual control for stability)
   - Unnecessary services disabled

3. **Baseline Documentation Location:**
   - `~/Documents/SecureMac Project Docs/` on macOS host
   - Copies archived on DataStore NAS: `/Volumes/Cyberinabox/Secure_Mac/`
   - VM configuration backed up as UTM bundle: `diwai-services.utm`

### 3.2 Configuration Change Control (CM-3)

**Change Management Process:**

1. **Change Request Requirements:**
   - All configuration changes require documented justification
   - Changes classified by risk level:
     - **Low:** Application updates, user account changes
     - **Medium:** Service configuration changes, new software installation
     - **High:** OS upgrades, security control modifications, pf rule changes

2. **Change Approval:**
   - **Low risk:** ISSO review (Donald E. Shannon)
   - **Medium risk:** ISSO review and documented approval
   - **High risk:** System Owner approval + testing on VM snapshot before applying

3. **Change Testing:**
   - **High-risk changes:** VM snapshot taken before change; tested and rolled back if needed
   - **Medium-risk changes:** Applied during maintenance window with rollback plan
   - **Emergency changes:** Document post-implementation within 24 hours

4. **Change Documentation:**
   - Change log maintained in `~/Documents/SecureMac Project Docs/Change_Log.md`
   - Include: Date, change description, approver, outcome, rollback procedure
   - POA&M updated if change addresses security finding

5. **Prohibited Changes:**
   - Disabling FIPS mode
   - Disabling SELinux
   - Disabling auditd
   - Removing LUKS or FileVault encryption
   - Disabling USB Guard without ISSO authorization
   - Installing unauthorized software
   - Modifying pf rules without change documentation

### 3.3 Security Impact Analysis (CM-4)

**Before implementing changes, analyze:**

1. Impact on security controls (weakening vs. strengthening)
2. Effect on CUI confidentiality, integrity, availability
3. Compatibility with FIPS 140-2 and NIST 800-171 requirements
4. Potential for introducing vulnerabilities
5. Dependencies on other system components

**High-impact changes require:**
- Written security impact analysis (filed in Change_Log.md)
- VM snapshot prior to implementation
- Post-implementation validation (OpenSCAP re-scan where applicable)

### 3.4 Access Restrictions for Change (CM-5)

**Physical Access Controls:**
- Mac mini secured in dedicated home office space
- Physical access limited to Donald E. Shannon
- Physical access log maintained for any external party access

**Logical Access Controls:**
- Administrative access requires SSH key authentication
- sudo elevation for privileged commands (logged via auditd)
- Root account disabled for remote SSH login
- LDAP admin credentials stored in KeePass vault only
- MFA for all administrative access — target 2026-07-01 (POA&M-001)

**Change Implementation Windows:**
- Planned changes: Tuesday/Thursday 1800-2000 MDT
- Emergency changes: Any time with immediate documentation

### 3.5 Configuration Settings (CM-6)

**Mandatory Security Settings:**

| Configuration Item | Required Setting | Verification |
|--------------------|------------------|--------------|
| FIPS Mode (Rocky Linux) | Enabled | `fips-mode-setup --check` |
| SELinux | Enforcing | `getenforce` |
| LUKS Encryption (VM) | AES-256-XTS | `cryptsetup status` |
| FileVault (macOS) | Enabled | `fdesetup status` |
| Firewall (macOS pf) | Enabled | `sudo pfctl -si` |
| Firewall (Rocky Linux) | Enabled | `sudo firewall-cmd --state` |
| auditd | Running, CUI profile | `systemctl status auditd` |
| SSH | Key-based only, no root login | `/etc/ssh/sshd_config` |
| Password Policy | 14-char min, 90-day expiry | 389-DS policy |
| Session Lock (macOS) | 15-minute timeout | System Preferences |
| USB Guard | On during production | `/var/lib/usb-guard/mode` |

### 3.6 Least Functionality (CM-7)

**diwai.org shall:**

1. **Disable Unnecessary Services (Rocky Linux VM):**
   - Only active services: sshd, 389-ds, postfix, dovecot, httpd, openvpn, wazuh-agent, clamd, freshclam, auditd, chronyd, firewalld
   - No graphical desktop environment
   - No development tools in production

2. **macOS Host (Minimal Service Profile):**
   - pf firewall (system)
   - SSH daemon (remote admin only)
   - UTM hypervisor (VM hosting)
   - USB Guard daemon
   - No unnecessary apps running on host

3. **Prohibited Software:**
   - Peer-to-peer file sharing applications
   - Unauthorized remote access tools
   - Games or entertainment software on production systems
   - Unapproved encryption software

### 3.7 Component Inventory (CM-8)

**System Inventory maintained in SBOM v1.0:**
- Location: `~/Documents/SecureMac Project Docs/Software_Bill_of_Materials.md`
- DataStore copy: `/Volumes/Cyberinabox/Secure_Mac/Software_Bill_of_Materials.md`
- Updated quarterly or upon major changes

**Inventory includes:**
- Hardware: Mac mini M4 Pro (serial, acquisition date)
- OS: macOS Tahoe, Rocky Linux 9.7
- All installed packages (via `rpm -qa` on VM, `brew list` on macOS)
- Security software versions (Wazuh, ClamAV, OpenSCAP, OpenVPN, certbot)
- Certificate details (Let's Encrypt wildcard, expiry 2026-07-09)

### 3.8 Configuration Management Plan (CM-9)

- This policy serves as the Configuration Management Plan
- System Security Plan (SSP v1.0) documents baseline configurations
- VM configuration tracked via UTM bundle backups (versioned by date)
- Significant config changes documented in Change_Log.md

### 3.9 Software Usage Restrictions (CM-10)

1. **Licensed Software Only:**
   - All software properly licensed (open source with OSI-approved license or commercial license)

2. **Package Sources:**
   - Rocky Linux: Official Rocky Linux 9 repositories (BaseOS, AppStream, EPEL)
   - macOS: App Store, official vendor downloads with verified signatures
   - Package signatures verified before installation

3. **Software Installation:**
   - Rocky Linux VM: `dnf install` from enabled repos only
   - macOS: Homebrew (formulae from homebrew-core only) or official downloads
   - Non-standard packages require ISSO review

### 3.10 User-Installed Software (CM-11)

1. **Rocky Linux VM:**
   - No user-installed software without ISSO approval
   - sudo access limited to dshannon (authorized admin)
   - Wazuh FIM detects unauthorized package changes

2. **macOS Host:**
   - Software installation via Homebrew requires ISSO review for new tools
   - No unauthorized browser extensions or plugins

---

## 4. Roles and Responsibilities

### 4.1 System Owner / ISSO (Donald E. Shannon)

- Define and maintain security baseline configurations
- Review and approve all configuration changes
- Conduct security impact analysis for medium/high changes
- Maintain configuration management documentation
- Generate quarterly software inventory reports

---

## 5. Implementation Details

### 5.1 Baseline Configuration Files

**Rocky Linux VM (`services.diwai.org`):**
```
/etc/fips-mode-setup.conf          # FIPS mode configuration
/etc/selinux/config                # SELinux configuration
/etc/ssh/sshd_config               # SSH hardening
/etc/ssh/sshd_config.d/60-mfa.conf # MFA (when deployed)
/etc/audit/rules.d/               # Audit configuration (CUI profile)
/etc/firewalld/                   # Firewall rules
/etc/dirsrv/slapd-DIWAI/         # 389-DS configuration
/etc/postfix/main.cf              # Postfix configuration
/etc/letsencrypt/                 # certbot cert management
```

**macOS Host (securemac.diwai.org):**
```
/etc/pf.conf                      # pf firewall rules
/usr/local/sbin/usb-guard         # USB Guard toggle script
/usr/local/sbin/usb-guard-monitor # USB Guard monitor daemon
/Library/LaunchDaemons/org.diwai.usb-guard.plist
/var/lib/usb-guard/mode           # USB Guard state file
```

### 5.2 Configuration Compliance Verification

**Monthly Compliance Checks:**

1. **OpenSCAP Scans (Rocky Linux VM):**
   ```bash
   sudo oscap xccdf eval --profile \
     xccdf_org.ssgproject.content_profile_cui \
     --results-arf /root/oscap-$(date +%Y%m%d).xml \
     --report /root/oscap-$(date +%Y%m%d).html \
     /usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml
   ```

2. **Manual Verification:**
   ```bash
   fips-mode-setup --check       # FIPS mode
   getenforce                    # SELinux mode
   sudo firewall-cmd --state     # Rocky Linux firewall
   sudo pfctl -si | head -5      # macOS pf status
   fdesetup status               # FileVault status
   cat /var/lib/usb-guard/mode   # USB Guard mode
   ```

### 5.3 Change Management Log Format

**Required Fields (Change_Log.md entry):**
```
Date: YYYY-MM-DD HH:MM:SS MDT
Change ID: CM-YYYY-NNN
System(s): securemac.diwai.org | services.diwai.org
Risk Level: Low / Medium / High
Description: <detailed change description>
Justification: <business or security need>
Approved By: Donald E. Shannon, ISSO
Implemented By: Donald E. Shannon
Testing Performed: <test description and results>
Rollback Procedure: <steps to reverse change>
Outcome: Success / Failed / Rolled Back
Post-Implementation Validation: <verification results>
```

---

## 6. Compliance Mapping

| NIST SP 800-171 Control | Implementation |
|-------------------------|----------------|
| **CM-1** Policy and Procedures | This document |
| **CM-2** Baseline Configuration | Section 3.1 |
| **CM-3** Configuration Change Control | Section 3.2 |
| **CM-4** Security Impact Analysis | Section 3.3 |
| **CM-5** Access Restrictions for Change | Section 3.4 |
| **CM-6** Configuration Settings | Section 3.5 |
| **CM-7** Least Functionality | Section 3.6 |
| **CM-8** Information System Component Inventory | Section 3.7 |
| **CM-9** Configuration Management Plan | Section 3.8 |
| **CM-10** Software Usage Restrictions | Section 3.9 |
| **CM-11** User-Installed Software | Section 3.10 |

---

## 7. Policy Review and Updates

- **Review Frequency:** Annually or upon significant infrastructure changes
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
