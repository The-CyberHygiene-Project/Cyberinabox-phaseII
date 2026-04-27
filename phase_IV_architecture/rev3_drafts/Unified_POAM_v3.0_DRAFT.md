# Plan of Action and Milestones (POA&M) v3.0

**System:** CyberHygiene Production Network (CPN)
**Framework:** NIST SP 800-171 Revision 3
**POA&M Version:** 3.0 (Rev 3 Transition Tracking)
**Date:** March 18, 2026
**Owner:** sysadmin (System Owner, Authorizing Official)
**Update Frequency:** Monthly (per TCC-SPP-001 Section 4.1.3)
**Last Update:** March 18, 2026
**Next Review:** April 15, 2026

---

## Executive Summary

### Current Compliance Status

**NIST SP 800-171 Revision 2:**
- **SPRS Score:** 106/110 (96.4%)
- **OpenSCAP Compliance:** 100% (104/104 rules passing on all 4 systems)
- **Outstanding Gaps:** 2 controls (-4 SPRS points)
  - 3.11.1 (RA-3): Periodic Risk Assessment — -3 points
  - 3.6.3 (IR-3): Incident Response Testing — -1 point

**NIST SP 800-171 Revision 3 (Transition):**
- **Implementation Status:** 80.4% fully implemented (78 of 97 controls)
- **Determination Statements:** 340 of 422 MET (80.6%)
- **Transition Phase:** Phase 2 (Documentation) — 50% complete
- **Target Completion:** September 15, 2026 (6-month timeline)

### POA&M Item Count

| Status | Rev 2 Items | Rev 3 Items | Total |
|--------|-------------|-------------|-------|
| **OPEN** | 2 | 19 | 21 |
| **IN PROGRESS** | 0 | 6 | 6 |
| **CLOSED** | 8 | 0 | 8 |
| **TOTAL** | 10 | 25 | 35 |

### Key Milestones

| Milestone | Target Date | Status | Impact |
|-----------|-------------|--------|--------|
| Risk Assessment (RA-3) | 04/30/2026 | OPEN | +3 SPRS points when complete |
| IR Testing (IR-3) | 06/30/2026 | OPEN | +1 SPRS point when complete |
| Phase 2 Policies Complete | 04/15/2026 | IN PROGRESS | 14 Rev 3 policies (6/14 done) |
| Phase 3 Technical Complete | 06/15/2026 | PLANNED | SBOM v3.0, diagrams, evidence |
| Phase 4 Validation Complete | 09/15/2026 | PLANNED | 422 determination statements |
| **100% Rev 2 Compliance** | **06/30/2026** | **ON TRACK** | **SPRS 110/110** |
| **95%+ Rev 3 Compliance** | **09/15/2026** | **ON TRACK** | **Rev 3 assessment ready** |

---

## POA&M Item Categories

### Category 1: Rev 2 Remaining Gaps (2 items)
Critical items blocking 100% Rev 2 compliance (110/110 SPRS)

### Category 2: Rev 3 Documentation Gaps (6 items)
Phase 2 policy and SSP documentation updates

### Category 3: Rev 3 Technical Gaps (8 items)
Phase 3 technical implementations and evidence artifacts

### Category 4: Rev 3 Validation Gaps (5 items)
Phase 4 assessment preparation and determination statement validation

### Category 5: Closed Items (8 items)
Historical tracking of completed POA&M items

---

## CATEGORY 1: Rev 2 Remaining Gaps

### POA&M-001: Periodic Risk Assessment (3.11.1 / RA-3)

**Control Family:** Risk Assessment (RA)
**Control ID:** 3.11.1 (Rev 2), 3.11.1 (Rev 3 — unchanged)
**Severity:** HIGH
**SPRS Impact:** -3 points (current: 106/110, target: 109/110)
**Status:** OPEN
**Priority:** P1 (Critical Path)

**Control Requirement:**
```
Periodically assess the risk to organizational operations (including mission,
functions, image, or reputation), organizational assets, and individuals,
resulting from the operation of organizational systems and the associated
processing, storage, or transmission of CUI.
```

**Gap Description:**
Formal, documented risk assessment has not been conducted. Informal risk analysis
occurs continuously via OpenSCAP scanning, Wazuh monitoring, and vulnerability
management, but no comprehensive risk assessment report exists per NIST SP 800-30 Rev 1
methodology.

**Impact:**
- -3 SPRS points (largest single gap)
- Limits ability to demonstrate risk-based decision making to assessors
- Required for CMMC Level 2 certification

**Remediation Plan:**
1. Use GAP001_Risk_Assessment_Template.md (32-hour framework, Phase 1 deliverable)
2. Conduct formal risk assessment using NIST SP 800-30 Rev 1 methodology:
   - Identify threats (nation-states, cybercriminals, insiders, natural disasters)
   - Identify vulnerabilities (system weaknesses, process gaps, human factors)
   - Calculate risk levels (likelihood × impact matrix)
   - Develop risk mitigation strategies (accept, avoid, mitigate, transfer)
3. Document 15+ risk scenarios (pre-populated in GAP001):
   - Ransomware attack (HIGH likelihood, HIGH impact)
   - Insider threat (LOW likelihood, MEDIUM impact — solopreneur mitigates)
   - Supply chain compromise (MEDIUM likelihood, MEDIUM impact)
   - Physical theft/damage (LOW likelihood, HIGH impact)
   - [Continue for all 15 scenarios]
4. Create Risk Assessment Report (20-30 pages)
5. Brief findings to Authorizing Official (sysadmin)
6. Update TCC-RA-001 Risk Management Policy with assessment results
7. Update POA&M to reflect any newly identified risks
8. Close POA&M-001

**Resources Required:**
- **Effort:** 32 hours (sysadmin)
- **References:** NIST SP 800-30 Rev 1, GAP001 template, CMMC Assessment Guide
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** April 1, 2026
- **Target Completion:** April 30, 2026
- **Review/Approval:** May 5, 2026
- **POA&M Closure:** May 5, 2026

**Success Criteria:**
- [ ] Risk Assessment Report completed per NIST SP 800-30 Rev 1
- [ ] 15+ risk scenarios documented with likelihood/impact scores
- [ ] Risk mitigation strategies defined for HIGH/MEDIUM risks
- [ ] Authorizing Official (sysadmin) briefs and approves report
- [ ] TCC-RA-001 updated with assessment reference
- [ ] SPRS score increases to 109/110

**Risks to Completion:**
- **Resource constraint:** 32 hours is significant time commitment (mitigate: block calendar, prioritize)
- **Scope creep:** Risk assessment can expand indefinitely (mitigate: use GAP001 template boundaries)

**Notes:**
- GAP001 template pre-populates 15 risk scenarios based on CyberHygiene environment
- Methodology aligns with CMMC Assessment Guide expectations
- Once complete, repeat every 3 years or upon significant system changes (per ODP-RA-1)

**Last Updated:** March 18, 2026

---

### POA&M-002: Incident Response Testing (3.6.3 / IR-3)

**Control Family:** Incident Response (IR)
**Control ID:** 3.6.3 (Rev 2), 3.6.3 (Rev 3 — unchanged)
**Severity:** MEDIUM
**SPRS Impact:** -1 point (current: 106/110, target: 110/110)
**Status:** OPEN
**Priority:** P1 (Critical Path)

**Control Requirement:**
```
Test the organizational incident response capability.
```

**Gap Description:**
Incident Response Plan (TCC-IRP-001) exists and is comprehensive, but has not been
tested via tabletop exercise, simulation, or actual incident response. Rev 3 requires
annual testing (ODP-IR-1).

**Impact:**
- -1 SPRS point
- Unknown effectiveness of IR plan until tested
- May discover gaps in procedures, roles, communications during actual incident

**Remediation Plan:**
1. Use GAP002_IR_Tabletop_Exercise_Plan.md (8-hour ransomware exercise, Phase 1 deliverable)
2. Conduct tabletop exercise with 5 injects:
   - **Inject 1:** Initial phishing email detection (Wazuh alert)
   - **Inject 2:** Ransomware execution and lateral movement
   - **Inject 3:** Critical system encryption and ransom demand
   - **Inject 4:** Backup recovery and system restoration
   - **Inject 5:** Post-incident analysis and lessons learned
3. Document participant responses (sysadmin as all roles: ISSO, Admin, AO)
4. Identify gaps in IR plan, communication procedures, technical response
5. Update TCC-IRP-001 Incident Response Policy based on findings
6. Document results in Tabletop Exercise Report (10-15 pages)
7. Close POA&M-002

**Resources Required:**
- **Effort:** 8 hours (sysadmin)
- **References:** GAP002 exercise plan, TCC-IRP-001, NIST SP 800-61 Rev 2
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** June 15, 2026
- **Target Completion:** June 30, 2026
- **Review/Approval:** July 5, 2026
- **POA&M Closure:** July 5, 2026

**Success Criteria:**
- [ ] Tabletop exercise conducted with all 5 injects
- [ ] Responses documented for each inject (decision points, actions taken)
- [ ] Gaps identified and documented (e.g., backup recovery time, communication procedures)
- [ ] TCC-IRP-001 updated based on findings
- [ ] Tabletop Exercise Report completed
- [ ] SPRS score increases to 110/110 (100% Rev 2 compliance)

**Risks to Completion:**
- **Scheduling:** Easy to defer non-critical testing (mitigate: calendar block, accountability)
- **Solopreneur challenge:** Limited ability to simulate multi-person response (mitigate: document workarounds)

**Notes:**
- GAP002 tabletop is ransomware-focused (most likely high-impact scenario)
- Exercise can be conducted solo (document how solopreneur would handle each role)
- Repeat annually per ODP-IR-1 (next: July 2027)
- Once complete, CyberHygiene achieves **110/110 SPRS (100% Rev 2 compliance)**

**Last Updated:** March 18, 2026

---

## CATEGORY 2: Rev 3 Documentation Gaps

### POA&M-101: Complete Remaining 8 Policy Updates (Rev 3)

