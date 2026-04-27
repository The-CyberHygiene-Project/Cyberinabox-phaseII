# System and Services Acquisition Policy

**Policy Number:** TCC-SAP-001
**Version:** 1.0 DRAFT
**Effective Date:** [TBD - Target: Phase 2 completion]
**Last Reviewed:** March 18, 2026
**Policy Owner:** System Owner (sysadmin)
**Approval Authority:** System Owner (sysadmin)

---

## 1. PURPOSE

This policy establishes requirements for the secure acquisition of systems, services, and software used within the CyberHygiene Production Network (CPN). This policy satisfies the System and Services Acquisition (SA) control family requirements in NIST SP 800-171 Revision 3, focusing on ensuring security is considered throughout the acquisition lifecycle.

---

## 2. SCOPE

This policy applies to:
- Acquisition of new systems, hardware, and equipment processing CUI
- Acquisition of Commercial Off-The-Shelf (COTS) software and services
- Acquisition of external services (cloud, managed services, SaaS)
- System documentation requirements
- Security workstation2 principles applied to system architecture

**In Scope:**
- Operating systems (Rocky Linux, pfSense)
- Applications and services (FreeIPA, Wazuh, Apache, etc.)
- Hardware (servers, workstations, network equipment)
- External services (SSL.com certificates, NTP, DNS, repositories)

**Out of Scope:**
- Custom software development (CyberHygiene uses 100% COTS products — no in-house development)

---

## 3. POLICY STATEMENTS

### 3.1 Allocation of Resources — NIST 3.12.1 (SA-2)

**3.1.1 Security Budget Allocation**

CyberHygiene shall allocate sufficient resources to protect CUI, including:

a) **Personnel resources:**
   - System Owner/Administrator time for security management
   - Security training and awareness (annual training per TCC-ATP-001)
   - External consultant support (as needed for assessments, remediation)

b) **Capital resources:**
   - Hardware: Servers, workstations, network equipment, UPS, backup storage
   - Software: Operating system subscriptions, security tools, certificates
   - Services: Internet connectivity, external services (SSL.com, etc.)

c) **Operational resources:**
   - Maintenance and support contracts
   - Security tool subscriptions (Wazuh, OpenSCAP content)
   - Incident response and recovery resources
   - Assessment and audit costs (C3PAO, annual assessments)

**3.1.2 Resource Planning**

Security resource requirements shall be:
- Identified during annual budget planning cycle
- Documented in SSP Section 2.5 (Resources)
- Reviewed quarterly for adequacy
- Adjusted as needed based on:
  - Risk assessment findings
  - New security requirements (contracts, regulations)
  - System changes or expansions
  - Incident response costs

**3.1.3 Resource Tracking**

Security expenditures shall be tracked and documented:
- Annual security budget vs. actual spending
- Major acquisitions (>$5,000) documented with justification
- ROI analysis for significant security investments

---

### 3.2 System Development Life Cycle (SDLC) — NIST 3.12.2 (SA-3)

**3.2.1 SDLC Applicability**

**CyberHygiene operates a 100% Commercial Off-The-Shelf (COTS) environment.** All systems, software, and services are acquired from commercial vendors (Rocky Linux, FreeIPA, Wazuh, pfSense, Apache, etc.). CyberHygiene does NOT develop custom software.

**Therefore:** Traditional SDLC phases (requirements, design, development, testing, deployment, maintenance) are **NOT APPLICABLE** to custom development.

**However:** CyberHygiene follows a **COTS Acquisition Lifecycle** with security integrated at each phase (see Section 3.3).

**3.2.2 COTS Acquisition Lifecycle (In Lieu of SDLC)**

For COTS products, CyberHygiene follows this lifecycle:

1. **Planning** — Identify need, define security requirements
2. **Vendor Evaluation** — Assess vendor security capabilities
3. **Product Selection** — Select product meeting security requirements
4. **Acquisition** — Procure product with security terms
5. **Deployment** — Install and configure per security baseline
6. **Operation & Maintenance** — Patch management, monitoring, updates
7. **Decommissioning** — Secure disposal, data sanitization

**3.2.3 Documentation Requirements**

While CyberHygiene does not maintain formal SDLC documentation, the following documents provide equivalent lifecycle oversight:

