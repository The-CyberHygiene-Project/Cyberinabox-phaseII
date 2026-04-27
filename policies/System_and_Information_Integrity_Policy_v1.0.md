# System and Information Integrity Policy

**Document ID:** DIWAI-SI-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually or upon system changes
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** Controlled Unclassified Information (CUI)

---

## Purpose

This policy establishes diwai.org (Do It With AI) requirements for maintaining the integrity of systems and information within the SecureMac Production Network (SPN), ensuring flaws are remediated, malicious code is detected, and security functions are monitored to protect Controlled Unclassified Information (CUI) and Federal Contract Information (FCI). It aligns with NIST SP 800-171 Revision 2 (SI-1 through SI-12) and supports CMMC Level 2.

---

## Scope

This policy applies to all SPN systems:

**macOS Host (securemac.diwai.org):**
- macOS Tahoe with FileVault, USB Guard, pf firewall
- UTM hypervisor
- System Integrity Protection (SIP) enabled

**Rocky Linux 9.7 VM (services.diwai.org, 10.10.1.10):**
- FIPS 140-2 mode enabled
- SELinux enforcing
- LUKS AES-256-XTS encryption
- 389 Directory Server, Postfix, Dovecot, Apache, OpenVPN

**Security Tools:**
- **Wazuh Agent:** Log forwarding, vulnerability detection, file integrity monitoring (FIM), security configuration assessment (SCA)
- **ClamAV:** Malware detection (bytecode disabled due to FIPS incompatibility — see Risk Acceptance documentation)
- **dnf-automatic:** Automated security patching (Rocky Linux)
- **OpenSCAP:** Compliance verification
- **auditd:** System audit logging (CUI profile)

---

## Definitions

- **Wazuh Agent:** Security agent on services.diwai.org forwarding logs and security events for local analysis and future SIEM integration
- **Flaw Remediation:** Process of patching vulnerabilities and correcting security weaknesses
- **File Integrity Monitoring (FIM):** Continuous monitoring of critical files for unauthorized changes (Wazuh agent)
- **CVE:** Common Vulnerabilities and Exposures identifier
- **CVSS:** Common Vulnerability Scoring System (0.0-10.0)

---

## Policy Statements

### 1. System and Information Integrity Policy and Procedures (SI-1)

diwai.org shall maintain and review this policy annually. Compliance verified through:
- Weekly review of auditd and Wazuh logs
- Quarterly OpenSCAP compliance scans
- Monthly security function verification

### 2. Flaw Remediation (SI-2)

**Vulnerability Identification:**
- Wazuh agent vulnerability detection — continuous
- OpenSCAP scans quarterly (CUI profile)
- Manual review: CISA alerts, Rocky Linux errata, vendor advisories — weekly

**Remediation Timelines:**
- **Critical (CVSS 9.0-10.0):** 7 days maximum
- **High (CVSS 7.0-8.9):** 30 days
- **Medium (CVSS 4.0-6.9):** 90 days
- **Low (CVSS 0.1-3.9):** Next scheduled maintenance window

**Automated Patching:**
- `dnf-automatic` enabled for security updates on Rocky Linux VM
- macOS: System Updates configured for automatic security patches
- Kernel updates applied manually (require VM reboot — planned maintenance window)

**Flaw Remediation Process:**
1. Identify flaw via Wazuh, OpenSCAP, or manual review
2. Assess CVSS score and exploitability
3. Take VM snapshot before patching (high-risk patches)
4. Apply security updates:
   ```bash
   # Rocky Linux VM
   sudo dnf update --security -y
   fips-mode-setup --check  # Verify FIPS mode post-update
   ```
5. Verify patch applied and system operational
6. Re-scan to confirm resolution
7. Document in POA&M if applicable

**Exception Process:**
- If patch unavailable or incompatible, implement compensating controls
- Document accepted risk with System Owner approval
- Add to POA&M with target remediation date

### 3. Malicious Code Protection (SI-3)

**Anti-Malware Deployment:**
- ClamAV installed on Rocky Linux VM (services.diwai.org)
- **Bytecode verification disabled** due to FIPS/OpenSSL incompatibility
  - Directive: `Bytecode no` in `/etc/clamd.d/scan.conf`
  - Risk acceptance documented: `~/Documents/SecureMac Project Docs/Evidence/Risk_Acceptance_ClamAV_FIPS_Incompatibility.md`
