# System Security Planning Policy

**Policy Number:** TCC-SPP-001
**Version:** 1.0 DRAFT
**Effective Date:** [TBD - Target: Phase 2 completion]
**Last Reviewed:** March 18, 2026
**Policy Owner:** System Owner (sysadmin)
**Approval Authority:** System Owner (sysadmin)

---

## 1. PURPOSE

This policy establishes requirements for the development, documentation, review, and maintenance of the System Security Plan (SSP), Plan of Action and Milestones (POA&M), and Rules of Behavior (RoB) for the CyberHygiene Production Network (CPN). This policy satisfies the Planning (PL) control family requirements in NIST SP 800-171 Revision 3.

---

## 2. SCOPE

This policy applies to:
- All systems within the CPN boundary processing Controlled Unclassified Information (CUI)
- The System Security Plan (SSP) and associated documentation
- The Plan of Action and Milestones (POA&M) tracking security deficiencies
- Rules of Behavior (RoB) for all users with CUI access
- Configuration baseline selection and management

**Systems in Scope:**
- dc1.example.local (10.0.0.10) — FreeIPA domain controller, Wazuh SIEM manager
- workstation1.example.local (10.0.0.115) — Development workstation
- workstation2.example.local (10.0.0.104) — Engineering workstation
- workstation3.example.local (10.0.0.113) — Accounting workstation

---

## 3. POLICY STATEMENTS

### 3.1 System Security Plan (SSP) — NIST 3.12.1 (PL-2)

**3.1.1 SSP Development**

CyberHygiene shall develop and maintain a comprehensive System Security Plan that:

a) **Describes the system boundary** — Clearly defines which systems, networks, and facilities are included in the CUI processing environment

b) **Documents the operational environment** — Describes:
   - System architecture and network topology
   - Hardware and software inventory
   - Data flows and CUI storage locations
   - Physical location and facility security
   - Personnel roles and responsibilities

c) **Identifies security requirements** — Documents:
   - Applicable NIST SP 800-171 Rev 3 controls (97 controls across 17 families)
   - Organization-Defined Parameters (ODPs) with tailored values
   - Contractual security requirements (DFARS, CMMC, etc.)

d) **Describes security control implementation** — For each applicable control:
   - Implementation status (implemented, partially implemented, planned, not applicable)
   - Implementation description (how the control is satisfied)
   - Responsible party (role or individual)
   - Assessment procedures and evidence

e) **Documents related security documentation** — References to:
   - Security policies (all TCC-* policy documents)
   - Procedures and work instructions
   - Configuration baselines
   - Risk assessments
   - Incident response plans
   - Contingency plans

**3.1.2 SSP Review and Update Frequency (ODP-PL-1)**

The SSP shall be reviewed and updated:

a) **Annually** — At minimum, a comprehensive review shall be conducted each year
   - **Target month:** April (aligned with annual risk assessment cycle)
   - **Review scope:** All 97 Rev 3 controls, system changes, updated threats

b) **Upon significant changes** — An interim review shall be conducted when:
   - New systems are added to the CUI boundary
   - Major system upgrades or architecture changes occur
   - New contracts impose additional security requirements
   - Security control implementations change significantly
   - Major security incidents occur
   - Risk assessment findings require control updates

c) **Change-driven updates** — Minor updates may occur as needed without full review:
   - Updating ODP values
   - Correcting errors or clarifications
   - Updating evidence references
   - Updating contact information

**3.1.3 SSP Version Control**

All SSP versions shall be:
- Numbered sequentially (e.g., v1.0, v1.1, v2.0)
- Major version (X.0) indicates comprehensive review/reorganization
- Minor version (x.Y) indicates updates or corrections
- Dated with effective date
- Approved by System Owner (signature/electronic approval)
- Archived for historical record (minimum 3 years)

**Current SSP:** System_Security_Plan_v2.9.docx (NIST 800-171 Rev 2)
**Planned SSP:** System_Security_Plan_v3.0.docx (NIST 800-171 Rev 3, target Phase 2)

**3.1.4 SSP Distribution and Protection**

The SSP contains sensitive security information and shall be:
- Marked "Controlled Unclassified Information" or "Internal Use Only"
- Distributed only to authorized personnel (system owner, assessors, auditors, contracting officers as required)
- Stored securely (encrypted at rest, access controls)
- Transmitted securely (encrypted email, secure file transfer)
- Not published publicly