- **SSP Section 2.2:** System architecture and design
- **SSP Section 2.3:** Software inventory (SBOM v3.0)
- **Configuration Baseline Document:** Deployment and configuration standards
- **TCC-SI-001:** Patch management and maintenance procedures
- **TCC-SAP-001 (this policy):** Acquisition security requirements

**Determination Statement DS-SA-002 Justification:** N/A — No custom development; COTS-only environment with equivalent acquisition lifecycle documented.

---

### 3.3 System and Services Acquisition — NIST 3.12.3 (SA-4)

**3.3.1 Acquisition Security Requirements**

All system and service acquisitions shall include security requirements addressing:

a) **Functional security requirements:**
   - Authentication mechanisms (MFA support preferred)
   - Encryption capabilities (FIPS 140-2 validated preferred)
   - Audit logging (comprehensive event logging)
   - Access controls (RBAC, least privilege)
   - Data protection (encryption at rest and in transit)

b) **Assurance security requirements:**
   - Vendor security certifications (ISO 27001, SOC 2, FedRAMP, etc.)
   - Vulnerability management (CVE disclosure, patch cadence)
   - Security testing (vendor penetration testing, bug bounty programs)
   - Supply chain security (software signing, provenance)

c) **Operational security requirements:**
   - Security documentation (admin guides, security configuration guides)
   - Incident response support (vendor escalation, security advisories)
   - End-of-life policies (advance notice, migration path)
   - Terms of service (data ownership, breach notification, audit rights)

**3.3.2 Security Requirements Checklist**

All acquisitions shall be evaluated using the **Security Requirements Checklist** (Appendix A of this policy):

**Category 1: Authentication & Access Control**
- [ ] Supports strong authentication (password complexity, key-based)
- [ ] Supports multi-factor authentication (MFA/2FA)
- [ ] Supports role-based access control (RBAC)
- [ ] Supports session timeouts and lockouts
- [ ] Supports audit logging of authentication events

**Category 2: Encryption & Cryptography**
- [ ] Supports FIPS 140-2 validated cryptographic modules
- [ ] Encrypts data at rest (AES-256 or equivalent)
- [ ] Encrypts data in transit (TLS 1.2+)
- [ ] Uses strong key management practices

**Category 3: Audit & Logging**
- [ ] Generates comprehensive security audit logs
- [ ] Logs include timestamps, user IDs, event types, outcomes
- [ ] Supports centralized log forwarding (syslog, Wazuh agent)
- [ ] Protects log integrity (tamper-resistant logs)

**Category 4: Vulnerability Management**
- [ ] Vendor publishes security advisories
- [ ] Vendor provides timely security patches
- [ ] Vendor has responsible disclosure policy (CVE reporting)
- [ ] Product has no known critical unpatched vulnerabilities

**Category 5: Supply Chain Security**
- [ ] Software packages are digitally signed (GPG, code signing)
- [ ] Vendor provides software bill of materials (SBOM) or component list
- [ ] Vendor discloses third-party dependencies
- [ ] Source code provenance is documented (for open-source)

**Category 6: Documentation & Support**
- [ ] Security configuration guide available
- [ ] Administrator documentation includes security best practices
- [ ] Vendor provides security update notifications
- [ ] Vendor has security incident response contact

**Scoring:**
- **High Risk:** <60% requirements met — Reconsider acquisition
- **Medium Risk:** 60-79% requirements met — Mitigate gaps before deployment
- **Low Risk:** 80-100% requirements met — Acceptable for acquisition

**3.3.3 Vendor Security Assessment**

For major acquisitions (>$5,000 or critical systems), conduct vendor security assessment:

**Vendor Assessment Questionnaire:**
1. **Security Certifications:** Does vendor hold ISO 27001, SOC 2, FedRAMP, or equivalent?
2. **Security Testing:** Does vendor conduct penetration testing? How often?
3. **Vulnerability Disclosure:** Does vendor have a bug bounty program or responsible disclosure policy?
4. **Data Protection:** How does vendor protect customer data (encryption, backups, DLP)?
5. **Incident Response:** What is vendor's security incident notification process?
6. **Compliance:** Is vendor compliant with NIST 800-171, GDPR, or other frameworks?
7. **Supply Chain:** Does vendor vet their own suppliers and dependencies?
8. **Terms of Service:** Are security terms favorable (breach notification, audit rights, data ownership)?