**Control Families:** Multiple (SC, SI, IR, RA, AT, PS, PE-MP, AUP)
**Severity:** MEDIUM
**SPRS Impact:** None (documentation gap, not technical control gap)
**Status:** IN PROGRESS
**Priority:** P2 (Phase 2 Deliverable)

**Gap Description:**
8 of 14 policies have Rev 3 update summaries created but need expansion to full
comprehensive policies for assessment readiness. Summaries exist in
POLICIES_4-11_Rev3_Update_Summaries.md (15-22 hours estimated effort).

**Policies Requiring Expansion:**
1. TCC-SCP-001: System and Communications Protection Policy v2.0 (2-3 hours)
2. TCC-SI-001: System and Information Integrity Policy v2.0 (2-3 hours)
3. TCC-IRP-001: Incident Response Policy v2.0 (2-3 hours)
4. TCC-RA-001: Risk Management Policy v2.0 (2-3 hours)
5. TCC-ATP-001: Awareness and Training Policy v2.0 (1-2 hours)
6. TCC-PS-001: Personnel Security Policy v2.0 (1-2 hours)
7. TCC-PE-MP-001: Physical and Media Protection Policy v2.0 (2 hours combined)
8. TCC-AUP-001: Acceptable Use Policy v2.0 (0.5-1 hour)

**Completed Policies (6 of 14):**
- ✅ TCC-SPP-001: System Security Planning Policy v1.0 (NEW)
- ✅ TCC-SAP-001: System and Services Acquisition Policy v1.0 (NEW)
- ✅ TCC-SRMP-001: Supply Chain Risk Management Policy v1.0 (NEW)
- ✅ TCC-AAP-001: Audit and Accountability Policy v2.0 (Rev 3 update)
- ✅ TCC-IAP-001: Identification and Authentication Policy v2.0 (Rev 3 update)
- ✅ TCC-CMP-001: Configuration Management Policy v2.0 (Rev 3 update)

**Remediation Plan:**
1. Use POLICIES_4-11_Rev3_Update_Summaries.md as detailed guidance
2. Expand each summary to full policy (1-3 hours per policy)
3. Add Rev 3 control references, ODP values, determination statement mappings
4. Update implementation sections with current technical controls
5. Review and approve each policy
6. Move from `/Rev3/Transition/Phase2_Documentation/` to `/Rev3/Policies/[family]/`
7. Update Control-to-Policy Quick Reference Rev 3

**Resources Required:**
- **Effort:** 15-22 hours (sysadmin or AI assistance)
- **References:** POLICIES_4-11_Rev3_Update_Summaries.md, existing Rev 2 policies
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** March 25, 2026
- **Target Completion:** April 15, 2026
- **POA&M Closure:** April 15, 2026

**Success Criteria:**
- [ ] All 8 policies expanded from summaries to full comprehensive policies
- [ ] All policies reviewed and approved by sysadmin (System Owner)
- [ ] All policies moved to `/Rev3/Policies/` directories
- [ ] Control-to-Policy Quick Reference Rev 3 updated with all 14 policies
- [ ] Phase 2 policy work 100% complete (14/14 policies)

**Last Updated:** March 18, 2026

---

### POA&M-102: Create System Security Plan (SSP) v3.0

**Control Family:** Planning (PL)
**Control ID:** PL-2 (System Security Plans)
**Severity:** HIGH
**SPRS Impact:** None (documentation requirement, not scored)
**Status:** IN PROGRESS
**Priority:** P1 (Critical Path — required for Rev 3 assessment)

**Gap Description:**
SSP v2.9 exists for Rev 2 (110 controls, 14 families), but Rev 3 requires reorganization
to 97 controls across 17 families with 3 new families (PL, SA, SR) and 49 ODPs
documented.

**Current Status:**
- SSP v2.9 (Rev 2): EXISTS — strong foundation
- SSP v3.0 Creation Framework: COMPLETE (104KB framework document with complete guidance)
- SSP v3.0 (Rev 3): NOT STARTED (estimated 20-30 hours using framework)

**Remediation Plan:**
1. Use SSP_v3.0_Creation_Framework.md (Phase 2 deliverable, complete guidance)
2. Follow **Option B: Strategic Update** approach (20-30 hours):
   - Start with SSP v2.9 as foundation
   - Reorganize from 110 controls → 97 controls
   - Add sections for 3 new families (PL, SA, SR)
   - Update significantly changed controls (IA, AU, CM, IR, RA, SC, SI)
   - Document all 49 ODPs in Section 21 and Appendix E
   - Create determination statement evidence mapping (Section 22)
   - Add Executive Summary (Section 0 — new in v3.0)
3. Use Section 6 (AU — Audit & Accountability) example as template for all families
4. Add Phase 3 deliverable placeholders (network diagrams, SBOM v3.0, evidence artifacts)
5. Review and approve SSP v3.0
6. Sign signature page (Appendix F)

**Resources Required:**
- **Effort:** 20-30 hours (sysadmin, using framework)
- **References:** SSP v2.9 (foundation), SSP_v3.0_Creation_Framework.md (guidance), Phase 1-2 deliverables
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** April 1, 2026
- **Target Completion:** May 15, 2026
- **Review/Approval:** May 20, 2026
- **POA&M Closure:** May 20, 2026

**Success Criteria:**
- [ ] SSP v3.0 reorganized for 97 Rev 3 controls across 17 families
- [ ] All 3 new families documented (PL, SA, SR)
- [ ] All 49 ODPs documented in Section 21 and Appendix E
- [ ] Determination statement evidence mapping created (Section 22, 422 statements)
- [ ] Executive Summary added (Section 0)
- [ ] Signature page signed by sysadmin (Authorizing Official)
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/SSP/System_Security_Plan_v3.0.docx`

**Notes:**
- Framework provides complete outline, section-by-section guidance, example (AU family)
- Strategic Update (Option B) leverages strong SSP v2.9 foundation for efficiency
- SSP v3.0 is largest single Phase 2 deliverable (estimated 40-50% of Phase 2 effort)

**Last Updated:** March 18, 2026

---

### POA&M-103: Create Control-to-Policy Quick Reference Rev 3

**Control Family:** Planning (PL)
**Control ID:** PL-2 (System Security Plans — supporting document)
**Severity:** LOW
**SPRS Impact:** None (supporting documentation)
**Status:** OPEN
**Priority:** P3 (Nice-to-have, not blocking)

**Gap Description:**
Control_to_Policy_Quick_Reference.md exists for Rev 2 (110 controls → 11 policies),
but Rev 3 version needed for 97 controls → 14 policies with 3 new families.

**Remediation Plan:**
1. Use Control_to_Policy_Quick_Reference.md (Rev 2) as template
2. Create new file: Control_to_Policy_Quick_Reference_Rev3.md
3. Map all 97 Rev 3 controls to 14 Rev 3 policies:
   - 3 new policies: TCC-SPP-001 (PL), TCC-SAP-001 (SA), TCC-SRMP-001 (SR)
   - 11 updated policies: TCC-AAP-001, TCC-IAP-001, TCC-CMP-001, TCC-SCP-001, etc.
4. Add columns: Rev 2 Control ID (if changed), Rev 3 Control ID, Policy, Section
5. Include in SSP v3.0 Appendix D

**Resources Required:**
- **Effort:** 4-6 hours (sysadmin or AI assistance)
- **References:** Control_to_Policy_Quick_Reference.md (Rev 2 template), 14 Rev 3 policies
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** April 20, 2026
- **Target Completion:** April 25, 2026
- **POA&M Closure:** April 25, 2026

**Success Criteria:**
- [ ] All 97 Rev 3 controls mapped to 14 policies
- [ ] Quick reference table created (similar to Rev 2 format)
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/Policies/Control_to_Policy_Quick_Reference_Rev3.md`
- [ ] Referenced in SSP v3.0 Appendix D

**Last Updated:** March 18, 2026

---

### POA&M-104: Rev 3 Policy Approval and Activation

**Control Family:** Planning (PL)
**Control ID:** PL-2 (System Security Plans)
**Severity:** MEDIUM
**SPRS Impact:** None (process requirement)
**Status:** OPEN
**Priority:** P2 (Required before operational use)

**Gap Description:**
14 Rev 3 policies exist as drafts in `/Rev3/Transition/Phase2_Documentation/` but
need formal approval and activation before operational use.

**Policies Requiring Approval:**
- 3 NEW policies: TCC-SPP-001, TCC-SAP-001, TCC-SRMP-001
- 11 UPDATED policies: TCC-AAP-001 v2.0, TCC-IAP-001 v2.0, TCC-CMP-001 v2.0, etc.

**Remediation Plan:**
1. Complete all 14 policies (POA&M-101 addresses 8 remaining)
2. Conduct final review of all 14 policies (sysadmin as System Owner)
3. Sign approval page on each policy
4. Update effective date to approval date
5. Remove "_DRAFT" suffix from filenames
6. Move from `/Rev3/Transition/Phase2_Documentation/` to `/Rev3/Policies/[family]/`
7. Update SSP v3.0 Section 24.1 (Related Documentation) with activation dates
8. Communicate policy activation to future users (when applicable)

**Resources Required:**
- **Effort:** 4-6 hours (final review and approval process)
- **References:** TCC-SPP-001 Section 4.1.2 (policy review procedures)
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** May 1, 2026
- **Target Completion:** May 15, 2026
- **POA&M Closure:** May 15, 2026

**Success Criteria:**
- [ ] All 14 policies reviewed and approved by sysadmin (System Owner)
- [ ] Approval signatures/dates on all policy documents
- [ ] "_DRAFT" removed from all filenames
- [ ] All policies moved to `/Rev3/Policies/` operational directories
- [ ] SSP v3.0 updated with policy activation dates
- [ ] Control-to-Policy Quick Reference Rev 3 updated with final policy references

**Last Updated:** March 18, 2026

---

### POA&M-105: Key Differences Document Refinement

