# System Security Plan v3.0 — Part 1: Front Matter and System Description

**NIST SP 800-171 Revision 3 Compliance**
**CyberHygiene Production Network**

---

## Document Control

**System Name:** CyberHygiene Production Network (CPN)
**System Identifier:** CPN-001
**SSP Version:** 3.0
**Framework:** NIST SP 800-171 Revision 3
**Date:** March 18, 2026
**Classification:** CUI (Controlled Unclassified Information)

**System Owner:** sysadmin
**Authorizing Official:** sysadmin
**Information System Security Officer (ISSO):** sysadmin
**System Administrator:** sysadmin

---

## Version History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 3.0 | 2026-03-18 | sysadmin | Rev 3 transition — 97 controls, 17 families, 49 ODPs documented |
| 2.9 | 2026-02-21 | sysadmin | MFA deployment, admin switchover to sysadmin+sudo, 100% OpenSCAP compliance |
| 2.8 | 2026-02-18 | sysadmin | Administrator access method change (PermitRootLogin no) |
| 2.7 | 2026-01-15 | sysadmin | Accounting deployment complete |
| 2.6 | 2026-01-10 | sysadmin | SSH hardening Phase 2 complete |
| 2.5 | 2025-12-20 | sysadmin | Engineering workstation deployed |
| 2.0-2.4 | 2025 | sysadmin | Initial Rev 2 SSP development and evolution |

---

## Distribution List

- **Internal:** sysadmin (System Owner, Authorizing Official, ISSO)
- **External (as required):**
  - Contracting Officers (GSA contracts requiring Rev 3 compliance)
  - C3PAO Assessors (when Rev 3 assessments become available)
  - Auditors (read-only access, specific engagement)

**Handling Instructions:** This document contains CUI. Protect per NIST SP 800-171 requirements. Do not distribute outside authorized personnel without System Owner approval.

---

## Review and Approval Schedule

**Review Frequency (per TCC-SPP-001 Section 4.1.2):**
- **Quarterly Review:** Sections 1-3 (System Description, Environment, Architecture)
- **Semi-Annual Review:** Sections 4-20 (Control Families)
- **Annual Review:** Complete document review, all sections, signature page update
- **Triggered Review:** Upon significant system changes, new ODPs, major policy updates, regulatory changes

**Next Scheduled Reviews:**
- **Quarterly:** June 15, 2026 (Sections 1-3)
- **Semi-Annual:** September 15, 2026 (Sections 4-20)
- **Annual:** March 18, 2027 (Complete document)

---

## Table of Contents

### Part 1: Front Matter and System Description
- Section 0: Executive Summary
- Section 1: System Identification and Description
- Section 2: System Environment
- Section 3: System Architecture

### Part 2: Core Control Families (Complete Policies)
- Section 6: Audit and Accountability (AU)
- Section 7: Configuration Management (CM)
- Section 8: Identification and Authentication (IA)

### Part 3: New Control Families (Rev 3)
- Section 14: Planning (PL) — NEW
- Section 18: System and Services Acquisition (SA) — NEW
- Section 19: Supply Chain Risk Management (SR) — NEW

### Part 4: Remaining Control Families
- Section 4: Access Control (AC)
- Section 5: Awareness and Training (AT)
- Section 9: Incident Response (IR)
- Section 10: Maintenance (MA)
- Section 11: Media Protection (MP)
- Section 12: Physical Protection (PE)
- Section 13: Personnel Security (PS)
- Section 15: Risk Assessment (RA)
- Section 16: System and Communications Protection (SC)
- Section 17: System and Information Integrity (SI)

### Part 5: Supporting Sections
- Section 21: Organization-Defined Parameters (ODP Summary)
- Section 22: Determination Statements Evidence Mapping
- Section 23: Plan of Action and Milestones (POA&M)
- Section 24: Related Documentation

### Appendices
- Appendix A: Acronyms and Definitions
- Appendix B: System Component Details
- Appendix C: Network Diagrams
- Appendix D: Control-to-Policy Mapping (Rev 3)
- Appendix E: ODP Tailoring Document
- Appendix F: Signature Page

---

# Section 0: Executive Summary

## 0.1. Document Purpose

This System Security Plan (SSP) documents the implementation of NIST SP 800-171 Revision 3 security controls for the CyberHygiene Production Network (CPN).

CPN handles Controlled Unclassified Information (CUI) for federal contracts requiring NIST SP 800-171 compliance, including General Services Administration (GSA) contracts mandating Revision 3 "adequate security" standards.

This SSP supersedes SSP v2.9 (Revision 2, February 2026) and reflects the transition from 110 Rev 2 controls across 14 families to 97 Rev 3 controls across 17 families. The transition addresses:

- **Three new control families:** Planning (PL), System and Services Acquisition (SA), Supply Chain Risk Management (SR)
- **49 explicit Organization-Defined Parameters (ODPs)** replacing ambiguous "periodically" language
- **422 determination statements** (up from 320 in Rev 2) requiring detailed evidence mapping
- **Control consolidations** reducing total count from 110 to 97 through merging related requirements

## 0.2. Revision 3 Transition Summary

**Transition Timeline:** March 18, 2026 — September 15, 2026 (6 months, 4 phases)

**Phase 1: Gap Analysis (Weeks 1-4)** — ✅ COMPLETE
- Control mapping matrix: 97 Rev 3 controls mapped to current implementations
- ODP tailoring: All 49 parameters defined with DoD baseline comparisons
- Determination statement checklist: Framework for validating 422 statements
- Gap analysis: 80.4% controls fully implemented, 17.5% partial, 2.1% not met

**Phase 2: Documentation (Weeks 5-10)** — 🔄 IN PROGRESS (50% complete)
- 14 Rev 3 policies: 6 complete (3 new + 3 updated), 8 summaries created
- SSP v3.0: Framework complete, implementation in progress (this document)
- POA&M v3.0: Complete, tracking 21 active items across Phases 2-4
- Key Differences document: Complete, 47KB policy review aid