**3.1.5 SSP Format and Content Requirements**

The SSP shall follow the format specified in NIST SP 800-171 Rev 3 Appendix D or a substantially equivalent format. Minimum content:

1. **Section 1: System Identification**
   - System name, boundary, and authorization
   - System owner and key personnel
   - System categorization (CUI, impact level)

2. **Section 2: System Overview**
   - System description and purpose
   - System architecture diagrams
   - Network topology
   - Hardware and software inventory (reference SBOM)

3. **Section 3-19: Security Control Families** (17 families)
   - Access Control (AC) — 3.1.x
   - Awareness and Training (AT) — 3.2.x
   - Audit and Accountability (AU) — 3.3.x
   - Configuration Management (CM) — 3.4.x
   - Identification and Authentication (IA) — 3.5.x
   - Incident Response (IR) — 3.6.x
   - Maintenance (MA) — 3.7.x
   - Media Protection (MP) — 3.8.x
   - Personnel Security (PS) — 3.9.x
   - Physical Protection (PE) — 3.10.x
   - Risk Assessment (RA) — 3.11.x
   - Planning (PL) — 3.12.x **(NEW in Rev 3)**
   - System and Communications Protection (SC) — 3.13.x
   - System and Information Integrity (SI) — 3.14.x
   - System and Services Acquisition (SA) — 3.12.x **(NEW in Rev 3)**
   - Supply Chain Risk Management (SR) — 3.13.x **(NEW in Rev 3)**

4. **Appendices**
   - Appendix A: Acronyms and Abbreviations
   - Appendix B: References
   - Appendix C: Organization-Defined Parameters (ODPs)
   - Appendix D: Security Control Assessment Results
   - Appendix E: POA&M Summary
   - Appendix F: Software Bill of Materials (SBOM)

---

### 3.2 Plan of Action and Milestones (POA&M) — NIST 3.12.3 (PL-3)

**3.2.1 POA&M Purpose**

The Plan of Action and Milestones (POA&M) is a living document that:
- Identifies security deficiencies (controls not fully implemented)
- Documents planned remediation actions
- Establishes milestones and target completion dates
- Tracks remediation progress
- Provides accountability for security improvements

**3.2.2 POA&M Content Requirements**

Each POA&M item shall include:

a) **Deficiency Identification**
   - Control ID and name (e.g., 3.11.1 Periodic Risk Assessments)
   - Gap description (what is missing or insufficient)
   - Risk level (Critical, High, Medium, Low based on impact)
   - Discovery date and source (assessment, audit, incident, etc.)

b) **Remediation Plan**
   - Specific actions required to close the gap
   - Resources required (personnel, budget, tools)
   - Dependencies (prerequisites, related items)
   - Responsible party

c) **Milestones and Dates**
   - Target completion date
   - Interim milestones (if multi-phase remediation)
   - Status (Planned, In Progress, Completed, Delayed)

d) **Impact Assessment**
   - SPRS score impact (if applicable)
   - Operational impact (severity if exploited)
   - Compliance impact (blocks certification, contract award, etc.)

**3.2.3 POA&M Update Frequency (ODP-PL-2)**

The POA&M shall be updated:

a) **Monthly** — At minimum, a review shall be conducted each month
   - Update status of all open items
   - Add new items as identified
   - Close completed items with evidence
   - Adjust target dates if needed (with justification)

b) **Event-driven updates** — Immediate updates when:
   - New gaps identified (assessments, audits, incidents)
   - POA&M items completed (with verification evidence)
   - Target dates change significantly (>30 days)
   - Risk levels change

**3.2.4 POA&M Prioritization**

POA&M items shall be prioritized using:

**Risk-Based Prioritization:**
- **Critical:** SPRS impact ≥3 points, blocks contract award, or major operational risk
- **High:** SPRS impact 1-2 points, compliance requirement, or moderate risk
- **Medium:** Best practice, minor compliance gap, or low risk
- **Low:** Enhancement, future planning

**Remediation Timelines:**
- **Critical:** Target ≤90 days
- **High:** Target ≤180 days
- **Medium:** Target ≤365 days
- **Low:** As resources allow

**3.2.5 POA&M Reporting**

