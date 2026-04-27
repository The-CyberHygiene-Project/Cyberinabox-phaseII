# Configuration Management Policy

**Policy Number:** TCC-CMP-001
**Version:** 2.0 Rev 3 DRAFT (Updated for NIST SP 800-171 Rev 3)
**Effective Date:** [TBD - Target: Phase 2 completion]
**Last Reviewed:** March 18, 2026
**Policy Owner:** System Owner (sysadmin)
**Approval Authority:** System Owner (sysadmin)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | [Original] | Initial policy (NIST 800-171 Rev 2) |
| 2.0 Rev 3 DRAFT | March 18, 2026 | Updated for Rev 3: Added baseline selection (PL-10), configuration baseline document requirement, updated for 100% OpenSCAP compliance achievement, expanded determination statements |

---

## 1. PURPOSE

This policy establishes requirements for configuration management within the CyberHygiene Production Network (CPN). This policy satisfies the Configuration Management (CM) control family requirements in NIST SP 800-171 Revision 3 (controls 3.4.1 through 3.4.11).

**Rev 3 Updates:**
- Added Configuration Baseline Selection requirements (cross-references PL-10 from Planning family)
- Updated for 100% OpenSCAP compliance achievement (104/104 rules passing on all 4 systems)
- Added determination statement coverage (48 statements vs. 36 in Rev 2)
- Enhanced change control documentation requirements

---

## 2. SCOPE

This policy applies to:
- All systems processing CUI (dc1, workstation1, workstation2, workstation3)
- All configuration items: hardware, software, firmware, documentation
- Configuration baseline (SCAP Security Guide - CUI profile)
- Configuration changes (system updates, configuration modifications, software installations)

---

## 3. POLICY STATEMENTS

### 3.1 Baseline Configuration — NIST 3.4.1 (CM-2), 3.12.10 (PL-10)

**3.1.1 Configuration Baseline Selection**

CyberHygiene has selected the following configuration baseline:

**Primary Baseline:** SCAP Security Guide (SSG) — CUI Profile for Rocky Linux 9

**Baseline Details:**
- **Publisher:** ComplianceAsCode Project (NIST-certified content provider)
- **Profile ID:** `xccdf_org.ssgproject.content_profile_cui`
- **Rule Count:** 104 automated rules
- **Target:** NIST SP 800-171 Rev 2/Rev 3 CUI protection
- **Validation:** OpenSCAP scanner

**Baseline Selection Justification:**
- Specifically designed for NIST 800-171 CUI protection requirements
- Maps directly to NIST 800-171 controls (automated validation)
- Maintained and updated by security community for new threats
- Supports automated compliance scanning (weekly validation)
- Industry-standard baseline for RHEL-derivative systems

**Baseline Documentation:** `/home/sysadmin/CyberSecurity/Rev3/Evidence/Configuration_Baseline_Document_v1.0.md` (to be created Phase 3)

**3.1.2 Baseline Implementation Status**

**Achievement:** ✅ **100% OpenSCAP Compliance** on all 4 CPN systems

| System | OpenSCAP Score | Last Scan | Status |
|--------|---------------|-----------|--------|
| **dc1** | 104/104 (100%) | Weekly (Sunday 2:00 AM) | ✅ PASS |
| **workstation1** | 104/104 (100%) | Weekly (Sunday 2:05 AM) | ✅ PASS |
| **workstation2** | 104/104 (100%) | Weekly (Sunday 2:10 AM) | ✅ PASS |
| **workstation3** | 104/104 (100%) | Weekly (Sunday 2:15 AM) | ✅ PASS |

**Dashboard:** https://dc1.example.local/dashboard/openscap-dashboard.html

**3.1.3 Baseline Management**

Configuration baseline shall be:

a) **Documented:**
   - Configuration Baseline Document (Phase 3 deliverable)
   - OpenSCAP profile specification (SCAP Security Guide documentation)
   - System-specific configuration notes (deviations, if any)

b) **Reviewed and Updated:**
   - **Annually:** System Owner reviews baseline adequacy (April each year)
   - **Upon SCAP updates:** When SCAP Security Guide releases new CUI profile version
   - **Upon system changes:** When new software/services added requiring baseline updates

c) **Validated:**
   - **Weekly:** Automated OpenSCAP scans (every Sunday)
   - **Continuously:** Wazuh File Integrity Monitoring detects configuration changes
   - **Pass Criteria:** 100% compliance (104/104 rules) required