**Phase 3: Technical (Weeks 11-18)** — ⏸️ PLANNED
- SBOM v3.0: Enhance v2.4 with supply chain provenance, critical component flags
- Network diagrams: Architecture, topology, data flow (SC-7 evidence)
- Evidence artifacts: Baseline docs, audit inventory, external services, security principles
- Target start: May 1, 2026

**Phase 4: Validation (Weeks 19-24)** — ⏸️ PLANNED
- 422 determination statements validated with evidence
- ODP verification: All 49 parameters verified against technical implementations
- Evidence package: Complete assessment-ready directory structure
- Self-assessment: Rev 3 compliance validation, 95%+ target
- Target start: July 1, 2026

**Estimated Completion:** September 15, 2026 (on track)

## 0.3. Compliance Status Overview

### Revision 2 (Current Production Standard)

**SPRS Score:** 106/110 (96.4% compliant)

**Control Implementation:**
- Fully Implemented: 108 of 110 controls (98.2%)
- Outstanding Gaps: 2 controls (-4 SPRS points)
  - 3.11.1 (RA-3): Periodic Risk Assessment — Target: 04/30/2026 (-3 points)
  - 3.6.3 (IR-3): Incident Response Testing — Target: 06/30/2026 (-1 point)

**OpenSCAP Compliance:** 100% (104 of 104 rules passing on all 4 systems)
- dc1.example.local: 104/104 (100%)
- workstation1.example.local: 104/104 (100%)
- workstation2.example.local: 104/104 (100%)
- workstation3.example.local: 104/104 (100%)
- Last validated: Weekly automated scans (Tuesdays)

**Target:** 110/110 SPRS (100% compliance) by June 30, 2026

### Revision 3 (Transition in Progress)

**Implementation Status:** 80.4% fully implemented (78 of 97 controls)
- Fully Implemented: 78 controls (80.4%)
- Partially Implemented: 17 controls (17.5%) — mostly documentation gaps
- Not Implemented: 2 controls (2.1%) — same as Rev 2 gaps (RA-3, IR-3)

**Determination Statements:** 340 of 422 MET (80.6%)
- MET: 340 statements (80.6%)
- PARTIAL: 70 statements (16.6%) — evidence exists, documentation needed
- NOT MET: 12 statements (2.8%) — tied to RA-3, IR-3 gaps

**Organization-Defined Parameters:** 43 of 49 meet/exceed DoD baseline (87.8%)
- Meets/Exceeds DoD: 43 ODPs (87.8%)
- Justified Deviations: 6 ODPs (12.2%) — all LOW risk, compensating controls documented

**Target:** 95%+ compliance (92-95 of 97 controls) by September 15, 2026

## 0.4. Key Achievements

### Multi-Factor Authentication (MFA) Deployed — February 21, 2026

**Implementation:** SSH key (ECDSA-521) + TOTP on all 4 systems
- **Technology:** pam_google_authenticator with Microsoft Authenticator app
- **Systems:** dc1 (.10), workstation1 (.115), workstation2 (.104), workstation3 (.113)
- **Configuration:** `/etc/ssh/sshd_config.d/60-mfa.conf` — AuthenticationMethods publickey,keyboard-interactive
- **SPRS Impact:** +5 points (101 → 106)
- **Rev 3 Alignment:** Exceeds IA-2 MFA requirements

**Significance:** MFA deployment ahead of most organizations of similar size. Demonstrates commitment to authentication security and positions CyberHygiene favorably for CMMC Level 2 certification.

### 100% OpenSCAP Compliance — Maintained Since February 21, 2026

**Achievement:** All 104 SCAP Security Guide CUI profile rules passing on all 4 systems
- **Baseline:** SCAP Security Guide CUI profile for Rocky Linux 9
- **Validation:** Weekly automated scans, dashboard monitoring
- **Dashboard:** https://dc1.example.local/dashboard/openscap-dashboard.html
- **Scope:** 104 rules across AC, AU, CM, IA, SC, SI control families

**Significance:** 100% OpenSCAP compliance is rare and demonstrates exceptional technical control maturity. Provides automated validation of 80%+ of Rev 3 technical requirements.

### Comprehensive Software Bill of Materials (SBOM) — v2.4, Enhancing to v3.0

**Current State:** SBOM v2.4 tracks 5,626 packages across 6 systems
- **Format:** Markdown table with Package Name, Version, System, Update Date
- **Update Frequency:** Weekly automated collection
- **Coverage:** 100% of installed packages (OS + applications)

**Enhancement (v3.0):** Adding supply chain provenance per Rev 3 SR family
- Source repository URLs
- GPG signature verification status
- Critical component designation (Top 100)
- Supply chain trust chain documentation
- Target completion: May 30, 2026

**Significance:** SBOM v2.4 already exceeds most organizations' Rev 3 SR (Supply Chain Risk Management) readiness. Rare for organizations of this size to have comprehensive package tracking. Enhancement to v3.0 positions CyberHygiene as supply chain security leader.

### Wazuh SIEM — 100% System Coverage

**Implementation:** Centralized security monitoring with real-time correlation
- **Coverage:** 100% of systems (dc1 as manager, all workstations as agents)
- **Rules:** 2,500+ correlation rules (built-in + custom)
- **Integration:** auditd logs, SSH logs, application logs, file integrity monitoring
- **Alerting:** Real-time email + dashboard notifications
- **Retention:** 90 days local + 1 year Wazuh + indefinite backup (exceeds Rev 3 AU-11)

**Significance:** Comprehensive SIEM coverage provides continuous monitoring capability required by SI-4, AU-6, and IR-4. Real-time correlation enables rapid incident detection and response.

### FIPS 140-2 Validated Encryption Throughout

