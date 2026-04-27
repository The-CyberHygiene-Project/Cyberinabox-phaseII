# Incident Response Policy and Procedures

**Document ID:** DIWAI-IRP-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** CUI

---

## 1. Purpose

This policy establishes diwai.org (Do It With AI) requirements for identifying, responding to, and recovering from security incidents affecting the SecureMac Production Network (SPN). It ensures CUI and Federal Contract Information (FCI) are protected during and after incidents, in compliance with NIST SP 800-171 Rev 2 (IR-1 through IR-8), DFARS 252.204-7012, and CMMC Level 2.

---

## 2. Scope

This policy applies to:

- **All SPN Systems:**
  - Mac mini M4 Pro (securemac.diwai.org) — macOS Tahoe host
  - Rocky Linux 9.7 VM (services.diwai.org, 10.10.1.10)
  - Network infrastructure (pf firewall, 10.10.1.0/24 LAN)

- **All Security Incidents:** Any actual or suspected unauthorized access, data breach, malware infection, service disruption, or CUI compromise

- **All Personnel:** Donald E. Shannon and any contractors with SPN access

---

## 3. Policy Statements

### 3.1 Incident Response Policy and Procedures (IR-1)

diwai.org shall maintain documented incident response procedures and review them annually. Tabletop exercise required annually to validate effectiveness.

**Tabletop Exercise:**
- Status: NOT MET — POA&M-003, target 2026-06-30
- Schedule: Annual tabletop exercise covering realistic incident scenarios

### 3.2 Incident Response Training (IR-2)

- ISSO (Donald E. Shannon) completes incident response training before assuming IR responsibilities
- Training covers: incident classification, containment procedures, DFARS reporting, evidence preservation
- Training updated annually or after significant incidents
- Resources: NIST SP 800-61 Rev 2, CISA incident response guides

### 3.3 Incident Response Testing (IR-3)

- Annual tabletop exercise (POA&M-003, target 2026-06-30)
- Exercise scenarios include: ransomware, CUI exfiltration, unauthorized access, hardware failure
- Results documented and used to improve procedures

### 3.4 Incident Handling (IR-4)

Incident response follows the NIST SP 800-61 Rev 2 lifecycle:

1. **Preparation** → 2. **Detection and Analysis** → 3. **Containment, Eradication, and Recovery** → 4. **Post-Incident Activity**

Detailed procedures in Section 5.

### 3.5 Incident Monitoring (IR-5)

- Wazuh agent on services.diwai.org provides continuous security event monitoring
- pf logs on macOS host captured and reviewed weekly
- OpenVPN connection logs reviewed for anomalies
- Incident tracking maintained in `~/Documents/SecureMac Project Docs/Incidents/`

### 3.6 Incident Reporting (IR-6)

**Internal Reporting:**
- ISSO (Donald E. Shannon) is primary incident responder and reporter
- All incidents documented within 24 hours of detection

**External Reporting — DFARS 252.204-7012:**
- **Mandatory reporting within 72 hours** of discovery of any cyber incident involving covered defense information (CDI) or operationally critical systems
- Report to: DoD Cyber Crime Center (DC3) at `https://dibnet.dod.mil`
- Provide malware samples to DC3 as requested
- Notify cognizant contracting officer within 72 hours
- Preserve images of compromised systems for 90 days post-reporting

**CISA Reporting:**
- Report significant incidents to CISA: `us-cert.cisa.gov/report`

### 3.7 Incident Response Assistance (IR-7)

External resources available if needed:
- CISA 24/7 helpline: 1-888-282-0870
- DCSA Counterintelligence: if insider threat suspected
- Local law enforcement: if criminal activity suspected

### 3.8 Incident Response Plan (IR-8)

This policy and the procedures in Section 5 constitute the Incident Response Plan. Plan reviewed and updated:
- Annually
- After each significant incident
- After tabletop exercise (incorporating lessons learned)

---

## 4. Incident Classification

### 4.1 Severity Levels

**Category 1 — Critical:**
- Confirmed CUI or FCI exfiltration
- Active ransomware encrypting SPN data
- Unauthorized privileged access to SPN systems
- **Response:** Immediate isolation; DFARS 72-hour reporting timer starts