**Vendor Risk Levels:**
- **Trusted Vendor:** Established vendor with strong security posture (e.g., Red Hat, Wazuh, pfSense)
- **Vetted Vendor:** Vendor assessed and passed security evaluation
- **Unknown Vendor:** New vendor, limited security information — proceed with caution
- **High-Risk Vendor:** Vendor with poor security track record — avoid

**3.3.4 Acquisition Documentation**

For each significant acquisition, maintain documentation:
- **Acquisition justification:** Business need, why this product/vendor
- **Security requirements:** Checklist completed
- **Vendor assessment:** Questionnaire responses (if applicable)
- **Contract or agreement:** Terms of service, SLA, security terms
- **Approval:** System Owner approval for acquisition

**Documentation Location:** `/home/sysadmin/CyberSecurity/Current/Evidence/Acquisition_Records/`

---

### 3.4 System Documentation — NIST 3.12.5 (SA-5)

**3.4.1 Documentation Requirements**

CyberHygiene shall obtain and maintain documentation for all systems and services, including:

a) **Administrator documentation:**
   - Installation and configuration guides
   - Security configuration guides (hardening guides)
   - Administrator manuals and command references
   - Troubleshooting and maintenance guides

b) **User documentation:**
   - End-user guides (if applicable)
   - Acceptable use policies (TCC-AUP-001)
   - Security awareness materials (TCC-ATP-001)

c) **Security documentation:**
   - System Security Plan (SSP v3.0)
   - Security policies (all TCC-* policies)
   - Configuration baseline documentation
   - Risk assessment and POA&M
   - Incident response plans (TCC-IRP-001)
   - Audit and assessment reports

d) **Technical documentation:**
   - System architecture diagrams
   - Network topology diagrams
   - Data flow diagrams
   - Software inventory (SBOM v3.0)
   - Hardware inventory

**3.4.2 Documentation Management**

Documentation shall be:
- **Maintained:** Kept current with system changes
- **Accessible:** Available to administrators and assessors
- **Protected:** Marked as CUI or Internal Use Only; stored securely
- **Version controlled:** Previous versions archived
- **Reviewed annually:** Verified for accuracy during SSP review

**Documentation Repository:** `/home/sysadmin/CyberSecurity/Current/`

**3.4.3 Documentation for External Services**

For external services (SSL.com, NTP servers, DNS, etc.), maintain:
- Service provider contact information
- Terms of service and SLA
- Security and privacy policies
- Incident notification procedures
- Documented in **External Services Inventory** (to be created Phase 3)

---

### 3.5 Security Engineering Principles — NIST 3.12.8 (SA-8)

**3.5.1 Security Engineering Principles Applied**

CyberHygiene applies the following security workstation2 principles in system design and operation:

**1. Defense-in-Depth (Layered Security)**

Multiple layers of security controls protect CUI:
- **Layer 1: Network boundary** — pfSense firewall with default-deny ruleset
- **Layer 2: System hardening** — OpenSCAP CUI baseline (100% compliance)
- **Layer 3: Access controls** — FreeIPA RBAC, SSH key + TOTP MFA
- **Layer 4: Encryption** — FIPS 140-2 validated crypto, LUKS disk encryption, TLS 1.2+
- **Layer 5: Monitoring** — Wazuh SIEM with real-time alerting
- **Layer 6: Audit logging** — Comprehensive auditd rules, centralized log collection
- **Layer 7: Physical security** — Locked server room, physical access controls

**Benefit:** If one layer fails or is breached, additional layers provide protection.

---

**2. Least Privilege**

Users and processes are granted the minimum access necessary:
- **User accounts:** FreeIPA RBAC assigns roles based on job function
- **Sudo access:** NOPASSWD sudo only for sysadmin (system owner/admin)
- **Service accounts:** Applications run as non-root users (e.g., apache, wazuh, freeipa)
- **SELinux:** Mandatory Access Control (MAC) enforces process confinement
- **File permissions:** 644 (rw-r--r--) for files, 755 (rwxr-xr-x) for directories, 600 for sensitive files

**Benefit:** Limits damage from compromised accounts or processes.

---

**3. Fail-Safe Defaults (Secure by Default)**