**3.1.4 Baseline Deviations**

Any deviations from the baseline must be:
- **Documented:** Deviation justification, technical/operational reason
- **Approved:** System Owner approval required
- **Risk Assessed:** Evaluate security impact of deviation
- **Tracked:** Document in Configuration Baseline Document or POA&M
- **Re-evaluated:** Review deviation necessity annually

**Current Status:** ✅ **Zero baseline deviations** (100% compliance, no exceptions needed)

---

### 3.2 Configuration Change Control — NIST 3.4.2 (CM-3)

**3.2.1 Change Control Process**

All configuration changes shall follow this process:

a) **Change Request:**
   - Identify configuration change needed (e.g., install new package, modify firewall rule)
   - Document change purpose, justification, affected systems

b) **Security Impact Analysis:**
   - Evaluate security impact (see Section 3.3)
   - Determine if change affects CUI protection
   - Identify risks introduced by change

c) **Change Approval:**
   - **Low-risk changes:** Administrator approval (self-approval for solopreneur)
   - **Medium-risk changes:** System Owner approval
   - **High-risk changes:** System Owner approval + testing in lab environment

d) **Change Implementation:**
   - Implement change on target system(s)
   - Document implementation date, who performed change
   - Retain rollback capability (previous configs saved)

e) **Change Validation:**
   - Verify change implemented correctly
   - Run OpenSCAP scan to ensure baseline compliance maintained
   - Test affected functionality

f) **Change Documentation:**
   - Update Configuration Baseline Document (if baseline affected)
   - Update SBOM (if software added/removed)
   - Log change in change management log

**3.2.2 Change Management Log**

Configuration changes are logged:
- **Location:** Git repository for configuration files (`/etc/` tracked in Git)
- **Format:** Git commit messages document changes
- **Content:** Date, administrator, change description, justification
- **Retention:** Indefinite (Git history preserved)

**Example Git Workflow:**
```bash
cd /etc
git add sshd/sshd_config
git commit -m "Update SSH configuration: Enable MFA (TOTP + SSH key)
Justification: NIST 3.5.3 multi-factor authentication requirement
Date: 2026-02-21, By: sysadmin"
git push origin main
```

**3.2.3 Emergency Changes**

For emergency changes (security incidents, critical vulnerabilities):
- Implement change immediately (no delay for approval)
- Document change as soon as possible after implementation
- Conduct post-implementation review within 24 hours
- Retrospective approval by System Owner

---

### 3.3 Configuration Change Security Impact Analysis — NIST 3.4.3 (CM-4)

**3.3.1 Impact Analysis Criteria**

Before implementing configuration changes, assess security impact:

**Low-Risk Changes (minimal security impact):**
- Documentation updates
- Non-security software package updates (applications)
- Adding log entries, monitoring rules
- Non-security configuration tweaks (performance tuning)

**Medium-Risk Changes (moderate security impact):**
- Software installation/removal (non-critical packages)
- Configuration changes affecting non-CUI systems
- Network configuration changes (IP addresses, routing)
- Firewall rule additions (allowing new traffic)

**High-Risk Changes (significant security impact):**
- Security software changes (firewall, SELinux, auditd, Wazuh)
- Kernel updates (potential boot failure, driver issues)
- Authentication/authorization changes (PAM, FreeIPA, MFA)
- Encryption changes (LUKS, TLS, SSH)
- Firewall rule removals (opening previously blocked ports)
- Changes affecting CUI protection

**3.3.2 Impact Analysis Questions**

For each change, answer:
1. **Confidentiality:** Could change allow unauthorized CUI access?
2. **Integrity:** Could change allow unauthorized CUI modification?
3. **Availability:** Could change disrupt system availability?
4. **Compliance:** Does change affect NIST 800-171 compliance (OpenSCAP score)?
5. **Reversibility:** Can change be easily rolled back if problems occur?

**3.3.3 Impact Analysis Documentation**

Document impact analysis:
- For **low-risk:** Brief justification in change log (Git commit message)
- For **medium-risk:** Impact analysis in change request (email to System Owner)
- For **high-risk:** Formal impact analysis document, approval signature

