# System and Information Integrity Policy

**Policy Number:** TCC-SI-001
**Version:** 2.0 Rev 3 DRAFT (Updated for NIST SP 800-171 Rev 3)
**Effective Date:** [TBD - Target: Phase 2 completion]
**Last Reviewed:** March 22, 2026
**Policy Owner:** System Owner (sysadmin)
**Approval Authority:** System Owner (sysadmin)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | November 2, 2025 | Initial policy (NIST 800-171 Rev 2) |
| 2.0 Rev 3 DRAFT | March 22, 2026 | Updated for Rev 3: Added ODPs (flaw remediation timeframes, malware update frequency, monitoring frequency), expanded YARA custom rules documentation, updated for current implementations (Wazuh SIEM, 100% OpenSCAP, daily CVE detection) |

---

## 1. PURPOSE

This policy establishes requirements for maintaining the integrity of systems and information within the CyberHygiene Production Network (CPN). This policy satisfies the System and Information Integrity (SI) control family requirements in NIST SP 800-171 Revision 3 (controls 3.14.1 through 3.14.7).

**Rev 3 Updates:**
- Added Organization-Defined Parameters (ODPs) for flaw remediation timeframes, malware signature updates, system monitoring frequency
- Expanded YARA custom rules documentation
- Enhanced vulnerability management procedures
- Updated for current Wazuh SIEM and OpenSCAP compliance status (100%)

---

## 2. SCOPE

This policy applies to:

**Systems in Scope:**
- dc1.cyberinabox.net (192.168.1.10) — FreeIPA domain controller, Wazuh SIEM manager, Samba file server
- labrat.cyberinabox.net (192.168.1.115) — Development workstation
- engineering.cyberinabox.net (192.168.1.104) — Engineering workstation
- accounting.cyberinabox.net (192.168.1.113) — Accounting workstation

**Security Tools:**
- Wazuh SIEM v4.9.2 — Log aggregation, vulnerability detection, FIM, active response
- ClamAV — Signature-based malware detection
- YARA — Custom malware detection rules
- dnf-automatic — Automated security patching
- OpenSCAP — Compliance verification (100% CUI profile compliance)
- Suricata IDS/IPS — Network intrusion detection (pfSense integration)

---

## 3. POLICY STATEMENTS

### 3.1 Flaw Remediation — NIST 3.14.1 (SI-2)

**3.1.1 Identify and Remediate Flaws (ODP-SI-1 - Flaw Remediation Timeframes)**

CyberHygiene shall identify, report, and correct system flaws within the following organization-defined timeframes based on CVSS score:

**Remediation Timelines (ODP-SI-1):**
- **Critical (CVSS 9.0-10.0):** 7 calendar days maximum
- **High (CVSS 7.0-8.9):** 30 calendar days maximum
- **Moderate (CVSS 4.0-6.9):** 90 calendar days maximum
- **Low (CVSS 0.1-3.9):** Next scheduled maintenance window (quarterly)

**Vulnerability Identification Methods:**
- **Wazuh Vulnerability Detector:** Continuous scanning on all systems
  - CVE feed updates: Every 60 minutes
  - Vulnerability database: NVD, Red Hat Security Data, OVAL
  - Detection method: Package inventory cross-referenced against CVE database
- **OpenSCAP Scans:** Weekly automated scans using SCAP Security Guide CUI profile
  - Scan schedule: Every Sunday at 03:00
  - Compliance status: 100% (104/104 rules passing as of 2026-02-21)
- **Manual Reviews:** Weekly security bulletin monitoring
  - US-CERT/CISA alerts
  - Rocky Linux security errata
  - Vendor-specific bulletins (pfSense, hardware)

**Automated Patching Implementation:**
```bash
# dnf-automatic configuration on all systems
# /etc/dnf/automatic.conf
apply_updates = yes
upgrade_type = security
```

**Flaw Remediation Process:**
1. **Detection:** Wazuh vulnerability detector identifies CVE and generates alert
2. **Assessment:** Review CVSS score, exploitability, and affected systems
3. **Prioritization:** Assign remediation timeframe based on severity (ODP-SI-1)
4. **Testing:** Test patch on lowest-criticality system first (labrat)
5. **Application:** Deploy patch to remaining systems:
   - Workstations: engineering, accounting
   - Critical infrastructure: dc1 (during maintenance window if possible)