Systems default to secure state; access requires explicit authorization:
- **Firewall:** Default-deny ruleset (all traffic blocked unless explicitly allowed)
- **Authentication:** No anonymous access; all users must authenticate
- **Encryption:** Encryption enabled by default (TLS, SSH, LUKS)
- **Services:** Unnecessary services disabled by default (OpenSCAP enforces minimal services)

**Benefit:** Misconfigurations default to secure rather than insecure state.

---

**4. Separation of Duties**

Critical functions divided among multiple people or roles (where feasible):
- **Limitation:** Solopreneur environment limits separation
- **Compensating controls:**
  - Comprehensive audit logging (Wazuh SIEM) provides accountability
  - Git version control for configuration changes (allows rollback, provides audit trail)
  - External review of critical changes (consultant review, peer review when available)
  - Immutable audit logs (cannot be altered by administrator)

**Benefit:** Reduces risk of fraud, error, or malicious activity by single individual.

---

**5. Economy of Mechanism (Simplicity)**

Systems kept simple to reduce attack surface:
- **Minimal installations:** Only required packages installed (OpenSCAP enforces least functionality)
- **No unnecessary services:** Unused services disabled or removed
- **Standard configurations:** Consistent baseline across all systems (SCAP CUI profile)
- **COTS-only:** No custom development; rely on well-tested commercial products

**Benefit:** Simpler systems have fewer vulnerabilities and are easier to secure.

---

**6. Complete Mediation (Check Every Access)**

Every access to CUI or system resources is authorized:
- **Authentication:** Every login requires credentials (SSH key + TOTP)
- **Authorization:** FreeIPA checks permissions for every resource access
- **Session management:** Sessions terminate after inactivity (30 min SSH, 15 min HTTPS)
- **Encryption:** Every network transmission encrypted (SSH, TLS, IPSec if VPN)

**Benefit:** Prevents bypassing security controls.

---

**7. Open Design (No Security Through Obscurity)**

Security does not rely on secrecy of design:
- **Public standards:** NIST 800-171, FIPS 140-2, OpenSCAP (publicly documented)
- **Open-source software:** Rocky Linux, FreeIPA, Wazuh (code publicly auditable)
- **Industry best practices:** CIS benchmarks, SCAP Security Guide
- **Documented architecture:** System design documented in SSP (available to assessors)

**Benefit:** Security can be independently verified; no reliance on hidden mechanisms.

---

**8. Least Common Mechanism (Isolation)**

Minimize resource sharing between users/processes:
- **User isolation:** Each user has separate home directory, no shared directories
- **Process isolation:** SELinux enforces process confinement (processes cannot interfere with each other)
- **Network isolation:** Firewall segments networks (internal vs. external)
- **Virtual machine isolation:** If VMs used, each VM isolated from host and other VMs

**Benefit:** Limits lateral movement and privilege escalation.

---

**9. Psychological Acceptability (Usability)**

Security controls are user-friendly to encourage compliance:
- **MFA:** TOTP via smartphone app (familiar, convenient)
- **SSH keys:** Easier than passwords once configured
- **OpenSCAP automation:** Security validation automatic (weekly scans, no manual effort)
- **Wazuh dashboard:** Security status visible, easy to understand
- **Documentation:** Security procedures clearly documented

**Benefit:** Users more likely to follow security procedures if not burdensome.

---

**3.5.2 Documentation of Security Engineering Principles**

These principles are documented in:
- **This policy (TCC-SAP-001 Section 3.5)** — Describes principles and how applied
- **Security Engineering Principles Document** (to be created Phase 3) — Detailed technical implementation
- **SSP Section 2.1:** System architecture applying these principles

---

### 3.6 External System Services — NIST 3.12.9 (SA-9)

**3.6.1 External Services Identification**

CyberHygiene uses the following external services:

| Service | Provider | Purpose | CUI Exposure | Risk Level |
|---------|----------|---------|--------------|------------|
| **TLS Certificates** | SSL.com | HTTPS/TLS certificate issuance | None (metadata only) | Low |
| **Rocky Linux Repos** | Rocky Enterprise Software Foundation | Operating system updates | None | Low |
| **EPEL Repos** | Fedora Project | Additional software packages | None | Low |
| **NTP Servers** | pool.ntp.org | Time synchronization | None | Low |
| **DNS Forwarders** | [ISP or public DNS] | Domain name resolution | Metadata (domains queried) | Low |