**Category 2 — High:**
- Suspected unauthorized access (failed attempts with indicators of compromise)
- Malware detection on SPN systems
- Unplanned service outage affecting CUI availability
- **Response:** Same-day response; assess for Category 1 escalation

**Category 3 — Medium:**
- Policy violations (AUP breach, unauthorized software)
- Anomalous behavior requiring investigation
- Failed backup or monitoring tool outage
- **Response:** Within 48 hours

**Category 4 — Low:**
- Security awareness concerns (phishing email received but not clicked)
- Minor configuration drift detected
- **Response:** Within 1 week; log and monitor

---

## 5. Incident Response Procedures

### 5.1 Phase 1: Detection and Analysis

**Detection Sources:**
- Wazuh agent alerts (authentication failures, FIM changes, malware)
- auditd alerts (unusual privilege escalation, CUI access)
- ClamAV detection logs (`/var/log/clamav/`)
- pf log anomalies
- User-reported suspicious activity

**Initial Analysis Steps:**
```bash
# Check recent authentication failures (Rocky Linux VM)
sudo aureport -au --failed --summary -ts recent

# Check for new/modified files in critical paths
sudo ausearch -k config-change -ts recent
sudo ausearch -k cui-access -ts recent

# Check currently logged-in sessions
who
w
last | head -20

# Check for unexpected processes
ps aux | sort -k3 -rn | head -20
sudo lsof -i  # Open network connections

# Check Wazuh alerts
sudo tail -100 /var/ossec/logs/alerts/alerts.log

# macOS: Check for unexpected network connections
netstat -an | grep ESTABLISHED
```

**Document during analysis:**
- Date/time of detection
- Source of detection alert
- Systems and data potentially affected
- Initial severity classification

### 5.2 Phase 2: Containment

**Short-Term Containment (immediate — preserve evidence first):**

```bash
# PRESERVE EVIDENCE BEFORE CONTAINING if time allows
# Copy audit logs to secure location
sudo cp -r /var/log/audit/ /tmp/incident-$(date +%Y%m%d)/
sudo cp /var/ossec/logs/alerts/alerts.log /tmp/incident-$(date +%Y%m%d)/

# Network isolation — block suspicious IP at Rocky Linux firewall
sudo firewall-cmd --add-rich-rule='rule family=ipv4 source address="<IP>" reject'

# Network isolation — block at pf on macOS host (if needed)
# Edit /etc/pf.conf to add block rule, then:
sudo pfctl -f /etc/pf.conf

# Disable compromised user account
ldapmodify -x -D "cn=Directory Manager" -W -H ldap://services.diwai.org << EOF
dn: uid=username,ou=People,dc=diwai,dc=org
changetype: modify
replace: nsAccountLock
nsAccountLock: true
EOF

# Revoke SSH access
sudo sed -i '/username_key/d' /home/username/.ssh/authorized_keys
```

**For Active Ransomware or Active Breach:**
1. Immediately power off affected VM (UTM → Stop VM)
2. Preserve VM bundle as forensic image before any recovery
3. Isolate macOS host from network (physically disconnect en6 LAN cable)
4. Do not power back on until investigation is complete

### 5.3 Phase 3: Eradication and Recovery

**Eradication:**
```bash
# Remove malware (after ClamAV detection)
sudo clamscan -r --remove=yes /var/quarantine/

# Remove unauthorized user accounts
ldapdelete -x -D "cn=Directory Manager" -W \
  "uid=unauthorized_user,ou=People,dc=diwai,dc=org"

# Verify system integrity
sudo rpm -Va | grep -E '^..5'  # Check modified RPM files
sudo auditctl -l              # Verify audit rules intact
fips-mode-setup --check       # Verify FIPS mode
getenforce                    # Verify SELinux enforcing

# Patch vulnerabilities that were exploited
sudo dnf update --security -y
```

**Recovery:**
```bash
# Restore from clean backup if system was compromised
# Option 1: Restore VM from DataStore backup
# Mount DataStore and copy clean .utm bundle
# Open in UTM

# Option 2: Restore specific files from backup
sudo rsync -av /mnt/backup/home/ /home/
sudo rsync -av /mnt/backup/srv/ /srv/

# Post-restoration verification
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cui \
  --report /root/post-incident-oscap-$(date +%Y%m%d).html \
  /usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml
```