**Example Impact Analysis (Medium-Risk):**
```
Change: Install Postfix mail server
Impact Analysis:
- Confidentiality: Medium - mail server could relay sensitive data if misconfigured
- Integrity: Low - mail server does not process CUI directly
- Availability: Low - mail server failure does not affect CUI systems
- Compliance: Low - mail server not in OpenSCAP baseline (manual config needed)
- Reversibility: High - can uninstall if issues arise
Overall Risk: MEDIUM
Mitigation: Configure Postfix with TLS-only, restrict relay, monitor with Wazuh
Approval: System Owner (sysadmin) - Approved 2026-03-20
```

---

### 3.4 Security Functionality Verification — NIST 3.4.4 (CM-6)

**3.4.1 Security Function Verification**

Security functionality shall be verified:

a) **Post-Installation:**
   - After new system deployment
   - Run OpenSCAP scan within 24 hours of deployment
   - Verify 100% baseline compliance

b) **Post-Change:**
   - After configuration changes
   - Run OpenSCAP scan within 24 hours of change
   - Verify compliance not degraded (still 100%)

c) **Weekly Automated:**
   - OpenSCAP scans every Sunday at 2:00 AM (via cron)
   - Wazuh ingests scan results
   - Email alert if any rules fail

d) **On-Demand:**
   - Administrator can trigger scan anytime: `oscap xccdf eval ...`
   - Used for troubleshooting, pre-assessment validation

**3.4.2 Verification Procedures**

**OpenSCAP Scan Execution:**
```bash
oscap xccdf eval \
  --profile cui \
  --results /var/www/internal-dashboards/openscap/$(hostname)-scan.xml \
  --report /var/www/internal-dashboards/openscap/$(hostname)-report.html \
  /usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml
```

**Pass Criteria:**
- **Score:** 104/104 rules passing (100%)
- **No failures:** Zero "fail" results
- **No errors:** Zero "error" results (rule execution failures)

**If Scan Fails:**
1. Investigate failed rule(s)
2. Remediate configuration issue
3. Re-run scan
4. Document remediation in change log

---

### 3.5 Access Restrictions for Change — NIST 3.4.5 (CM-5)

**3.5.1 Change Authorization**

Configuration changes are restricted to authorized personnel:

a) **Physical Access:**
   - Server room access restricted to System Owner (sysadmin)
   - Workstation physical access restricted to authorized users

b) **Logical Access:**
   - Root access required for most configuration changes
   - Root access via sudo (requires MFA: SSH key + TOTP)
   - Service accounts cannot sudo (no privilege escalation)

c) **Configuration File Protection:**
   - `/etc/` owned by root:root, permissions 0644 (read-only for non-root)
   - `/etc/ssh/sshd_config`, `/etc/audit/auditd.conf`: permissions 0600 (root-only)
   - SELinux enforces mandatory access control (prevents unauthorized changes even by root)

**3.5.2 Change Audit Trail**

All configuration changes are audited:
- **Git:** Configuration files tracked in Git (commit history = audit trail)
- **auditd:** auditd logs file modifications in `/etc/`, `/usr/bin/`, `/usr/sbin/`
- **Wazuh FIM:** File Integrity Monitoring alerts on unexpected changes
- **sudo logs:** All sudo usage logged (privilege escalation for changes)

**Audit Rules for Configuration Changes:**
```bash
-w /etc/ -p wa -k config_changes
-w /usr/bin/ -p wa -k system_binaries
-w /usr/sbin/ -p wa -k system_binaries
```

---

### 3.6 Least Functionality — NIST 3.4.6 (CM-7)

**3.6.1 Least Functionality Principle**

CPN systems are configured with only necessary functionality:

a) **Minimal Package Installation:**
   - Only required packages installed (no unnecessary software)
   - "Minimal Install" Rocky Linux option used during deployment
   - Periodic package review (remove unused packages)

b) **Disabled Services:**
   - Unnecessary services disabled: `systemctl disable <service>`
   - OpenSCAP enforces service disablement (e.g., Avahi, Bluetooth, rsh)

c) **Disabled Ports/Protocols:**
   - Only required ports open (SSH 22, HTTPS 443, Wazuh 1514/1515)
   - Unused ports blocked by firewall (default-deny ruleset)

d) **Disabled Kernel Modules:**
   - Unused kernel modules blacklisted (e.g., USB storage, Firewire)
   - OpenSCAP enforces module blacklisting

**3.6.2 Functionality Review**