**Note:** CyberHygiene does NOT use cloud services, managed services, or external hosting for CUI processing. All CUI remains on-premises.

**3.6.2 External Service Security Requirements**

For each external service, document:

a) **Service provider information:**
   - Provider name and contact
   - Service description
   - Terms of service and SLA

b) **Security controls:**
   - How service is secured (TLS, authentication, access controls)
   - Data protection (what data is transmitted, how protected)
   - Monitoring (how service health is monitored)

c) **Risk assessment:**
   - CUI exposure risk (what data provider can access)
   - Availability risk (impact if service unavailable)
   - Supply chain risk (provider's security posture)

d) **Risk mitigation:**
   - Compensating controls (e.g., encrypted DNS, NTP authentication)
   - Contingency plans (alternative providers, fallback)
   - Contract terms (security requirements, breach notification)

**3.6.3 External Service Agreements**

For external services involving contracts:
- Include security and privacy terms in contract
- Require breach notification within 72 hours (DFARS 252.204-7012 flow-down)
- Require audit rights (ability to assess provider security)
- Require data return/destruction upon termination

**3.6.4 External Service Review Frequency (ODP-SA-2)**

External service agreements shall be reviewed:
- **Annually** — Review during SSP annual review (April each year)
- **Upon renewal** — When service contract renews
- **Upon incident** — If provider has security incident affecting service

**Documentation:** **External Services Inventory v1.0** (to be created Phase 3)

---

## 4. ROLES AND [REDACTED_TOTP_SECRET]

### 4.1 System Owner (sysadmin)

- Approve all system and service acquisitions
- Ensure security requirements included in acquisitions
- Conduct vendor security assessments for major acquisitions
- Approve external service agreements
- Allocate budget for security resources
- Review acquisition documentation annually

### 4.2 Administrator (sysadmin)

- Complete security requirements checklist for all acquisitions
- Maintain acquisition documentation
- Deploy and configure systems per security baseline
- Maintain system documentation (SSP, SBOM, diagrams)
- Monitor external service security
- Maintain External Services Inventory

---

## 5. PROCEDURES

### 5.1 COTS Acquisition Procedure

**When to Use:** Acquiring new system, software, or service

**Steps:**

1. **Identify need and requirements** (Business justification)
   - What problem does this solve?
   - Why is this product needed?
   - Are there security requirements? (e.g., FIPS 140-2, MFA support)

2. **Complete Security Requirements Checklist** (Appendix A)
   - Evaluate product against 6 categories (Authentication, Encryption, Audit, Vuln Mgmt, Supply Chain, Documentation)
   - Score: 80%+ acceptable, 60-79% mitigate gaps, <60% reconsider

3. **Conduct Vendor Security Assessment** (if acquisition >$5,000 or critical)
   - Complete Vendor Assessment Questionnaire (Section 3.3.3)
   - Research vendor security certifications, incident history
   - Classify vendor: Trusted, Vetted, Unknown, High-Risk

4. **Document acquisition decision**
   - Business justification
   - Security checklist results
   - Vendor assessment (if applicable)
   - Risk mitigation plan (if gaps identified)

5. **Obtain System Owner approval**
   - Present acquisition documentation
   - System Owner reviews and approves or denies

6. **Procure product/service**
   - Include security terms in contract (if applicable)
   - Obtain documentation (admin guides, security guides)

7. **Deploy per security baseline**
   - Install and configure per Configuration Baseline (OpenSCAP CUI profile)
   - Scan with OpenSCAP to verify 100% compliance
   - Add to SBOM v3.0 (software inventory)
   - Update SSP if new system or significant service

8. **Maintain and monitor**
   - Follow patch management procedures (TCC-SI-001)
   - Monitor with Wazuh SIEM
   - Review security advisories from vendor

---

### 5.2 External Service Approval Procedure

**When to Use:** Adding new external service (cloud, SaaS, managed service, etc.)

**Steps:**

1. **Identify external service**
   - Service provider and description
   - What data will be transmitted to provider?
   - Does service process, store, or transmit CUI? (If YES, special review required)

