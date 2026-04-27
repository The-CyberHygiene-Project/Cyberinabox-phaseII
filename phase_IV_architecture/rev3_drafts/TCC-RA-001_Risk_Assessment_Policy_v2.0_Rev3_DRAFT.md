# Risk Assessment Policy

**Policy Number:** TCC-RA-001
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
| 2.0 Rev 3 DRAFT | March 22, 2026 | Updated for Rev 3: Added ODPs (risk assessment frequency - annual, vulnerability scanning - weekly/daily, remediation timeframes), integrated supply chain risk assessment requirements (NEW in Rev 3), referenced GAP-001 risk assessment template, documented Wazuh vulnerability tracking |

---

## 1. PURPOSE

This policy establishes requirements for risk assessment within the CyberHygiene Production Network (CPN). This policy satisfies the Risk Assessment (RA) control family requirements in NIST SP 800-171 Revision 3 (controls 3.11.1 through 3.11.3).

**Rev 3 Updates:**
- Added Organization-Defined Parameters (ODPs) for risk assessment frequency (annual), vulnerability scanning frequency (weekly/daily), remediation timeframes
- **NEW:** Supply chain risk assessment integration (required in Rev 3)
- Referenced GAP-001 Risk Assessment Template (Phase 1 deliverable)
- Enhanced vulnerability management procedures (Wazuh + OpenSCAP)
- Updated for current implementation status (100% OpenSCAP, daily CVE detection)

---

## 2. SCOPE

This policy applies to:

**Systems in Scope:**
- dc1.cyberinabox.net (192.168.1.10) — FreeIPA domain controller, Wazuh SIEM manager
- labrat.cyberinabox.net (192.168.1.115) — Development workstation
- engineering.cyberinabox.net (192.168.1.104) — Engineering workstation
- accounting.cyberinabox.net (192.168.1.113) — Accounting workstation

**Risk Types:**
- **Cybersecurity risks:** Malware, unauthorized access, data breach, denial of service
- **Supply chain risks:** Compromised software, vendor breaches, malicious updates (NEW in Rev 3)
- **Operational risks:** Hardware failure, service disruption, resource exhaustion
- **Insider threats:** Accidental or intentional misuse, privilege abuse
- **Physical security risks:** Theft, unauthorized physical access, environmental hazards

---

## 3. POLICY STATEMENTS

### 3.1 Risk Assessment — NIST 3.11.1 (RA-3)

**3.1.1 Conduct Risk Assessment (ODP-RA-1 - Assessment Frequency)**

CyberHygiene shall conduct risk assessments **annually** or when significant changes occur (ODP-RA-1):

**Assessment Frequency:**
- **Annual (Primary):** Complete risk assessment every 12 months
- **Next Scheduled:** April 30, 2026 (POA&M-035, -3 SPRS points)
- **Ad-Hoc Triggers:**
  - Significant system changes (new systems, major upgrades)
  - New types of CUI handled
  - Security incidents impacting CUI
  - New threat intelligence affecting CPN
  - Vendor/supply chain changes

**Assessment Methodology:**
- **Standard:** NIST SP 800-30 Rev 1 (Guide for Conducting Risk Assessments)
- **Template:** GAP-001 Risk Assessment Template (Phase 1 deliverable)
- **Approach:**
  1. System characterization (identify assets, data, threats)
  2. Threat identification (malware, insiders, supply chain, natural disasters)
  3. Vulnerability identification (Wazuh, OpenSCAP, manual review)
  4. Control analysis (evaluate effectiveness of existing controls)
  5. Likelihood determination (Low/Medium/High probability)
  6. Impact analysis (Low/Medium/High consequence)
  7. Risk determination (Likelihood × Impact matrix)
  8. Control recommendations (mitigate, accept, transfer, avoid)
  9. Residual risk documentation

**Risk Scoring Matrix:**
|  | **Low Impact** | **Medium Impact** | **High Impact** |
|---|----------------|-------------------|-----------------|
| **High Likelihood** | Medium | High | Critical |
| **Medium Likelihood** | Low | Medium | High |
| **Low Likelihood** | Low | Low | Medium |

**Assessment Outputs:**
- Risk register: `/home/dshannon/CyberSecurity/Rev3/Assessments/Risk_Register_FY2026.xlsx`
- Risk assessment report: GAP-001 template completed
- POA&M updates: High/Critical risks added as remediation items
- SSP updates: Risk assessment results documented in Section 9

**Critical Gap:** First formal risk assessment target 04/30/2026 (POA&M-035)

**3.1.2 Supply Chain Risk Assessment (NEW in Rev 3)**

CyberHygiene shall include supply chain risks in risk assessments:

**Supply Chain Scope:**
- **Software vendors:** Rocky Linux, Wazuh, SSL.com, pfSense/Netgate
- **Hardware vendors:** HP (servers), Dell (workstations)
- **Service providers:** ISP, SSL certificate authority
- **Third-party software:** SBOM v2.4 tracks 5,626 packages

**Supply Chain Risk Categories:**
- **Compromised updates:** Malicious software updates from vendor
- **Vendor breach:** Vendor compromise affecting customer data/software
- **Counterfeit components:** Fake hardware/software
- **Vendor bankruptcy/discontinuation:** Loss of support/updates
- **Geopolitical risks:** Foreign vendor access restrictions

**Supply Chain Risk Mitigation:**
- Software signature verification (GPG for all packages)
- SBOM maintenance (track all software provenance)
- Vendor monitoring (security bulletins, breach notifications)
- Multi-source strategy (avoid single vendor lock-in where possible)
- Update testing (test on labrat before production deployment)

**Supply Chain Risk Assessment Integration:**
- Included in GAP-001 Risk Assessment Template (Section 5: Supply Chain Risks)
- Annual review of vendor security postures
- SBOM analysis for vulnerable/deprecated packages

### 3.2 Vulnerability Monitoring and Scanning — NIST 3.11.2 (RA-5)

**3.2.1 Monitor and Scan for Vulnerabilities (ODP-RA-2 - Scanning Frequency)**

CyberHygiene shall monitor and scan for vulnerabilities with the following frequencies (ODP-RA-2):

**Vulnerability Scanning Schedule:**
- **Operating System:** Weekly (OpenSCAP) + Daily (Wazuh CVE detection)
  - **Exceeds DoD baseline** (DoD: Monthly for OS)
- **Applications:** Weekly (OpenSCAP) + Daily (Wazuh package inventory)
  - **Exceeds DoD baseline** (DoD: Quarterly for applications)

**OpenSCAP Scanning:**
- Frequency: Weekly (every Sunday at 03:00)
- Profile: SCAP Security Guide CUI profile
- Current status: 100% compliance (104/104 rules passing as of 2026-02-21)
- Scan command:
  ```bash
  oscap xccdf eval --profile cui --results /home/dshannon/openscap-results/$(date +%Y%m%d)-oscap.xml \
    /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml
  ```
- Results: `/home/dshannon/openscap-results/`
- Dashboard: `/var/www/internal-dashboards/openscap-dashboard.html`

**Wazuh Vulnerability Detection:**
- Frequency: Continuous (real-time CVE detection)
- CVE feed updates: Every 60 minutes
- Package inventory: Checked against NVD, Red Hat Security Data, OVAL
- Detection method: Installed packages cross-referenced with vulnerability database
- Alert generation: Immediate for CVSS 7.0+ (High/Critical)
- Dashboard: https://dc1.cyberinabox.net (Wazuh Vulnerability Detection module)

**Manual Vulnerability Review:**
- Security bulletins: Weekly review
  - US-CERT/CISA alerts
  - Rocky Linux security errata
  - Vendor advisories (pfSense, hardware)
- Threat intelligence: Continuous monitoring (RSS feeds, mailing lists)

**Vulnerability Tracking:**
- Wazuh dashboard: Real-time CVE status per system
- POA&M: Critical/High vulnerabilities tracked if remediation > 30 days
- Risk register: Vulnerabilities with no patch available

### 3.3 Vulnerability Remediation — NIST 3.11.3 (RA-5)

**3.3.1 Remediate Vulnerabilities (ODP-RA-3 - Remediation Timeframes)**

CyberHygiene shall remediate vulnerabilities within the following organization-defined timeframes based on CVSS score (ODP-RA-3):

**Remediation Timeframes:**
- **Critical (CVSS 9.0-10.0):** 7 calendar days maximum
- **High (CVSS 7.0-8.9):** 30 calendar days maximum
- **Moderate (CVSS 4.0-6.9):** 90 calendar days maximum
- **Low (CVSS 0.1-3.9):** 180 calendar days or next maintenance window

**Automated Remediation:**
- dnf-automatic enabled on all systems
- Security patches applied automatically (after testing)
- Configuration: `/etc/dnf/automatic.conf`
  ```ini
  [commands]
  apply_updates = yes
  upgrade_type = security
  ```

**Manual Remediation Process:**
1. **Detection:** Wazuh or OpenSCAP identifies vulnerability
2. **Assessment:** Review CVSS score, exploitability, affected systems
3. **Testing:** Test patch on labrat workstation first
4. **Deployment:** Apply patch to remaining systems:
   - Workstations: engineering, accounting
   - Critical systems: dc1 (during maintenance window)
5. **Verification:**
   - FIPS integrity check: `fips-mode-setup --check`
   - Vulnerability rescan (Wazuh + OpenSCAP)
   - Service functionality verification
6. **Documentation:** Update POA&M if remediation delayed

