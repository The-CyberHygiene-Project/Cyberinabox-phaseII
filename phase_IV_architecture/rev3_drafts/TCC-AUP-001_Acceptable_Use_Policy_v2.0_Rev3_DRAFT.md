# Acceptable Use Policy (Rules of Behavior)

**Policy Number:** TCC-AUP-001
**Version:** 2.0 Rev 3 DRAFT (Updated for NIST SP 800-171 Rev 3)
**Effective Date:** [TBD - Target: Phase 2 completion]
**Last Reviewed:** March 22, 2026
**Policy Owner:** System Owner (sysadmin)
**Approval Authority:** System Owner (sysadmin)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | February 15, 2026 | Initial policy (NIST 800-171 Rev 2, Acceptable Use focus) |
| 2.0 Rev 3 DRAFT | March 22, 2026 | Updated for Rev 3: Relabeled as "Rules of Behavior" (becomes PL-4 in Planning family), cross-reference to TCC-SPP-001 System Security Planning Policy, minor enhancements for Rev 3 compliance |

---

## 1. PURPOSE

This policy establishes rules of behavior for individuals accessing the CyberHygiene Production Network (CPN). This policy satisfies the Planning (PL) control family requirement for Rules of Behavior in NIST SP 800-171 Revision 3 (control 3.12.4, formerly Acceptable Use in Rev 2).

**Rev 3 Updates:**
- **Relabeled:** "Acceptable Use Policy" → "Rules of Behavior" (NIST SP 800-171 Rev 3 terminology)
- **Control Family:** Moves from implicit AT (Awareness & Training) to explicit PL-4 (Planning family)
- **Cross-reference:** Links to TCC-SPP-001 System Security Planning Policy (new in Rev 3)
- **Content:** Minor enhancements, core rules unchanged

---

## 2. SCOPE

This policy applies to:

**Personnel:**
- System Owner (sysadmin)
- Future employees, contractors, or third-party personnel with CPN access

**Systems:**
- All CPN systems (dc1, labrat, engineering, accounting)
- Network infrastructure (pfSense firewall)
- Email and collaboration tools

---

## 3. RULES OF BEHAVIOR

### 3.1 Access and Authentication

**Users SHALL:**
- Use only assigned user accounts (no shared accounts)
- Use strong passwords (20+ characters, complexity required)
- Use multi-factor authentication (SSH key + TOTP)
- Lock screen when leaving workstation (15-minute timeout automatic)
- Log out at end of work session

**Users SHALL NOT:**
- Share passwords or SSH keys
- Write down passwords (use password manager instead)
- Disable MFA or security controls
- Attempt to bypass authentication mechanisms

### 3.2 CUI Handling

**Users SHALL:**
- Mark CUI documents with appropriate labels (header/footer)
- Store CUI only on encrypted CPN systems (LUKS encryption)
- Transmit CUI only via encrypted channels (TLS, SSH, SFTP)
- Report CUI spillage or exposure immediately

**Users SHALL NOT:**
- Store CUI on unencrypted devices
- Transmit CUI via unencrypted email or messaging
- Use personal cloud storage for CUI (Dropbox, Google Drive, OneDrive)
- Share CUI with unauthorized individuals

### 3.3 Physical Security

**Users SHALL:**
- Follow clean desk policy (lock CUI documents when unattended)
- Secure workstations in locked areas when possible
- Escort visitors (if any) in server room
- Report lost/stolen devices immediately

**Users SHALL NOT:**
- Leave CUI documents on printers or unattended desks
- Allow unauthorized physical access to server room
- Prop open locked doors

### 3.4 Malware and Security Threats

**Users SHALL:**
- Report suspicious emails, links, or attachments immediately
- Run malware scans if instructed
- Keep systems updated (automatic patching enabled)
- Report unusual system behavior

**Users SHALL NOT:**
- Disable anti-malware tools (ClamAV, YARA)
- Open suspicious email attachments
- Click links in unsolicited emails
- Download software from untrusted sources
- Execute unknown scripts or programs

### 3.5 Removable Media and External Devices

**Users SHALL:**
- Use only approved encrypted USB drives for CUI
- Scan external media for malware before use
- Sanitize media before disposal (per TCC-PE-MP-001)

**Users SHALL NOT:**
- Use unencrypted USB drives for CUI storage
- Use personal USB drives on CPN systems
- Connect unauthorized devices to CPN network

### 3.6 Network and Internet Use

**Users SHALL:**
- Use CPN network for authorized business purposes
- Report network anomalies or outages
- Follow incident response procedures if compromise suspected

**Users SHALL NOT:**
- Use CPN systems for illegal activities
- Access inappropriate or offensive content
- Download pirated software or media
- Perform penetration testing without authorization
- Use P2P file sharing applications

### 3.7 Email and Communication

**Users SHALL:**
- Use professional communication standards
- Encrypt sensitive emails containing CUI
- Verify recipient before sending CUI
- Report phishing attempts immediately