**Control Family:** Planning (PL)
**Control ID:** PL-2 (System Security Plans — supporting document)
**Severity:** LOW
**SPRS Impact:** None (supporting documentation)
**Status:** COMPLETE
**Priority:** P3 (Optional enhancement)

**Gap Description:**
Rev2_to_Rev3_Key_Differences_Summary.md exists (47KB, comprehensive) but may benefit
from user feedback and refinement after initial policy review.

**Remediation Plan:**
1. User reviews Key Differences document
2. Provide feedback on clarity, completeness, usefulness
3. Refine based on feedback (if needed)
4. Use as reference during policy and SSP review

**Resources Required:**
- **Effort:** 0-2 hours (refinement only if user requests changes)
- **Budget:** $0

**Timeline:**
- **Start Date:** March 18, 2026
- **Target Completion:** March 25, 2026 (or as needed)
- **POA&M Closure:** Upon user acceptance or "no changes needed"

**Success Criteria:**
- [ ] User reviews Key Differences document
- [ ] User provides feedback (or confirms no changes needed)
- [ ] Refinements made (if applicable)
- [ ] Document serves as useful policy review aid

**Status:** COMPLETE — Document created March 18, 2026. Awaiting user review.

**Last Updated:** March 18, 2026

---

### POA&M-106: SSP v3.0 Framework Utilization

**Control Family:** Planning (PL)
**Control ID:** PL-2 (System Security Plans)
**Severity:** MEDIUM
**SPRS Impact:** None (process tool)
**Status:** COMPLETE
**Priority:** P1 (Enables POA&M-102)

**Gap Description:**
SSP v3.0 creation requires comprehensive framework to ensure all Rev 3 requirements
addressed efficiently.

**Remediation Plan:**
1. Create SSP v3.0 Creation Framework with:
   - Complete outline (Sections 0-24 + Appendices A-F)
   - Section-by-section guidance for all 17 control families
   - Complete example (AU family with all controls, ODPs, determination statements)
   - Implementation checklist (8 phases)
   - 3 approach options (Full Rewrite, Strategic Update, Phased)
2. Use framework for SSP v3.0 creation (POA&M-102)

**Resources Required:**
- **Effort:** 10-12 hours (framework creation)
- **Budget:** $0

**Timeline:**
- **Start Date:** March 18, 2026
- **Target Completion:** March 18, 2026
- **POA&M Closure:** March 18, 2026

**Success Criteria:**
- [✅] Complete SSP outline with all sections
- [✅] Section-by-section guidance for 17 families
- [✅] Complete AU family example (all controls documented)
- [✅] Implementation checklist (8 phases, detailed)
- [✅] 3 approach options with effort estimates
- [✅] File location: `/home/sysadmin/CyberSecurity/Rev3/Transition/Phase2_Documentation/SSP_v3.0_Creation_Framework.md`

**Status:** COMPLETE — Framework created March 18, 2026 (104KB). Ready for use in POA&M-102.

**Last Updated:** March 18, 2026

---

## CATEGORY 3: Rev 3 Technical Gaps

### POA&M-201: Software Bill of Materials (SBOM) v3.0 Enhancement

**Control Family:** Supply Chain Risk Management (SR)
**Control ID:** SR-2, SR-4 (Supply Chain Risk Management Plan, Provenance)
**Severity:** MEDIUM
**SPRS Impact:** None (Rev 3 enhancement)
**Status:** OPEN
**Priority:** P2 (Phase 3 Deliverable)

**Gap Description:**
SBOM v2.4 exists with 5,626 packages tracked, but Rev 3 SR family requires enhanced
supply chain provenance, critical component designation, and source repository documentation.

**Current Status:**
- SBOM v2.4: EXISTS — strong foundation (5,626 packages across 6 systems)
- Format: Markdown table with columns: Package Name, Version, System, Update Date
- Update frequency: Weekly (automated collection via script)