System functionality shall be reviewed:
- **Frequency:** Annually (during baseline review)
- **Process:**
  1. List installed packages: `rpm -qa | wc -l` (current: ~1,400 packages)
  2. Identify packages not used in last 12 months
  3. Evaluate necessity (required for operations, dependencies, security?)
  4. Remove unnecessary packages: `dnf remove <package>`
  5. Update SBOM

---

### 3.7 Nonessential Programs and Functions — NIST 3.4.7 (CM-7)

**3.7.1 Prohibited Programs**

The following programs/functions are **prohibited** on CPN systems:

a) **Games and Entertainment:**
   - ❌ Games packages
   - ❌ Media players (unless required for operations)

b) **Unapproved Network Services:**
   - ❌ Telnet server (cleartext protocol)
   - ❌ FTP server (cleartext protocol)
   - ❌ Sendmail (use Postfix if mail needed)
   - ❌ rsh/rlogin (insecure remote access)

c) **Insecure Protocols:**
   - ❌ HTTP (use HTTPS)
   - ❌ Unencrypted SMTP (use TLS)
   - ❌ Unencrypted LDAP (use LDAPS)

**3.7.2 Allowed Services (Current)**

Only the following network services are authorized:

| Service | Port | Purpose | Systems |
|---------|------|---------|---------|
| **SSH** | 22 | Remote administration (MFA) | All 4 systems |
| **HTTPS** | 443 | Web UI (FreeIPA, Wazuh, dashboards) | dc1 |
| **Kerberos** | 88 | Authentication | dc1 (FreeIPA) |
| **LDAP/LDAPS** | 389/636 | Directory services | dc1 (FreeIPA) |
| **Wazuh Agent** | 1514/1515 | SIEM logging | All 4 systems (agents → dc1 manager) |
| **NTP** | 123 | Time synchronization | All 4 systems (client) |
| **DNS** | 53 | Name resolution | dc1 (if DNS server role active) |

**Service Authorization:** All other services prohibited unless approved by System Owner.

---

### 3.8 Application Whitelisting — NIST 3.4.8 (CM-7(2))

**3.8.1 Application Control Strategy**

CyberHygiene employs the following application control mechanisms:

a) **Execution Prevention (Partial):**
   - **Home directories:** `noexec` mount option prevents execution from `/home/` (if configured)
   - **Temporary directories:** `/tmp` and `/var/tmp` with `noexec` option (prevents running scripts from /tmp)
   - **Policy Enforcement:** SELinux prevents unauthorized program execution

b) **Application Inventory (SBOM):**
   - All installed applications tracked in SBOM v2.4 (5,626 packages)
   - Only packages from trusted repositories (Rocky Linux, EPEL) allowed
   - Package installation logged (auditd, Wazuh)

c) **Future Enhancement: fapolicyd**
   - **fapolicyd** (File Access Policy Daemon) provides application whitelisting
   - **Status:** Not yet deployed (complexity for solopreneur environment)
   - **Plan:** Evaluate fapolicyd deployment during Phase 3 technical work

**3.8.2 Current Status**

**Application Control Status:** ⚠️ **PARTIAL IMPLEMENTATION**

- ✅ Trusted repository enforcement (only Rocky/EPEL packages)
- ✅ SELinux mandatory access control (limits unauthorized execution)
- ✅ Comprehensive application inventory (SBOM)
- ⏸️ Full application whitelisting (fapolicyd) not yet deployed

**Gap Justification:**
- Solopreneur environment with single trusted administrator
- Compensating controls: comprehensive audit logging, SIEM monitoring, SBOM tracking
- Risk level: LOW (single user, strong access controls, monitoring)

**POA&M:** Document application whitelisting as partial implementation (acceptable with compensating controls)

---

### 3.9 User-Installed Software Restrictions — NIST 3.4.9 (CM-11)

**3.9.1 User Software Installation Restrictions**

Non-privileged users cannot install software:

a) **Package Installation Restricted:**
   - `dnf`, `rpm` require root privileges
   - Users cannot run: `dnf install <package>` (permission denied)
   - Users cannot run: `rpm -i <package>` (permission denied)

b) **Sudo Restrictions:**
   - Only authorized administrators (sysadmin) can sudo
   - Service accounts cannot sudo
   - `/etc/sudoers.d/sysadmin-admin`: `sysadmin ALL=(ALL) NOPASSWD: ALL`