**Users SHALL NOT:**
- Send mass unsolicited emails (spam)
- Impersonate others in communications
- Forward sensitive emails to personal accounts
- Auto-forward CPN email to external addresses

### 3.8 System Monitoring and Privacy

**Users SHALL:**
- Understand that all system activity is monitored and logged
- Consent to monitoring as condition of access
- Expect no privacy for CPN system use

**Monitoring Notice:**
- All logins, commands, file access, and network activity logged
- Wazuh SIEM monitors in real-time
- Audit logs retained 1 year minimum
- Logs may be reviewed for security, compliance, or investigation purposes

### 3.9 Incident Reporting

**Users SHALL:**
- Report security incidents immediately:
  - Suspected malware infection
  - Unauthorized access attempts
  - Lost/stolen devices or credentials
  - CUI spillage or exposure
  - Policy violations
- Use incident reporting procedures (TCC-IRP-001):
  - Email: sysadmin@cyberinabox.net
  - Internal notification: Immediate
  - External notification: US-CERT (within 1 hour for CUI breach)

**Users SHALL NOT:**
- Attempt to remediate incidents without authorization
- Conceal security incidents or policy violations
- Delay reporting due to fear of consequences

### 3.10 Account and Access Termination

**Users SHALL:**
- Return all equipment upon termination (if applicable)
- Acknowledge ongoing NDA obligations
- Transfer work files to authorized personnel

**Users SHALL NOT:**
- Retain CUI or credentials after termination
- Access systems after termination
- Share information about CPN security with unauthorized parties

---

## 4. CONSEQUENCES OF VIOLATIONS

**Policy violations may result in:**
- Verbal or written warning
- Temporary account suspension
- Permanent account revocation
- Contract termination
- Legal action (if criminal activity)
- Incident investigation and documentation

**All violations documented in:**
- Incident logs (TCC-IRP-001)
- Personnel records (TCC-PS-001)
- POA&M (if remediation required)

---

## 5. ACKNOWLEDGMENT

**Users must acknowledge:**
- Receipt and understanding of this policy
- Agreement to comply with all rules of behavior
- Understanding that violations may result in consequences
- Consent to system monitoring and logging

**Acknowledgment Method:**
- Signed acknowledgment form (for new personnel)
- Annual re-acknowledgment during security awareness training
- Current Status: System Owner acknowledges via annual training completion (FY2026)

---

## 6. COMPLIANCE

**Regulatory Requirements:**
- NIST SP 800-171 Rev 3: Control 3.12.4 (PL-4 Rules of Behavior, Planning family)
- CMMC Level 2: Rules of Behavior requirement
- DFARS 252.204-7012: User responsibility for CUI protection

**Assessment Evidence:**
- Policy acknowledgment: Training completion records (FY2026)
- Audit logs: Wazuh SIEM demonstrates monitoring and compliance
- Incident reports: Violations documented per TCC-IRP-001

---

## 7. RELATED DOCUMENTS

**Policies:**
- TCC-SPP-001: System Security Planning Policy v1.0 Rev 3 DRAFT (Planning family, NEW in Rev 3)
- TCC-ATP-001: Awareness and Training Policy v2.0 Rev 3 (annual acknowledgment)
- TCC-IRP-001: Incident Response Policy v2.0 Rev 3 (incident reporting)
- TCC-PE-MP-001: Physical and Media Protection Policy v2.0 Rev 3 (media handling)
- TCC-PS-001: Personnel Security Policy v2.0 Rev 3 (termination procedures)

**Standards:**
- NIST SP 800-171 Rev 3: Protecting Controlled Unclassified Information
- NIST SP 800-53 Rev 5: Security and Privacy Controls (PL family)

---

## 8. REVIEW AND UPDATES

**Review Frequency:** Annually or when significant changes occur

**Next Scheduled Review:** March 2027

**Version Control:** All policy versions maintained in `/home/dshannon/CyberSecurity/Rev3/Policies/`

**Change Log:**
- v2.0 Rev 3 DRAFT (March 22, 2026): Updated for Rev 3 - Relabeled as "Rules of Behavior" (PL-4), cross-referenced TCC-SPP-001, moved to Planning family from implicit AT family

---

## 9. APPROVAL

**Policy Owner:** System Owner (sysadmin)

**Approval Date:** [TBD - Target: Phase 2 completion]

**Signature:** _________________________________

**Next Review Date:** [Approval Date + 12 months]

---

*This policy satisfies NIST SP 800-171 Rev 3 control 3.12.4 (PL-4 Rules of Behavior, Planning family).*

**Rev 3 Status:** DRAFT - Pending final review and approval
**Phase 2 Target Completion:** April 2026

**Rev 3 Note:** This policy was previously "Acceptable Use Policy" in Rev 2. Rev 3 explicitly requires "Rules of Behavior" as part of the Planning (PL) family. The content is substantially the same with minor enhancements for Rev 3 terminology and cross-references.