6. **Verification:**
   - FIPS mode integrity check: `fips-mode-setup --check`
   - Wazuh rescan to confirm remediation
   - OpenSCAP rescan (weekly)
7. **Documentation:** Update POA&M if remediation extends beyond timeframe

**Compensating Controls:**
- If patch unavailable: Implement network isolation, disable affected service, or add firewall rules
- Risk acceptance: Documented and approved by System Owner
- POA&M tracking: Monthly review until resolved

**Evidence:**
- Wazuh Vulnerability Dashboard: Real-time CVE detection status
- OpenSCAP scan results: `/home/dshannon/openscap-results/` (weekly reports)
- dnf-automatic logs: `/var/log/dnf.log`

### 3.2 Malicious Code Protection — NIST 3.14.2, 3.14.4 (SI-3)

**3.2.1 Employ Malicious Code Protection (ODP-SI-2 - Malware Update Frequency)**

CyberHygiene shall employ malicious code protection mechanisms and update them at least **daily** (ODP-SI-2):

**Anti-Malware Deployment:**

**ClamAV (Signature-Based Detection):**
- Installed on: All 4 CPN systems
- Signature database: `/var/lib/clamav/`
- Update frequency: **Daily via freshclam** (exceeds ODP-SI-2 daily minimum)
- Update schedule: 06:00 daily + on-demand
- Real-time scanning: Samba VFS module (`vfs_clamav`)

**YARA (Custom Rule-Based Detection):**
- Installed on: All 4 CPN systems
- Rules location: `/var/lib/yara/rules/`
- Update frequency: Quarterly (Q1/Q2/Q3/Q4)
- Rule categories:
  - **Crypto miners:** Detects coinminers, XMRig, cryptojacking scripts
  - **Backdoors:** Detects web shells, reverse shells, bind shells
  - **Rootkits:** Detects kernel-level rootkits, userland rootkits
  - **Obfuscated code:** Detects base64 encoding, hex encoding, suspicious JavaScript
  - **Ransomware indicators:** File encryption patterns, ransom note templates

**YARA Rule Example:**
```yara
rule CryptoMiner_XMRig {
    meta:
        description = "Detects XMRig cryptocurrency miner"
        author = "CyberHygiene Project"
        date = "2026-01-15"
        severity = "high"
    strings:
        $s1 = "stratum+tcp://" ascii
        $s2 = "donate-level" ascii
        $s3 = "RandomX" ascii
        $s4 = "xmrig" nocase
    condition:
        2 of ($s*)
}
```

**Wazuh Integration:**
- Malware detection alerts forwarded to Wazuh Manager
- ClamAV logs: `/var/log/clamav/` monitored by Wazuh agent
- YARA scan results: Integrated via custom Wazuh decoder
- Active response: Automatic quarantine of detected malware to `/var/quarantine/`

**Scanning Schedule:**
- **Real-time:** Samba file share access (ClamAV VFS module)
- **Daily:** Full system scan at 02:00 (ClamAV)
- **Weekly:** YARA rule scan at 04:00 Sunday
- **On-demand:** User-initiated scans for suspicious files

**Malware Response:**
1. **Detection:** ClamAV or YARA identifies malicious file
2. **Quarantine:** Wazuh active response moves file to `/var/quarantine/`
3. **Alerting:** Wazuh generates Level 12 alert (Critical)
4. **Investigation:** ISSO reviews malware sample, determines scope
5. **Remediation:**
   - Remove malware from quarantine after analysis
   - Scan all systems for indicators of compromise (IOCs)
   - Review authentication logs for unauthorized access
   - Update YARA rules if new malware variant
6. **Reporting:** Document in incident log (TCC-IRP-001 procedures)

**User Responsibilities:**
- Report suspicious files immediately to System Owner
- Do not disable anti-malware tools (systemctl stop/disable prohibited)
- Avoid downloading software from untrusted sources
- Do not execute files from external media without scanning

### 3.3 System Monitoring — NIST 3.14.6 (SI-4)

**3.3.1 Monitor Systems (ODP-SI-3 - Monitoring Frequency)**

CyberHygiene shall monitor systems to detect attacks, unauthorized activities, and indicators of compromise on a **continuous** basis (ODP-SI-3, exceeds DoD baseline):