- Signature updates: freshclam daily (certbot-renew.timer analogue)
  - Status: `sudo systemctl status clamav-freshclam`
  - Databases: `/var/lib/clamav/` (main.cvd, daily.cvd, bytecode.cvd)

**Scanning Schedule:**
- **Daily:** Automated scan via cron at 02:00 (when implemented)
- **On-demand:** Manual scan for suspicious files: `sudo clamscan -r /path/`
- **clamd daemon:** Auto-starts when main.cvd and daily.cvd present
  - Condition: `ConditionPathExists=/var/lib/clamav/main.cvd`
  - Config: `/etc/systemd/system/clamd@scan.service.d/wait-for-db.conf`

**Compensating Controls for ClamAV Limitations:**
- Wazuh FIM detects unauthorized file changes
- SELinux enforcing prevents malware from executing outside allowed contexts
- auditd logs all file execution events
- pf firewall blocks unknown inbound connections
- USB Guard prevents unauthorized removable media

**Malware Response:**
```bash
# If ClamAV detects malware
sudo clamscan -r --move=/var/quarantine/ /suspicious/path/

# Review ClamAV logs
sudo tail -f /var/log/clamd.scan

# Verify quarantine
ls -la /var/quarantine/

# Notify ISSO and initiate incident response (DIWAI-IRP-001)
```

**User Responsibilities:**
- Report suspicious files immediately to ISSO
- Do not attempt to open suspected malware
- Do not disable anti-malware tools

### 4. System Monitoring (SI-4)

**Continuous Monitoring via Wazuh Agent:**
- Log aggregation from auditd, auth.log, messages, secure
- FIM: 12-hour intervals on critical paths
- SCA: CIS Rocky Linux 9 Benchmark
- Alert storage: `/var/ossec/logs/alerts/alerts.log`

**Monitoring Scope:**
- Authentication attempts (SSH, LDAP, web)
- Privilege escalation (sudo usage via auditd)
- CUI directory access (/srv/, /home/ — auditd rules)
- System configuration changes (/etc/)
- USB device events (macOS USB Guard daemon)
- Process execution anomalies

**Network Monitoring:**
- pf logs on macOS host (inbound/outbound traffic)
- Suricata (if deployed on VM): network intrusion detection
- OpenVPN connection logs

**File Integrity Monitoring (Wazuh FIM):**
Critical paths monitored (12-hour scan interval):
- `/etc/` — system configuration
- `/var/ossec/` — Wazuh configuration
- `/etc/dirsrv/` — 389-DS configuration
- `/etc/postfix/` and `/etc/dovecot/` — mail config
- `/etc/httpd/` — web config
- `/etc/ssh/` — SSH config
- `/boot/` — boot files and kernel
- `/usr/local/bin/` and `/usr/local/sbin/` — custom scripts

**Alert Priorities:**
- **Critical:** Investigate immediately (unauthorized root access, malware, CUI exfiltration indicators)
- **High:** Investigate within 4 hours
- **Medium:** Review within 24 hours
- **Low:** Weekly summary review

**Review Schedule:**
- **Daily:** Review auditd and Wazuh alert logs for critical/high events
- **Weekly:** Comprehensive review of all alerts and trends
- **Monthly:** Statistical analysis; security function verification

### 5. Security Alerts, Advisories, and Directives (SI-5)

**Information Sources:**
- CISA US-CERT alerts (email subscription + `cisa.gov/known-exploited-vulnerabilities`)
- Rocky Linux Security Errata (`errata.rockylinux.org`)
- NIST NVD (CVE notifications)
- Wazuh vulnerability feed (integrated)
- Apple Security Releases (`support.apple.com/en-us/HT201222`)
- DISA STIGs (DoD security guidance)

**Alert Processing:**
1. Wazuh automatically ingests CVE feeds
2. ISSO reviews CISA alerts weekly
3. Critical alerts trigger immediate SPN exposure assessment
4. Applicable alerts generate POA&M items