2. **Assess CUI exposure risk**
   - **High Risk:** CUI transmitted to provider → requires additional security terms
   - **Medium Risk:** Metadata transmitted (e.g., DNS queries, NTP) → encryption recommended
   - **Low Risk:** No data transmitted (e.g., publicly accessible repos) → minimal controls

3. **Complete security review**
   - Review provider's security and privacy policies
   - Review terms of service
   - Identify security requirements (encryption, authentication, breach notification)

4. **Document in External Services Inventory**
   - Add service to inventory (Phase 3 deliverable)
   - Document provider, purpose, CUI exposure, controls, review date

5. **Obtain System Owner approval**
   - Present external service documentation
   - System Owner approves or denies

6. **Implement and monitor**
   - Configure service per security requirements
   - Monitor service health and security
   - Review annually (or upon renewal)

---

### 5.3 Security Engineering Principles Review

**When to Use:** Designing new system architecture or major system change

**Steps:**

1. **Review 9 security workstation2 principles** (Section 3.5.1)
2. **Evaluate proposed architecture against each principle:**
   - Defense-in-depth: Are there multiple security layers?
   - Least privilege: Are users/processes granted minimal access?
   - Fail-safe defaults: Does system default to secure state?
   - Separation of duties: Are critical functions divided? (compensating controls if not)
   - Economy of mechanism: Is design simple and minimal?
   - Complete mediation: Is every access authorized?
   - Open design: Does security rely on public standards (not obscurity)?
   - Least common mechanism: Are resources isolated between users/processes?
   - Psychological acceptability: Are security controls user-friendly?

3. **Document how each principle is applied** (or justify exceptions)
4. **Update Security Engineering Principles Document** (Phase 3 deliverable)
5. **Update SSP Section 2.1** (System Architecture)

---

## 6. COMPLIANCE

This policy supports compliance with:
- NIST SP 800-171 Rev 3 System and Services Acquisition (SA) family:
  - 3.12.1 (SA-2): Allocation of Resources
  - 3.12.2 (SA-3): System Development Life Cycle (N/A for COTS)
  - 3.12.3 (SA-4): Acquisition Process
  - 3.12.5 (SA-5): System Documentation
  - 3.12.8 (SA-8): Security Engineering Principles
  - 3.12.9 (SA-9): External System Services
- DFARS 252.204-7012 (Safeguarding CUI)
- CMMC Level 2 (System and Communications Protection domain overlaps)

---

## 7. DEFINITIONS

**Commercial Off-The-Shelf (COTS):** Software or hardware products commercially available and ready-made, as opposed to custom-developed solutions.

**External Service:** A service provided by an external entity (outside organizational control), such as cloud services, managed services, or internet-based services.

**Security Engineering Principles:** Fundamental concepts applied in system design to achieve security objectives (e.g., defense-in-depth, least privilege).

**Software Bill of Materials (SBOM):** A comprehensive inventory of software components, including version numbers and dependencies.

**System Development Life Cycle (SDLC):** The process of planning, creating, testing, and deploying an information system.

---

## 8. REFERENCES

- NIST SP 800-171 Rev 3 (SA family, controls 3.12.x)
- NIST SP 800-53 Rev 5 (SA family source controls)
- NIST SP 800-160 Vol 1 (Systems Security Engineering)
- NIST SP 800-64 Rev 2 (Security Considerations in the SDLC)
- DFARS 252.204-7012 (Safeguarding CUI)
- CyberHygiene SSP v2.9 (current), v3.0 (planned)
- CyberHygiene SBOM v2.4 (current), v3.0 (planned)

---

## 9. POLICY REVIEW

This policy shall be reviewed and updated:
- **Annually** — Target month: April (aligned with SSP review)
- **Upon significant changes** — New external services, acquisition process changes, vendor incidents

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

## APPENDIX A: SECURITY REQUIREMENTS CHECKLIST

**Instructions:** Complete this checklist for all system and service acquisitions. Score each category Yes/No. Calculate percentage of "Yes" responses.

**Acquisition:** ______________________________
**Vendor/Provider:** __________________________
**Date:** _______________
**Evaluated By:** ____________________________

---

### Category 1: Authentication & Access Control (5 questions)

