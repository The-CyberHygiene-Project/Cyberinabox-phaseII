# Security Awareness and Training Policy

**Policy Number:** TCC-ATP-001
**Version:** 2.0 Rev 3 DRAFT (Updated for NIST SP 800-171 Rev 3)
**Effective Date:** [TBD - Target: Phase 2 completion]
**Last Reviewed:** March 22, 2026
**Policy Owner:** System Owner (sysadmin)
**Approval Authority:** System Owner (sysadmin)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | February 15, 2026 | Initial policy (NIST 800-171 Rev 2) |
| 2.0 Rev 3 DRAFT | March 22, 2026 | Updated for Rev 3: Added ODP (training frequency - annual), consolidated controls (5→3, merged role-based training, training records, phishing into main controls), enhanced insider threat training, documented training effectiveness assessment, referenced FY2026 training completion records |

---

## 1. PURPOSE

This policy establishes requirements for security awareness and training within the CyberHygiene Production Network (CPN). This policy satisfies the Awareness and Training (AT) control family requirements in NIST SP 800-171 Revision 3 (controls 3.2.1 through 3.2.2).

**Rev 3 Updates:**
- Added Organization-Defined Parameter (ODP-AT-1) for training frequency (annual)
- Consolidated 5 Rev 2 controls into 3 Rev 3 controls (training records and phishing awareness merged)
- Enhanced insider threat training module
- Documented training effectiveness assessment (quiz results)
- Updated control numbering (role-based training now 3.2.2 instead of 3.2.3)

---

## 2. SCOPE

This policy applies to:

**Personnel:**
- System Owner (sysadmin)
- Future employees, contractors, or third-party personnel with CPN access

**Training Topics:**
- CUI handling and protection
- Password security and MFA
- Phishing and social engineering awareness (consolidated in Rev 3)
- Incident reporting procedures
- Insider threat indicators
- Physical security practices
- Acceptable use of systems

---

## 3. POLICY STATEMENTS

### 3.1 Security Awareness Training — NIST 3.2.1 (AT-2)

**3.1.1 Provide Awareness Training (ODP-AT-1 - Training Frequency)**

CyberHygiene shall provide security awareness training to all personnel **annually** (ODP-AT-1):

**Training Frequency:**
- **Annual (Required):** Complete training every 12 months
- **Initial:** Before granting system access (for new personnel)
- **Ad-Hoc:** After significant security incidents or policy changes
- **Last Completed:** February 2026 (FY2026 training cycle)
- **Next Due:** February 2027

**Training Content:**

**1. CUI Fundamentals:**
- Definition and examples of Controlled Unclassified Information
- CUI marking requirements (header/footer labeling)
- Storage restrictions (encrypted systems only)
- Transmission requirements (encrypted channels)
- Destruction procedures (shred, wipe, NIST SP 800-88)

**2. Password Security and Authentication:**
- Password requirements: 20+ characters (current CPN standard)
- Password manager usage (KeePassXC recommended)
- Multi-factor authentication (MFA): SSH key + TOTP required
- Prohibition on password sharing or reuse
- TOTP token security (backup codes, device protection)

**3. Phishing and Social Engineering (Consolidated in Rev 3):**
- Recognizing phishing emails:
  - Suspicious sender addresses
  - Urgency or pressure tactics
  - Unexpected attachments or links
  - Grammar/spelling errors
- Verification procedures: Contact sender via known channel
- Reporting: Forward suspicious emails to sysadmin@cyberinabox.net
- Real-world examples: Recent phishing campaigns targeting DoD contractors

**4. Incident Recognition and Reporting:**
- What constitutes a security incident:
  - Unauthorized access attempts
  - Malware detection
  - Lost/stolen devices
  - CUI exposure or spillage
  - Policy violations
- Reporting procedures:
  - Internal: Immediate notification to System Owner
  - External: DFARS 252.204-7012 (US-CERT within 1 hour, DoD within 72 hours)
- Do not attempt remediation without authorization

**5. Insider Threat Awareness (Enhanced in Rev 3):**
- Insider threat indicators:
  - Unauthorized data access or copying
  - After-hours access without business need
  - Disgruntlement or grievances
  - Financial difficulties
  - Unusual network traffic patterns
- Reporting: Confidential reporting to System Owner
- Self-awareness: Audit logging, POA&M documentation, external reviews

**6. Physical Security:**
- Clean desk policy: Lock CUI files when unattended
- Screen lock: 15 minutes automatic (TMOUT=900)
- Visitor procedures: No visitors expected in home office
- Secure disposal: Shred paper CUI, wipe digital media per NIST SP 800-88

**7. Removable Media and Mobile Devices:**
- USB device restrictions: Only authorized, encrypted USB drives
- Prohibition on personal cloud storage (Dropbox, Google Drive, OneDrive)
- Mobile device encryption required (if accessing CUI)
- No CUI on personal devices

**Training Delivery:**
- Format: Self-paced reading (CyberHygiene_Security_Awareness_Training_FY2026.md)
- Location: `/home/dshannon/CyberSecurity/Current/Training/`
- Duration: 1-2 hours
- Assessment: Quiz with 10 questions (80% passing score required)

**Training Effectiveness (Rev 3):**
- Quiz results documented: Training_Assessment_Quiz_FY2026.md
- Completion tracking: Training_Completion_Record_FY2026.md
- FY2026 Status: Completed February 2026, quiz score 100%

**Records Retention (Consolidated in Rev 3):**
- Training completion records: 3 years minimum
- Quiz results: 3 years minimum
- Location: `/home/dshannon/CyberSecurity/Current/Training/`
- Evidence for CMMC assessment

### 3.2 Role-Based Training — NIST 3.2.2 (AT-3, Consolidated in Rev 3)