The POA&M shall be:
- Reviewed monthly by System Owner
- Provided to assessors during C3PAO assessments
- Provided to contracting officers as required by contract (e.g., DFARS 252.204-7012)
- Maintained for 3 years after item closure

**Current POA&M:** Unified_POAM_v2.11.md (Rev 2)
**Planned POA&M:** Unified_POAM_v3.0.md (Rev 3, target Phase 2)

---

### 3.3 Rules of Behavior (RoB) — NIST 3.12.4 (PL-4)

**3.3.1 Rules of Behavior Purpose**

Rules of Behavior establish user responsibilities and expected behavior for:
- Accessing CUI
- Using CPN systems
- Protecting sensitive information
- Reporting security incidents
- Complying with security policies

**3.3.2 Rules of Behavior Content**

The Rules of Behavior document shall address:

a) **Access and Authentication**
   - Use of strong passwords and multi-factor authentication (MFA)
   - Protection of credentials (no sharing, no writing down)
   - Session lock and termination requirements
   - Remote access security procedures

b) **CUI Handling**
   - CUI identification and marking requirements
   - Authorized CUI storage locations (no personal devices, cloud storage)
   - CUI transmission security (encrypted email, secure file transfer)
   - CUI disposal procedures (secure deletion, media sanitization)

c) **Acceptable Use**
   - Authorized use of systems and data
   - Prohibited activities (personal use, unauthorized software, etc.)
   - Email and internet usage guidelines
   - Mobile device and portable media restrictions

d) **Security Responsibilities**
   - Reporting security incidents immediately
   - Reporting suspicious activity or anomalies
   - Participating in security awareness training
   - Complying with security policies and procedures

e) **Consequences of Non-Compliance**
   - Disciplinary actions (warning, suspension, termination)
   - Legal consequences (criminal prosecution for willful violations)
   - Contract implications (loss of CUI access, clearance suspension)

**3.3.3 Rules of Behavior Acknowledgment (ODP-PL-3)**

All users with CUI access shall:

a) **Initial acknowledgment** — Before being granted access:
   - Read and understand the Rules of Behavior
   - Sign acknowledgment form (electronic or physical signature)
   - Receive copy of Rules of Behavior document

b) **Annual re-acknowledgment** — Once per year:
   - Review updated Rules of Behavior (if changed)
   - Re-sign acknowledgment form
   - Aligned with annual security awareness training cycle

c) **Update-driven acknowledgment** — When Rules of Behavior change significantly:
   - Users notified of changes
   - Users required to re-acknowledge within 30 days

**Exception for Solopreneur Environment:**
For CyberHygiene (owner-operator with no additional users), annual acknowledgment may be documented via:
- Self-certification in annual security review documentation
- Integration with annual SSP review process
- Acknowledgment documented in SSP or training records

**3.3.4 Rules of Behavior Document Location**

The Rules of Behavior shall be:
- Published as standalone document: `Rules_of_Behavior_v1.0.docx` (to be created Phase 3)
- **OR** integrated into existing TCC-AUP-001 (Acceptable Use Policy) Section 2 and relabeled as "Rules of Behavior"
- Accessible to all users with CUI access
- Referenced in TCC-ATP-001 (Awareness and Training) annual training materials

---

### 3.4 Baseline Selection — NIST 3.12.10 (PL-10)

**3.4.1 Configuration Baseline Purpose**

A configuration baseline establishes the approved, standardized configuration for CPN systems that:
- Ensures consistent security settings across all systems
- Provides a reference for detecting unauthorized changes
- Satisfies NIST SP 800-171 Rev 3 configuration management requirements
- Enables automated compliance validation

**3.4.2 Baseline Selection Methodology**

CyberHygiene has selected the following configuration baseline:

**Primary Baseline:** SCAP Security Guide (SSG) — CUI Profile for Rocky Linux 9

**Justification:**
- Published by NIST-certified content provider (ComplianceAsCode project)
- Specifically designed for NIST SP 800-171 CUI protection
- Maps directly to NIST 800-171 controls (automated validation)
- Maintained and updated for new threats and vulnerabilities
- Supports automated scanning via OpenSCAP

**Baseline Components:**
- Operating system: Rocky Linux 9.x
- Kernel: 5.14.0+ with FIPS 140-2 mode enabled
- Security profile: SCAP Security Guide (SSG) CUI profile
- 104 automated configuration rules
- Manual controls documented in SSP