**Continuous Monitoring via Wazuh SIEM:**
- **Deployment:** Wazuh Manager on dc1 (192.168.1.10), agents on all 4 systems
- **Log Aggregation:** rsyslog forwards all logs to Wazuh Manager in real-time
- **Analysis:** Wazuh decoders and rules analyze logs as they arrive (< 1 second latency)
- **Alerting:** Real-time notifications for security events (email, dashboard)
- **Dashboard:** Web UI at https://dc1.cyberinabox.net:443 (continuous visibility)

**Monitoring Scope:**

**Authentication Events:**
- Successful/failed login attempts (SSH, console, FreeIPA)
- MFA challenges (TOTP token validation)
- Privilege escalation (sudo usage, su commands)
- Account lockouts (fail2ban triggers)
- Password changes

**File System Events (FIM):**
- Critical directories monitored (12-hour scan interval):
  - `/etc/` — System configuration
  - `/var/ossec/` — Wazuh configuration
  - `/etc/ipa/` — FreeIPA configuration
  - `/etc/samba/` — Samba configuration
  - `/srv/samba/` — CUI file shares
  - `/usr/local/bin/` — Custom scripts
  - `/boot/` — Boot files and kernel
  - `/lib/modules/` — Kernel modules

**Network Events (Suricata IDS):**
- All network traffic monitored via pfSense + Suricata integration
- Ruleset: Emerging Threats + Snort community rules (updated daily)
- Detection: Malware C2, data exfiltration, port scans, DoS attacks
- Integration: Suricata EVE JSON logs forwarded to Wazuh

**Process Execution:**
- New binary execution (auditd integration)
- Suspicious commands (curl | bash, wget | sh, nc listeners)
- Service starts/stops/restarts
- Cron job execution

**System Changes:**
- Software installation/removal (dnf, rpm)
- Firewall rule changes (firewalld)
- SELinux policy modifications
- System configuration changes (sysctl)

**Alert Severity Levels:**
| Level | Priority | Response Time | Notification Method |
|-------|----------|---------------|---------------------|
| 12-15 | Critical | 1 hour | Email + SMS + Dashboard |
| 10-11 | High | 4 hours | Email + Dashboard |
| 7-9 | Medium | 24 hours | Dashboard |
| 3-6 | Low | Weekly review | Dashboard (aggregated) |

**Review Schedule:**
- **Continuous:** Real-time dashboard monitoring during business hours
- **Daily:** Morning review of overnight alerts (high/critical)
- **Weekly:** Comprehensive review of all alerts and trend analysis
- **Monthly:** Statistical reporting and effectiveness assessment

### 3.4 Security Alerts, Advisories, and Directives — NIST 3.14.5 (SI-5)

**3.4.1 Receive and Respond to Security Alerts**

CyberHygiene shall receive security alerts, advisories, and directives from external organizations:

**Information Sources:**
- **US-CERT/CISA:** Email subscriptions for alerts and bulletins
- **NIST NVD:** CVE notifications via Wazuh vulnerability feed
- **Rocky Linux Security:** Errata monitoring via dnf-automatic
- **Wazuh Threat Intelligence:** Integrated CTI feeds
- **Vendor Bulletins:** pfSense security advisories

**Alert Processing:**
1. **Receipt:** Security alerts received via email, RSS, or Wazuh feed
2. **Assessment:** Determine relevance to CPN systems and configurations
3. **Prioritization:** Assign urgency based on exploitability and exposure
4. **Action:**
   - Immediate: Apply patches, implement workarounds, or block IOCs
   - Scheduled: Plan remediation within ODP-SI-1 timeframes
   - Monitor: Track for future relevance
5. **Communication:** Notify System Owner of critical alerts
6. **Documentation:** Record actions taken in system logs

**Internal Dissemination:**
- Single user environment (sysadmin) — email notifications sufficient
- Critical alerts: Immediate notification
- Non-critical: Weekly digest

### 3.5 Security Function Verification — NIST 3.14.7 (SI-7)

**3.5.1 Verify Security Function Integrity**

CyberHygiene shall verify the integrity of security functions using File Integrity Monitoring (FIM):