**Enhancement Requirements (v3.0):**
1. Add column: **Source Repository URL** (e.g., https://dl.rockylinux.org/pub/rocky/9/...)
2. Add column: **GPG Signature Status** (Verified / Not Verified / N/A)
3. Add column: **Critical Component** (Yes / No) — flag top 100 critical packages
4. Add column: **Last Update Date** (from package metadata)
5. Add column: **Update Frequency** (Daily / Weekly / Monthly / As Needed)
6. Add section: **Top 100 Critical Components** detailed documentation
7. Add section: **Supply Chain Trust Chain** (Rocky Linux → RHEL → upstream source)
8. Add section: **GPG Key Management** (keyring, verification procedures)

**Top 100 Critical Components (examples):**
- freeipa-server (identity management core)
- wazuh-manager, wazuh-agent (SIEM core)
- auditd (audit logging)
- kernel (operating system core)
- openssl, gnutls (cryptography)
- openssh-server (remote access)
- sudo (privilege escalation)
- [Continue to 100...]

**Remediation Plan:**
1. Export current SBOM v2.4 data
2. Add 5 new columns with populated data:
   - Query RPM database for source URLs: `rpm -qi <package> | grep URL`
   - Verify GPG signatures: `rpm --checksig <package>`
   - Manually designate top 100 critical components (security workstation2 judgment)
   - Extract last update dates: `rpm -qi <package> | grep "Install Date"`
   - Determine update frequency based on package type (kernel=monthly, security tools=weekly, etc.)
3. Create Top 100 Critical Components section with justifications
4. Document supply chain trust chain: Rocky Linux → RHEL → upstream (kernel.org, OpenSSL, etc.)
5. Document GPG key management procedures
6. Generate SBOM v3.0 (estimated 6,000+ packages as systems updated)
7. Integrate into SSP v3.0 Section 19 (SR family) and Appendix

**Resources Required:**
- **Effort:** 16-24 hours (data collection, analysis, documentation)
- **References:** SBOM v2.4 (foundation), TCC-SRMP-001 (policy guidance), NIST SP 800-161 (supply chain)
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** May 1, 2026
- **Target Completion:** May 30, 2026
- **POA&M Closure:** May 30, 2026

**Success Criteria:**
- [ ] SBOM v3.0 with 5 new columns (source URL, GPG status, critical flag, update date, frequency)
- [ ] Top 100 Critical Components documented with justifications
- [ ] Supply chain trust chain documented (Rocky → RHEL → upstream)
- [ ] GPG key management procedures documented
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/Evidence/Software_Inventory/Software_Bill_of_Materials_v3.0.md`
- [ ] Referenced in SSP v3.0 Section 19 (SR family)

**Notes:**
- SBOM v2.4 provides strong foundation (rare for organizations this size)
- Enhancement to v3.0 positions CyberHygiene as supply chain security leader
- Automated script can maintain v3.0 format going forward (weekly updates)

**Last Updated:** March 18, 2026

---

### POA&M-202: Network Architecture Diagram

**Control Family:** System and Communications Protection (SC)
**Control ID:** SC-7 (Boundary Protection)
**Severity:** MEDIUM
**SPRS Impact:** None (evidence enhancement)
**Status:** OPEN
**Priority:** P2 (Phase 3 Deliverable)

**Gap Description:**
Network topology exists but formal network architecture diagram with security boundaries,
CUI data flows, and external connections not yet created for SSP v3.0 and assessor review.

**Current Status:**
- Network topology: OPERATIONAL (10.0.0.X/24, pfSense firewall, 4 workstations, dc1, NAS)
- Diagram: DOES NOT EXIST (described in text, but no visual diagram)

**Remediation Plan:**
1. Create professional network architecture diagram using draw.io or Visio:
   - **Layer 1: Internet Boundary**
     - ISP connection
     - pfSense firewall (10.0.0.1)
     - Firewall icon with "default-deny ruleset" label
   - **Layer 2: Internal Network (10.0.0.X/24)**
     - dc1.example.local (10.0.0.10) — FreeIPA, Wazuh Manager
     - workstation1.example.local (10.0.0.115) — Primary Workstation
     - workstation2.example.local (10.0.0.104) — Dev Workstation
     - workstation3.example.local (10.0.0.113) — Business Workstation
     - ai.example.local (10.0.0.7) — AI/ML Workstation
     - NAS (192.168.1.[X]) — Backup Storage
   - **Layer 3: External Services**
     - SSL.com (TLS certificates)
     - Rocky Linux repositories (package updates)
     - Let's Encrypt (TLS certificates)
     - NTP servers (time sync)
     - DNS forwarders (Google 8.8.8.8, Cloudflare 1.1.1.1)
   - **Security Boundaries:**
     - Dotted line around internal network (authorization boundary)
     - Red line for internet boundary (trust boundary)
   - **CUI Data Flows:**
     - Red arrows showing CUI paths (workstations → NAS, workstations → dc1 for auth)
     - Green arrows for audit logs (all systems → Wazuh on dc1)
   - **Legend:**
     - Color coding (red=CUI, green=audit, blue=management, gray=infrastructure)
     - Icon key (server, workstation, firewall, cloud service, storage)
2. Create editable source file (draw.io XML or Visio .vsdx)
3. Export to PDF for SSP v3.0 inclusion
4. Include in SSP v3.0 Section 3.1 (Network Topology) and Appendix C

**Resources Required:**
- **Effort:** 8-12 hours (diagram creation, refinement, documentation)
- **Tools:** draw.io (free), Visio (if available), or similar
- **References:** Current network configuration, pfSense config, FreeIPA topology
- **Budget:** $0 (free tools available)

**Timeline:**
- **Start Date:** May 15, 2026
- **Target Completion:** May 30, 2026
- **POA&M Closure:** May 30, 2026

**Success Criteria:**
- [ ] Professional network architecture diagram created
- [ ] Shows all 6 systems, firewall, NAS, external services
- [ ] Security boundaries clearly marked (dotted lines)
- [ ] CUI data flows documented (red arrows)
- [ ] Legend included (colors, icons)
- [ ] Editable source file saved (draw.io XML or .vsdx)
- [ ] PDF exported for SSP v3.0
- [ ] File locations:
  - `/home/sysadmin/CyberSecurity/Rev3/Evidence/Network_Architecture_Diagram_v1.0.pdf` (PDF)
  - `/home/sysadmin/CyberSecurity/Rev3/Evidence/Network_Architecture_Diagram_v1.0.drawio` (source)
- [ ] Referenced in SSP v3.0 Section 3.1 and Appendix C

**Last Updated:** March 18, 2026

---

### POA&M-203: Configuration Baseline Document

**Control Family:** Planning (PL), Configuration Management (CM)
**Control ID:** PL-10 (Baseline Selection), CM-2 (Baseline Configuration)
**Severity:** MEDIUM
**SPRS Impact:** None (documentation enhancement)
**Status:** OPEN
**Priority:** P2 (Phase 3 Deliverable)

**Gap Description:**
OpenSCAP CUI profile is implicit baseline (100% compliance), but Rev 3 PL-10 requires
formal baseline selection documentation with rationale and management procedures.

**Current Status:**
- Baseline: SCAP Security Guide CUI profile for Rocky Linux 9
- Compliance: 100% (104/104 rules passing on all 4 systems)
- Documentation: DOES NOT EXIST (implied in OpenSCAP usage, not formally documented)

**Remediation Plan:**
1. Create Configuration Baseline Document (10-15 pages):
   - **Section 1: Baseline Selection Rationale**
     - Why SCAP Security Guide CUI profile selected
     - Alignment with NIST SP 800-53 Rev 5
     - DoD approval and widespread adoption
     - Technical coverage (104 rules across AC, AU, CM, IA, SC, SI families)
   - **Section 2: Baseline Content**
     - List all 104 OpenSCAP rules with control mappings
     - Document rule groups (partitions, passwords, services, accounts, audit, etc.)
     - Reference SCAP Security Guide documentation
   - **Section 3: Baseline Management Procedures**
     - Weekly OpenSCAP scans (automated, Tuesdays)
     - Dashboard monitoring: https://dc1.example.local/dashboard/openscap-dashboard.html
     - Exception process (document any deviations from baseline)
     - Update procedures (when SCAP Security Guide releases new profile versions)
   - **Section 4: Baseline Compliance Status**
     - Current: 100% (104/104 rules passing, 0 fail, as of 2026-02-21)
     - Historical: Track compliance over time
     - Deviation log: Document any temporary or permanent deviations
   - **Section 5: Baseline Review Schedule**
     - Annual review of baseline selection (PL-10)
     - Quarterly review of compliance status (CM-2)
     - Triggered review upon SCAP Security Guide updates
2. Reference OpenSCAP dashboard as evidence
3. Include sample OpenSCAP scan report as appendix
4. Integrate into SSP v3.0 Section 14 (PL-10) and Section 7 (CM-2)

**Resources Required:**
- **Effort:** 6-8 hours (documentation, OpenSCAP rule analysis)
- **References:** SCAP Security Guide documentation, OpenSCAP scan reports, TCC-CMP-001, TCC-SPP-001
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** May 20, 2026
- **Target Completion:** June 5, 2026
- **POA&M Closure:** June 5, 2026

**Success Criteria:**
- [ ] Configuration Baseline Document created (10-15 pages)
- [ ] Baseline selection rationale documented (PL-10 requirement)
- [ ] All 104 OpenSCAP rules listed with control mappings
- [ ] Baseline management procedures documented
- [ ] 100% compliance status documented with evidence
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/Evidence/Configuration_Baseline_Document_v1.0.md`
- [ ] Referenced in SSP v3.0 Sections 14 (PL-10) and 7 (CM-2)

**Last Updated:** March 18, 2026

---

### POA&M-204: Audit Event Inventory

**Control Family:** Audit and Accountability (AU)
**Control ID:** AU-2 (Event Logging)
**Severity:** MEDIUM
**SPRS Impact:** None (evidence enhancement)
**Status:** OPEN
**Priority:** P2 (Phase 3 Deliverable)

**Gap Description:**
Rev 3 AU-2 requires explicit audit event inventory (ODP-AU-1) documenting what events
are logged and why. Current: 150+ auditd rules operational, but no formal inventory.

**Current Status:**
- auditd: OPERATIONAL (150+ rules, comprehensive coverage)
- Wazuh: OPERATIONAL (2,500+ correlation rules)
- Event inventory: DOES NOT EXIST (rules exist, but no inventory document)

**Remediation Plan:**
1. Create Audit Event Inventory document (10-15 pages):
   - **Section 1: Auditable Event Selection Process**
     - How events selected (NIST SP 800-53 AU-2 guidance, risk-based)
     - Review frequency (annual, per ODP-AU-2)
   - **Section 2: Event Categories and Mappings**
     - Authentication events (successful/failed login, logout) → IA, AC controls
     - Account management (create/delete/modify users/groups) → AC-2
     - File access (read/write/delete CUI, configs, SSH keys) → AU-2, AC-3
     - Privileged commands (sudo, su, root actions) → AC-6
     - System calls (execve, open, unlink, chmod, chown) → AU-12
     - Network events (firewall blocks, VPN connections) → SC-7, AC-17
     - Security events (malware, intrusion attempts, policy violations) → SI-3, SI-4
     - Audit system events (auditd start/stop, rule changes) → AU-5
   - **Section 3: Technical Implementation**
     - auditd rules: `/etc/audit/rules.d/` on all systems
     - Example rules with explanations
     - Wazuh integration for correlation and alerting
   - **Section 4: Event-to-Control Mapping**
     - Map 50+ event types to Rev 3 controls
     - Justify why each event type is logged (security relevance)
   - **Section 5: Review and Maintenance**
     - Annual review of event inventory (ODP-AU-2)
     - Process for adding/removing event types
2. Extract sample events from `/var/log/audit/audit.log` as examples
3. Map events to 422 determination statements (where AU evidence needed)
4. Integrate into SSP v3.0 Section 6 (AU-2)

**Resources Required:**
- **Effort:** 6-8 hours (analysis of auditd rules, documentation, mapping)
- **References:** `/etc/audit/rules.d/`, Wazuh rules, NIST SP 800-53 AU-2, TCC-AAP-001
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** May 25, 2026
- **Target Completion:** June 10, 2026
- **POA&M Closure:** June 10, 2026

**Success Criteria:**
- [ ] Audit Event Inventory created (10-15 pages)
- [ ] 50+ event types documented with security justifications
- [ ] Event-to-control mapping (Rev 3 controls)
- [ ] Technical implementation documented (auditd rules, Wazuh)
- [ ] Example audit records included
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/Evidence/Audit_Event_Inventory_v1.0.md`
- [ ] Referenced in SSP v3.0 Section 6 (AU-2)
- [ ] ODP-AU-1 (auditable events) explicitly satisfied

**Last Updated:** March 18, 2026

---

### POA&M-205: External Services Inventory

**Control Family:** System and Services Acquisition (SA)
**Control ID:** SA-9 (External System Services)
**Severity:** MEDIUM
**SPRS Impact:** None (documentation requirement)
**Status:** OPEN
**Priority:** P2 (Phase 3 Deliverable)

**Gap Description:**
External dependencies exist (SSL.com, Rocky repos, NTP, DNS) but Rev 3 SA-9 requires
formal external services inventory with security controls and risk assessments.

**Current Status:**
- External services: OPERATIONAL (5-7 services in use)
- Inventory: DOES NOT EXIST (services documented in text, but no formal inventory)

**Remediation Plan:**
1. Create External Services Inventory document (8-10 pages):
   - **Service 1: SSL.com (TLS Certificate Provider)**
     - Purpose: X.509 certificate issuance for HTTPS/TLS
     - Data exchanged: CSRs (public keys), certificates (public)
     - Security controls: HTTPS communication, certificate validation, no CUI exposure
     - Risk level: LOW (public certificates only)
     - Vendor assessment: Commercial CA, audited per CA/Browser Forum requirements
     - Contract/SLA: [Document if formal agreement exists]
   - **Service 2: Rocky Linux Repositories (Package Updates)**
     - Purpose: OS and application software distribution
     - Data exchanged: Package metadata, RPM binaries
     - Security controls: GPG signature verification (mandatory), HTTPS mirrors
     - Risk level: MEDIUM (supply chain risk)
     - Mitigation: SBOM v3.0 tracking, signature verification, FIPS 140-2 validation
     - Vendor assessment: Community-supported, RHEL-compatible, strong reputation
   - **Service 3: Let's Encrypt (TLS Certificate Provider)**
     - Purpose: Automated certificate issuance via ACME protocol
     - Data exchanged: Domain validation challenges, certificates (public)
     - Security controls: HTTPS, automated renewal, 90-day expiration
     - Risk level: LOW (public certificates only)
     - Vendor assessment: Nonprofit, widely trusted, automated validation
   - **Service 4: NTP Servers (Time Synchronization)**
     - Purpose: Network Time Protocol (pool.ntp.org)
     - Data exchanged: Time synchronization packets (NTP)
     - Security controls: Multiple sources, outlier detection, authenticated time
     - Risk level: LOW (public time service, no CUI)
     - Vendor assessment: Public NTP pool, multiple redundant sources
   - **Service 5: DNS Forwarders (Domain Name Resolution)**
     - Purpose: Recursive DNS queries (Google 8.8.8.8, Cloudflare 1.1.1.1)
     - Data exchanged: DNS queries and responses
     - Security controls: DNSSEC validation (where available), multiple providers
     - Risk level: LOW (public DNS, no CUI in queries)
     - Vendor assessment: Google/Cloudflare (reputable, privacy policies documented)
   - **Service 6: [Additional services if applicable]**
     - Wazuh vulnerability feeds (if external)
     - GitHub (if used for version control)
     - Backup service (if offsite backups used)
2. Document security control flow-down requirements for each service
3. Document third-party risk assessment procedures
4. Integrate into SSP v3.0 Section 18 (SA-9)

**Resources Required:**
- **Effort:** 6-8 hours (inventory creation, risk assessment, documentation)
- **References:** TCC-SAP-001 Section 4.6 (SA-9), SSP v2.9 Section 2.5 (external connections)
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** June 1, 2026
- **Target Completion:** June 15, 2026
- **POA&M Closure:** June 15, 2026

**Success Criteria:**
- [ ] External Services Inventory created (8-10 pages)
- [ ] 5-7 external services documented with security controls
- [ ] Risk assessments completed for each service (LOW/MEDIUM/HIGH)
- [ ] Vendor assessments documented
- [ ] Third-party risk management procedures documented
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/Evidence/External_Services_Inventory_v1.0.md`
- [ ] Referenced in SSP v3.0 Section 18 (SA-9)

**Last Updated:** March 18, 2026

---

### POA&M-206: Rules of Behavior Formalization

**Control Family:** Planning (PL)
**Control ID:** PL-4 (Rules of Behavior)
**Severity:** LOW
**SPRS Impact:** None (documentation enhancement)
**Status:** OPEN
**Priority:** P3 (Phase 3 Deliverable — nice-to-have)

**Gap Description:**
TCC-AUP-001 (Acceptable Use Policy) covers Rules of Behavior implicitly, but Rev 3 PL-4
requires explicit "Rules of Behavior" document with user acknowledgment tracking.

**Current Status:**
- Acceptable Use Policy: EXISTS (TCC-AUP-001 v1.0)
- Rules of Behavior (explicit): DOES NOT EXIST
- User acknowledgment: N/A (solopreneur — sysadmin implicitly acknowledges as policy owner)

**Remediation Plan:**
**Option A:** Create standalone Rules of Behavior document (4-6 hours)
**Option B:** Rebrand TCC-AUP-001 Section 2 as "Rules of Behavior" (2-3 hours) **← RECOMMENDED**

**Option B Implementation:**
1. Update TCC-AUP-001 v2.0 (Rev 3 update):
   - Rename Section 2 to "Rules of Behavior (RoB)"
   - Add explicit PL-4 cross-reference
   - Add subsection: "User Acknowledgment Requirements"
     - Current: sysadmin (implicit acknowledgment as System Owner)
     - Future: Contract employees must sign acknowledgment form before account creation
   - Add Appendix A: Rules of Behavior Acknowledgment Form template
2. Create user acknowledgment tracking log:
   - Spreadsheet: User Name, Date Signed, Policy Version, Next Review Date
   - Current entry: sysadmin, [effective date], v2.0, [annual review date]
3. Document acknowledgment tracking procedures in TCC-SPP-001 Section 4.2
4. Integrate into SSP v3.0 Section 14 (PL-4)

**Resources Required:**
- **Effort:** 2-3 hours (Option B: update TCC-AUP-001, create acknowledgment form/log)
- **References:** TCC-AUP-001 v1.0, TCC-SPP-001, NIST SP 800-53 PL-4
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** June 5, 2026
- **Target Completion:** June 15, 2026
- **POA&M Closure:** June 15, 2026

**Success Criteria:**
- [ ] TCC-AUP-001 v2.0 updated with explicit "Rules of Behavior" section
- [ ] PL-4 cross-reference added
- [ ] User acknowledgment requirements documented
- [ ] Acknowledgment form template created (Appendix A)
- [ ] User acknowledgment tracking log created
- [ ] File locations:
  - `/home/sysadmin/CyberSecurity/Rev3/Policies/Planning/TCC-AUP-001_Acceptable_Use_Policy_v2.0.docx` (updated)
  - `/home/sysadmin/CyberSecurity/Rev3/Evidence/Rules_of_Behavior_Acknowledgment_Log.xlsx` (new)
- [ ] Referenced in SSP v3.0 Section 14 (PL-4)

**Last Updated:** March 18, 2026

---

### POA&M-207: Security Engineering Principles Document

**Control Family:** System and Services Acquisition (SA)
**Control ID:** SA-8 (Security Engineering Principles)
**Severity:** LOW
**SPRS Impact:** None (documentation enhancement)
**Status:** OPEN
**Priority:** P3 (Phase 3 Deliverable — nice-to-have)

**Gap Description:**
Security workstation2 principles are implemented throughout CyberHygiene (defense-in-depth,
least privilege, fail-safe defaults), but Rev 3 SA-8 requires explicit documentation.

**Current Status:**
- Security principles: OPERATIONAL (implicitly designed into architecture)
- Documentation: DOES NOT EXIST (principles evident in design, but not formally documented)

**Remediation Plan:**
1. Create Security Engineering Principles document (6-8 pages):
   - **Principle 1: Defense-in-Depth (Layered Security)**
     - Network layer: pfSense firewall with default-deny
     - Host layer: LUKS full disk encryption, local firewall (firewalld)
     - Application layer: MFA (SSH key + TOTP), RBAC (FreeIPA + sudo)
     - Data layer: TLS 1.3 in transit, FIPS 140-2 encryption at rest
   - **Principle 2: Least Privilege**
     - User accounts: Standard users (no sudo by default)
     - Administrator: sysadmin with NOPASSWD sudo (justified: solopreneur)
     - Service accounts: Minimal permissions, no interactive shells
     - File permissions: Restrictive (700/600 for sensitive files)
     - FreeIPA RBAC: Role-based group membership
   - **Principle 3: Fail-Safe Defaults**
     - Firewall: Default-deny egress and ingress
     - SELinux: Enforcing mode (deny by default)
     - SSH: Deny root login, deny password authentication (key-based only)
     - Sudo: Explicit NOPASSWD only where justified
   - **Principle 4: Separation of Duties**
     - Challenge: Solopreneur (sysadmin = System Owner + Admin + AO + ISSO)
     - Mitigation: Comprehensive audit logging (AU), peer review via assessors (future)
     - Future: Contract employees will have separate roles (standard user vs admin)
   - **Principle 5: Economy of Mechanism (Keep It Simple)**
     - Minimal installations: Only required packages installed
     - Avoid complexity: No custom development (COTS only per TCC-SAP-001)
     - Standard configurations: Follow SCAP Security Guide baseline
   - **Principle 6: Complete Mediation (Check Every Access)**
     - SELinux: Mandatory Access Control (MAC) on all file access
     - FreeIPA: Authentication check on every system access (Kerberos tickets expire)
     - Firewall: Stateful inspection on every packet
   - **Principle 7: Open Design (Security Through Transparency)**
     - Use of open-source software (Rocky Linux, FreeIPA, Wazuh)
     - Security through validated cryptography (FIPS 140-2), not obscurity
     - Documented configurations (no "security through obscurity")
   - **Principle 8: Least Common Mechanism**
     - Dedicated systems: dc1 for FreeIPA/Wazuh, workstations for users
     - Isolation: No shared accounts, no shared SSH keys
     - Segmentation: Network segmentation via firewall (future: VLANs if needed)
   - **Principle 9: Psychological Acceptability (Usability)**
     - MFA usable: TOTP via smartphone app (Microsoft Authenticator)
     - SSH keys: Persistent authentication (no password fatigue)
     - Dashboards: OpenSCAP dashboard for quick compliance visibility
2. Map each principle to Rev 3 controls
3. Document how each principle is operationalized in CyberHygiene
4. Integrate into SSP v3.0 Section 18 (SA-8)

**Resources Required:**
- **Effort:** 6-8 hours (analysis, documentation, control mapping)
- **References:** TCC-SAP-001 Section 4.5 (SA-8), system architecture, NIST SP 800-160
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** June 10, 2026
- **Target Completion:** June 20, 2026
- **POA&M Closure:** June 20, 2026

**Success Criteria:**
- [ ] Security Engineering Principles document created (6-8 pages)
- [ ] 9 principles documented with CyberHygiene implementations
- [ ] Principle-to-control mapping (Rev 3 controls)
- [ ] Solopreneur separation of duties challenge documented with mitigations
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/Evidence/Security_Engineering_Principles_v1.0.md`
- [ ] Referenced in SSP v3.0 Section 18 (SA-8)

**Last Updated:** March 18, 2026

---

### POA&M-208: Data Flow Diagram

**Control Family:** System and Communications Protection (SC)
**Control ID:** SC-7 (Boundary Protection)
**Severity:** LOW
**SPRS Impact:** None (evidence enhancement — optional)
**Status:** OPEN
**Priority:** P4 (Nice-to-have, not blocking)

**Gap Description:**
Network architecture diagram (POA&M-202) shows topology, but data flow diagram showing
CUI data paths through systems would enhance SC-7 and overall SSP v3.0 documentation.

**Remediation Plan:**
1. Create data flow diagram (using draw.io or Visio):
   - **CUI Creation:** Workstations (workstation1, workstation2, workstation3) create contract deliverables
   - **CUI Storage:** NAS receives encrypted backups from all workstations
   - **CUI Transit:** TLS 1.3 encrypted connections (red arrows showing CUI paths)
   - **Authentication:** FreeIPA (dc1) provides Kerberos tickets to workstations (green arrows)
   - **Audit Logs:** All systems send logs to Wazuh (dc1) (blue arrows)
   - **Backups:** Workstations and dc1 → NAS (orange arrows showing backup flows)
   - **External:** Rocky repos → workstations (package updates, purple arrows)
2. Add legend and annotations
3. Export to PDF for SSP v3.0
4. Include in SSP v3.0 Section 3.6 (Data Flows and CUI Paths) and Appendix C

**Resources Required:**
- **Effort:** 4-6 hours (diagram creation)
- **Tools:** draw.io (free) or Visio
- **Budget:** $0

**Timeline:**
- **Start Date:** June 15, 2026 (after Network Architecture Diagram complete)
- **Target Completion:** June 20, 2026
- **POA&M Closure:** June 20, 2026

**Success Criteria:**
- [ ] Data flow diagram created showing CUI paths
- [ ] All major data flows documented (CUI, auth, audit, backup, external)
- [ ] Color-coded arrows with legend
- [ ] PDF exported for SSP v3.0
- [ ] File locations:
  - `/home/sysadmin/CyberSecurity/Rev3/Evidence/Data_Flow_Diagram_v1.0.pdf` (PDF)
  - `/home/sysadmin/CyberSecurity/Rev3/Evidence/Data_Flow_Diagram_v1.0.drawio` (source)
- [ ] Referenced in SSP v3.0 Section 3.6 and Appendix C

**Priority:** P4 (optional enhancement — defer if time-constrained)

**Last Updated:** March 18, 2026

---

## CATEGORY 4: Rev 3 Validation Gaps

### POA&M-301: Determination Statements Validation (422 statements)

**Control Family:** All (17 families)
**Control ID:** All 97 Rev 3 controls
**Severity:** HIGH
**SPRS Impact:** None (validation activity, not gap)
**Status:** OPEN
**Priority:** P1 (Phase 4 Deliverable — required for assessment)

**Gap Description:**
Rev 3 assessment requires validation of all 422 determination statements with specific
evidence artifacts. Current status: 340 MET (80.6%), 70 PARTIAL (16.6%), 12 NOT MET (2.8%).

**Current Status:**
- Determination Statement Checklist: EXISTS (Phase 1 deliverable, framework)
- Evidence mapping: PARTIAL (some evidence exists, but not systematically mapped)
- Validation: NOT COMPLETE (each statement needs independent evidence verification)

**Remediation Plan:**
1. Use Rev3_Determination_Statement_Checklist.md as starting point
2. For each of 422 determination statements:
   - **Step 1:** Identify evidence artifact(s) that satisfy statement
     - Technical evidence: Configuration files, logs, screenshots, scan results
     - Policy evidence: TCC-XXX-001 policy, specific section
     - Process evidence: Procedures, training records, acknowledgment forms
   - **Step 2:** Verify evidence is current and complete
   - **Step 3:** Mark statement as MET / PARTIAL / NOT MET
   - **Step 4:** Document evidence location and validation date
3. Create Determination Statements Compliance Matrix (Excel or CSV):
   - Columns: DS ID, Control, Statement Text, Status, Evidence Artifact(s), Validation Date, Notes
   - 422 rows (one per determination statement)
4. Identify gaps where statements are PARTIAL or NOT MET
5. Update POA&M with any new gaps discovered
6. Prioritize remediation (HIGH/MEDIUM/LOW based on control criticality)
7. Integrate matrix into SSP v3.0 Section 22

**Resources Required:**
- **Effort:** 60-80 hours (most intensive Phase 4 activity — ~8-10 minutes per statement)
- **References:** Rev3_Determination_Statement_Checklist.md, SSP v3.0, all policies, all evidence artifacts
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** July 1, 2026
- **Target Completion:** August 15, 2026
- **POA&M Closure:** August 15, 2026

**Success Criteria:**
- [ ] All 422 determination statements validated with evidence
- [ ] Determination Statements Compliance Matrix created (422 rows)
- [ ] 95%+ statements MET (target: 400+ of 422)
- [ ] All PARTIAL/NOT MET statements have POA&M items created
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/Evidence/Rev3_Determination_Statements_Compliance_Matrix.xlsx`
- [ ] Referenced in SSP v3.0 Section 22

**Notes:**
- This is the most time-intensive Phase 4 activity (60-80 hours estimated)
- Systematic approach: Validate by control family (17 families, ~25 statements per family avg)
- 80.6% already MET per Phase 1 gap analysis — focus on 70 PARTIAL + 12 NOT MET statements first
- Once complete, CyberHygiene is assessment-ready for Rev 3

**Last Updated:** March 18, 2026

---

### POA&M-302: ODP Verification Report

**Control Family:** All (49 ODPs across multiple families)
**Control ID:** All controls with ODPs
**Severity:** MEDIUM
**SPRS Impact:** None (verification activity)
**Status:** OPEN
**Priority:** P2 (Phase 4 Deliverable)

**Gap Description:**
All 49 ODPs are defined in Rev3_ODP_Tailoring_Document.md (Phase 1), but technical
verification that implementations match documented ODP values not yet completed.

**Current Status:**
- ODP definitions: EXISTS (49 parameters defined in Phase 1)
- Technical implementation: EXISTS (configurations operational)
- Verification: NOT COMPLETE (need to verify configs match ODP values)

**Remediation Plan:**
1. Use Rev3_ODP_Tailoring_Document.md as reference
2. For each of 49 ODPs:
   - **Step 1:** Review documented ODP value (e.g., ODP-IA-2: 12 characters password length)
   - **Step 2:** Identify technical implementation location (e.g., FreeIPA password policy, /etc/security/pwquality.conf)
   - **Step 3:** Verify configuration matches ODP value:
     - Example: `ipa pwpolicy-show` → verify `Min Length: 12`
     - Example: `cat /etc/security/pwquality.conf | grep minlen` → verify `minlen = 12`
   - **Step 4:** Document verification evidence (command output, screenshot, config file excerpt)
   - **Step 5:** Mark ODP as VERIFIED / DISCREPANCY / N/A
3. Create ODP Verification Report (10-15 pages):
   - Table: ODP ID, Parameter, Documented Value, Actual Value, Verification Method, Status
   - 49 rows (one per ODP)
   - Appendices: Evidence artifacts (screenshots, config file excerpts, command outputs)
4. Resolve any discrepancies discovered
5. Update configurations or ODP documentation as needed
6. Integrate into SSP v3.0 Section 21 or as standalone report

**Resources Required:**
- **Effort:** 8-12 hours (~10-15 minutes per ODP verification)
- **References:** Rev3_ODP_Tailoring_Document.md, system configurations, policy documents
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** August 1, 2026
- **Target Completion:** August 15, 2026
- **POA&M Closure:** August 15, 2026

**Success Criteria:**
- [ ] All 49 ODPs verified against technical implementations
- [ ] ODP Verification Report created (10-15 pages with evidence)
- [ ] 100% ODPs verified as matching documented values (or discrepancies resolved)
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/Evidence/Rev3_ODP_Verification_Report.md`
- [ ] Referenced in SSP v3.0 Section 21

**Notes:**
- Key ODPs to verify:
  - ODP-IA-2 to ODP-IA-5: Password policies (FreeIPA)
  - ODP-AU-2 to ODP-AU-3: Audit review frequency, retention (Wazuh, auditd)
  - ODP-AC-1, ODP-AC-2: Lockout, session timeout (PAM, SSH)
  - ODP-RA-1, ODP-RA-2: Risk assessment, vulnerability scan frequency (OpenSCAP, Wazuh)

**Last Updated:** March 18, 2026

---

### POA&M-303: Policy Compliance Review

**Control Family:** Planning (PL)
**Control ID:** PL-2 (System Security Plans)
**Severity:** MEDIUM
**SPRS Impact:** None (validation activity)
**Status:** OPEN
**Priority:** P2 (Phase 4 Deliverable)

**Gap Description:**
14 Rev 3 policies will be complete and approved, but formal compliance review verifying
all policies cover all Rev 3 requirements and are current/effective not yet conducted.

**Current Status:**
- Policies: 6 complete, 8 summaries (awaiting expansion per POA&M-101)
- Approval: PENDING (per POA&M-104)
- Compliance review: NOT COMPLETE

**Remediation Plan:**
1. After all 14 policies approved (POA&M-101, POA&M-104 complete):
2. Conduct Policy Compliance Review:
   - **Review 1: Coverage Completeness**
     - Verify all 97 Rev 3 controls mapped to policies (use Control-to-Policy Quick Reference Rev 3)
     - Identify any controls without policy coverage (gap)
   - **Review 2: Policy Currency**
     - Verify all policies have effective dates within last 12 months
     - Verify all policies have review dates scheduled (per TCC-SPP-001 annual review)
     - Check for any outdated policy versions still referenced
   - **Review 3: Consistency Check**
     - Cross-reference policies for consistency (no contradictions)
     - Verify ODP values consistent across policies and ODP Tailoring Document
     - Verify terminology consistent (e.g., "CUI" vs "sensitive information")
   - **Review 4: Approval Verification**
     - Verify all 14 policies have signed approval pages
     - Verify effective dates match approval dates
     - Verify "_DRAFT" removed from all filenames
3. Create Policy Compliance Review Report (8-10 pages):
   - Summary of findings (coverage, currency, consistency, approval)
   - Recommendations for any gaps or improvements
   - Sign-off by System Owner (sysadmin)
4. Resolve any findings before assessment
5. Integrate into Phase 4 validation package

**Resources Required:**
- **Effort:** 12-16 hours (comprehensive review of 14 policies)
- **References:** All 14 Rev 3 policies, Control-to-Policy Quick Reference Rev 3, TCC-SPP-001
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** August 10, 2026 (after POA&M-101, POA&M-104 complete)
- **Target Completion:** August 25, 2026
- **POA&M Closure:** August 25, 2026

**Success Criteria:**
- [ ] All 14 policies reviewed for coverage, currency, consistency, approval
- [ ] Policy Compliance Review Report created (8-10 pages)
- [ ] All findings resolved or POA&M items created
- [ ] System Owner (sysadmin) sign-off on review report
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/Evidence/Rev3_Policy_Compliance_Review.md`

**Last Updated:** March 18, 2026

---

### POA&M-304: Rev 3 Evidence Package Assembly

**Control Family:** Planning (PL)
**Control ID:** PL-2 (System Security Plans)
**Severity:** MEDIUM
**SPRS Impact:** None (assessment preparation)
**Status:** OPEN
**Priority:** P2 (Phase 4 Deliverable)

**Gap Description:**
Complete Rev 3 evidence package for C3PAO assessment or self-assessment not yet assembled
in organized directory structure for easy access.

**Current Status:**
- Evidence artifacts: IN PROGRESS (some complete, some Phase 3/4 deliverables)
- Organization: AD HOC (files in various directories)
- Evidence package: DOES NOT EXIST (no organized assessment-ready package)

**Remediation Plan:**
1. Create Rev 3 Evidence Package directory structure:
   ```
   /home/sysadmin/CyberSecurity/Rev3/Evidence_Package/
   ├── 01_System_Security_Plan/
   │   └── System_Security_Plan_v3.0.docx
   ├── 02_Policies/
   │   ├── TCC-SPP-001_System_Security_Planning_Policy_v1.0.docx
   │   ├── TCC-SAP-001_System_and_Services_Acquisition_Policy_v1.0.docx
   │   ├── TCC-SRMP-001_Supply_Chain_Risk_Management_Policy_v1.0.docx
   │   ├── [11 other updated policies...]
   │   └── Control_to_Policy_Quick_Reference_Rev3.md
   ├── 03_POAM/
   │   └── Unified_POAM_v3.0.md
   ├── 04_Technical_Evidence/
   │   ├── OpenSCAP_Scan_Results/ (all 4 systems, latest scans)
   │   ├── Wazuh_Reports/ (SIEM logs, alerts, dashboard screenshots)
   │   ├── FreeIPA_Configuration/ (password policy, user list, group membership)
   │   ├── Firewall_Rulesets/ (pfSense config export)
   │   ├── MFA_Configuration/ (SSH configs, PAM configs, TOTP screenshots)
   │   └── Audit_Logs/ (sample auditd logs, Wazuh correlation examples)
   ├── 05_Evidence_Artifacts/
   │   ├── Software_Bill_of_Materials_v3.0.md
   │   ├── Network_Architecture_Diagram_v1.0.pdf
   │   ├── Configuration_Baseline_Document_v1.0.md
   │   ├── Audit_Event_Inventory_v1.0.md
   │   ├── External_Services_Inventory_v1.0.md
   │   ├── Security_Engineering_Principles_v1.0.md
   │   └── Data_Flow_Diagram_v1.0.pdf (optional)
   ├── 06_Assessment_Reports/
   │   ├── CMMC_L2_Preliminary_Gap_Analysis.md (Feb 9, 2026)
   │   ├── Rev3_Gap_Analysis_Report.md (Phase 1)
   │   ├── Rev3_Self_Assessment_Report.md (Phase 4, to be created)
   │   └── OpenSCAP_Dashboard_Screenshots/
   ├── 07_Determination_Statements/
   │   ├── Rev3_Determination_Statement_Checklist.md
   │   └── Rev3_Determination_Statements_Compliance_Matrix.xlsx (POA&M-301)
   ├── 08_ODPs/
   │   ├── Rev3_ODP_Tailoring_Document.md
   │   └── Rev3_ODP_Verification_Report.md (POA&M-302)
   ├── 09_Training_Records/
   │   ├── CyberHygiene_Security_Awareness_Training_FY2026.md
   │   ├── Training_Assessment_Quiz_FY2026.md
   │   └── Training_Completion_Record_FY2026.md
   └── 10_Review_Reports/
       ├── Rev3_Policy_Compliance_Review.md (POA&M-303)
       └── Risk_Assessment_Report.md (POA&M-001)
   ```
2. Copy/symlink all artifacts into organized structure
3. Create README.md in Evidence_Package root explaining structure and artifact locations
4. Create Evidence_Package_Inventory.xlsx listing all files with descriptions
5. Verify completeness (all artifacts from Phases 1-4)
6. Test package accessibility (ensure all paths valid, no broken links)

**Resources Required:**
- **Effort:** 16-24 hours (file organization, copying/symlinking, inventory creation, verification)
- **References:** All Phase 1-4 deliverables, SSP v3.0 Section 24 (Related Documentation)
- **Budget:** $0 (internal labor only)

**Timeline:**
- **Start Date:** August 20, 2026
- **Target Completion:** September 5, 2026
- **POA&M Closure:** September 5, 2026

**Success Criteria:**
- [ ] Rev3_Evidence_Package/ directory created with 10 subdirectories
- [ ] All artifacts copied/symlinked into organized structure
- [ ] README.md created explaining package structure
- [ ] Evidence_Package_Inventory.xlsx created (complete file list with descriptions)
- [ ] Completeness verified (no missing artifacts)
- [ ] Package tested (all paths valid, accessible)
- [ ] Directory location: `/home/sysadmin/CyberSecurity/Rev3/Evidence_Package/`
- [ ] Ready for C3PAO assessment or self-assessment

**Notes:**
- Evidence package provides one-stop-shop for assessors
- Organized structure reduces assessment time and cost
- Can be zipped/archived for transmission to C3PAO when ready

**Last Updated:** March 18, 2026

---

### POA&M-305: Rev 3 Self-Assessment Report

**Control Family:** Planning (PL)
**Control ID:** PL-2 (System Security Plans)
**Severity:** MEDIUM
**SPRS Impact:** None (assessment preparation)
**Status:** OPEN
**Priority:** P2 (Phase 4 Deliverable)

**Gap Description:**
Internal self-assessment using Rev 3 assessment methodology not yet conducted to validate
compliance status before formal C3PAO assessment.

**Current Status:**
- Assessment methodology: KNOWN (NIST SP 800-171A Rev 3)
- Assessment execution: NOT COMPLETE
- Assessment report: DOES NOT EXIST

**Remediation Plan:**
1. Conduct Rev 3 self-assessment (40-60 hours):
   - **Phase 1: Document Review (8-10 hours)**
     - Review SSP v3.0, POA&M v3.0, all 14 policies
     - Review determination statements compliance matrix (422 statements)
     - Review ODP verification report (49 parameters)
   - **Phase 2: Technical Validation (16-24 hours)**
     - Verify all 97 Rev 3 controls implemented per SSP v3.0
     - Test sample controls for effectiveness (not just implementation)
     - Review OpenSCAP scans, Wazuh logs, FreeIPA configs
     - Validate MFA (test SSH key + TOTP on all systems)
     - Validate audit logging (generate test events, verify capture)
     - Validate encryption (verify FIPS 140-2, TLS 1.3)
   - **Phase 3: Evidence Verification (12-16 hours)**
     - Verify all evidence artifacts exist and are current
     - Cross-reference evidence package contents
     - Identify any missing evidence
   - **Phase 4: Gap Identification (4-6 hours)**
     - Identify any controls that are PARTIAL or NOT IMPLEMENTED
     - Assess severity of gaps (HIGH/MEDIUM/LOW)
     - Recommend remediation for gaps
2. Create Rev 3 Self-Assessment Report (20-30 pages):
   - **Section 1: Executive Summary**
     - Overall compliance status (% controls fully implemented)
     - SPRS score estimate (if Rev 3 scoring available)
     - Assessment methodology (NIST SP 800-171A Rev 3, CMMC 2.0 practices)
   - **Section 2: Assessment Scope**
     - Systems assessed (all 4 systems + dc1 + pfSense + NAS)
     - Timeframe (dates of assessment)
     - Assessor (sysadmin as internal assessor)
   - **Section 3: Findings by Control Family**
     - 17 control family sections
     - For each family: Controls assessed, findings, evidence reviewed
   - **Section 4: Gaps and Weaknesses**
     - List of controls with PARTIAL or NOT IMPLEMENTED status
     - Severity assessment
     - Recommended remediation
   - **Section 5: Strengths and Achievements**
     - 100% OpenSCAP compliance
     - MFA deployment (exceeds Rev 3 requirements)
     - SBOM v3.0 (rare for organizations this size)
     - Comprehensive SIEM (Wazuh 100% coverage)
   - **Section 6: Recommendations**
     - Path to 95%+ compliance (complete POA&M items)
     - Preparation for C3PAO assessment
     - Continuous monitoring plan
   - **Appendices:**
     - Determination statements summary (422 statements, MET/PARTIAL/NOT MET counts)
     - ODP verification summary (49 parameters)
     - Evidence artifact inventory
3. Brief findings to Authorizing Official (sysadmin)
4. Update POA&M v3.0 with any new gaps discovered
5. Use report to prepare for formal C3PAO assessment (when Rev 3 assessments available)

**Resources Required:**
- **Effort:** 40-60 hours (most intensive Phase 4 activity)
  - Assessment execution: 40-50 hours
  - Report writing: 8-12 hours
- **References:** NIST SP 800-171A Rev 3, SSP v3.0, all evidence artifacts, CMMC 2.0 Assessment Guide
- **Budget:** $0 (internal self-assessment) OR $5,000-$15,000 (optional external consultant review)

**Timeline:**
- **Start Date:** August 25, 2026
- **Target Completion:** September 10, 2026
- **Review/Approval:** September 15, 2026
- **POA&M Closure:** September 15, 2026

**Success Criteria:**
- [ ] All 97 Rev 3 controls assessed for implementation and effectiveness
- [ ] All 422 determination statements validated with evidence
- [ ] Rev 3 Self-Assessment Report completed (20-30 pages)
- [ ] Estimated Rev 3 compliance: 95%+ (target)
- [ ] Authorizing Official (sysadmin) briefed and approves report
- [ ] POA&M v3.0 updated with any new gaps discovered
- [ ] File location: `/home/sysadmin/CyberSecurity/Rev3/Assessments/Rev3_Self_Assessment_Report_20260910.md`
- [ ] Ready for formal C3PAO assessment (when Rev 3 assessments available)

**Notes:**
- Self-assessment identifies gaps before formal assessment (reduces surprises)
- Estimated Rev 3 compliance: 80.6% → 95%+ upon Phase 4 completion
- Once complete, CyberHygiene is Rev 3 assessment-ready
- **Phase 4 target completion: September 15, 2026** (6-month transition timeline met)

**Last Updated:** March 18, 2026

---

## CATEGORY 5: Closed Items (Historical Tracking)

### POA&M-CLOSED-001: Multi-Factor Authentication (MFA) Deployment

**Control Family:** Identification and Authentication (IA)
**Control ID:** 3.5.3 (Rev 2), 3.5.3 (Rev 3 — unchanged)
**Severity:** HIGH (when open)
**SPRS Impact:** +5 points (101 → 106)
**Status:** CLOSED
**Date Closed:** February 21, 2026

**Original Gap:**
MFA not deployed on workstations. SSH key authentication only (single factor).

**Remediation Implemented:**
- Deployed TOTP (Time-based One-Time Password) on all 4 systems
- SSH key (ECDSA-521) + TOTP via pam_google_authenticator
- Configuration: `/etc/ssh/sshd_config.d/60-mfa.conf` (AuthenticationMethods publickey,keyboard-interactive)
- PAM config: `/etc/pam.d/sshd` (pam_google_authenticator.so nullok)
- SELinux custom module: sshd_google_auth.te (allows sshd_t write to user_home_dir_t + auth_home_t)
- dc1 exemption: pam_succeed_if.so rhost=10.0.0.10 (dc1 can SSH to workstations without TOTP)
- TOTP app: Microsoft Authenticator (smartphone-based)

**Evidence:**
- Deployment date: February 21, 2026
- Systems: dc1 (.10), workstation1 (.115), workstation2 (.104), workstation3 (.113)
- SPRS impact: +5 points (101 → 106, now 106/110 = 96.4%)
- Policy reference: TCC-IAP-001 Section 5 (Authenticator Management)
- Technical reference: MFA configuration files, TOTP secrets (encrypted, backed up)

**Lessons Learned:**
- PAM configuration critical: Use `auth sufficient pam_succeed_if.so` NOT `[success=1 default=ignore]`
- SELinux custom module required for TOTP secret storage in user home directories
- dc1 exemption necessary for FreeIPA domain controller management access
- Testing on one system first (workstation1) prevented widespread issues

**Last Updated:** February 21, 2026

---

### POA&M-CLOSED-002: Administrator Access Method Switchover

**Control Family:** Access Control (AC)
**Control ID:** AC-6 (Least Privilege)
**Severity:** MEDIUM (when open)
**SPRS Impact:** None (compliance improvement, not scored directly)
**Status:** CLOSED
**Date Closed:** February 21, 2026

**Original Gap:**
Administrator access via root SSH (PermitRootLogin yes). Rev 2/3 best practice: Disable
root SSH, use named accounts with sudo.

**Remediation Implemented:**
- Created sysadmin NOPASSWD sudo on all 3 workstations
- Updated SSH config: PermitRootLogin no
- Updated nsswitch.conf: `sudoers: files` (removed sss to prevent SSSD override)
- Updated /root/.ssh/config: User sysadmin, IdentityFile /home/sysadmin/.ssh/id_ecdsa
- Sudoers file: /etc/sudoers.d/sysadmin-admin (NOPASSWD: ALL)
- Key: ECDSA-521 (/home/sysadmin/.ssh/id_ecdsa)

**Evidence:**
- Deployment date: February 18-21, 2026
- Systems: workstation1 (.115), workstation2 (.104), workstation3 (.113)
- Configuration: PermitRootLogin no in /etc/ssh/sshd_config or /etc/ssh/sshd_config.d/
- Scripts updated: collect_openscap_results.sh, trigger_all_openscap_scans.sh, deploy-ws-controls.sh
- SPRS impact: None direct, but satisfies AC-6 Least Privilege best practice

**Lessons Learned:**
- nsswitch.conf `sudoers: files` critical (SSSD was overriding NOPASSWD)
- Test access before disabling root SSH (ensure sysadmin sudo works)
- Update all automation scripts to use sysadmin@ instead of root@

**Last Updated:** February 21, 2026

---

### POA&M-CLOSED-003 through POA&M-CLOSED-008

[Additional closed items — historical tracking of previous POA&M remediation]

Examples:
- CLOSED-003: Login Banner Update (CIS notice, USG text removed) — Closed 2026-02-21
- CLOSED-004: 100% OpenSCAP Compliance Achieved (104/104 rules) — Closed 2026-02-21
- CLOSED-005: FreeIPA Centralized Identity Management Deployment — Closed [prior date]
- CLOSED-006: Wazuh SIEM 100% System Coverage — Closed [prior date]
- CLOSED-007: FIPS 140-2 Validated Encryption Deployment — Closed [prior date]
- CLOSED-008: SBOM v2.4 Creation (5,626 packages) — Closed [prior date]

**Note:** Historical closed items demonstrate continuous compliance improvement over time.

---

## POA&M Management Procedures

### Update Frequency
- **Monthly:** Review all OPEN and IN PROGRESS items (1st of each month)
- **Quarterly:** Comprehensive POA&M review with Authorizing Official (sysadmin)
- **Triggered:** Upon significant system changes, new gaps discovered, or milestones met

### Roles and Responsibilities
- **System Owner (sysadmin):** POA&M oversight, approval, budget allocation
- **Authorizing Official (sysadmin):** POA&M approval, risk acceptance decisions
- **ISSO (sysadmin):** POA&M maintenance, tracking, monthly updates

### Prioritization Criteria
- **P1 (Critical Path):** Blocking Rev 2 100% compliance or Rev 3 assessment readiness
- **P2 (High Priority):** Phase deliverables, required for compliance
- **P3 (Medium Priority):** Enhancements, nice-to-have but not blocking
- **P4 (Low Priority):** Optional, defer if resource-constrained

### Risk Acceptance Process
1. Identify POA&M item that may be deferred or accepted as residual risk
2. Document risk acceptance rationale (cost, timeline, compensating controls)
3. Authorizing Official (sysadmin) formally accepts risk
4. Update POA&M item status to "RISK ACCEPTED" with justification
5. Review annually (or upon significant change)

### Closure Criteria
All POA&M items must meet the following criteria for closure:
1. Remediation plan fully implemented
2. Evidence artifacts created and validated
3. Testing completed (if applicable)
4. Documentation updated (SSP, policies, POA&M)
5. Authorizing Official (sysadmin) approval
6. Date closed and evidence location documented

### Reporting
- **Monthly POA&M Update Report:** Sent to sysadmin (System Owner) by 5th of each month
- **Quarterly POA&M Review:** Briefing to Authorizing Official (sysadmin)
- **Annual POA&M Summary:** Included in SSP v3.0 Section 23, annual review

---

## Metrics and Tracking

### Current POA&M Metrics (as of March 18, 2026)

**By Status:**
- OPEN: 19 items (65.5%)
- IN PROGRESS: 2 items (6.9%)
- CLOSED: 8 items (27.6%)
- TOTAL: 29 items

**By Category:**
- Rev 2 Remaining Gaps: 2 items (OPEN)
- Rev 3 Documentation: 6 items (2 IN PROGRESS, 2 COMPLETE, 2 OPEN)
- Rev 3 Technical: 8 items (OPEN)
- Rev 3 Validation: 5 items (OPEN)
- Closed: 8 items (historical)

**By Priority:**
- P1 (Critical Path): 5 items (17.2%)
- P2 (High Priority): 14 items (48.3%)
- P3 (Medium Priority): 4 items (13.8%)
- P4 (Low Priority): 1 item (3.4%)
- CLOSED: 8 items (27.6%)

**By Target Completion Date:**
- April 2026: 4 items (RA-3, policies, SSP framework)
- May 2026: 3 items (SSP v3.0, policy approval, SBOM v3.0)
- June 2026: 6 items (IR-3, Phase 3 evidence artifacts)
- July-August 2026: 5 items (Phase 4 validation)
- September 2026: 1 item (self-assessment, final)

**SPRS Score Progression:**
- Current: 106/110 (96.4%)
- After RA-3 (04/30): 109/110 (99.1%)
- After IR-3 (06/30): 110/110 (100% Rev 2 compliance)
- Rev 3 target (09/15): 95%+ (estimated 92-95 of 97 controls fully implemented)

### Key Performance Indicators (KPIs)

**KPI 1: Rev 2 Compliance**
- Current: 106/110 (96.4%)
- Target (06/30/2026): 110/110 (100%)
- On Track: YES (2 POA&M items scheduled, resources allocated)

**KPI 2: Rev 3 Transition Progress**
- Current: Phase 2 (50% complete — 6 of 14 policies done)
- Target (09/15/2026): Phase 4 complete, 95%+ compliance
- On Track: YES (ahead of schedule — Key Differences + SSP Framework done early)

**KPI 3: POA&M Item Closure Rate**
- February 2026: 2 items closed (MFA, admin access)
- March 2026: 2 items closed (Key Differences, SSP Framework)
- Target: 3-5 items per month through Phase 2-3
- On Track: YES

**KPI 4: OpenSCAP Compliance**
- Current: 100% (104/104 rules passing, all 4 systems)
- Target: Maintain 100% throughout transition
- On Track: YES (weekly monitoring, no degradation)

---

## Next Review

**Next POA&M Review Date:** April 15, 2026
**Review Type:** Monthly update (all OPEN/IN PROGRESS items)
**Reviewer:** sysadmin (ISSO, System Owner)

**Focus Areas for Next Review:**
1. POA&M-001 (RA-3): Verify start date (04/01) and progress
2. POA&M-101: Policy expansion progress (8 remaining policies)
3. POA&M-102: SSP v3.0 progress (target 05/15 completion)
4. Phase 2 overall: Target 04/15 for policy work, assess if on track

---

## Document Control

**POA&M Version:** 3.0 (Rev 3 Transition Tracking)
**Date Created:** March 18, 2026
**Last Updated:** March 18, 2026
**Next Update:** April 15, 2026 (monthly review)
**Owner:** sysadmin (System Owner, Authorizing Official, ISSO)
**Classification:** CUI (Controlled Unclassified Information)

**Version History:**
| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 3.0 | 2026-03-18 | sysadmin | Rev 3 transition tracking — added 19 Rev 3 items across Phases 2-4 |
| 2.11 | 2026-02-21 | sysadmin | Closed MFA and admin access items, updated SPRS 106/110 |
| 2.10 | 2026-02-17 | sysadmin | SSH hardening, 100% OpenSCAP, CIS banner |
| [2.0-2.9] | [prior dates] | sysadmin | [Rev 2 evolution] |

---

**END OF POA&M v3.0**

*This POA&M tracks all open and closed security control gaps for NIST SP 800-171*
*Revision 2 (current: 106/110 SPRS) and Revision 3 (transition in progress).*
*Target: 110/110 Rev 2 SPRS by 06/30/2026, 95%+ Rev 3 compliance by 09/15/2026.*