**3.4.3 Baseline Documentation**

The configuration baseline shall be documented in:
- **Configuration Baseline Document** (to be created Phase 3): Describes baseline selection, rationale, and deviations
- **OpenSCAP scan results:** Weekly automated validation (100% compliance required)
- **SSP Section 4.2:** System configuration standards

**3.4.4 Baseline Validation**

Configuration compliance shall be validated via:

a) **Automated scanning** — OpenSCAP scans:
   - **Frequency:** Weekly (every Sunday at 2:00 AM via cron)
   - **Tool:** OpenSCAP 1.3.x with SCAP Security Guide
   - **Profile:** xccdf_org.ssgproject.content_profile_cui
   - **Pass criteria:** 100% compliance (all 104 rules passing)
   - **Results:** Stored in `/var/www/internal-dashboards/openscap/`
   - **Dashboard:** https://dc1.example.local/dashboard/openscap-dashboard.html

b) **Manual validation** — Annual review:
   - System Owner reviews OpenSCAP results
   - Verifies no unauthorized deviations
   - Documents approved exceptions (if any)
   - Updates baseline documentation if configuration changes

**3.4.5 Baseline Deviations**

Any deviations from the baseline must be:
- **Documented** with technical and operational justification
- **Approved** by System Owner
- **Tracked** in SSP or POA&M (if deviation creates security gap)
- **Re-evaluated** annually

**Current Status:** Zero baseline deviations (100% OpenSCAP compliance on all 4 systems as of March 18, 2026)

---

## 4. ROLES AND [REDACTED_TOTP_SECRET]

### 4.1 System Owner (sysadmin)

- Approve SSP and all updates
- Approve POA&M and prioritize remediation
- Approve Rules of Behavior and configuration baseline
- Conduct annual reviews of all planning documents
- Sign acknowledgment of Rules of Behavior (self-certification)
- Ensure compliance with this policy

### 4.2 Administrator (sysadmin)

- Maintain SSP, POA&M, and related documentation
- Update POA&M monthly with status of open items
- Collect evidence for SSP control implementation
- Conduct OpenSCAP scans and monitor compliance
- Implement configuration baseline on all systems
- Report baseline deviations to System Owner

### 4.3 Users (if applicable)

- Acknowledge Rules of Behavior before CUI access
- Re-acknowledge annually
- Comply with Rules of Behavior at all times
- Report security incidents and violations

**Note:** For CyberHygiene (solopreneur), System Owner and Administrator are the same person (sysadmin), and there are currently no additional users with CUI access.

---

## 5. PROCEDURES

### 5.1 SSP Annual Review Procedure

**Frequency:** Annually, target month April

**Steps:**
1. **Schedule review** — Block 8-10 hours in April for comprehensive review
2. **Gather inputs:**
   - Risk assessment results (completed by 04/30 per POA&M)
   - POA&M status (items closed since last review)
   - OpenSCAP scan results (last 12 months)
   - Wazuh SIEM reports (security incidents, alerts)
   - System changes (new hardware, software, services)
   - Contract changes (new requirements, updated DFARS clauses)
3. **Review each control family (17 families):**
   - Verify control implementation status unchanged or improved
   - Update control descriptions if implementation changed
   - Add evidence references (logs, configs, policies, test results)
   - Update ODPs if values changed
4. **Update system descriptions:**
   - Hardware inventory (reference SBOM)
   - Network topology (update diagrams if changed)
   - Data flows (add/remove CUI data types)
5. **Increment version number:**
   - Major version if comprehensive reorganization (e.g., v2.9 → v3.0 for Rev 2 → Rev 3)
   - Minor version if updates only (e.g., v3.0 → v3.1)
6. **Approve and distribute:**
   - System Owner reviews and approves (signature/date)
   - Archive previous version
   - Distribute to authorized parties (assessors, contracting officers if requested)
7. **Document review completion:**
   - Record review date in SSP Section 1
   - Record next review date (12 months)
   - Update POA&M if new gaps identified

### 5.2 POA&M Monthly Update Procedure

**Frequency:** Monthly, first week of each month

**Steps:**
1. **Review all open POA&M items:**
   - Check status (Planned → In Progress → Completed)
   - Verify progress against milestones
   - Update completion percentage (if applicable)
