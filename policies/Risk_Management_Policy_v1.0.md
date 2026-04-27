# Risk Management Policy and Procedures

**Document ID:** DIWAI-RA-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually or upon significant changes
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** Controlled Unclassified Information (CUI)

---

## 1. Risk Management Policy

### Purpose

This policy establishes a structured framework for identifying, assessing, prioritizing, responding to, and monitoring risks to diwai.org's SecureMac Production Network (SPN) and associated operations. It ensures the protection of Controlled Unclassified Information (CUI) and Federal Contract Information (FCI) by integrating risk management into daily activities, aligning with NIST SP 800-171 Revision 2 (RA-1 through RA-9) and supporting CMMC Level 2 requirements.

### Scope

This policy applies to all SPN assets and personnel involved in handling CUI/FCI, including:

**Systems:**
- **Mac mini M4 Pro (securemac.diwai.org):**
  - macOS Tahoe host — pf firewall, USB Guard, FileVault
  - UTM hypervisor hosting diwai-services VM

- **Rocky Linux 9.7 VM (services.diwai.org, 10.10.1.10):**
  - 389 Directory Server (identity/authentication)
  - Postfix / Dovecot (email)
  - Apache HTTPD (web services)
  - OpenVPN (remote access)
  - Wazuh agent (SIEM forwarding)
  - ClamAV (anti-malware — FIPS-constrained, see Risk Acceptance)

- **Network Infrastructure:**
  - pf firewall (macOS Tahoe built-in)
  - LAN: 10.10.1.0/24
  - DataStore NAS (10.10.1.100 — LAN-only access)

**Personnel:**
- Donald E. Shannon (ISSO/System Owner)
- Contractors accessing SPN via OpenVPN or LDAP (when applicable)

**Risk Types:**
- Cybersecurity threats (malware, unauthorized access, data exfiltration)
- Operational disruptions (hardware failure, power outage, VM corruption)
- Insider threats (accidental or intentional)
- Supply chain vulnerabilities (third-party software, vendors)
- Physical security risks (theft, damage)
- Natural disasters (fire, flood)
- FIPS compatibility risks (ClamAV FIPS incompatibility — documented)

### Definitions

- **Risk:** Potential for loss of confidentiality, integrity, or availability of CUI/FCI due to threats exploiting vulnerabilities
- **Risk Assessment:** Systematic process to identify, analyze, and evaluate risks (NIST SP 800-30)
- **Risk Response:** Actions to avoid, mitigate, transfer, or accept risks
- **Residual Risk:** Risk remaining after risk response actions are implemented
- **Threat:** Potential cause of an unwanted incident
- **Vulnerability:** Weakness that can be exploited by a threat
- **Impact:** Magnitude of harm resulting from threat exploitation
- **Likelihood:** Probability that a threat will exploit a vulnerability

### Policy Statements

#### 1. Risk Management Policy and Procedures (RA-1)

diwai.org shall maintain and review this policy annually. Compliance verified through:
- Quarterly SSP and POA&M reviews
- Wazuh agent alerts for real-time risk indicators
- OpenSCAP compliance scanning results
- Incident response lessons learned

#### 2. Security Categorization (RA-2)

All SPN systems and information categorized based on potential impact (FIPS 199):

**System Categorization:**
- **Overall SPN:** Moderate impact (CUI/FCI handling)
- **Mac mini host:** Moderate impact (gateway; controls all network access; hosts VM)
- **Rocky Linux VM:** Moderate impact (critical services — authentication, email, CUI storage)
- **DataStore NAS:** Moderate impact (backup storage for CUI documents and VM bundles)

**Information Categorization:**
- **CUI/FCI:** Moderate confidentiality impact
- **System configuration:** Moderate integrity impact
- **Service availability:** Moderate availability impact

**Recategorization Triggers:**
- New DoD contracts with different data classifications
- Significant architecture changes
- Addition of new services or capabilities
- Annual review cycle

#### 3. Risk Assessment (RA-3)

Conduct comprehensive risk assessments at the following intervals:

**Frequency:**
- **Annual:** Complete risk assessment of all systems
  - Status: NOT MET — POA&M-002, target 2026-04-30 (**SPRS impact: -3 points**)
- **Ad-hoc:** Triggered by system changes, new threats, vendor changes
- **Post-Incident:** Within 72 hours of security incidents

**Assessment Methods:**
- Wazuh agent vulnerability detection (continuous)
- OpenSCAP compliance scans (quarterly, CUI profile)
- Threat modeling for common attack vectors (phishing, supply chain, ransomware)
- NIST SP 800-30 Rev 1 risk assessment methodology

