# Policies 4-11: Rev 3 Update Summaries

**Purpose:** Quick reference for updating remaining 8 policies from Rev 2 to Rev 3
**Date:** March 18, 2026
**Status:** DRAFT summaries — expand into full policies during review

---

## Policy 4/11: TCC-SCP-001 — System & Communications Protection

### Rev 2 → Rev 3 Changes

**Control Count:** 23 controls (Rev 2) → 20 controls (Rev 3)
- **3 controls consolidated** into others (PKI, session protection, session authenticity)

**Key Rev 3 Updates:**

1. **Add Network Architecture Diagram requirement** (SC-7, 3.13.1)
   - Current gap: Network topology documented in SSP but no formal diagram
   - Action: Create Network Architecture Diagram v1.0 (Phase 3, Activity 3.1)
   - Location: `/Rev3/Evidence/Network_Architecture_Diagram_v1.0.pdf`

2. **Enhanced cryptographic requirements** (SC-8, SC-13)
   - Document FIPS 140-2 validation certificates explicitly:
     - OpenSSL: Cert #3980
     - libgcrypt: Cert #3739
     - Kernel crypto: Cert #4046
   - Update ODP-SC-1: Document approved cryptographic algorithms
   - Current: AES-256-XTS (disk), AES-256-GCM (TLS), ECDSA-521 (SSH), RSA-4096 (certs)

3. **Session termination ODP** (SC-10, 3.13.9)
   - ODP-SC-2: Session termination timeout
   - Current: 30 min SSH, 15 min HTTPS
   - DoD baseline: 15 min
   - Justification: 30 min SSH for operational convenience, documented in ODP doc

4. **Consolidated controls** (update numbering):
   - Rev 2 3.13.17 (PKI) → merged into Rev 3 3.13.10 (Cryptographic Key Establishment)
   - Rev 2 3.13.18 (Protect sessions) → merged into Rev 3 3.13.8 (Transmission confidentiality)
   - Rev 2 3.13.19 (Session authenticity) → merged into Rev 3 3.13.15 (Protect authenticity)

**Current Implementations to Highlight:**
- ✅ pfSense firewall with default-deny ruleset (SC-7)
- ✅ TLS 1.2+ encryption for all transmission (SC-8)
- ✅ FIPS 140-2 validated crypto (SC-13)
- ✅ LUKS disk encryption AES-256-XTS (SC-28)
- ⚠️ Network diagram missing (create in Phase 3)

**Estimated Update Effort:** 3-4 hours (mostly adding diagram requirement, FIPS cert details)

---

## Policy 5/11: TCC-SI-001 — System & Information Integrity

### Rev 2 → Rev 3 Changes

**Control Count:** 16 controls (unchanged)

**Key Rev 3 Updates:**

1. **Flaw remediation ODPs** (SI-2, 3.14.1)
   - ODP-SI-1: Flaw remediation timeframes
   - Critical: 7 days, High: 30 days, Moderate: 90 days
   - Current: dnf-automatic applies security updates automatically
   - Document: Automated patching + manual verification procedures

2. **Malware update frequency ODP** (SI-3, 3.14.4)
   - ODP-SI-2: Malware signature update frequency
   - Current: Daily (ClamAV freshclam) + real-time (YARA rules)
   - Meets DoD baseline (daily)

3. **System monitoring ODP** (SI-4, 3.14.6)
   - ODP-SI-3: System monitoring frequency
   - Current: Continuous (Wazuh SIEM, real-time)
   - Exceeds DoD baseline

4. **Enhanced malware protection documentation** (SI-3, 3.14.2)
   - Document YARA custom rules implementation
   - YARA rules location: `/var/lib/yara/rules/`
   - Custom rules for: crypto miners, backdoors, rootkits, obfuscated code

**Current Implementations to Highlight:**
- ✅ dnf-automatic security patching (SI-2)
- ✅ ClamAV + YARA malware protection (SI-3)
- ✅ Wazuh SIEM continuous monitoring (SI-4)
- ✅ OpenSCAP vulnerability scanning weekly (SI-2)
- ✅ Wazuh vulnerability detection daily (SI-2)
- ✅ File integrity monitoring via Wazuh (SI-7)

**Estimated Update Effort:** 2-3 hours (add ODP values, expand YARA documentation)

---

## Policy 6/11: TCC-IRP-001 — Incident Response

### Rev 2 → Rev 3 Changes

**Control Count:** 6 controls (unchanged)

**Key Rev 3 Updates:**