c) **Local Compilation Restrictions:**
   - Development tools (gcc, make) not installed on workstations (only on development systems if needed)
   - Users can compile code but cannot install to system directories (permission denied)

**3.9.2 Exception Process**

If user needs software installed:
1. User submits request to System Owner
2. System Owner evaluates security risk (see Section 3.3)
3. If approved, administrator installs software
4. Software added to SBOM

---

### 3.10 Software Usage Restrictions — NIST 3.4.10 (CM-10)

**3.10.1 Software Licensing Compliance**

CyberHygiene shall use software in compliance with licensing:

a) **Open Source Software:**
   - Rocky Linux: Open source (BSD-like license)
   - FreeIPA: Open source (GPL)
   - Wazuh: Open source (GPL v2)
   - Apache: Open source (Apache License 2.0)
   - **Compliance:** Use freely, no license fees, comply with license terms (attribution, source availability)

b) **Commercial Software:**
   - SSL.com: Paid TLS certificates (annual subscription)
   - **Compliance:** Renew certificates before expiration, pay subscription

c) **Prohibited Software:**
   - ❌ Pirated software
   - ❌ Software without valid licenses
   - ❌ Trial software beyond trial period

**3.10.2 License Tracking**

Software licenses tracked:
- **Location:** SBOM v2.4 includes license information
- **Commercial licenses:** Contract/invoice records in `/home/sysadmin/CyberSecurity/Current/Evidence/Acquisition_Records/`

---

### 3.11 Installed Software and Firmware Verification — NIST 3.4.11 (CM-11)

**3.11.1 Software Integrity Verification**

All installed software shall be verified for integrity:

a) **RPM Package Signature Verification:**
   - All packages verified with GPG signatures before installation
   - `dnf` automatically verifies signatures (`gpgcheck=1` in repo configs)
   - Manual verification: `rpm --checksig <package>`

b) **Installed Package Verification:**
   - Verify integrity of installed packages: `rpm -Va` (compare installed files to package manifest)
   - Detects modified files (configuration changes vs. unauthorized tampering)
   - Run monthly via cron or on-demand

c) **File Integrity Monitoring (Wazuh FIM):**
   - Monitors critical system files and binaries
   - Alerts on unexpected changes
   - Real-time detection of tampering

**3.11.2 Firmware Verification**

Firmware integrity is verified:

a) **UEFI Secure Boot:**
   - Enabled on all systems (if hardware supports)
   - Only signed bootloaders and kernels can boot
   - Prevents rootkit/bootkit malware

b) **Firmware Updates:**
   - Firmware updates obtained from trusted vendor sources (Dell, HP)
   - Verify firmware signatures before applying (vendor-provided tools)

c) **TPM (Trusted Platform Module):**
   - If available, TPM provides hardware-based integrity verification
   - Measured boot: BIOS/UEFI measurements stored in TPM

---

## 4. ROLES AND [REDACTED_TOTP_SECRET]

### 4.1 System Owner (sysadmin)

- Approve configuration management policy
- Approve configuration baseline
- Approve high-risk configuration changes
- Conduct annual baseline and functionality reviews
- Approve baseline deviations

### 4.2 Administrator (sysadmin)

- Implement configuration baseline (OpenSCAP CUI profile)
- Perform configuration changes per change control process
- Run OpenSCAP scans weekly (automated)
- Investigate and remediate OpenSCAP failures
- Maintain configuration documentation (Git, SBOM, Baseline Document)
- Verify software/firmware integrity

### 4.3 Users (currently: sysadmin only)

- Comply with software usage restrictions
- Do not install unauthorized software
- Report unauthorized changes or suspicious system behavior

---

## 5. PROCEDURES

### 5.1 OpenSCAP Baseline Scan Procedure

**Frequency:** Weekly (automated via cron, Sunday 2:00 AM)

**Manual Execution:**
```bash
oscap xccdf eval \
  --profile cui \
  --results /var/www/internal-dashboards/openscap/$(hostname)-scan-$(date +%Y%m%d).xml \
  --report /var/www/internal-dashboards/openscap/$(hostname)-report-$(date +%Y%m%d).html \
  /usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml
```

**Automated Collection Script:** `/home/sysadmin/scripts/collect_openscap_results.sh`
- Runs weekly on dc1
- SSHes to each workstation (workstation1, workstation2, workstation3)
- Triggers OpenSCAP scan
- Collects results to central dashboard