**Implementation:** Federal-grade cryptography across all layers
- **At Rest:** LUKS full disk encryption (FIPS 140-2 validated, all systems)
- **In Transit:** TLS 1.3 (OpenSSL FIPS module, Let's Encrypt/SSL.com certificates)
- **SSH:** ECDSA-521 keys, ChaCha20-Poly1305 cipher
- **Validation:** Rocky Linux 9 FIPS 140-2 mode enabled, cryptographic module validation verified

**Significance:** FIPS 140-2 validation exceeds Rev 3 SC-13 requirements and demonstrates commitment to federal cryptographic standards. Mandatory for DoD contracts, positions well for high-security environments.

### Administrator Access Control — Implemented February 18-21, 2026

**Implementation:** Named account (sysadmin) with sudo, root SSH disabled
- **Method:** PermitRootLogin no, sysadmin NOPASSWD sudo
- **Key:** ECDSA-521 (/home/sysadmin/.ssh/id_ecdsa)
- **Systems:** All 3 workstations (workstation1, workstation2, workstation3)
- **Compliance:** Satisfies AC-6 Least Privilege best practice

**Significance:** Disabling root SSH and using named accounts with MFA provides accountability and audit trail for all administrative actions. Aligns with CMMC and federal best practices.

## 0.5. Assessment Readiness

### Documentation Completeness

**Policies:** 14 Rev 3 policies (11 updated from Rev 2 + 3 new)
- ✅ TCC-SPP-001: System Security Planning Policy v1.0 (Planning family) — NEW
- ✅ TCC-SAP-001: System and Services Acquisition Policy v1.0 (SA family) — NEW
- ✅ TCC-SRMP-001: Supply Chain Risk Management Policy v1.0 (SR family) — NEW
- ✅ TCC-AAP-001: Audit and Accountability Policy v2.0 (Rev 3 update)
- ✅ TCC-IAP-001: Identification and Authentication Policy v2.0 (Rev 3 update)
- ✅ TCC-CMP-001: Configuration Management Policy v2.0 (Rev 3 update)
- 📋 8 additional policies: Summaries created, expansion in progress

**System Security Plan:** This document (SSP v3.0)
- Status: In progress (foundation sections complete, control families in progress)
- Target completion: May 15, 2026

**Plan of Action and Milestones:** POA&M v3.0
- Status: Complete, tracking 21 active items + 8 closed items
- Update frequency: Monthly (per TCC-SPP-001)
- Last updated: March 18, 2026

### Technical Evidence

**OpenSCAP Scan Results:**
- Weekly scans on all 4 systems
- 100% compliance (104/104 rules passing)
- Dashboard: https://dc1.example.local/dashboard/openscap-dashboard.html
- Historical data: 3+ months of consistent 100% compliance

**Wazuh SIEM Logs and Reports:**
- Real-time monitoring operational
- Audit log retention: 90 days local + 1 year Wazuh + indefinite backup
- Sample logs and correlation reports available for assessor review

**FreeIPA Configuration Exports:**
- User accounts, group memberships, RBAC policies
- Password policy settings (12 chars min, 90-day expiration, 24 history, 3 classes)
- Kerberos ticket policy
- Account lockout settings (3 attempts, 15-minute lockout)

**Firewall Rulesets (pfSense):**
- Default-deny egress and ingress
- Configuration export available
- Rule documentation mapping to SC-7 requirements

**MFA Configuration Evidence:**
- SSH configurations: `/etc/ssh/sshd_config.d/60-mfa.conf` (all systems)
- PAM configurations: `/etc/pam.d/sshd` (pam_google_authenticator integration)
- TOTP deployment screenshots (Microsoft Authenticator)
- SELinux custom module: sshd_google_auth.te (allows TOTP secret storage)

### Process Evidence

**Training Records (FY2026):**
- Security Awareness Training: Complete (sysadmin)
- Training Assessment Quiz: Passed
- Training Completion Record: On file
- Frequency: Annual (per ODP-AT-1)

**Incident Response Plan:** TCC-IRP-001 (approved, tested tabletop scheduled 06/30/2026)

**Risk Assessment:** Template prepared (GAP001), formal assessment scheduled 04/30/2026

**Policy Review Logs:** Annual review cycle documented in TCC-SPP-001

### Remaining Gaps (POA&M Items)

**Critical Path (Blocking 100% Rev 2 Compliance):**
1. POA&M-001: Periodic Risk Assessment (RA-3) — Target: 04/30/2026 (-3 SPRS points)
2. POA&M-002: Incident Response Testing (IR-3) — Target: 06/30/2026 (-1 SPRS point)

**Phase 2 Documentation (Rev 3):**
3. POA&M-101: Complete 8 remaining policy updates — Target: 04/15/2026
4. POA&M-102: Finish SSP v3.0 — Target: 05/15/2026

**Phase 3 Technical (Rev 3):**
5. POA&M-201: SBOM v3.0 enhancement — Target: 05/30/2026
6. POA&M-202: Network architecture diagram — Target: 05/30/2026
7. POA&M-203: Configuration baseline document — Target: 06/05/2026
8. POA&M-204: Audit event inventory — Target: 06/10/2026
9. POA&M-205: External services inventory — Target: 06/15/2026
10. POA&M-206: Rules of Behavior formalization — Target: 06/15/2026
11. POA&M-207: Security workstation2 principles document — Target: 06/20/2026

**Phase 4 Validation (Rev 3):**
12. POA&M-301: 422 determination statements validation — Target: 08/15/2026
13. POA&M-302: ODP verification report — Target: 08/15/2026
14. POA&M-303: Policy compliance review — Target: 08/25/2026
15. POA&M-304: Evidence package assembly — Target: 09/05/2026
16. POA&M-305: Rev 3 self-assessment — Target: 09/10/2026

**Assessment Readiness Timeline:**
- **Rev 2 (100% SPRS):** June 30, 2026
- **Rev 3 (95%+ compliance):** September 15, 2026

---

# Section 1: System Identification and Description

## 1.1. System Name and Identifier

**System Name:** CyberHygiene Production Network (CPN)

**System Identifier:** CPN-001

**CAGE Code:** [If applicable — enter when obtained]

**DUNS Number:** [If applicable — enter when obtained]

**Alternative Names:** None

## 1.2. System Categorization

**FIPS 199 Security Categorization:**

| Security Objective | Impact Level | Rationale |
|-------------------|--------------|-----------|
| **Confidentiality** | MODERATE | System handles CUI for federal contracts. Loss of confidentiality could adversely affect organizational operations, assets, or individuals. No classified information. |
| **Integrity** | MODERATE | System supports business operations and contract performance. Loss of integrity could adversely affect mission completion, financial operations, and reputation. |
| **Availability** | MODERATE | System downtime impacts business continuity and contract deliverables. Not life-safety critical. Recovery time objective: 24-48 hours. |

**Overall System Categorization:** MODERATE

**Rationale for MODERATE:**
- CUI handling requires at minimum MODERATE confidentiality per NIST SP 800-171
- Business operations and contract performance depend on system integrity
- Availability loss impacts business but not life-safety or critical infrastructure
- No classified information handling (would require HIGH)
- Not public information system (would allow LOW)

**NIST SP 800-171 Applicability:** YES — System processes, stores, and transmits CUI

**NIST SP 800-60 Category:** General Support System (GSS) supporting contract operations

## 1.3. System Description and Purpose

### System Overview

The CyberHygiene Production Network provides secure computing infrastructure for federal contract support, CUI handling, software development, and business operations. The system consists of 4 workstations, 1 centralized server (domain controller and SIEM manager), network security infrastructure (firewall), and backup storage (NAS).

### Primary Functions

1. **Identity and Access Management**
   - FreeIPA centralized identity provider (Kerberos, LDAP)
   - User authentication (SSH key + TOTP multi-factor)
   - Role-based access control (RBAC via FreeIPA groups + sudo)
   - Password policy enforcement (12 chars, 90-day expiration, complexity)

2. **Security Information and Event Management (SIEM)**
   - Wazuh manager (dc1) with 100% agent coverage
   - Real-time log correlation and analysis
   - Intrusion detection and alerting
   - File integrity monitoring
   - Vulnerability assessment

3. **Centralized Logging and Audit**
   - auditd kernel-level audit logging (all systems)
   - Wazuh log aggregation and retention
   - 90 days local + 1 year Wazuh + indefinite backup retention
   - Compliance reporting (OpenSCAP, Wazuh dashboards)

4. **File Storage and Backup**
   - NAS encrypted backup storage
   - Automated daily backups (all workstations + dc1)
   - Encrypted backup archives (GPG)
   - Offsite backup capability (future planned)

5. **Workstation Environment**
   - Rocky Linux 9.5 (RHEL-compatible, FIPS 140-2 validated)
   - Development tools (software workstation2, AI/ML)
   - Business applications (workstation3, communications)
   - CUI document creation and storage

6. **Network Security**
   - pfSense firewall with default-deny ruleset
   - Stateful packet inspection
   - VPN capability (OpenVPN, future planned)
   - Network segmentation (future VLANs if needed)

### System Mission

Support federal contract performance by providing a secure, compliant computing environment that:
- Protects CUI per NIST SP 800-171 requirements
- Enables software development and delivery
- Facilitates business operations and communications
- Maintains audit trails for accountability
- Provides continuous security monitoring

### System Lifecycle Stage

**Current Stage:** Operations and Maintenance

- **Development:** Complete (initial deployment 2024-2025)
- **Implementation:** Complete (incremental system additions through 2026)
- **Operations:** Active (daily production use)
- **Maintenance:** Ongoing (weekly updates, quarterly reviews, annual assessments)
- **Disposition:** Not applicable (active production system)

### System Dependencies

**Upstream Dependencies (External):**
- Internet connectivity (ISP)
- SSL.com / Let's Encrypt (TLS certificates)
- Rocky Linux repositories (OS and application updates)
- NTP servers (time synchronization)
- DNS forwarders (domain name resolution)

**Downstream Dependencies (Internal):**
- FreeIPA (dc1) provides authentication for all workstations
- Wazuh (dc1) provides monitoring for all systems
- pfSense firewall protects all internal systems
- NAS provides backup for all systems

## 1.4. CUI Handling and Classification

### CUI Categories Handled

Per CUI Registry (https://www.archives.gov/cui/registry/category-list):

**1. Contract Performance Data**
- **Category:** Procurement and Acquisition
- **Examples:** Source code, technical deliverables, design documents, test results
- **Marking:** "CUI//SP-PROCURE" or "CONTROLLED"
- **Justification:** Federal contracts require protection of contractor-developed information

**2. System Security Information**
- **Category:** Information Systems Security
- **Examples:** SSP (this document), POA&M, security policies, vulnerability assessments, configuration baselines
- **Marking:** "CUI//SP-INFOSEC" or "CONTROLLED"
- **Justification:** Security-related information requires protection per NIST SP 800-171

**3. Authentication Credentials**
- **Category:** Privacy Information
- **Examples:** FreeIPA user database, SSH keys, TOTP secrets, Kerberos tickets
- **Marking:** "CUI//SP-PRIVACY" or "CONTROLLED"
- **Justification:** Authentication data enables system access, requires strict protection

**4. Audit and Monitoring Logs**
- **Category:** Information Systems Security / Law Enforcement
- **Examples:** auditd logs, Wazuh SIEM logs, access logs, security event logs
- **Marking:** "CUI//SP-INFOSEC" or "CONTROLLED"
- **Justification:** Audit logs contain security-relevant information and user activity

**5. Business Operations Data**
- **Category:** Procurement and Acquisition / Financial
- **Examples:** Proposals, invoices, financial records, personnel information (future employees)
- **Marking:** "CUI//SP-PROCURE" or "CUI//SP-FIN" or "CONTROLLED"
- **Justification:** Business data related to federal contracts requires protection

### CUI Marking and Handling

**Marking Requirements:**
- All CUI documents must be marked with "CONTROLLED" or specific CUI banner
- Electronic files: Filename prefix or metadata field
- Printed materials: Header/footer on each page
- Emails: Subject line prefix "[CUI]"

**Handling Requirements:**
- Storage: Encrypted filesystems (LUKS full disk encryption)
- Transit: TLS 1.3 encrypted connections (FIPS 140-2 validated)
- Access: Multi-factor authentication required (SSH key + TOTP)
- Disposal: NIST SP 800-88 Rev 1 media sanitization
- Transmission: Encrypted channels only (HTTPS, SSH, encrypted email)

**CUI Registry Reference:** Maintained at https://www.archives.gov/cui/registry/category-list

**CUI Training:** Annual security awareness training includes CUI handling (completed FY2026)

### No Classified Information

**Important:** CyberHygiene Production Network does NOT handle classified information (CONFIDENTIAL, SECRET, TOP SECRET). All information is unclassified CUI or below. Classified information requires separate accreditation and facility security clearance not currently in place.

## 1.5. Authorization Boundary

### Boundary Definition

The authorization boundary encompasses all systems, data, and network connections within the CyberHygiene Production Network that process, store, or transmit CUI.

**Inside Boundary (Controlled Assets):**

**Systems:**
1. dc1.example.local (10.0.0.10) — Server (FreeIPA, Wazuh Manager)
2. workstation1.example.local (10.0.0.115) — Primary Workstation
3. workstation2.example.local (10.0.0.104) — Development Workstation
4. workstation3.example.local (10.0.0.113) — Business Workstation
5. ai.example.local (10.0.0.7) — AI/ML Workstation
6. pfSense Firewall (10.0.0.1) — Network Security
7. NAS (192.168.1.[X]) — Encrypted Backup Storage

**Network:**
- Internal network: 10.0.0.X/24 (all systems within this subnet)
- All traffic between systems (Kerberos, LDAP, SSH, HTTPS, Wazuh, NFS)

**Data:**
- All CUI stored on systems within boundary
- Encrypted backups on NAS
- FreeIPA user database and Kerberos tickets
- Audit logs (auditd, Wazuh)
- System configurations

**Outside Boundary (External Dependencies):**

**Internet:** Untrusted network, protected by pfSense firewall

**External Services (SA-9):**
1. SSL.com — TLS certificate provider (no CUI exchanged)
2. Let's Encrypt — TLS certificate provider (no CUI exchanged)
3. Rocky Linux repositories — OS/application packages (GPG signed)
4. NTP servers (pool.ntp.org) — Time synchronization (no CUI)
5. DNS forwarders (8.8.8.8, 1.1.1.1) — Domain name resolution (no CUI in queries)

**User Home Networks:** When accessing via VPN (future), home networks outside boundary

**Physical World:** Visitors, delivery personnel, physical access outside locked room

### Boundary Controls

**Network Boundary:**
- pfSense firewall with default-deny ruleset
- Stateful packet inspection
- Inbound traffic blocked except explicitly allowed services
- Outbound traffic filtered (whitelist approach where feasible)

**Physical Boundary:**
- Locked room (keyed access, sysadmin only)
- Camera surveillance (24/7 recording, 30-day retention)
- Intrusion detection (door/window sensors, alarm on breach)

**Logical Boundary:**
- FreeIPA authentication (Kerberos tickets required for system access)
- MFA (SSH key + TOTP) for all user accounts
- RBAC (sudo access controlled, NOPASSWD only where justified)
- SELinux (Mandatory Access Control, enforcing mode)

**Data Boundary:**
- LUKS full disk encryption (FIPS 140-2 validated, all systems)
- TLS 1.3 in transit (FIPS 140-2 validated)
- Encrypted backups (GPG, AES-256)

### Boundary Diagram

[Diagram to be included in Phase 3 — POA&M-202: Network Architecture Diagram]

Diagram will show:
- Authorization boundary (dotted line around internal network)
- Trust boundary (solid red line at firewall)
- Systems within boundary (servers, workstations, firewall, NAS)
- External services outside boundary (SSL.com, Rocky repos, NTP, DNS)
- CUI data flows (red arrows within boundary)
- Encrypted connections (green padlock icons)

## 1.6. System Owner and Key Personnel

### System Owner

**Name:** sysadmin
**Role:** System Owner
**Responsibilities:**
- Overall accountability for system security and compliance
- Approval of SSP, POA&M, and security policies
- Budget allocation for security controls and remediation
- Risk acceptance decisions
- System lifecycle management

**Contact:** [Contact information - not disclosed in this CUI document template]

### Authorizing Official

**Name:** sysadmin
**Role:** Authorizing Official (AO)
**Responsibilities:**
- Formal authorization to operate (ATO) decision
- Risk acceptance for POA&M items
- Approval of significant system changes
- Annual SSP review and signature
- Assessment results review and action approval

**Note:** In larger organizations, AO is typically separate from System Owner. For solopreneur organization, roles combined with documented acknowledgment of inherent conflict.

### Information System Security Officer (ISSO)

**Name:** sysadmin
**Role:** ISSO
**Responsibilities:**
- Daily security operations and monitoring
- POA&M maintenance (monthly updates)
- Policy implementation and enforcement
- Security event response and incident management
- Compliance reporting (OpenSCAP, Wazuh)
- Assessment coordination (C3PAO, self-assessments)

### System Administrator

**Name:** sysadmin
**Role:** System Administrator
**Responsibilities:**
- System installation, configuration, and maintenance
- User account management (FreeIPA)
- Patch management (weekly reviews, daily automated updates)
- Backup management (NAS, verification)
- Performance monitoring and optimization
- Technical troubleshooting

### Separation of Duties Considerations

**Challenge:** Solopreneur organization results in all roles performed by single individual (sysadmin)

**Mitigations:**
- **Comprehensive audit logging:** All administrative actions logged via auditd + Wazuh (AU family controls)
- **External review:** C3PAO assessments provide independent oversight (planned when Rev 3 assessments available)
- **Policy-driven:** Documented procedures in 14 security policies reduce ad-hoc decision making
- **Automated compliance:** OpenSCAP weekly scans provide objective validation (100% compliance)
- **Future expansion:** When contract employees hired, roles will be distributed (standard users, future admin)

**Documented in:** TCC-PS-001 Personnel Security Policy, Section on Separation of Duties

---

# Section 2: System Environment

## 2.1. Operational Environment

**Deployment Model:** On-premise (dedicated hardware in controlled facility)

**Organization Type:** Solopreneur (single-person company)

**Mission:** Federal contract support, CUI handling, software development, business operations

**Operating System:** Rocky Linux 9.5 (all systems)
- **Base:** RHEL-compatible (Red Hat Enterprise Linux binary-compatible clone)
- **FIPS 140-2:** Validated cryptographic modules enabled
- **Support:** Community-supported, 10-year lifecycle (through ~2032)
- **Updates:** Daily automated security updates, weekly manual review

**Virtualization:** None (bare metal deployment)
- **Rationale:** Maximum security, performance, and simplicity
- **Trade-off:** No VM isolation, but offset by physical system separation and firewall segmentation

**Cloud Services:** None (100% on-premise infrastructure)
- **Rationale:** Maximum control over CUI, no third-party cloud risk
- **Trade-off:** Physical security responsibility, but mitigated by locked facility

**Backup Strategy:** Local encrypted backups (NAS) + future offsite capability
- **Frequency:** Daily automated backups (all systems)
- **Encryption:** GPG AES-256 encrypted archives
- **Retention:** 30 days local (rotating), 1 year archived, critical configs indefinite
- **Offsite:** Planned (encrypted offsite storage for disaster recovery)

## 2.2. Physical Location

**Address:** [REDACTED — Physical address not disclosed in CUI document]

**Facility Type:** Dedicated office/workspace with computer room

**Physical Security Measures:**

**1. Physical Access Controls (PE-2, PE-3):**
- **Locked Room:** Keyed access, sysadmin only authorized
- **Visitor Logs:** Maintained for all non-sysadmin access (contractors, delivery, guests)
- **Escort Requirement:** All visitors escorted by sysadmin
- **Access Revocation:** Keys changed if compromised, future electronic locks for scalability

**2. Surveillance (PE-6):**
- **Camera System:** 24/7 video recording
- **Coverage:** Entry points, computer equipment area
- **Retention:** 30 days rolling (overwrite oldest)
- **Monitoring:** Periodic review, triggered review on security events

**3. Intrusion Detection (PE-6):**
- **Door/Window Sensors:** Alarm triggers on unauthorized breach
- **Notification:** Audio alarm + notification to sysadmin

**4. Environmental Controls (PE-14, PE-15):**
- **HVAC:** Temperature and humidity controlled (equipment within operating ranges)
- **Fire Suppression:** Smoke detectors, fire extinguisher (ABC rated)
- **Power:** UPS (Uninterruptible Power Supply) for graceful shutdown on outage
- **Water Detection:** Water sensors near equipment (if applicable)

**5. Physical Media Protection (MP-6):**
- **Media Disposal:** NIST SP 800-88 Rev 1 sanitization before disposal
- **Decommissioned Drives:** Physical destruction or cryptographic erasure (LUKS encryption renders data unrecoverable when keys destroyed)
- **Backup Media:** Encrypted, stored in locked room

**Compliance:** All physical security measures meet PE (Physical Protection) family requirements (PE-2, PE-3, PE-6, PE-14, PE-15)

## 2.3. User Community

### Current Users

**User: sysadmin**
- **Roles:** System Owner, Authorizing Official, ISSO, System Administrator, Primary User
- **Access Level:** Full administrative access (sudo NOPASSWD on all systems)
- **Authentication:** SSH key (ECDSA-521) + TOTP multi-factor
- **Workstations:** workstation1 (primary), workstation2 (dev), workstation3 (business), ai (AI/ML)
- **Training:** Security awareness training completed FY2026 (annual)

### Future Users (Planned Expansion)

**Contract Employees (Future):**
- **Roles:** Standard users (developers, contractors, consultants)
- **Access Level:** Limited access (specific workstations, no sudo by default)
- **Authentication:** SSH key + TOTP multi-factor (same as sysadmin)
- **Onboarding:** Security awareness training, Rules of Behavior acknowledgment, background check (if required)
- **Account Lifecycle:** FreeIPA account creation, role assignment, termination procedures (PS-4)

**Auditors (Read-Only):**
- **Roles:** C3PAO assessors, government auditors
- **Access Level:** Read-only access to evidence artifacts (SSP, policies, logs, configs)
- **Authentication:** Temporary accounts, MFA required
- **Duration:** Assessment period only (days to weeks), accounts disabled after completion

### User Roles and Responsibilities

**Administrator (sysadmin):**
- System configuration and maintenance
- User account management (FreeIPA)
- Security policy enforcement
- Incident response and remediation
- Compliance monitoring (OpenSCAP, Wazuh)

**Standard User (future employees):**
- CUI creation and handling per policies
- Compliance with Rules of Behavior (TCC-AUP-001)
- Security awareness (annual training)
- Incident reporting to ISSO (sysadmin)

**Auditor (temporary):**
- Evidence review (read-only)
- Assessment procedures execution
- Findings documentation
- No system modifications

### Authentication and Authorization

**Authentication (IA family):**
- **Mechanism:** SSH key (ECDSA-521) + TOTP (pam_google_authenticator)
- **MFA Deployment:** 100% (all user accounts require MFA)
- **TOTP App:** Microsoft Authenticator (smartphone-based)
- **Session Timeout:** 15 minutes inactivity (ODP-AC-2, per DoD baseline)
- **Account Lockout:** 3 unsuccessful attempts, 15-minute lockout (ODP-AC-1, per DoD baseline)

**Authorization (AC family):**
- **Primary:** FreeIPA RBAC (group-based permissions)
- **Sudo:** /etc/sudoers.d/ files (NOPASSWD for sysadmin, future: require password for standard users)
- **SELinux:** Mandatory Access Control (enforcing mode, default-deny)
- **File Permissions:** Restrictive (700/600 for sensitive files, least privilege)

**User Management (FreeIPA):**
- Centralized identity provider (dc1.example.local)
- Kerberos authentication (tickets expire, require renewal)
- LDAP directory (user/group database)
- Password policy (12 chars min, 90-day expiration, 24 history, 3 classes per ODP-IA-2 through ODP-IA-5)

## 2.4. Network Architecture Overview

**Topology:** Single-site, flat network with firewall boundary protection

**Network Diagram:** [To be included in Phase 3 — POA&M-202]

### Network Configuration

**Internet Connection:**
- **ISP:** [Provider name]
- **Bandwidth:** [Mbps down / Mbps up]
- **Type:** [Cable / Fiber / DSL / etc.]

**Firewall:** pfSense [version]
- **IP Address:** 10.0.0.1 (internal), [external IP] (WAN)
- **Ruleset:** Default-deny (block all inbound, filter outbound)
- **Logging:** All firewall events logged to Wazuh

**Internal Network:** 10.0.0.X/24
- **Subnet Mask:** 255.255.255.0 (254 usable addresses)
- **DHCP:** Static IP assignments (all systems have fixed IPs)
- **DNS:** pfSense forwards to 8.8.8.8 (Google), 1.1.1.1 (Cloudflare)
- **NTP:** pfSense synchronizes to pool.ntp.org, internal systems sync to pfSense

**DMZ:** None
- **Rationale:** No public-facing services (no web servers, mail servers, etc.)
- **Future:** If public services needed, DMZ on separate VLAN

**VPN:** OpenVPN capability
- **Status:** Configured but not yet in production use
- **Purpose:** Remote access (future planned when travel/remote work needed)
- **Authentication:** SSH key + TOTP (same MFA as SSH)

### System IP Addresses

| Hostname | IP Address | MAC Address | Role |
|----------|------------|-------------|------|
| dc1.example.local | 10.0.0.10 | [MAC] | FreeIPA DC, Wazuh Manager |
| workstation1.example.local | 10.0.0.115 | [MAC] | Primary Workstation |
| workstation2.example.local | 10.0.0.104 | [MAC] | Dev Workstation |
| workstation3.example.local | 10.0.0.113 | [MAC] | Business Workstation |
| ai.example.local | 10.0.0.7 | [MAC] | AI/ML Workstation (Ollama server) |
| pfSense firewall | 10.0.0.1 | [MAC] | Network Security Gateway |
| NAS | 192.168.1.[X] | [MAC] | Encrypted Backup Storage |

**DNS Resolution:** Internal DNS via FreeIPA (dc1), forwards to pfSense for external queries

**Routing:** All traffic routes through pfSense firewall (default gateway 10.0.0.1)

### Key Network Services

**FreeIPA (dc1):**
- **Kerberos (TCP/UDP 88, 464):** Authentication tickets
- **LDAP (TCP 389, 636 SSL):** User/group directory
- **DNS (TCP/UDP 53):** Internal name resolution
- **NTP (UDP 123):** Time synchronization source for workstations

**Wazuh (dc1):**
- **Agent Communication (TCP 1514, 1515):** Wazuh agents → manager
- **API (TCP 55000):** Management interface
- **Dashboard (HTTPS 443):** Web interface for monitoring

**SSH (all systems):**
- **TCP 22:** Encrypted remote access (SSH key + TOTP MFA)

**NAS:**
- **NFS (TCP 2049):** Network file sharing for backups
- **SMB/CIFS (TCP 445):** Alternative file sharing (if used)

**Firewall Rules Summary:**
- **Inbound (from Internet):** All blocked by default (no public-facing services)
- **Outbound (to Internet):** Allowed for specific services (HTTPS 443, DNS 53, NTP 123, SSH 22 for remote repos)
- **Internal:** All allowed within 10.0.0.X/24 (trusted network)

## 2.5. System Interconnections and External Services

### External Service Dependencies

Per TCC-SAP-001 Section 4.6 (SA-9: External System Services), CyberHygiene relies on the following external services. Complete inventory in Phase 3 deliverable (POA&M-205).

**Service 1: SSL.com — TLS Certificate Provider**
- **Purpose:** X.509 certificate issuance for HTTPS/TLS
- **Data Exchanged:** Certificate Signing Requests (CSRs), public certificates
- **CUI Exposure:** None (public certificates, no CUI)
- **Security Controls:** HTTPS communication, certificate validation
- **Risk Level:** LOW
- **Vendor Assessment:** Commercial Certificate Authority, audited per CA/Browser Forum requirements

**Service 2: Rocky Linux Repositories — OS Package Updates**
- **Purpose:** Software package distribution (RPM packages for OS and applications)
- **Data Exchanged:** Package metadata, software binaries
- **CUI Exposure:** None (public packages)
- **Security Controls:** GPG signature verification (mandatory), HTTPS mirrors
- **Risk Level:** MEDIUM (supply chain risk)
- **Mitigation:** SBOM v3.0 tracking (5,626 packages), signature verification enforced, FIPS 140-2 validation
- **Vendor Assessment:** Community-supported, RHEL-compatible, strong reputation

**Service 3: Let's Encrypt — TLS Certificate Provider**
- **Purpose:** Automated certificate issuance via ACME protocol
- **Data Exchanged:** Domain validation challenges, certificates (public)
- **CUI Exposure:** None (public certificates)
- **Security Controls:** HTTPS, automated renewal, 90-day expiration (reduces exposure window)
- **Risk Level:** LOW
- **Vendor Assessment:** Nonprofit, widely trusted, industry-standard ACME protocol

**Service 4: NTP Servers (pool.ntp.org)**
- **Purpose:** Network Time Protocol for accurate time synchronization
- **Data Exchanged:** Time synchronization packets (NTP)
- **CUI Exposure:** None (time data only)
- **Security Controls:** Multiple redundant sources, outlier detection
- **Risk Level:** LOW
- **Vendor Assessment:** Public NTP pool, multiple independent time sources

**Service 5: DNS Forwarders (Google 8.8.8.8, Cloudflare 1.1.1.1)**
- **Purpose:** Recursive DNS for domain name resolution
- **Data Exchanged:** DNS queries and responses
- **CUI Exposure:** None (domain names only, no CUI in queries)
- **Security Controls:** DNSSEC validation where available, multiple providers for redundancy
- **Risk Level:** LOW
- **Vendor Assessment:** Google and Cloudflare (reputable, published privacy policies)

**Complete External Services Inventory:** Phase 3 deliverable (POA&M-205, target 06/15/2026)

### Interconnection Security Agreements (ISAs)

**Current Status:** No formal ISAs in place (all external services are public, no peer-to-peer system interconnections)

**Future:** If interconnecting with customer systems or peer organizations, formal ISAs will be established per CA-3 (System Interconnections) and SA-9 (External System Services)

## 2.6. Applicable Laws and Regulations

### Federal Compliance Frameworks

**Primary Framework: NIST SP 800-171 Revision 3**
- **Authority:** Federal Information Security Modernization Act (FISMA)
- **Applicability:** Required for federal contractors processing, storing, or transmitting CUI
- **Implementation:** This SSP documents compliance with all 97 Rev 3 controls
- **Assessment:** NIST SP 800-171A Rev 3 (Assessment Guide), 422 determination statements
- **Status:** 80.4% fully implemented (target 95%+ by September 2026)

**DFARS 252.204-7012 — Safeguarding Covered Defense Information**
- **Authority:** Department of Defense Federal Acquisition Regulation Supplement
- **Applicability:** Required for DoD contracts with CUI (Covered Defense Information)
- **Implementation:** NIST SP 800-171 Rev 2 currently mandated (DoD Class Deviation 2024-O0013)
- **Scoring:** SPRS score 106/110 (96.4%), target 110/110 by June 2026
- **Assessment:** Self-assessment + C3PAO certification (CMMC 2.0 Level 2)

**FAR 52.204-21 — Basic Safeguarding of Covered Contractor Information Systems**
- **Authority:** Federal Acquisition Regulation
- **Applicability:** Federal contracts (non-DoD) with CUI
- **Implementation:** NIST SP 800-171 subset (15 basic controls) — CyberHygiene exceeds with full 97 Rev 3 controls
- **Status:** Fully compliant (basic controls are subset of comprehensive controls implemented)

**CMMC 2.0 Level 2 — Cybersecurity Maturity Model Certification**
- **Authority:** Department of Defense (DoD) program for assessing contractor cybersecurity**
- **Applicability:** Required for DoD contracts with CUI (phased rollout)
- **Alignment:** CMMC Level 2 maps to NIST SP 800-171 Rev 2 (110 controls)
- **Assessment:** C3PAO (Certified Third-Party Assessment Organization) certification required
- **Status:** Preliminary gap analysis complete (Feb 9, 2026), ready for C3PAO assessment when available
- **Rev 3 Transition:** CMMC assessment guide will eventually align with Rev 3 (estimated late 2026-2027)

### Cryptography Standards

**FIPS 140-2 — Security Requirements for Cryptographic Modules**
- **Authority:** National Institute of Standards and Technology (NIST)
- **Applicability:** Federal systems requiring validated cryptography
- **Implementation:** Rocky Linux 9 FIPS mode enabled, validated modules (OpenSSL, kernel crypto)
- **Status:** Fully compliant (LUKS encryption, TLS 1.3, SSH all use FIPS 140-2 validated modules)

**FIPS 199 — Standards for Security Categorization**
- **Authority:** NIST
- **Implementation:** System categorized as MODERATE (see Section 1.2)

**FIPS 200 — Minimum Security Requirements**
- **Authority:** NIST
- **Implementation:** NIST SP 800-171 Rev 3 satisfies FIPS 200 requirements for MODERATE systems

### Privacy and Data Protection

**Privacy Act of 1974**
- **Applicability:** If system stores Personally Identifiable Information (PII) of federal employees/citizens
- **Status:** Limited PII (authentication credentials only), protected per NIST SP 800-171 requirements

**CUI Program (32 CFR Part 2002)**
- **Authority:** National Archives and Records Administration (NARA)
- **Applicability:** Establishes CUI categories, marking, and handling requirements
- **Implementation:** CUI handled per Section 1.4 (CUI Handling and Classification)

### Industry Standards (Informative, Not Mandatory)

**NIST Cybersecurity Framework (CSF)**
- Used for continuous improvement and risk management alignment
- NIST SP 800-171 Rev 3 controls map to CSF categories

**CIS Controls (Center for Internet Security)**
- Login banner and baseline hardening informed by CIS benchmarks
- OpenSCAP SCAP Security Guide CUI profile aligns with CIS controls

**ISO/IEC 27001 (Information Security Management)**
- Policy structure and documentation practices informed by ISO 27001
- Not formally certified, but practices aligned

### Export Control (If Applicable)

**ITAR (International Traffic in Arms Regulations):**
- **Status:** NOT APPLICABLE (no defense articles or technical data currently handled)
- **Future:** If ITAR data introduced, additional export control procedures required

**EAR (Export Administration Regulations):**
- **Status:** NOT APPLICABLE (no dual-use technology currently handled)

### State and Local Laws

**State Privacy Laws (if applicable):**
- Compliance with state data breach notification laws (varies by state)
- GDPR/CCPA: Not applicable (no EU/California consumer data handling)

---

# Section 3: System Architecture

## 3.1. Network Topology

**Network topology diagram to be included in Phase 3 (POA&M-202, target 05/30/2026).**

Diagram will illustrate:
- **Internet Gateway and Firewall:** pfSense at 10.0.0.1 with default-deny ruleset
- **Internal Network:** 10.0.0.X/24 subnet with all 7 systems
- **Server (dc1):** FreeIPA domain controller + Wazuh SIEM manager at 10.0.0.10
- **Workstations:** workstation1 (.115), workstation2 (.104), workstation3 (.113), ai (.7)
- **Storage:** NAS backup storage (encrypted)
- **External Services:** SSL.com, Rocky repos, Let's Encrypt, NTP, DNS (outside boundary)
- **Security Boundaries:** Dotted line (authorization boundary), solid red line (trust boundary at firewall)
- **CUI Data Flows:** Red arrows showing CUI paths (workstations → NAS backups, workstations → dc1 for auth)
- **Encrypted Connections:** Green padlock icons (TLS 1.3, SSH, LUKS)
- **Legend:** Color coding and icon key

**Reference:** Network_Architecture_Diagram_v1.0.pdf (Phase 3 deliverable)

**File Location:** `/home/sysadmin/CyberSecurity/Rev3/Evidence/Network_Architecture_Diagram_v1.0.pdf`

## 3.2. System Components and Inventory

[TABLE CONTINUES IN PART 2...]

---

**END OF PART 1**

**Next:** Part 2 will cover system component details (Section 3.2-3.6) and begin core control families (Sections 6, 7, 8).