1. **IR testing frequency ODP** (IR-2, 3.6.3)
   - ODP-IR-1: Incident response testing frequency
   - DoD baseline: Annually
   - Current: First tabletop planned 06/30/2026 (POA&M item)
   - **Critical gap:** Complete tabletop exercise (GAP-002 template created)

2. **Enhanced incident handling procedures** (IR-1, 3.6.1)
   - Expand determination statement coverage (28 statements vs. 18 in Rev 2)
   - Document incident categories: malware, unauthorized access, data breach, DoS, supply chain
   - Document containment strategies per incident type

3. **Incident monitoring integration** (IR-2, 3.6.2)
   - Document Wazuh SIEM integration explicitly
   - Real-time alerting (Level 10+ = Critical)
   - Incident detection → alerting → response workflow

4. **CUI breach notification** (IR-2, 3.6.2)
   - Emphasize DFARS 252.204-7012 notification requirements:
     - US-CERT within 1 hour
     - Contracting Officer within 72 hours
     - DIBnet (if DoD contract) within 72 hours
   - Document notification templates (to be created)

**Current Implementations to Highlight:**
- ✅ TCC-IRP-001 policy operational
- ✅ Wazuh SIEM monitoring and alerting
- ❌ **IR tabletop exercise not yet conducted** (target 06/30/2026)
- ⚠️ Notification templates not prepared

**Estimated Update Effort:** 2-3 hours (add ODP, expand procedures, reference GAP-002 tabletop plan)

---

## Policy 7/11: TCC-RA-001 — Risk Assessment

### Rev 2 → Rev 3 Changes

**Control Count:** 3 controls (unchanged)

**Key Rev 3 Updates:**

1. **Risk assessment frequency ODP** (RA-1, 3.11.1)
   - ODP-RA-1: Risk assessment frequency
   - DoD baseline: Annually or when significant changes
   - Current: First formal assessment planned 04/30/2026 (POA&M item)
   - **Critical gap:** Complete risk assessment (GAP-001 template created)

2. **Supply chain risk assessment integration** (RA-1, 3.11.1)
   - **NEW in Rev 3:** Must address supply chain risks
   - Integration: Conduct supply chain risk assessment as part of annual risk assessment
   - Reference: GAP-001 template includes supply chain risk section

3. **Vulnerability scanning frequency ODP** (RA-2, 3.11.2)
   - ODP-RA-2: Vulnerability scan frequency
   - DoD baseline: Monthly (OS), Quarterly (apps)
   - Current: Weekly OpenSCAP + Daily Wazuh CVE detection
   - **Exceeds DoD baseline**

4. **Vulnerability remediation ODPs** (RA-3, 3.11.3)
   - ODP-RA-3: Remediation timeframes
   - Critical: 7 days, High: 30 days, Moderate: 90 days, Low: 180 days
   - Current: dnf-automatic handles critical/high automatically
   - Document remediation tracking (Wazuh vulnerability dashboard)

**Current Implementations to Highlight:**
- ❌ **Formal risk assessment not yet conducted** (target 04/30/2026)
- ✅ OpenSCAP weekly scans (RA-2)
- ✅ Wazuh daily vulnerability detection (RA-2)
- ✅ Automated patching (RA-3)

**Estimated Update Effort:** 2-3 hours (add ODP values, reference GAP-001 template, add supply chain section)

---

## Policy 8/11: TCC-ATP-001 — Awareness & Training

### Rev 2 → Rev 3 Changes

**Control Count:** 5 controls (Rev 2) → 3 controls (Rev 3)
- **2 controls consolidated** (training records, phishing awareness merged into main controls)

**Key Rev 3 Updates:**

1. **Training frequency ODP** (AT-1, 3.2.1)
   - ODP-AT-1: Security awareness training frequency
   - Current: Annual (FY2026 training completed 2026-02)
   - Meets DoD baseline (annually)

2. **Consolidated controls** (update numbering):
   - Rev 2 3.2.3 (Role-based training) → merged into Rev 3 3.2.2
   - Rev 2 3.2.4 (Training records) → implicit requirement, not separate control
   - Rev 2 3.2.5 (Phishing awareness) → merged into Rev 3 3.2.1

3. **Enhanced insider threat training** (AT-2, 3.2.2)
   - Expand insider threat module in annual training
   - Document role-based training for administrator role
   - Reference FY2026 training modules

4. **Training effectiveness** (AT-2, 3.2.2)
   - Document training assessment (quiz results)
   - Track training completion
   - Reference: Training_Completion_Record_FY2026.md