**Review Results:**
- Navigate to: https://dc1.example.local/dashboard/openscap-dashboard.html
- Verify all systems show 100% compliance
- Investigate any failures

---

### 5.2 Configuration Change Implementation Procedure

**Steps:**

1. **Document Change Request:**
   - What: Describe configuration change
   - Why: Business/security justification
   - Systems: Which systems affected
   - Risk: Low/Medium/High (Section 3.3)

2. **Conduct Security Impact Analysis:**
   - Answer 5 impact questions (Section 3.3.2)
   - Document mitigation strategies

3. **Obtain Approval:**
   - Low-risk: Self-approval (document in change log)
   - Medium/High-risk: Email System Owner for approval

4. **Backup Current Configuration:**
   ```bash
   cp /etc/configfile /etc/configfile.bak.$(date +%Y%m%d)
   ```
   - OR commit to Git: `cd /etc && git commit -am "Pre-change backup"`

5. **Implement Change:**
   - Make configuration change
   - Restart affected services if needed

6. **Test and Validate:**
   - Test affected functionality
   - Run OpenSCAP scan: Verify 100% compliance maintained

7. **Document Change:**
   - Git commit: `cd /etc && git add <file> && git commit -m "Change description with justification"`
   - Update SBOM if software changed
   - Update Baseline Document if baseline affected

8. **Rollback if Needed:**
   - If change causes issues: `cp /etc/configfile.bak.YYYYMMDD /etc/configfile`
   - OR: `cd /etc && git revert <commit-hash>`

---

## 6. COMPLIANCE

This policy supports compliance with:
- NIST SP 800-171 Rev 3 Configuration Management (CM) family:
  - 3.4.1 (CM-2): Baseline Configuration
  - 3.4.2 (CM-3): Configuration Change Control
  - 3.4.3 (CM-4): Security Impact Analysis
  - 3.4.4 (CM-6): Security Functionality Verification
  - 3.4.5 (CM-5): Access Restrictions for Change
  - 3.4.6 (CM-7): Least Functionality
  - 3.4.7 (CM-7): Nonessential Programs
  - 3.4.8 (CM-7(2)): Application Whitelisting
  - 3.4.9 (CM-11): User-Installed Software
  - 3.4.10 (CM-10): Software Usage Restrictions
  - 3.4.11 (CM-11): Software Verification
- NIST SP 800-171 Rev 3 Planning (PL) family:
  - 3.12.10 (PL-10): Baseline Selection
- DFARS 252.204-7012 (Safeguarding CUI)
- CMMC Level 2 (CM domain)

---

## 7. DEFINITIONS

**Baseline Configuration:** The approved, standardized configuration for a system or component.

**Configuration Item:** Hardware, software, firmware, or documentation under configuration management.

**Configuration Management:** Process of identifying, controlling, and tracking changes to configuration items.

**Least Functionality:** Configure systems with only necessary functions (minimize attack surface).

**OpenSCAP:** Open Source Security Content Automation Protocol scanner (compliance validation tool).

---

## 8. REFERENCES

- NIST SP 800-171 Rev 3 (CM family 3.4.x, PL-10 3.12.10)
- NIST SP 800-53 Rev 5 (CM family source controls)
- NIST SP 800-128 (Guide for Security-Focused Configuration Management)
- SCAP Security Guide: https://www.open-scap.org/security-policies/scap-security-guide/
- OpenSCAP documentation: https://www.open-scap.org/
- CyberHygiene Configuration Baseline Document v1.0 (to be created Phase 3)

---

## 9. POLICY REVIEW

This policy shall be reviewed and updated:
- **Annually** — Target month: April (aligned with SSP review, baseline review)
- **Upon baseline changes** — SCAP Security Guide updates, new CUI profile versions
- **Upon major configuration changes** — New services, system architecture changes

**Next Review Date:** April 2027

---

## 10. APPROVAL

**Policy Approved By:**

**System Owner:** _____________________________ Date: __________
sysadmin

---

**END OF POLICY**

---

**TCC-CMP-001 v2.0 Rev 3 DRAFT**
**Created:** March 18, 2026
**Status:** DRAFT — Ready for review and customization
**Estimated customization effort:** 2-3 hours (review baseline details, verify OpenSCAP configs, approve)