2. **Add new items:**
   - From assessments, audits, scans, incidents
   - Assign risk level, target date, responsible party
3. **Close completed items:**
   - Verify remediation implemented
   - Collect evidence (configs, test results, policies)
   - Update SSP control status if applicable
   - Mark item "Completed" with closure date
4. **Adjust target dates if needed:**
   - Document justification for delays
   - Update milestones
   - Re-prioritize if risk level changed
5. **Increment version number:**
   - Minor version for monthly updates (e.g., v3.0 → v3.1)
6. **Save and archive:**
   - Save updated POA&M with new version number
   - Archive in `/home/sysadmin/CyberSecurity/Current/POAM/`

### 5.3 Rules of Behavior Acknowledgment Procedure

**Frequency:** Annually (aligned with training cycle)

**Steps:**
1. **Distribute Rules of Behavior:**
   - Provide document to all users with CUI access
   - Explain any changes since last version
2. **User reads and acknowledges:**
   - User signs acknowledgment form
   - Electronic signature acceptable (email confirmation, digital signature)
3. **Record acknowledgment:**
   - Maintain acknowledgment records for 3 years
   - Track in training records or SSP Appendix
4. **For solopreneur (CyberHygiene):**
   - System Owner self-certifies compliance with RoB
   - Document certification in annual SSP review or training completion record
   - No separate acknowledgment form required

### 5.4 Configuration Baseline Validation Procedure

**Frequency:** Weekly (automated), Annually (manual review)

**Automated Validation (Weekly):**
1. **OpenSCAP scan executes** — Every Sunday at 2:00 AM via cron
2. **Results collected** — Script `/home/sysadmin/scripts/collect_openscap_results.sh` aggregates results from all 4 systems
3. **Dashboard updated** — https://dc1.example.local/dashboard/openscap-dashboard.html
4. **Pass criteria:** 100% compliance (104/104 rules passing)
5. **Alerting:** If any rules fail, Wazuh alert generated

**Manual Review (Annual):**
1. **Review 12 months of OpenSCAP results** — Verify consistent 100% compliance
2. **Investigate any failures** — Root cause analysis for any failed scans
3. **Document exceptions** — If baseline deviations approved, document in Configuration Baseline Document
4. **Update baseline if needed** — If SCAP Security Guide updated, test new profile before deployment

---

## 6. COMPLIANCE

This policy supports compliance with:
- NIST SP 800-171 Rev 3 Planning (PL) family controls:
  - 3.12.1 (PL-2): System Security Plans
  - 3.12.2: SSP Updates
  - 3.12.3 (PL-3): Plan of Action and Milestones
  - 3.12.4 (PL-4): Rules of Behavior
  - 3.12.10 (PL-10): Baseline Selection (referenced from CM family)
- DFARS 252.204-7012 (Safeguarding CUI)
- CMMC Level 2 (Planning domain)

---

## 7. DEFINITIONS

**Configuration Baseline:** The approved, standardized configuration for a system or component.

**Controlled Unclassified Information (CUI):** Information the Government creates or possesses, or an entity creates or possesses for or on behalf of the Government, that a law, regulation, or Government-wide policy requires or permits an agency to handle using safeguarding or dissemination controls.

**Organization-Defined Parameter (ODP):** A variable in a security control that must be defined by the organization (e.g., password length, audit retention period).

**Plan of Action and Milestones (POA&M):** A document identifying tasks to be accomplished to close security gaps, with milestones and target dates.

**Rules of Behavior (RoB):** A document describing user responsibilities and expected behavior for accessing and using systems and information.

**System Security Plan (SSP):** A comprehensive document describing the system boundary, operational environment, security requirements, and control implementations.

---

## 8. REFERENCES

- NIST SP 800-171 Rev 3 (Planning family, controls 3.12.x)
- NIST SP 800-18 Rev 1 (Guide for Developing Security Plans)
- NIST SP 800-37 Rev 2 (Risk Management Framework)
- NIST SP 800-53 Rev 5 (PL family source controls)
- DFARS 252.204-7012 (Safeguarding CUI and Cyber Incident Reporting)
- SCAP Security Guide (SSG) for Rocky Linux 9
- CyberHygiene SSP v2.9 (current), v3.0 (planned)
- CyberHygiene POA&M v2.11 (current), v3.0 (planned)
- CyberHygiene TCC-AUP-001 (Acceptable Use Policy) — contains implicit Rules of Behavior