### 5.4 Phase 4: Post-Incident Activity

**Within 72 hours:**
- Complete incident report (see Appendix A template)
- DFARS reporting to DC3 if CDI was involved
- Notify contracting officer if applicable

**Within 2 weeks:**
- Lessons learned review
- Update incident response procedures if needed
- Update risk register and POA&M
- Additional training if human error was a factor
- Brief System Owner on findings

---

## 6. Evidence Preservation

**Evidence Collection Requirements:**
- Do not modify or delete any logs before collection
- Chain of custody documentation for each evidence item
- Store evidence in: `~/Documents/SecureMac Project Docs/Incidents/<incident-id>/`
- DataStore archive copy: `/Volumes/Cyberinabox/Secure_Mac/Incidents/`

**Evidence Items:**
- Full audit log export (auditd)
- Wazuh alert logs
- pf logs
- System snapshots (UTM VM bundle if applicable)
- Network pcap captures (if available)
- Screenshot documentation of indicators

**Retention:** 3 years post-incident (per DFARS 252.204-7012 for CDI incidents)

---

## 7. Roles and Responsibilities

| Role | IR Responsibilities |
|------|---------------------|
| **ISSO (Don Shannon)** | Detect, classify, contain, eradicate, recover; maintain incident log; execute DFARS reporting; preserve evidence; conduct lessons learned |
| **System Owner (Don Shannon)** | Authorize major response actions (system isolation, service shutdown); approve DFARS reports before submission; accept residual risk decisions |

---

## Appendix A: Incident Report Template

```
INCIDENT REPORT — diwai.org

Incident ID: INC-YYYY-NNN
Date Detected: YYYY-MM-DD HH:MM MDT
Date Reported: YYYY-MM-DD HH:MM MDT
Reported By: Donald E. Shannon, ISSO

INCIDENT SUMMARY:
[Brief description of what occurred]

DETECTION METHOD:
□ Wazuh alert  □ auditd alert  □ ClamAV detection  □ User report  □ Other

AFFECTED SYSTEMS:
□ securemac.diwai.org (macOS host)
□ services.diwai.org (Rocky Linux VM)
□ Both systems
□ Network only

SEVERITY: □ Critical (Cat 1)  □ High (Cat 2)  □ Medium (Cat 3)  □ Low (Cat 4)

CUI/CDI INVOLVED: □ Yes  □ No  □ Unknown
If Yes — DFARS 72-hour reporting required

TIMELINE:
- [Date/Time]: [Event]

CONTAINMENT ACTIONS TAKEN:
[Description]

ERADICATION ACTIONS TAKEN:
[Description]

RECOVERY ACTIONS TAKEN:
[Description]

ROOT CAUSE:
[Analysis of how the incident occurred]

IMPACT ASSESSMENT:
[Systems affected, data affected, duration of impact]

LESSONS LEARNED:
[What improvements will be made]

DFARS REPORTING:
□ Not required  □ Required — Submitted to DC3 on: YYYY-MM-DD
DC3 Case Number: _______________________

INCIDENT CLOSED: YYYY-MM-DD
APPROVED BY: /s/ Donald E. Shannon, System Owner
```

---

## 8. Compliance Mapping

| NIST SP 800-171 Control | Implementation |
|-------------------------|----------------|
| **IR-1** Policy and Procedures | This document |
| **IR-2** Incident Response Training | Section 3.2 |
| **IR-3** Incident Response Testing | Section 3.3 — NOT MET (POA&M-003) |
| **IR-4** Incident Handling | Section 3.4, Section 5 |
| **IR-5** Incident Monitoring | Section 3.5 |
| **IR-6** Incident Reporting | Section 3.6 |
| **IR-7** Incident Response Assistance | Section 3.7 |
| **IR-8** Incident Response Plan | This document |

**SPRS Impact:**
- IR-3 (Incident Response Testing): -1 point (NOT MET)
- POA&M-003: Tabletop exercise target 2026-06-30

---

## 9. Policy Review and Updates

- **Review Frequency:** Annually or after significant incidents
- **Approval Authority:** System Owner / ISSO (Donald E. Shannon)

---

## 10. Approval Signatures

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