**Wazuh FIM Implementation:**
- Scan frequency: Every 12 hours (00:00, 12:00 daily)
- Method: SHA-256 hash comparison
- Baseline: Established on initial deployment, updated after approved changes
- Detection: Real-time alerts for unauthorized modifications

**Monitored Security Components:**
- Wazuh agent binaries: `/var/ossec/bin/`
- Wazuh configuration: `/var/ossec/etc/`
- SELinux policy: `/etc/selinux/`
- Audit daemon: `/sbin/auditd`, `/etc/audit/`
- ClamAV binaries: `/usr/bin/clamscan`, `/usr/sbin/clamd`
- SSH daemon: `/usr/sbin/sshd`, `/etc/ssh/sshd_config`
- Firewall: `/usr/sbin/firewalld`, `/etc/firewalld/`

**FIM Alert Response:**
1. **Alert:** Wazuh generates Level 7+ alert for file modification
2. **Verification:** Determine if change was authorized (change control log)
3. **Investigation:** If unauthorized:
   - Review authentication logs for access
   - Check command history (auditd)
   - Scan system for malware (ClamAV + YARA)
   - Assess scope (single file or widespread compromise)
4. **Remediation:**
   - Restore from known-good backup
   - Re-install affected package (rpm --reinstall)
   - Full system restore if compromise confirmed
5. **Prevention:** Update FIM baseline after verified authorized changes

**Integration with VirusTotal (Operational Update 02/21/2026):**
- Tuned integration: Alert level threshold raised from 7 to 10
- Purpose: High-severity file modifications trigger VT hash lookup
- Quota management: MD5 deduplication cache, 490/day limit guard
- Note: Routine FIM events (level 7-9) no longer trigger VT API calls

**RPM Verification:**
```bash
# Weekly cron job verifies package integrity
rpm -Va | grep -v '^.....UG' | mail -s "RPM Verification" sysadmin@cyberinabox.net
```

**OpenSCAP Integrity Verification:**
- Weekly scans verify security baseline (100% compliance)
- Automated remediation for deviations (where safe)
- Manual review for complex deviations

### 3.6 Software, Firmware, and Information Integrity — NIST 3.14.2 (SI-7(1))

**3.6.1 Verify Software Integrity**

CyberHygiene shall perform integrity checks on software and firmware:

**RPM Package Verification:**
- All software installed via DNF (Rocky Linux repositories)
- GPG signature verification enforced (gpgcheck=1 in dnf.conf)
- Repository metadata signed with Red Hat GPG keys
- Installation fails if signature invalid

**Firmware Integrity:**
- UEFI Secure Boot enabled on all systems (where supported)
- BIOS/firmware updates: Manual process, vendor-signed only
- Verification: Boot process validates kernel signature

**Application Integrity:**
- No custom-compiled software (COTS only environment)
- Third-party software: Verified via vendor signatures (e.g., Wazuh GPG key)
- Scripts: Stored in version control, change tracking via git

### 3.7 Spam Protection — NIST 3.14.3 (SI-8)

**3.7.1 Implement Spam Protection**

CyberHygiene shall implement spam protection mechanisms for email:

**Postfix Anti-Spam Configuration:**
- **Greylisting:** Enabled via policyd-weight
- **SPF checks:** Reject emails failing SPF validation
- **DKIM validation:** Verify email signatures
- **Rate limiting:** 10 messages/hour per sender
- **RBL checks:** Spamhaus, Barracuda, SORBS

**User-Level Filtering:**
- Thunderbird spam filters enabled
- Automatic training via user feedback (mark as spam)
- Spam folder: Reviewed weekly, purged monthly

**Quarantine:**
- Suspected spam held in Postfix queue for review
- Release mechanism: Admin can whitelist sender
- Log retention: 90 days

### 3.8 Information Handling and Retention — NIST 3.14.1 (SI-12)

**3.8.1 Handle and Retain Information**

CyberHygiene shall handle and retain information in accordance with applicable laws and policies:

**CUI Handling:**
- Stored on encrypted volumes (LUKS AES-256-XTS)
- Transmission encrypted (TLS 1.2+, SSH)
- Access restricted via file permissions (chmod 600 for sensitive files)
- Marking: CUI label applied to sensitive documents

**Information Retention:**
- **Audit logs:** 1 year minimum (Wazuh archives), 3 years for critical systems
- **Email:** 1 year retention (configurable per user)
- **CUI documents:** Retained per contract requirements (typically 3-7 years)
- **Backup retention:** Weekly full (4 weeks), monthly archives (12 months)

