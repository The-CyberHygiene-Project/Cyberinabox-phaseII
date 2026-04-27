# Incident Response Policy

**Policy Number:** TCC-IRP-001
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
| 2.0 Rev 3 DRAFT | March 22, 2026 | Updated for Rev 3: Added ODP (IR testing frequency - annual), expanded incident categories and containment strategies, documented Wazuh SIEM integration workflow, enhanced CUI breach notification procedures (DFARS 252.204-7012), referenced GAP-002 tabletop exercise plan |

---

## 1. PURPOSE

This policy establishes requirements for incident response capability within the CyberHygiene Production Network (CPN). This policy satisfies the Incident Response (IR) control family requirements in NIST SP 800-171 Revision 3 (controls 3.6.1 through 3.6.3).

**Rev 3 Updates:**
- Added Organization-Defined Parameter (ODP-IR-1) for incident response testing frequency (annual tabletop exercises)
- Expanded incident categories: malware, unauthorized access, data breach, denial of service, supply chain compromise
- Enhanced containment strategies per incident type
- Documented Wazuh SIEM detection→alerting→response workflow
- Strengthened CUI breach notification procedures (US-CERT, Contracting Officer, DIBNet)
- Enhanced determination statement coverage (28 statements vs. 18 in Rev 2)

---

## 2. SCOPE

This policy applies to:

**Systems in Scope:**
- dc1.cyberinabox.net (192.168.1.10) — FreeIPA domain controller, Wazuh SIEM manager
- labrat.cyberinabox.net (192.168.1.115) — Development workstation
- engineering.cyberinabox.net (192.168.1.104) — Engineering workstation
- accounting.cyberinabox.net (192.168.1.113) — Accounting workstation

**Incident Types:**
- **Malware infection:** Virus, worm, trojan, ransomware, spyware
- **Unauthorized access:** Account compromise, privilege escalation, insider threat
- **Data breach:** CUI exfiltration, unauthorized disclosure, data loss
- **Denial of Service (DoS):** Network flooding, resource exhaustion, service disruption
- **Supply chain compromise:** Compromised software update, vendor breach affecting CPN
- **Physical security:** Theft, unauthorized physical access
- **Policy violations:** Acceptable use violations, non-compliance with security controls

---

## 3. POLICY STATEMENTS

### 3.1 Incident Response Capability — NIST 3.6.1 (IR-4, IR-5, IR-6, IR-8)

**3.1.1 Implement Incident Handling Capability**

CyberHygiene shall implement an incident handling capability for security incidents that includes preparation, detection, analysis, containment, eradication, and recovery:

**Incident Response Phases:**

**1. Preparation (Ongoing):**
- Maintain incident response procedures (this policy)
- Deploy and maintain monitoring tools:
  - Wazuh SIEM v4.9.2 (continuous monitoring)
  - Suricata IDS/IPS (network detection)
  - ClamAV + YARA (malware detection)
  - OpenSCAP (configuration compliance)
- Maintain backup and recovery capability (ReaR + encrypted storage)
- Conduct annual training and tabletop exercises (ODP-IR-1)

**2. Detection and Analysis:**
- **Automated Detection:**
  - Wazuh Manager: Real-time log analysis and correlation
  - Suricata IDS: Network-based intrusion detection
  - ClamAV/YARA: Malware detection
  - Wazuh FIM: Unauthorized file modifications
- **Manual Detection:**
  - User reports of suspicious activity
  - Security bulletin monitoring (US-CERT, vendor advisories)