| Requirement | Yes | No | N/A | Notes |
|-------------|-----|-----|-----|-------|
| 1.1 Supports strong authentication (password complexity, key-based) | [ ] | [ ] | [ ] | |
| 1.2 Supports multi-factor authentication (MFA/2FA) | [ ] | [ ] | [ ] | |
| 1.3 Supports role-based access control (RBAC) or equivalent | [ ] | [ ] | [ ] | |
| 1.4 Supports session timeouts and account lockouts | [ ] | [ ] | [ ] | |
| 1.5 Generates audit logs for authentication events | [ ] | [ ] | [ ] | |

**Category 1 Score:** ____ / 5 = _____%

---

### Category 2: Encryption & Cryptography (4 questions)

| Requirement | Yes | No | N/A | Notes |
|-------------|-----|-----|-----|-------|
| 2.1 Supports or uses FIPS 140-2 validated cryptographic modules | [ ] | [ ] | [ ] | |
| 2.2 Encrypts sensitive data at rest (AES-256 or equivalent) | [ ] | [ ] | [ ] | |
| 2.3 Encrypts data in transit (TLS 1.2+ or equivalent) | [ ] | [ ] | [ ] | |
| 2.4 Uses secure key management practices (documented) | [ ] | [ ] | [ ] | |

**Category 2 Score:** ____ / 4 = _____%

---

### Category 3: Audit & Logging (4 questions)

| Requirement | Yes | No | N/A | Notes |
|-------------|-----|-----|-----|-------|
| 3.1 Generates comprehensive security audit logs | [ ] | [ ] | [ ] | |
| 3.2 Logs include timestamps, user IDs, event types, outcomes | [ ] | [ ] | [ ] | |
| 3.3 Supports log forwarding (syslog, SIEM integration) | [ ] | [ ] | [ ] | |
| 3.4 Protects log integrity (tamper-resistant logs) | [ ] | [ ] | [ ] | |

**Category 3 Score:** ____ / 4 = _____%

---

### Category 4: Vulnerability Management (4 questions)

| Requirement | Yes | No | N/A | Notes |
|-------------|-----|-----|-----|-------|
| 4.1 Vendor publishes security advisories | [ ] | [ ] | [ ] | |
| 4.2 Vendor provides timely security patches (<30 days for critical) | [ ] | [ ] | [ ] | |
| 4.3 Vendor has responsible disclosure policy (CVE reporting) | [ ] | [ ] | [ ] | |
| 4.4 Product has no known critical unpatched vulnerabilities | [ ] | [ ] | [ ] | |

**Category 4 Score:** ____ / 4 = _____%

---

### Category 5: Supply Chain Security (4 questions)

| Requirement | Yes | No | N/A | Notes |
|-------------|-----|-----|-----|-------|
| 5.1 Software packages are digitally signed (GPG, code signing) | [ ] | [ ] | [ ] | |
| 5.2 Vendor provides SBOM or component list | [ ] | [ ] | [ ] | |
| 5.3 Vendor discloses third-party dependencies | [ ] | [ ] | [ ] | |
| 5.4 Source code provenance is documented (for open-source) | [ ] | [ ] | [ ] | |

**Category 5 Score:** ____ / 4 = _____%

---

### Category 6: Documentation & Support (4 questions)

| Requirement | Yes | No | N/A | Notes |
|-------------|-----|-----|-----|-------|
| 6.1 Security configuration guide available | [ ] | [ ] | [ ] | |
| 6.2 Administrator documentation includes security best practices | [ ] | [ ] | [ ] | |
| 6.3 Vendor provides security update notifications | [ ] | [ ] | [ ] | |
| 6.4 Vendor has security incident response contact | [ ] | [ ] | [ ] | |

**Category 6 Score:** ____ / 4 = _____%

---

### OVERALL SCORE

**Total "Yes" Responses:** ____ / 25 = _____%

**Risk Classification:**
- [ ] **Low Risk (80-100%):** Acceptable for acquisition
- [ ] **Medium Risk (60-79%):** Mitigate gaps before deployment
- [ ] **High Risk (<60%):** Reconsider acquisition or justify exceptions

**Approval:**

**Evaluated By:** _____________________________ Date: __________

**System Owner Approval:** _____________________________ Date: __________

---

**TCC-SAP-001 Policy v1.0 DRAFT**
**Created:** March 18, 2026
**Status:** DRAFT — Ready for review and customization in Phase 2
**Estimated customization effort:** 4-6 hours (review, adjust for your environment, approve)