---

## 9. POLICY REVIEW

This policy shall be reviewed and updated:
- **Annually** — Target month: April (aligned with SSP review)
- **Upon significant changes** — To NIST 800-171 requirements, organizational structure, or system architecture

**Next Review Date:** April 2027

---

## 10. APPROVAL

**Policy Approved By:**

**System Owner:** _____________________________ Date: __________
sysadmin

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 DRAFT | March 18, 2026 | Claude (AI Assistant) | Initial draft created for Rev 3 transition (Phase 2) |
| 1.0 | [TBD] | sysadmin | Reviewed, customized, and approved |

---

**END OF POLICY**

---

## APPENDIX A: SSP TEMPLATE OUTLINE (For SSP v3.0 Creation)

**System Security Plan v3.0 — Table of Contents**

1. System Identification
   1.1 System Name and Boundary
   1.2 System Owner and Personnel
   1.3 System Categorization

2. System Overview
   2.1 System Description and Purpose
   2.2 System Architecture
   2.3 Network Topology
   2.4 Hardware and Software Inventory (Reference SBOM v3.0)
   2.5 Data Flows and CUI Storage

3. Access Control (AC) — 3.1.x (22 controls)
4. Awareness and Training (AT) — 3.2.x (3 controls)
5. Audit and Accountability (AU) — 3.3.x (9 controls)
6. Configuration Management (CM) — 3.4.x (11 controls)
7. Identification and Authentication (IA) — 3.5.x (11 controls)
8. Incident Response (IR) — 3.6.x (6 controls)
9. Maintenance (MA) — 3.7.x (6 controls)
10. Media Protection (MP) — 3.8.x (8 controls)
11. Personnel Security (PS) — 3.9.x (7 controls)
12. Physical Protection (PE) — 3.10.x (6 controls)
13. Risk Assessment (RA) — 3.11.x (3 controls)
14. Planning (PL) — 3.12.x (4 controls) **(NEW in Rev 3)**
15. System and Communications Protection (SC) — 3.13.x (20 controls)
16. System and Information Integrity (SI) — 3.14.x (16 controls)
17. System and Services Acquisition (SA) — 3.12.x (9 controls) **(NEW in Rev 3)**
18. Supply Chain Risk Management (SR) — 3.13.x (5 controls) **(NEW in Rev 3)**

Appendices
- Appendix A: Acronyms
- Appendix B: References
- Appendix C: Organization-Defined Parameters (49 ODPs)
- Appendix D: Assessment Results
- Appendix E: POA&M Summary
- Appendix F: Software Bill of Materials (SBOM v3.0)

---

## APPENDIX B: POA&M TEMPLATE

**Plan of Action and Milestones (POA&M) v3.0 Template**

| Item # | Control ID | Control Name | Gap Description | Risk Level | Discovery Date | Target Date | Status | Responsible | Actions Required | Evidence | SPRS Impact |
|--------|------------|--------------|-----------------|------------|----------------|-------------|--------|-------------|------------------|----------|-------------|
| 1 | 3.11.1 | Periodic Risk Assessments | No formal risk assessment conducted | Critical | 2026-02-09 | 2026-04-30 | In Progress | sysadmin | Conduct formal risk assessment per NIST 800-30 | Risk Assessment Report v1.0 | -3 pts |
| 2 | 3.6.3 | IR Testing | No IR tabletop exercise conducted | High | 2026-02-09 | 2026-06-30 | Planned | sysadmin | Conduct ransomware tabletop exercise | Exercise documentation, lessons learned | -1 pt |
| 3 | 3.13.1 | Supply Chain Risk Assessment | No formal SCRM assessment | High | 2026-03-18 | 2026-04-30 | Planned | sysadmin | Conduct supply chain risk assessment (integrate with Item 1) | SCRM section in Risk Assessment | N/A (Rev 3) |

---

**TCC-SPP-001 Policy v1.0 DRAFT**
**Created:** March 18, 2026
**Status:** DRAFT — Ready for review and customization in Phase 2
**Estimated customization effort:** 4-6 hours (review, adjust for your environment, approve)