**Response Actions:**
```bash
# Check CVE exposure on Rocky Linux VM
uname -r
rpm -q kernel

# Check Wazuh vulnerability alerts
sudo grep -i "CVE-" /var/ossec/logs/alerts/alerts.log | tail -50

# Apply emergency security patch
sudo dnf update <package-name> --security

# Verify FIPS mode post-patch
fips-mode-setup --check
```

### 6. Security Functionality Verification (SI-6)

**Monthly Critical Security Function Verification:**

```bash
# Rocky Linux VM
fips-mode-setup --check              # Must return: FIPS mode is enabled
getenforce                           # Must return: Enforcing
sudo systemctl status auditd         # active (running)
sudo systemctl status clamav-freshclam # active (running)
sudo /var/ossec/bin/wazuh-control status # Wazuh processes running
sudo firewall-cmd --state            # running
sudo dnf list updates --security     # Review pending security updates

# macOS host
fdesetup status                      # FileVault is On
sudo pfctl -si | grep -i enabled     # Enabled: YES
cat /var/lib/usb-guard/mode          # Check USB Guard mode
```

**Quarterly OpenSCAP Compliance Verification:**
```bash
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cui \
  --results /root/oscap-$(date +%Y%m%d).xml \
  --report /root/oscap-$(date +%Y%m%d).html \
  /usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml

# Copy report for evidence
cp /root/oscap-$(date +%Y%m%d).html \
  "/Volumes/Cyberinabox/Secure_Mac/OpenSCAP/oscap-$(date +%Y%m%d).html"
```

**Deviation Response:**
- Any security function failure triggers immediate investigation
- Critical functions (FIPS, SELinux): same-day remediation
- Other failures: remediate within 30 days or document compensating control
- Update POA&M with remediation plan

### 7. Software, Firmware, and Information Integrity (SI-7)

**Software Integrity:**
- All software installed via trusted repositories (Rocky Linux BaseOS, AppStream, EPEL)
- Package signature verification enforced: `dnf install` verifies GPG signatures
- Custom scripts reviewed before deployment
- Wazuh FIM detects unauthorized changes to binaries

**macOS Firmware/Software:**
- macOS updates from Apple Software Update only
- App signatures verified by Gatekeeper (SIP enabled)
- Homebrew packages from homebrew-core with SHA256 verification

**File Integrity Monitoring Response:**
```bash
# Investigate a Wazuh FIM alert
# Check when file was last legitimately modified
sudo ausearch -f /path/to/file -ts recent

# Verify RPM package integrity (Rocky Linux)
sudo rpm -V package_name
sudo rpm -Va | grep -E '^..5'  # Files with changed hash

# Restore from backup if unauthorized change confirmed
# 1. Preserve evidence: sudo cp /changed/file /tmp/evidence/
# 2. Restore: sudo rpm -e --nodeps package && sudo dnf install package
# 3. Initiate incident response per DIWAI-IRP-001
```

### 8. Spam Protection (SI-8)

**Current implementation on Postfix:**
- SPF record: Published in Cloudflare DNS for diwai.org
- DKIM: Configured in Postfix (if deployed) for outbound signing
- DMARC: Published in Cloudflare DNS for diwai.org

**Inbound spam filtering:**
- SpamAssassin or Rspamd — planned for Postfix/Dovecot deployment
- Until deployed: User awareness of phishing indicators (DIWAI-ATP-001)

### 9. Information Input Validation (SI-10)

**Application-Level Controls:**
- 389-DS web console validates all inputs
- Apache HTTPD: ModSecurity WAF (if deployed)
- Roundcube webmail: built-in input validation
- SELinux enforces type enforcement for all processes
- Firewall restricts inputs to authorized ports/protocols

### 10. Error Handling (SI-11)

**Error Message Policy:**
- System errors shall not reveal sensitive information (credentials, internal IPs, file paths)
- User-facing errors provide minimal detail
- Detailed errors logged to audit logs (ISSO access only)
- SELinux prevents unauthorized error log access

### 11. Information Handling and Retention (SI-12)

**CUI Data Handling:**
- All CUI stored on LUKS-encrypted VM partition or FileVault macOS volume
- Access restricted via 389-DS LDAP group membership
- auditd rules track all CUI directory access