**Current Implementations to Highlight:**
- ✅ Annual security awareness training completed (2026-02)
- ✅ Training includes: passwords, phishing, CUI handling, MFA
- ✅ Training assessment quiz (FY2026)
- ✅ Training records maintained

**Estimated Update Effort:** 1-2 hours (consolidate controls, add ODP, update references)

---

## Policy 9/11: TCC-PS-001 — Personnel Security

### Rev 2 → Rev 3 Changes

**Control Count:** 7 controls (unchanged)

**Key Rev 3 Updates:**

1. **Personnel screening ODP** (PS-1, 3.9.1)
   - ODP-PS-1: Personnel screening criteria
   - Current: Owner-operator with active security clearance
   - Exceeds DoD baseline

2. **Personnel transfer review ODP** (PS-5, 3.9.5)
   - ODP-PS-2: Personnel transfer review frequency
   - Current: N/A (solopreneur, no personnel transfers)
   - Document justification

3. **Enhanced third-party personnel procedures** (PS-7, 3.9.7)
   - Expand documentation for third-party contractors (if applicable)
   - Document vendor access procedures
   - Current: Limited third-party access (consultant review, vendor support)

4. **Personnel sanctions** (PS-3, 3.9.3)
   - Document sanctions process (though single-person operation)
   - Self-accountability: Audit logging, external review

**Current Implementations to Highlight:**
- ✅ Owner-operator holds active security clearance
- ✅ Background check completed
- ✅ No additional personnel requiring screening
- ⏸️ Third-party access limited (consultants, vendors on case-by-case basis)

**Estimated Update Effort:** 1-2 hours (add ODP values, document N/A justifications for solopreneur)

---

## Policy 10/11: TCC-PE-MP-001 — Physical & Media Protection

### Rev 2 → Rev 3 Changes

**Control Count:** 14 total (PE: 6, MP: 8 — both families unchanged)

**Key Rev 3 Updates:**

1. **Physical access log review ODP** (PE-3, 3.10.3)
   - ODP-PE-1: Physical access log review frequency
   - DoD baseline: Monthly
   - Current: Quarterly
   - Justification: Single-occupant facility, low-traffic, quarterly sufficient for low risk

2. **Physical access authorization ODP** (PE-1, 3.10.1)
   - ODP-PE-2: Physical access authorization
   - Current: Owner-operator only
   - Stricter than DoD baseline (single authorized person)

3. **Media sanitization ODP** (MP-6, 3.8.6)
   - ODP-MP-1: Media sanitization methods
   - Current: NIST SP 800-88 Rev 1 (Clear, Purge, Destroy)
   - Meets DoD baseline

4. **Enhanced backup protection** (MP-9, 3.8.9)
   - Document encrypted backup procedures
   - Backup to NAS: encrypted (LUKS), daily, 3-2-1 strategy
   - Test restoration quarterly (add to policy)

**Current Implementations to Highlight:**
- ✅ Locked server room (physical access control)
- ✅ Physical access logs maintained
- ✅ NIST 800-88 media sanitization procedures
- ✅ Encrypted backups to NAS (MP-9)
- ⚠️ Physical access log review quarterly (more permissive than monthly DoD baseline, justified)

**Estimated Update Effort:** 1-2 hours (add ODP values, justify quarterly review)

---

## Policy 11/11: TCC-AUP-001 — Acceptable Use Policy

### Rev 2 → Rev 3 Changes

**No direct NIST 800-171 Rev 3 control mapping** (policy supports multiple families)

**Key Rev 3 Updates:**

1. **Cross-reference to Rules of Behavior** (PL-4, 3.12.4)
   - Rev 3 introduces explicit Rules of Behavior requirement (new Planning family)
   - Current: TCC-AUP-001 Section 2 implicitly serves as Rules of Behavior
   - Options:
     - **Option A:** Rebrand TCC-AUP-001 Section 2 as "Rules of Behavior"
     - **Option B:** Create standalone Rules of Behavior document (Phase 3, Activity 3.5)
     - **Option C:** Add forward reference: "TCC-AUP-001 satisfies PL-4 Rules of Behavior requirement"

2. **MFA acknowledgment** (IA-2, 3.5.3)
   - Update policy to reflect MFA deployment (2026-02-21)
   - Users must use SSH key + TOTP for all remote access
   - Acknowledge in acceptable use: "I will protect my SSH private key and TOTP secret"