**Assessment Outputs:**
- Risk register: `~/Documents/SecureMac Project Docs/Risk_Register.xlsx`
- Risk scoring: Likelihood (L/M/H) × Impact (L/M/H) = Score (1-9)
- Documented mitigation strategies with target dates
- Residual risk acceptance decisions

#### 4. Risk Assessment Updates (RA-3)

Update risk assessments within 72 hours of:
- Security incidents (per DIWAI-IRP-001)
- Wazuh vulnerability alerts with CVSS scores >7.0
- OpenSCAP compliance failures
- New threat intelligence (CISA advisories)
- System configuration changes

#### 5. Vulnerability Monitoring and Scanning (RA-5)

**Automated Scanning:**
- **Wazuh Agent (services.diwai.org):** Continuous monitoring
  - Vulnerability detection enabled (syscollector module)
  - Security Configuration Assessment (SCA) per CIS Rocky Linux 9 Benchmark
  - File Integrity Monitoring (FIM): 12-hour intervals

- **OpenSCAP:** Quarterly full compliance evaluations
  - Profile: `xccdf_org.ssgproject.content_profile_cui`
  - HTML reports for evidence
  - Results stored in `~/Documents/SecureMac Project Docs/Evidence/OpenSCAP/`

**Remediation Timelines:**
- **Critical (CVSS 9.0-10.0):** 7 days
- **High (CVSS 7.0-8.9):** 30 days
- **Medium (CVSS 4.0-6.9):** 90 days
- **Low (CVSS 0.1-3.9):** Next maintenance window

**Evidence Retention:** 3 years minimum

#### 6. Supply Chain Risk Assessment (RA-6)

**Key Software Vendors:**
- **Rocky Linux:** Community-supported RHEL rebuild; NIST-vetted packages
- **389 Directory Server:** Red Hat-maintained; from Rocky Linux repos
- **ClamAV:** Open source; bytecode disabled due to FIPS incompatibility (documented risk acceptance)
- **Wazuh:** Community edition; agent only; no external data exfiltration
- **Let's Encrypt / certbot:** ISRG CA; Cloudflare DNS API for ACME challenge

**Vendor Assessment:**
- Annual review of critical vendor security posture
- Monitor vendor security bulletins
- Update SBOM when software versions change

#### 7. Criticality Analysis (RA-7)

**Criticality Levels:**

**High Criticality:**
- Rocky Linux VM (services.diwai.org)
  - All authentication, email, web, VPN services
  - CUI document storage
  - Loss impact: All services offline; CUI inaccessible
  - RTO: 4 hours (VM restore from backup)

- Mac mini M4 Pro (hardware host)
  - All VM functions depend on host
  - pf firewall — all network routing
  - Loss impact: Complete SPN outage
  - RTO: 24 hours (restore to replacement hardware if needed)

**Medium Criticality:**
- DataStore NAS (10.10.1.100)
  - VM bundle backups; documentation archive
  - Loss impact: No active service impact; backup capability lost
  - RTO: 72 hours

**Low Criticality:**
- Shannon_Home NAS (secondary backup)
  - Redundant VM backup only (Wi-Fi, not LAN)
  - Loss impact: Secondary backup unavailable
  - RTO: Replaced when available

#### 8. All-Hazards Risk Assessment (RA-8)

**Physical Security Risks:**
- Unauthorized physical access to home office
- Theft or damage to Mac mini (LUKS/FileVault protects data)
- Loss of power — UPS recommended

**Personnel Risks:**
- Solo operator risk — no redundancy (single-person operation)
- Key person dependency (Donald E. Shannon is sole ISSO/admin)
- Mitigations: Documentation, DataStore NAS backup, recovery procedures

**Operational Risks:**
- macOS Tahoe compatibility bugs (e.g., SuperDuper! clone issue)
- UTM VM disk corruption
- Let's Encrypt certificate expiry (monitored; auto-renew active)
- ClamAV FIPS incompatibility (documented risk acceptance)

**Natural Disasters:**
- Fire, flood — DataStore NAS on LAN (local only; Shannon_Home provides off-site backup potential)

#### 9. Ongoing Risk Monitoring (RA-9)

**Continuous Monitoring:**
- Wazuh agent: FIM every 12 hours, vulnerability detection continuous
- pf logs on macOS host: reviewed weekly
- USB Guard daemon: active monitoring of USB connections
- certbot: auto-renewal timer (certbot-renew.timer) active