**Data Retention:**
- Audit logs: 90 days online, 3 years archived
- System backups: 30 days (VM bundle snapshots), 1 year full backups
- CUI documents: Per contract requirements (minimum 3 years)
- Compliance reports: 3 years
- Incident records: 3 years post-incident

**Secure Disposal:**
- LUKS-encrypted media: `cryptsetup luksErase` (destroys master key)
- FileVault macOS: Factory restore or `diskutil secureErase`
- Unencrypted media: `shred -vfz -n 3` (NIST SP 800-88)
- Physical media destruction for high-sensitivity data
- Document all disposal (DIWAI-PE-MP-001 Media Sanitization Log)

---

## Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| **ISSO (Don Shannon)** | Configure Wazuh and auditd; review logs daily/weekly; oversee vulnerability remediation; conduct integrity verifications; maintain documentation; respond to security alerts; initiate IR for integrity violations |
| **System Owner (Don Shannon)** | Approve critical remediation; review quarterly compliance reports; accept residual risks; authorize emergency patches |

---

## Compliance and Enforcement

**Monitoring:**
- Wazuh agent provides continuous security metrics
- Quarterly OpenSCAP compliance reports
- Monthly vulnerability trending
- Integration with Audit and Accountability Policy (DIWAI-AAP-001)

**Metrics:**
- Patch compliance rate: Target >95% within timeline
- OpenSCAP compliance score: Target >90%
- FIM alert investigation rate: 100% within defined SLA
- Mean Time to Detect (MTTD): Target <24 hours

---

## Section 2: System and Information Integrity Procedures

### Procedure 1: Weekly Security Review

**Process:**
```bash
# Review authentication failures
sudo aureport -au --failed --summary -ts week

# Check for privilege escalation
sudo aureport -x --summary | grep -i sudo

# Review Wazuh alerts
sudo tail -200 /var/ossec/logs/alerts/alerts.log | \
  grep -E '"level":"(10|11|12|13|14|15)"'

# Check system updates available
sudo dnf updateinfo list security

# Check ClamAV database freshness
sudo sigtool --info /var/lib/clamav/main.cvd | grep Build
```

### Procedure 2: Monthly Compliance Check

**Process:**
```bash
# Verify all critical security functions
fips-mode-setup --check
getenforce
sudo systemctl status auditd clamav-freshclam
sudo /var/ossec/bin/wazuh-control status
sudo firewall-cmd --state
fdesetup status  # macOS host

# Check certificate expiry
openssl x509 -in /etc/pki/tls/certs/diwai.org.crt -noout -enddate

# Review USB Guard log
sudo tail -50 /var/log/usb-guard.log  # macOS host

# Check LUKS keyslots are intact
sudo cryptsetup luksDump /dev/sdX | grep Keyslot
```

### Procedure 3: Quarterly OpenSCAP Compliance Scan

**Process:** See Section 6 (Security Functionality Verification) — run OpenSCAP, review results, create POA&M items for failures, archive report.

---

## Appendix: Common Alert Responses

### File Integrity Alert
**Alert:** Wazuh FIM — `/etc/ssh/sshd_config modified`
**Response:**
1. Verify if authorized change (check Change_Log.md)
2. If authorized: update change log confirmation
3. If unauthorized: preserve evidence, restore from backup, initiate IR

### Critical Vulnerability Alert
**Alert:** Wazuh — `CVE-XXXX-XXXXX CVSS 9.x detected`
**Response:**
1. Assess exploitability (check NVD, CISA KEV)
2. Take VM snapshot (UTM snapshot)
3. Apply patch within 7 days
4. Document in POA&M

### ClamAV Detection
**Alert:** ClamAV — malware detected in `/path/to/file`
**Response:**
1. Quarantine: `sudo clamscan --move=/var/quarantine/ /path/to/file`
2. Identify origin: review auditd logs for file creation
3. Scan affected paths
4. Initiate IR if widespread or CUI was exposed

---

## Approval

**Prepared By:**
Donald E. Shannon, ISSO

**Approved By:**
/s/ Donald E. Shannon
System Owner, diwai.org

**Date:** April 10, 2026

**Next Review Date:** April 10, 2027

---

**CLASSIFICATION:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)
**DISTRIBUTION:** Official Use Only - Need to Know Basis
**STATUS:** APPROVED