- **Alert Workflow:**
  1. Security event occurs on system
  2. Wazuh agent logs event
  3. Wazuh Manager analyzes and correlates event
  4. Alert generated (Level 10+ = Critical)
  5. Email notification sent to System Owner
  6. Dashboard alert displayed (https://dc1.cyberinabox.net)
- **Analysis:**
  - Review Wazuh alert details (MITRE ATT&CK mapping)
  - Examine affected system logs (auditd, secure, messages)
  - Determine scope (single system or multiple)
  - Assess CUI impact (is CUI compromised?)
  - Classify severity (Low/Medium/High)

**3. Containment:**
- **Short-Term Containment (Target: 4 hours):**
  - **Account compromise:** Disable user account via FreeIPA
    ```bash
    ipa user-disable <username>
    ```
  - **Malware:** Isolate infected system from network
    ```bash
    sudo systemctl stop NetworkManager
    sudo ip link set <interface> down
    ```
  - **Data breach:** Revoke access to affected CUI files
  - **DoS:** Block attacking IP at firewall (pfSense)
- **Long-Term Containment:**
  - Maintain system isolation while investigating
  - Preserve evidence for forensic analysis
  - Implement compensating controls

**4. Eradication:**
- **Malware:** Remove malicious code, patch vulnerabilities
- **Unauthorized access:** Remove backdoors, reset compromised credentials
- **Data breach:** Identify and secure data exposure vectors
- **System restore:** Restore from known-good backup if necessary (ReaR)

**5. Recovery:**
- **System restoration:** Rebuild from backup or clean install
- **Service restoration:** Return systems to production
- **Monitoring:** Enhanced monitoring for recurrence (30 days post-incident)
- **Validation:** Verify all security controls operational

**6. Post-Incident Activity:**
- Lessons learned review (within 7 days)
- Update POA&M with any identified gaps
- Update SSP if system changes made
- Update incident response procedures if needed
- Archive incident documentation (3-year retention)

**Incident Classification:**
| Severity | Criteria | Response Time | Escalation |
|----------|----------|---------------|------------|
| **High** | CUI compromised, confirmed unauthorized access, widespread malware | Immediate (1 hour) | External reporting required |
| **Medium** | Potential CUI exposure, single system compromise, malware contained | 4 hours | Internal notification |
| **Low** | Failed attack attempts, policy violations, no CUI impact | 24 hours | Log and monitor |

**3.1.2 Track and Document Incidents**

CyberHygiene shall track, document, and report incidents to appropriate officials:

**Incident Documentation:**
- Incident log location: `/backup/logs/incidents/`
- Incident log format: `YYYYMMDD-IR-###.txt`
- Required information:
  - Detection timestamp
  - Incident description
  - Affected systems/users
  - CUI impact assessment
  - Actions taken (containment, eradication, recovery)
  - Evidence preserved (log locations, screenshots)
  - Lessons learned

**Wazuh Integration:**
- All incidents tracked in Wazuh Manager
- Alert ID cross-referenced in incident log
- MITRE ATT&CK tactics/techniques documented
- Timeline reconstruction via Wazuh archive

**Reporting:**
- Internal: Notify System Owner immediately for High severity
- External: See Section 3.2 for CUI breach reporting requirements
- Record retention: 3 years minimum for audit purposes

**3.1.3 Test Incident Response Capability (ODP-IR-1 - Testing Frequency)**

CyberHygiene shall test incident response capability **annually** (ODP-IR-1):

**Testing Method: Tabletop Exercises**
- Frequency: Annual (every 12 months)
- Next scheduled: June 30, 2026 (POA&M-SPRS-2)
- Format: Tabletop exercise using scenario-based discussion
- Scenarios: Malware outbreak, data breach, unauthorized access, DoS attack
- Template: GAP-002 IR Tabletop Exercise Plan (Phase 1 deliverable)

**Exercise Objectives:**
- Validate incident response procedures
- Test communication channels (email, phone)
- Verify access to tools (Wazuh, FreeIPA, backup systems)
- Identify gaps in procedures or capabilities
- Practice external notification procedures

**Documentation:**
- Exercise date and participants
- Scenario used
- Findings and gaps identified
- Corrective actions required
- POA&M updates (if gaps identified)

**Additional Testing:**
- Backup restoration tests: Quarterly
- Failover tests: Semi-annually
- Monitoring tool verification: Quarterly

### 3.2 Incident Monitoring — NIST 3.6.2 (IR-4)

**3.2.1 Monitor and Detect Security Events**

CyberHygiene shall monitor and track security incidents using automated mechanisms:

**Wazuh SIEM Monitoring:**
- **Deployment:** Wazuh Manager on dc1, agents on all 4 systems
- **Coverage:** 100% of CPN systems monitored
- **Log aggregation:** rsyslog forwards all logs to Wazuh Manager
- **Analysis:** Real-time correlation and rule matching
- **Alerting:** Immediate notification for Critical/High severity (Level 10+)

**Detection→Alerting→Response Workflow:**
```
[Security Event] → [Wazuh Agent] → [Wazuh Manager] → [Rule Analysis]
     ↓
[Alert Generated] → [Email Notification] → [Dashboard Display]
     ↓
[ISSO Review] → [Incident Response] → [Containment/Eradication]
```

**Monitored Event Categories:**
- Authentication: Failed logins, account lockouts, privilege escalation
- File Access: CUI file modifications, unauthorized access attempts
- Network: Suspicious connections, port scans, data exfiltration
- Malware: ClamAV detections, YARA rule matches
- Configuration: System changes, security control modifications
- Vulnerability: CVE detections, patch status changes

**Alert Response Times:**
| Alert Level | Severity | Review Time | Action Required |
|-------------|----------|-------------|-----------------|
| 12-15 | Critical | 1 hour | Immediate incident response |
| 10-11 | High | 4 hours | Investigation and containment |
| 7-9 | Medium | 24 hours | Review and assess |
| 3-6 | Low | Weekly | Trend analysis |

**Integration with Other Systems:**
- Suricata IDS: Network alerts forwarded to Wazuh
- OpenSCAP: Compliance violations forwarded to Wazuh
- ClamAV: Malware detections forwarded to Wazuh
- FreeIPA: Authentication events forwarded to Wazuh

### 3.3 Incident Response Assistance — NIST 3.6.3 (IR-7)

**3.3.1 Provide Incident Response Support**

CyberHygiene shall provide incident response support resources:

**Internal Resources:**
- System Owner (ISSO): Primary incident response lead
- Wazuh SIEM: Detection and analysis tool
- Backup systems: Recovery capability (ReaR + encrypted storage)
- Documentation: Incident response procedures (this policy)

**External Resources:**
- **US-CERT (CISA):** Incident reporting and assistance
  - Website: https://www.cisa.gov/uscert
  - Email: soc@us-cert.gov
  - Phone: 888-282-0870
- **DIBCSIA:** Defense Industrial Base cybersecurity support
  - Website: https://dibnet.dod.mil
  - Phone: 301-225-0136
- **FBI IC3:** Cyber crime reporting
  - Website: https://www.ic3.gov
- **Vendor Support:**
  - Rocky Linux: Community forums, security mailing list
  - Wazuh: Community support, documentation
  - pfSense: Netgate support portal

**Third-Party Incident Response:**
- No formal IR retainer in place (single-user environment)
- If needed: Engage third-party IR firm for forensics or advanced analysis
- Cost consideration: Budget approval required for third-party engagement

### 3.4 CUI Breach Notification — DFARS 252.204-7012

**3.4.1 Report CUI Incidents to DoD**

For incidents involving CUI (Controlled Unclassified Information), CyberHygiene shall report to DoD and other authorities per DFARS 252.204-7012:

**Notification Requirements:**

**1. US-CERT (Immediate - Within 1 Hour):**
- Incident description
- CUI data affected (type and estimated volume)
- Systems compromised
- Contact information
- Initial assessment

**2. Contracting Officer (Within 72 Hours):**
- Detailed incident report
- CUI impact assessment
- Containment and remediation actions
- Timeline of events
- Evidence preservation confirmation

**3. DIBNet Portal (Within 72 Hours for DoD Contracts):**
- Upload incident report via https://dibnet.dod.mil
- Submit all required forms and documentation
- Provide media preservation confirmation

**CUI Incident Triggers:**
- Unauthorized disclosure of CUI
- CUI exfiltration (data theft)
- CUI loss or destruction
- Suspected CUI compromise (even if not confirmed)

**Notification Template:**
```
TO: soc@us-cert.gov
SUBJECT: CUI Incident Report - [Organization Name]

1. Incident Date/Time: [UTC timestamp]
2. Discovery Date/Time: [UTC timestamp]
3. CUI Affected: [Description and classification]
4. Systems Affected: [Hostnames and IPs]
5. Incident Type: [Unauthorized access / Data breach / Malware]
6. Current Status: [Contained / Under investigation / Eradicated]
7. Contact: [Name, Email, Phone]
8. Initial Assessment: [Brief description]
```

**Media Preservation:**
- Forensic image of affected systems (if feasible)
- Preserved logs (audit, Wazuh, system)
- Network traffic captures (if available)
- Retention: Until DoD confirms release (minimum 90 days)

**Client Notification:**
- If client CUI affected: Notify client within 24 hours
- Provide incident details, impact assessment, remediation status
- Coordinate with client on additional reporting requirements

---

## 4. INCIDENT RESPONSE PROCEDURES

### 4.1 Malware Incident Response

**Detection:**
- ClamAV real-time scanner detects malware
- YARA custom rules trigger
- Wazuh behavioral analysis detects suspicious activity

**Containment:**
1. Isolate infected system from network
2. Quarantine malicious files to `/var/quarantine/`
3. Disable user account if account-related

**Eradication:**
1. Remove malware using ClamAV or manual removal
2. Scan all systems for indicators of compromise
3. Update YARA rules if new malware variant

**Recovery:**
1. Full system malware scan (all systems)
2. Restore from backup if system integrity compromised
3. Update malware signatures
4. Monitor for 30 days post-incident

### 4.2 Unauthorized Access Incident Response

**Detection:**
- Failed login alerts (5+ failed attempts)
- Successful login from unusual location/time
- Privilege escalation detected (sudo without authorization)

**Containment:**
1. Disable compromised account: `ipa user-disable <user>`
2. Kill active sessions: `pkill -KILL -u <username>`
3. Review audit logs for actions taken
4. Identify data accessed (auditd file watches)

**Eradication:**
1. Reset all user passwords
2. Regenerate SSH keys
3. Review and remove any backdoors
4. Patch vulnerabilities that enabled access

**Recovery:**
1. Re-enable account with new credentials (if legitimate user)
2. Re-issue MFA tokens (new TOTP secret)
3. Monitor account activity for 30 days
4. Conduct security awareness training with user

### 4.3 Data Breach Incident Response

**Detection:**
- Large file transfer detected (Wazuh)
- Unauthorized access to CUI files (FIM alert)
- User report of missing or exposed files

**Containment:**
1. Identify scope of exposure (which files, how many)
2. Revoke access to affected CUI files
3. Block exfiltration channels (if active)
4. Preserve evidence of data access

**Notification:**
1. Immediate notification to US-CERT (within 1 hour)
2. DoD Contracting Officer (within 72 hours)
3. Affected clients (within 24 hours)

**Eradication:**
1. Identify and fix vulnerability that allowed breach
2. Implement additional access controls
3. Encrypt sensitive files (if not already encrypted)

**Recovery:**
1. Restore data from backup (if modified/deleted)
2. Implement enhanced monitoring on affected files
3. Conduct post-incident review
4. Update POA&M with corrective actions

### 4.4 Denial of Service Incident Response

**Detection:**
- High CPU/memory usage alerts
- Network saturation detected
- Service unavailability (users unable to connect)

**Containment:**
1. Identify source of DoS (IP addresses, attack vector)
2. Block attacking IPs at firewall (pfSense)
3. Rate limit suspicious traffic
4. Contact ISP if large-scale attack

**Eradication:**
1. Implement permanent firewall rules if pattern identified
2. Update Suricata IDS rules
3. Add attackers to blocklist

**Recovery:**
1. Restore normal service operation
2. Monitor for continued attack attempts
3. Review resource allocation (may need scaling)

### 4.5 Supply Chain Compromise Incident Response

**Detection:**
- Compromised software update detected (hash mismatch)
- Vendor notification of breach
- Unexpected software behavior

**Containment:**
1. Stop using affected software/service
2. Isolate systems with compromised software
3. Review SBOM for affected packages

**Eradication:**
1. Remove compromised software
2. Install clean version from trusted source
3. Scan for backdoors or malware introduced via supply chain

**Recovery:**
1. Verify integrity of all software packages (rpm -Va)
2. Update SBOM with remediation
3. Implement additional vendor vetting procedures

---

## 5. ROLES AND RESPONSIBILITIES

**System Owner (sysadmin):**
- Incident Commander for all incidents
- Detection, analysis, containment, eradication, recovery
- External notifications (US-CERT, DoD, clients)
- Post-incident review and documentation
- Conduct annual tabletop exercises
- Maintain incident response capability

**Users (if additional users added):**
- Report suspicious activity immediately
- Cooperate with incident investigation
- Preserve evidence if instructed
- Do not attempt remediation without authorization

---

## 6. COMPLIANCE

**Regulatory Requirements:**
- NIST SP 800-171 Rev 3: Controls 3.6.1 through 3.6.3 (all 3 IR controls)
- DFARS 252.204-7012: Safeguarding CUI and cyber incident reporting
- FAR 52.204-21: Basic safeguarding of covered contractor information systems
- CMMC Level 2: Incident Response domain

**Assessment Evidence:**
- Incident logs: `/backup/logs/incidents/`
- Wazuh alert history: Incident detection and response timeline
- Tabletop exercise documentation: Annual testing (GAP-002)
- Training records: Security awareness training includes IR procedures
- External notifications: US-CERT, DoD reporting confirmation

---

## 7. DEFINITIONS

**CUI:** Controlled Unclassified Information requiring safeguarding per NIST SP 800-171.

**Incident:** Security event that threatens confidentiality, integrity, or availability of CUI.

**ODP:** Organization-Defined Parameter, value tailored by organization per Rev 3 guidance.

**Tabletop Exercise:** Discussion-based exercise to validate incident response procedures.

**Wazuh SIEM:** Security Information and Event Management platform for continuous monitoring.

---

## 8. ENFORCEMENT

**Non-Compliance:**
- Failure to report incidents: Immediate account suspension
- Disabling monitoring tools: System access revocation
- Policy violations: Disciplinary action per TCC-PS-001

**Reporting:**
- Security incidents: Immediate notification to System Owner
- Suspected CUI breach: Immediate escalation (external reporting required)

---

## 9. RELATED DOCUMENTS

**Policies:**
- TCC-AAP-001: Audit and Accountability Policy v2.0 Rev 3
- TCC-SI-001: System and Information Integrity Policy v2.0 Rev 3
- TCC-AUP-001: Acceptable Use Policy (to be updated to Rev 3)
- TCC-PS-001: Personnel Security Policy (to be updated to Rev 3)

**Procedures:**
- GAP-002: IR Tabletop Exercise Plan (Phase 1 deliverable)
- Backup and Recovery Procedures
- Wazuh Operations Guide

**Standards:**
- NIST SP 800-171 Rev 3: Protecting Controlled Unclassified Information
- NIST SP 800-53 Rev 5: Security and Privacy Controls (IR family)
- NIST SP 800-61: Computer Security Incident Handling Guide
- DFARS 252.204-7012: Safeguarding CUI and Cyber Incident Reporting

---

## 10. REVIEW AND UPDATES

**Review Frequency:** Annually or after significant incidents

**Next Scheduled Review:** March 2027

**Version Control:** All policy versions maintained in `/home/dshannon/CyberSecurity/Rev3/Policies/`

**Change Log:**
- v2.0 Rev 3 DRAFT (March 22, 2026): Updated for Rev 3 - ODP added (annual testing), incident categories expanded, containment strategies per type, Wazuh workflow documented, DFARS 252.204-7012 notification enhanced, GAP-002 tabletop plan referenced

---

## 11. APPROVAL

**Policy Owner:** System Owner (sysadmin)

**Approval Date:** [TBD - Target: Phase 2 completion]

**Signature:** _________________________________

**Next Review Date:** [Approval Date + 12 months]

---

*This policy satisfies NIST SP 800-171 Rev 3 controls 3.6.1 through 3.6.3 (Incident Response family). All 3 IR controls addressed.*

**Rev 3 Status:** DRAFT - Pending final review and approval
**Phase 2 Target Completion:** April 2026
**Critical Gap:** Annual tabletop exercise scheduled for June 30, 2026 (POA&M-SPRS-2)