**Secure Disposal:**
- Digital: `shred -vfz -n 3` for file deletion
- Disk wiping: NIST SP 800-88 procedures (ATA Secure Erase)
- Physical media: Cross-cut shredding for paper, physical destruction for disks

---

## 4. ROLES AND RESPONSIBILITIES

**System Owner (sysadmin):**
- Maintain this policy and ensure compliance
- Review Wazuh alerts daily (critical/high)
- Conduct weekly security bulletin reviews
- Apply security patches within ODP-SI-1 timeframes
- Update YARA rules quarterly
- Conduct annual policy review

**Users (if additional users added):**
- Report suspicious activities immediately
- Do not disable security tools
- Follow secure computing practices per TCC-AUP-001

---

## 5. COMPLIANCE

**Regulatory Requirements:**
- NIST SP 800-171 Rev 3: Controls 3.14.1 through 3.14.7 (all 7 SI controls)
- CMMC Level 2: System and Information Integrity domain
- DFARS 252.204-7012: Cyber incident reporting

**Assessment Evidence:**
- Wazuh SIEM dashboard: Real-time monitoring status
- OpenSCAP scan results: 100% compliance (104/104 rules)
- Vulnerability scan reports: Wazuh vulnerability detector
- Malware scan logs: ClamAV + YARA results
- FIM reports: Wazuh file integrity monitoring
- Patch management logs: dnf-automatic history

---

## 6. DEFINITIONS

**CVE:** Common Vulnerabilities and Exposures, standardized vulnerability identifier.

**CVSS:** Common Vulnerability Scoring System (0.0-10.0 severity scale).

**FIM:** File Integrity Monitoring, detection of unauthorized file modifications.

**ODP:** Organization-Defined Parameter, value tailored by organization per Rev 3 guidance.

**YARA:** Pattern matching tool for malware detection using custom rules.

**Wazuh SIEM:** Security Information and Event Management platform (v4.9.2).

---

## 7. ENFORCEMENT

**Non-Compliance:**
- Disabling security tools: Immediate account suspension, system access revocation
- Failure to report incidents: Disciplinary action per TCC-PS-001
- Policy violations: Documented and reviewed by System Owner

**Reporting:**
- Security incidents: Immediate notification to System Owner
- Policy violations: Report via TCC-IRP-001 procedures

---

## 8. RELATED DOCUMENTS

**Policies:**
- TCC-AAP-001: Audit and Accountability Policy v2.0 Rev 3
- TCC-SCP-001: System and Communications Protection Policy v2.0 Rev 3
- TCC-IRP-001: Incident Response Policy (to be updated to Rev 3)
- TCC-AUP-001: Acceptable Use Policy (to be updated to Rev 3)

**Procedures:**
- Incident Response Plan
- Flaw Remediation Procedures
- Malware Response Procedures

**Standards:**
- NIST SP 800-171 Rev 3: Protecting Controlled Unclassified Information
- NIST SP 800-53 Rev 5: Security and Privacy Controls (SI family)
- NIST SP 800-40: Patch Management
- NIST SP 800-83: Malware Incident Prevention and Handling

---

## 9. REVIEW AND UPDATES

**Review Frequency:** Annually or when significant changes occur

**Next Scheduled Review:** March 2027

**Version Control:** All policy versions maintained in `/home/dshannon/CyberSecurity/Rev3/Policies/`

**Change Log:**
- v2.0 Rev 3 DRAFT (March 22, 2026): Updated for Rev 3 - ODPs added (flaw remediation, malware updates, monitoring frequency), YARA documentation expanded, current implementation status updated (Wazuh, OpenSCAP 100%)

---

## 10. APPROVAL

**Policy Owner:** System Owner (sysadmin)

**Approval Date:** [TBD - Target: Phase 2 completion]

**Signature:** _________________________________

**Next Review Date:** [Approval Date + 12 months]

---

*This policy satisfies NIST SP 800-171 Rev 3 controls 3.14.1 through 3.14.7 (System and Information Integrity family). All 7 SI controls addressed.*

**Rev 3 Status:** DRAFT - Pending final review and approval
**Phase 2 Target Completion:** April 2026