**3.2.1 Provide Role-Based Security Training**

CyberHygiene shall provide role-based security training tailored to personnel responsibilities:

**Administrator Role (System Owner):**
- **Security Administration:**
  - FreeIPA user and group management
  - SSH key management and MFA configuration
  - Wazuh SIEM administration and rule tuning
  - OpenSCAP compliance scanning and remediation
  - Firewall rule management (pfSense)

- **Incident Response:**
  - Incident detection and analysis (Wazuh alerts)
  - Containment procedures (account disable, network isolation)
  - Evidence preservation (log collection, forensics)
  - External reporting (US-CERT, DoD Contracting Officer)

- **Vulnerability Management:**
  - Vulnerability scanning (OpenSCAP weekly, Wazuh daily)
  - Patch management (dnf-automatic, manual testing)
  - Remediation timeframes (Critical: 7 days, High: 30 days)

- **Backup and Recovery:**
  - ReaR backup procedures (weekly full, daily incremental)
  - Encryption verification (LUKS status checks)
  - Recovery testing (quarterly)

- **Compliance:**
  - POA&M maintenance
  - SSP updates
  - Risk assessment (annual, GAP-001 template)
  - Audit preparation

**Training Frequency:**
- Annual: Combined with general awareness training
- Continuous: On-the-job learning via documentation, vendor resources
- Ad-Hoc: When new tools deployed or procedures updated

**Training Sources:**
- Wazuh documentation and community forums
- Rocky Linux security guides
- NIST SP publications (800-171, 800-53, 800-30, 800-61, 800-88)
- OpenSCAP content (SCAP Security Guide)

**Role-Based Training Records:**
- Documentation: Self-certification via training completion record
- Evidence: System logs show administrative actions performed correctly
- Assessment: 100% OpenSCAP compliance demonstrates effective configuration management

---

## 4. ROLES AND RESPONSIBILITIES

**System Owner (sysadmin):**
- Complete annual security awareness training
- Complete role-based administrator training
- Pass training assessment quiz (80% minimum)
- Document training completion
- Update training materials annually (incorporate new threats, policy changes)
- Maintain training records (3-year retention)

**Future Personnel (if added):**
- Complete initial training before system access
- Complete annual refresher training
- Report training gaps or questions
- Acknowledge Acceptable Use Policy (TCC-AUP-001)

---

## 5. COMPLIANCE

**Regulatory Requirements:**
- NIST SP 800-171 Rev 3: Controls 3.2.1 through 3.2.2 (all 2 AT controls, consolidated from 5 in Rev 2)
- CMMC Level 2: Awareness and Training domain
- DFARS 252.204-7012: Training on CUI protection

**Assessment Evidence:**
- Training materials: `/home/dshannon/CyberSecurity/Current/Training/CyberHygiene_Security_Awareness_Training_FY2026.md`
- Quiz: Training_Assessment_Quiz_FY2026.md (10 questions, 100% score)
- Completion record: Training_Completion_Record_FY2026.md
- FY2026 Status: Completed February 2026

---

## 6. DEFINITIONS

**CUI:** Controlled Unclassified Information requiring safeguarding per NIST SP 800-171.

**Insider Threat:** Threat posed by personnel with authorized access who misuse that access.

**MFA:** Multi-Factor Authentication, using two or more authentication factors (SSH key + TOTP).

**ODP:** Organization-Defined Parameter, value tailored by organization per Rev 3 guidance.

**Phishing:** Social engineering attack using fraudulent emails to obtain sensitive information.

---

## 7. ENFORCEMENT

**Non-Compliance:**
- Training not completed annually: System access suspended until training completed
- Quiz failure (<80%): Retake required within 5 business days
- Policy violations: Disciplinary action per TCC-PS-001

**Reporting:**
- Training completion: Self-reported via Training_Completion_Record
- Training gaps: Report to System Owner for remediation

---

## 8. RELATED DOCUMENTS

**Policies:**
- TCC-AUP-001: Acceptable Use Policy (to be updated to Rev 3)
- TCC-IRP-001: Incident Response Policy v2.0 Rev 3
- TCC-PS-001: Personnel Security Policy (to be updated to Rev 3)

**Training Materials:**
- CyberHygiene_Security_Awareness_Training_FY2026.md
- Training_Assessment_Quiz_FY2026.md
- Training_Completion_Record_FY2026.md

**Standards:**
- NIST SP 800-171 Rev 3: Protecting Controlled Unclassified Information
- NIST SP 800-53 Rev 5: Security and Privacy Controls (AT family)
- NIST SP 800-50: Building an Information Technology Security Awareness and Training Program

---

## 9. REVIEW AND UPDATES

**Review Frequency:** Annually

**Next Scheduled Review:** March 2027

**Version Control:** All policy versions maintained in `/home/dshannon/CyberSecurity/Rev3/Policies/`

**Change Log:**
- v2.0 Rev 3 DRAFT (March 22, 2026): Updated for Rev 3 - ODP added (annual training), controls consolidated (5→3), insider threat training enhanced, training effectiveness documented (FY2026 quiz 100%), phishing awareness merged into 3.2.1

---

## 10. APPROVAL

**Policy Owner:** System Owner (sysadmin)

**Approval Date:** [TBD - Target: Phase 2 completion]

**Signature:** _________________________________

**Next Review Date:** [Approval Date + 12 months]

---

*This policy satisfies NIST SP 800-171 Rev 3 controls 3.2.1 through 3.2.2 (Awareness and Training family). All 2 AT controls addressed (consolidated from 5 in Rev 2).*

**Rev 3 Status:** DRAFT - Pending final review and approval
**Phase 2 Target Completion:** April 2026
