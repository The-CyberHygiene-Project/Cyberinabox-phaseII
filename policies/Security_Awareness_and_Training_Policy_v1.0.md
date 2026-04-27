# Security Awareness and Training Policy

**Document ID:** DIWAI-ATP-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** CUI

---

## 1. Purpose

This policy establishes diwai.org (Do It With AI) requirements for security awareness and training on the SecureMac Production Network (SPN). It ensures all personnel with access to SPN resources or CUI understand their security responsibilities, in compliance with NIST SP 800-171 Rev 2 (AT-1 through AT-6) and CMMC Level 2.

---

## 2. Scope

This policy applies to:

- **All Personnel:**
  - System Owner / ISSO: Donald E. Shannon
  - Any contractors or temporary users granted SPN access
  - Any personnel with physical access to SecureMac hardware

- **All SPN Systems:**
  - Mac mini M4 Pro (securemac.diwai.org) — macOS Tahoe host
  - Rocky Linux 9.7 VM (services.diwai.org, 10.10.1.10)

---

## 3. Policy Statements

### 3.1 Security Awareness and Training Policy and Procedures (AT-1)

diwai.org shall maintain this policy and supporting training procedures. Policy is reviewed annually. Training completion is documented and retained for 3 years.

### 3.2 Literacy Training and Awareness (AT-2)

**Initial Training:**
- All new personnel complete security awareness training before accessing SPN or CUI
- Training covers at minimum:
  - CUI identification, handling, and protection requirements
  - Acceptable use policy overview
  - Password and credential management
  - Phishing and social engineering recognition
  - Incident reporting procedures
  - Physical security requirements

**Annual Refresher Training:**
- All active personnel complete annual refresher training
- Topics updated to reflect new threats and policy changes
- Completion documented

**Awareness Topics (maintained throughout the year):**
- Phishing simulations and recognition
- New threat bulletins (CISA alerts, vendor advisories)
- Security incident lessons learned
- CUI handling reminders

### 3.3 Role-Based Training (AT-3)

**System Owner / ISSO:**
- CMMC assessment preparation and self-assessment methodology
- NIST SP 800-171 control implementation and evidence collection
- Wazuh SIEM dashboard review and alert response
- OpenSCAP scan execution and result interpretation
- Incident response procedures and documentation
- POA&M maintenance and SPRS scoring
- CUI marking and handling requirements

**Contractors (when applicable):**
- Acceptable use policy (DIWAI-AUP-001)
- CUI handling and protection requirements
- SSH key management and credential hygiene
- Incident reporting to ISSO

### 3.4 Training Records (AT-4)

Training records shall document:
- Personnel name
- Training title and content summary
- Completion date
- Next required date (annual)

**Record Retention:** 3 years

**Record Location:** `~/Documents/SecureMac Project Docs/Evidence/Training_Records/`

---

## 4. Training Content Requirements

### 4.1 CUI Awareness

All personnel must understand:
- What constitutes CUI (per 32 CFR Part 2002 and NIST SP 800-171)
- CUI marking requirements
- Authorized storage locations (LUKS-encrypted SPN systems only)
- Prohibited transmission methods (no unencrypted email, no personal cloud storage)
- Disposal requirements (LUKS erase, shred per NIST SP 800-88)

### 4.2 Password and Credential Security

- Minimum 14-character passwords (enforced by 389-DS password policy)
- No password reuse (last 5 remembered)
- No sharing of credentials
- SSH keys: ECDSA-521, passphrase-protected
- LDAP passwords changed upon compromise suspicion
- LUKS passphrase stored in KeePass vault only

### 4.3 Phishing and Social Engineering

- Verify sender identity before opening attachments
- Never click links in unexpected emails — type URLs directly
- Report suspected phishing to ISSO immediately
- No credential entry on untrusted sites

### 4.4 Incident Reporting

All personnel must know to report:
- Suspected unauthorized access
- Lost or stolen devices
- Malware or suspicious behavior
- Accidental CUI disclosure
- Physical security breaches

Reporting method: Direct contact with ISSO (Donald E. Shannon)

---

## 5. Training Delivery Methods

**Available Training Resources:**
- CISA free training: `cisa.gov/cybersecurity-training-exercises`
- NIST SP 800-50 (Building an Information Technology Security Awareness and Training Program)
- DoD Cyber Awareness Challenge (available at `cyber.mil`)
- Vendor-specific training for deployed tools (Wazuh, Rocky Linux security)

**Documentation of Completion:**
- Screenshot or certificate saved to Evidence/Training_Records/
- Log entry in training records spreadsheet

---

## 6. Roles and Responsibilities

| Role | Training Responsibilities |
|------|--------------------------|
| **ISSO (Don Shannon)** | Develop and deliver training content; maintain training records; track completion dates; update materials annually; complete role-based training |
| **System Owner (Don Shannon)** | Approve training program; complete all required training; ensure contractors complete training before access |
| **Contractors** | Complete initial training before SPN access; complete annual refresher; acknowledge AUP |

---

## 7. Compliance Mapping

| NIST SP 800-171 Control | Implementation |
|-------------------------|----------------|
| **AT-1** Policy and Procedures | This document |
| **AT-2** Literacy Training and Awareness | Section 3.2 |
| **AT-3** Role-Based Training | Section 3.3 |
| **AT-4** Training Records | Section 3.4 |

---

## 8. Policy Review and Updates

- **Review Frequency:** Annually
- **Approval Authority:** System Owner / ISSO (Donald E. Shannon)

---

## 9. Approval Signatures

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