**Compensating Controls:**
- If patch unavailable or incompatible:
  - Network isolation (disable affected service, add firewall rules)
  - Configuration changes (disable vulnerable feature)
  - Enhanced monitoring (Wazuh alerts on affected component)
- Risk acceptance: Documented and approved by System Owner
- POA&M tracking: Monthly review until patched

**Evidence:**
- Wazuh Vulnerability Dashboard: Real-time remediation status
- dnf logs: `/var/log/dnf.log` (patch application history)
- OpenSCAP reports: Weekly compliance verification
- POA&M: Outstanding vulnerabilities beyond timeframe

---

## 4. ROLES AND RESPONSIBILITIES

**System Owner (sysadmin):**
- Conduct annual risk assessments (GAP-001 template)
- Review Wazuh vulnerability alerts daily (CVSS 7.0+)
- Apply security patches within ODP-RA-3 timeframes
- Maintain risk register and POA&M
- Monitor supply chain risks (vendor notifications, SBOM analysis)
- Conduct annual policy review

**Users (if additional users added):**
- Report security concerns or anomalies
- Cooperate with risk assessment activities
- Follow secure configuration practices

---

## 5. COMPLIANCE

**Regulatory Requirements:**
- NIST SP 800-171 Rev 3: Controls 3.11.1 through 3.11.3 (all 3 RA controls)
- CMMC Level 2: Risk Assessment domain
- DFARS 252.204-7012: Risk management for CUI

**Assessment Evidence:**
- Risk assessment report: GAP-001 completed annually
- Risk register: `/home/dshannon/CyberSecurity/Rev3/Assessments/Risk_Register_FY2026.xlsx`
- Vulnerability scans: OpenSCAP weekly reports + Wazuh continuous detection
- Remediation tracking: Wazuh dashboard + POA&M + dnf logs
- SBOM: Software Bill of Materials v2.4 (5,626 packages for supply chain visibility)

---

## 6. DEFINITIONS

**CVSS:** Common Vulnerability Scoring System (0.0-10.0 severity scale).

**ODP:** Organization-Defined Parameter, value tailored by organization per Rev 3 guidance.

**Risk:** Measure of the extent to which an entity is threatened by a potential circumstance or event.

**Supply Chain Risk:** Risk arising from dependencies on external suppliers of goods or services.

**Vulnerability:** Weakness in a system that can be exploited by a threat source.

---

## 7. ENFORCEMENT

**Non-Compliance:**
- Failure to remediate critical vulnerabilities: Immediate escalation, system isolation if necessary
- Risk assessment not conducted annually: SPRS -3 points (POA&M-035 current gap)
- Policy violations: Disciplinary action per TCC-PS-001

**Reporting:**
- Critical vulnerabilities (CVSS 9.0+): Immediate notification to System Owner
- Risk assessment delays: POA&M tracking and monthly review

---

## 8. RELATED DOCUMENTS

**Policies:**
- TCC-SI-001: System and Information Integrity Policy v2.0 Rev 3
- TCC-IRP-001: Incident Response Policy v2.0 Rev 3
- TCC-SRMP-001: Supply Chain Risk Management Policy v1.0 Rev 3 DRAFT

**Templates:**
- GAP-001: Risk Assessment Template (Phase 1 deliverable)
- SBOM v2.4: Software Bill of Materials (5,626 packages)

**Standards:**
- NIST SP 800-171 Rev 3: Protecting Controlled Unclassified Information
- NIST SP 800-53 Rev 5: Security and Privacy Controls (RA family)
- NIST SP 800-30 Rev 1: Guide for Conducting Risk Assessments
- NIST SP 800-161: Cybersecurity Supply Chain Risk Management

---

## 9. REVIEW AND UPDATES

**Review Frequency:** Annually or when significant changes occur

**Next Scheduled Review:** March 2027

**Version Control:** All policy versions maintained in `/home/dshannon/CyberSecurity/Rev3/Policies/`

**Change Log:**
- v2.0 Rev 3 DRAFT (March 22, 2026): Updated for Rev 3 - ODPs added (annual assessment, weekly/daily scanning, remediation timeframes), supply chain risk assessment integrated (NEW), GAP-001 template referenced, SBOM v2.4 documented for supply chain visibility

---

## 10. APPROVAL

**Policy Owner:** System Owner (sysadmin)

**Approval Date:** [TBD - Target: Phase 2 completion]

**Signature:** _________________________________

**Next Review Date:** [Approval Date + 12 months]

---

*This policy satisfies NIST SP 800-171 Rev 3 controls 3.11.1 through 3.11.3 (Risk Assessment family). All 3 RA controls addressed.*

**Rev 3 Status:** DRAFT - Pending final review and approval
**Phase 2 Target Completion:** April 2026
**Critical Gap:** First formal risk assessment scheduled for April 30, 2026 (POA&M-035, -3 SPRS points)