**Periodic Reviews:**
- **Monthly:** ISSO reviews risk register and Wazuh alerts
- **Quarterly:** SSP and POA&M review
- **Annually:** Comprehensive formal risk assessment (POA&M-002)
- **Post-Incident:** Risk reassessment within 72 hours

**Record Retention:**
- Risk registers: 3 years
- Assessment reports: 3 years
- Incident-related risk documents: 3 years post-incident

### Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| **ISSO (Don Shannon)** | Lead risk assessments; maintain risk register; integrate Wazuh/OpenSCAP tools; report/accept risks; coordinate DoD reporting per DFARS 252.204-7012 |
| **System Owner (Don Shannon)** | Approve risk responses for Medium/High residual risks; authorize risk acceptance decisions |

**Note:** As a VSB sole operator, ISSO and System Owner roles are concurrent.

### Compliance and Enforcement

- FAR 52.204-21 (Basic Safeguarding of Covered Contractor Information Systems)
- DFARS 252.204-7012 (Safeguarding Covered Defense Information and Cyber Incident Reporting)
- CMMC Level 2 requirements
- NIST SP 800-171 Rev 2, RA Family

---

## 2. Risk Management Procedures

### Risk Register Format

**Location:** `~/Documents/SecureMac Project Docs/Risk_Register.xlsx`

**Required Fields:**
- Risk ID: RISK-YYYY-NNN
- Risk Description
- Threat Source: Internal / External / Environmental / Supply Chain
- Likelihood: Low (1) / Medium (2) / High (3)
- Impact: Low (1) / Medium (2) / High (3)
- Risk Score: Likelihood × Impact (1-9)
- Current Controls
- Residual Risk
- Response Strategy: Avoid / Mitigate / Transfer / Accept
- Planned Actions
- Target Date
- Status: Open / In Progress / Closed / Accepted

### Annual Risk Assessment Procedure

**Trigger:** Annual cycle; first formal assessment target 2026-04-30 (POA&M-002)

**Steps:**

1. Run OpenSCAP baseline scan (Rocky Linux VM):
   ```bash
   sudo oscap xccdf eval \
     --profile xccdf_org.ssgproject.content_profile_cui \
     --results /root/oscap-assessment-$(date +%Y%m%d).xml \
     --report /root/oscap-assessment-$(date +%Y%m%d).html \
     /usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml
   ```

2. Review Wazuh vulnerability alerts:
   ```bash
   sudo grep -i "vulnerability\|CVE" \
     /var/ossec/logs/alerts/alerts.log | tail -100
   ```

3. Review audit anomalies:
   ```bash
   sudo aureport -au --summary --failed
   sudo aureport -x --summary
   ```

4. Update risk register with findings
5. Determine risk response for each identified risk
6. Update POA&M with new items and target dates
7. File assessment report in `~/Documents/SecureMac Project Docs/Evidence/Risk_Assessments/`

### Vulnerability Scanning Procedure

```bash
# Quarterly OpenSCAP scan
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cui \
  --results ~/Documents/SecureMac\ Project\ Docs/Evidence/OpenSCAP/oscap-$(date +%Y%m%d).xml \
  --report ~/Documents/SecureMac\ Project\ Docs/Evidence/OpenSCAP/oscap-$(date +%Y%m%d).html \
  /usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml

# Review failures and create POA&M items
# Copy report to DataStore for archival
```

---

## Appendix A: Current Risk Register Summary (Initial — April 2026)

| Risk ID | Description | Score | Status | Controls |
|---------|-------------|-------|--------|----------|
| RISK-2026-001 | MFA not implemented (3.5.3) | 6 | Open (POA&M-001) | SSH key-only, pf ACL |
| RISK-2026-002 | Formal risk assessment not completed | 4 | Open (POA&M-002) | Informal continuous monitoring |
| RISK-2026-003 | No IR tabletop exercise completed | 3 | Open (POA&M-003) | Written procedures documented |
| RISK-2026-004 | ClamAV FIPS incompatibility | 3 | Accepted | Suricata, Wazuh FIM, SELinux |
| RISK-2026-005 | Single operator — key person dependency | 4 | Accepted | Documentation, backup procedures |
| RISK-2026-006 | SuperDuper! clone deferred (Tahoe bug) | 3 | Open (POA&M) | VM bundle backup (2 copies) |

---

## Approval

**Prepared By:**
Donald E. Shannon, ISSO

**Approved By:**
/s/ Donald E. Shannon
System Owner, diwai.org

**Date:** April 10, 2026

**Next Review Date:** April 10, 2027