3. **CUI handling procedures** (multiple controls)
   - Ensure CUI handling procedures comprehensive:
     - CUI marking requirements
     - CUI storage restrictions (no cloud, personal devices)
     - CUI transmission security (encrypted email, secure file transfer)
     - CUI disposal (secure deletion, media sanitization)

4. **Portable media restrictions** (MP-7, 3.8.7)
   - Update policy for USB storage restrictions
   - Document approved portable media (if any)
   - Reference USBGuard (if deployed)

**Current Implementations to Highlight:**
- ✅ TCC-AUP-001 comprehensive acceptable use policy
- ✅ Covers CUI handling, remote access, portable media, email, internet use
- ⚠️ Update for MFA (deployed 2026-02-21)
- ⚠️ Cross-reference to Planning family Rules of Behavior (PL-4)

**Estimated Update Effort:** 1-2 hours (add MFA acknowledgment, cross-reference PL-4)

---

## Summary: All 11 Policies Update Effort

| # | Policy | Family | Priority | Effort | Key Rev 3 Changes |
|---|--------|--------|----------|--------|-------------------|
| ✅ 1 | TCC-AAP-001 | Audit & Accountability | HIGH | 2-3 hrs | ODP values, Audit Event Inventory requirement, 100% implementation |
| ✅ 2 | TCC-IAP-001 | Identification & Authentication | HIGH | 2-3 hrs | **MFA deployment details**, ODP values, FreeIPA integration |
| ✅ 3 | TCC-CMP-001 | Configuration Management | HIGH | 2-3 hrs | Baseline selection (PL-10), 100% OpenSCAP achievement, Configuration Baseline Document |
| 4 | TCC-SCP-001 | System & Communications Protection | HIGH | 3-4 hrs | Network diagram requirement, FIPS certs, consolidated controls (23→20) |
| 5 | TCC-SI-001 | System & Information Integrity | HIGH | 2-3 hrs | ODP values, YARA documentation, patching procedures |
| 6 | TCC-IRP-001 | Incident Response | MEDIUM | 2-3 hrs | IR testing ODP (tabletop 06/30), notification templates, GAP-002 reference |
| 7 | TCC-RA-001 | Risk Assessment | MEDIUM | 2-3 hrs | Risk assessment ODP (04/30), supply chain integration, GAP-001 reference |
| 8 | TCC-ATP-001 | Awareness & Training | MEDIUM | 1-2 hrs | Training frequency ODP, consolidated controls (5→3), FY2026 training |
| 9 | TCC-PS-001 | Personnel Security | MEDIUM | 1-2 hrs | Screening ODP, N/A justifications for solopreneur, clearance holder |
| 10 | TCC-PE-MP-001 | Physical & Media Protection | LOW | 1-2 hrs | Physical access review ODP (quarterly vs monthly), backup procedures |
| 11 | TCC-AUP-001 | Acceptable Use | LOW | 1-2 hrs | MFA acknowledgment, PL-4 cross-reference (Rules of Behavior) |

**Total Estimated Effort:** 20-28 hours for all 11 policy updates

**Completed (full policies):** 3/11 (AAP, IAP, CMP) = ~6 hours of detailed work
**Remaining:** 8/11 summaries provided above

---

## Next Steps for User

### Option A: Expand summaries into full policies yourself
- Use the 3 complete policies (AAP, IAP, CMP) as templates
- Follow the update guidance in each summary above
- Estimated effort: 14-22 hours

### Option B: Request full policy expansions from Claude
- Ask me to create full comprehensive policies for any of the 8 remaining
- I can do them individually or in batches
- Example: "Create full TCC-SCP-001 policy" or "Create full policies 4-6"

### Option C: Use summaries as-is during Phase 2 review
- These summaries document the key Rev 3 changes
- Sufficient for understanding what needs updating
- Expand to full policies later (Phase 4 or during final review)

---

## Integration with New Policies (Already Created)

**3 NEW Rev 3 Policies (Complete):**
- ✅ TCC-SPP-001 — System Security Planning Policy (Planning family)
- ✅ TCC-SAP-001 — System & Services Acquisition Policy (SA family)
- ✅ TCC-SRMP-001 — Supply Chain Risk Management Policy (SR family)

**Total Phase 2 Policy Deliverables:**
- 11 updated existing policies (3 complete, 8 summaries)
- 3 new policies (complete)
- **= 14 policies for Rev 3 compliance**

---

**Document Created:** March 18, 2026
**Status:** DRAFT summaries for policies 4-11
**Next:** Create "Key Differences Rev 2 → Rev 3" summary document
