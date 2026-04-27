# Personnel Security Policy

**Policy Number:** TCC-PS-001
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
| 2.0 Rev 3 DRAFT | March 22, 2026 | Updated for Rev 3: Added ODPs (personnel screening criteria, transfer review frequency - N/A for solopreneur), documented third-party access procedures, enhanced sanctions process documentation, added N/A justifications for single-person operation |

---

## 1. PURPOSE

This policy establishes requirements for personnel security within the CyberHygiene Production Network (CPN). This policy satisfies the Personnel Security (PS) control family requirements in NIST SP 800-171 Revision 3 (controls 3.9.1 through 3.9.2).

**Rev 3 Updates:**
- Added Organization-Defined Parameters (ODPs) for personnel screening criteria and transfer reviews
- Enhanced third-party access procedures
- Documented N/A justifications for solopreneur operations
- Added self-accountability mechanisms (audit logging, external reviews)

---

## 2. SCOPE

This policy applies to:

**Current Personnel:**
- System Owner (sysadmin) — Holds active Top Secret security clearance

**Future Personnel (if added):**
- Employees requiring CPN access
- Contractors/consultants with CUI access
- Third-party service providers

---

## 3. POLICY STATEMENTS

### 3.1 Personnel Screening — NIST 3.9.1 (PS-3, ODP-PS-1)

**3.1.1 Screen Personnel Before Access (ODP-PS-1 - Screening Criteria)**

CyberHygiene shall screen individuals before authorizing access to CPN systems processing CUI:

**Current Status:**
- System Owner holds active **Top Secret (TS) security clearance**
- **Exceeds DoD baseline** requirements for CUI access
- Clearance includes:
  - FBI Single Scope Background Investigation (SSBI)
  - Credit history review
  - Reference interviews
  - Adjudication by DoD Consolidated Adjudication Facility (CAF)
- Reinvestigation: Every 5 years per TS clearance requirements

**Future Personnel Screening Criteria (ODP-PS-1):**
- **High-Risk Positions (Admin access):**
  - Secret or Top Secret clearance (preferred)
  - OR comprehensive background check (criminal, credit, references)
  - NDA execution required
- **Moderate-Risk (Limited CUI access):**
  - Basic background check (criminal history)
  - Citizenship/residency verification
  - NDA execution required
- **Third-Party (Temporary access):**
  - Self-attestation
  - NDA execution
  - Supervised access only

**Screening Documentation:**
- Clearance verification: Active TS clearance documentation on file
- Background check results: Stored securely (if applicable to future personnel)
- NDA: Signed and dated

### 3.2 Personnel Termination — NIST 3.9.2 (PS-4)

**3.2.1 Terminate Access Upon Separation**

CyberHygiene shall terminate CPN access upon personnel termination or transfer:

**Termination Procedures:**
1. **Disable Accounts:** FreeIPA user account disabled immediately
   ```bash
   ipa user-disable <username>
   ```
2. **Revoke Credentials:** SSH keys removed, TOTP tokens invalidated
3. **Collect Assets:** Return physical tokens, laptops, access badges (if applicable)
4. **Exit Interview:** Remind of ongoing CUI protection obligations (NDA remains in effect)
5. **Access Review:** Audit logs reviewed for 30 days post-termination

**Current Status:**
- N/A - Solopreneur operation (no personnel to terminate)
- Self-termination procedures: Documented for business succession planning

**Transfer Reviews (ODP-PS-2 - Transfer Frequency):**
- **Current:** N/A (solopreneur, no personnel transfers)
- **Future:** If personnel added, review access upon role changes
- **Frequency:** Immediate upon transfer notification

---

## 4. SOLOPRENEUR SPECIAL CONSIDERATIONS

**Single-Person Operation:**
CyberHygiene is a solopreneur business operated by a single individual (System Owner) with TS clearance. Many traditional personnel security controls are not applicable.

**Self-Accountability Mechanisms:**
- **Audit Logging:** All actions logged via auditd and Wazuh SIEM
- **External Reviews:** Independent CMMC assessor reviews, C3PAO gap analysis
- **POA&M Documentation:** Self-identified gaps tracked and remediated
- **Training:** Annual security awareness training completed (self-administered)
- **Policy Compliance:** Quarterly SSP reviews document adherence

**Insider Threat Mitigation:**
- Audit logs retained 1 year minimum (all administrative actions logged)
- Wazuh SIEM monitors for anomalous behavior
- No ability to delete audit logs without detection (centralized logging)
- External backups stored offsite (prevents data destruction)

**Third-Party Access (Limited):**
- Consultants: Case-by-case approval, supervised access only
- Vendors: Remote support via screen sharing (no direct system access)
- Assessors: Read-only access for CMMC assessment, escorted access

---

## 5. ROLES AND RESPONSIBILITIES

**System Owner (sysadmin):**
- Maintain active security clearance
- Complete required reinvestigations (TS: every 5 years)
- Self-administer security awareness training annually
- Document adherence to policies via audit logs
- Approve third-party access (case-by-case basis)

**Future Personnel (if added):**
- Complete screening before system access
- Execute NDA
- Complete initial and annual training
- Report policy violations or concerns

---

## 6. COMPLIANCE

**Regulatory Requirements:**
- NIST SP 800-171 Rev 3: Controls 3.9.1 through 3.9.2 (Personnel Security family)
- CMMC Level 2: Personnel Security domain
- DFARS 252.204-7012: Personnel screening for CUI access

**Assessment Evidence:**
- TS clearance verification: Active clearance documentation
- Audit logs: Wazuh SIEM, auditd (all administrative actions)
- Training records: Annual security awareness completion (FY2026)
- POA&M: Self-identified gaps and remediation tracking

---

## 7. RELATED DOCUMENTS

**Policies:**
- TCC-ATP-001: Awareness and Training Policy v2.0 Rev 3
- TCC-AUP-001: Acceptable Use Policy (to be updated to Rev 3)
- TCC-AAP-001: Audit and Accountability Policy v2.0 Rev 3

**Standards:**
- NIST SP 800-171 Rev 3: Protecting Controlled Unclassified Information
- NIST SP 800-53 Rev 5: Security and Privacy Controls (PS family)

---

## 8. APPROVAL

**Policy Owner:** System Owner (sysadmin)

**Approval Date:** [TBD - Target: Phase 2 completion]

**Signature:** _________________________________

---

*This policy satisfies NIST SP 800-171 Rev 3 controls 3.9.1 through 3.9.2 (Personnel Security family).*

**Rev 3 Status:** DRAFT - Pending final review and approval
