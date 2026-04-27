# Audit and Accountability Policy

**Document ID:** DIWAI-AAP-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** CUI

---

## 1. Purpose

This policy establishes diwai.org (Do It With AI) requirements for audit and accountability on the SecureMac Production Network (SPN). It ensures all security-relevant events are recorded, protected, and reviewed to support detection of unauthorized activity, forensic investigations, and compliance with NIST SP 800-171 Rev 2 (AU-1 through AU-16) and CMMC Level 2.

---

## 2. Scope

This policy applies to:

- **All SPN Systems:**
  - Mac mini M4 Pro running macOS Tahoe — firewall, gateway, host appliance (securemac.diwai.org)
  - Rocky Linux 9.7 VM — diwai-services UTM (services.diwai.org, 10.10.1.10)
    - 389 Directory Server (LDAP/identity)
    - Postfix/Dovecot (email)
    - Apache HTTPD (web)
    - OpenVPN (remote access)
    - Wazuh agent (SIEM forwarding)
    - ClamAV (anti-malware)

- **All Personnel:** System Owner/ISSO (Donald E. Shannon) and any contractors with system access

---

## 3. Policy Statements

### 3.1 Audit Policy and Procedures (AU-1)

diwai.org shall maintain and review this audit policy annually. Procedures in Section 5 support this policy. Compliance is verified through:
- Weekly manual review of audit logs
- Quarterly Wazuh dashboard reviews
- Quarterly OpenSCAP compliance scans

### 3.2 Audit Events (AU-2, AU-12)

The following events shall be audited on all SPN systems:

**Authentication and Authorization:**
- Successful and failed login attempts (SSH, web, LDAP)
- Privilege escalation (sudo usage)
- Account creation, modification, deletion
- Password changes
- Session establishment and termination

**System and Security Events:**
- System startup and shutdown
- Service start and stop
- Software installation and removal
- Configuration file changes (monitored via Wazuh FIM)
- SELinux policy violations
- FIPS mode status changes

**Data and Resource Access:**
- CUI directory access (auditd rules on /srv/, /home/)
- File creation, deletion, and modification in CUI paths
- USB device attach/detach (macOS USB Guard daemon)

**Network Events:**
- Firewall rule hits (pf on macOS)
- VPN connection attempts
- Suricata IDS/IPS alerts

### 3.3 Audit Record Content (AU-3)

Each audit record shall contain:
- Date and time (UTC)
- Event type and outcome (success/failure)
- Subject identity (user account or process)
- Object affected (file path, resource, host)
- Source address (IP/hostname where applicable)

**Configuration:**
- auditd on Rocky Linux with CUI profile (`/etc/audit/rules.d/`)
- pf logging on macOS host
- SSH LogLevel VERBOSE on services.diwai.org
- Wazuh agent on services.diwai.org forwards to local log aggregation

### 3.4 Audit Log Storage Capacity (AU-4)

- Audit logs on services.diwai.org stored on LUKS-encrypted partition (`/var/log/audit/`)
- Storage alert threshold: 75% partition usage (Wazuh monitor)
- Critical threshold: 90% — triggers immediate review and archival
- Logs rotated and archived per retention schedule (Section 3.7)

### 3.5 Response to Audit Logging Failure (AU-5)

In the event of audit logging failure:
1. auditd configured to halt system if disk fills (RAID-based action: `space_left_action = SUSPEND`, `disk_full_action = SUSPEND`)
2. ISSO notified immediately via Wazuh alert
3. Root cause investigated and resolved within 24 hours
4. Logging restored before resuming normal operations
5. Incident documented

### 3.6 Audit Review, Analysis, and Reporting (AU-6)

**Review Schedule:**
- **Daily:** ISSO reviews Wazuh dashboard for critical/high security events
- **Weekly:** Review authentication failures and anomalous access patterns
- **Monthly:** Statistical summary — failed logins, privilege escalations, FIM alerts
- **Quarterly:** Full audit log analysis; report to System Owner

**Analysis Criteria:**
- >5 failed authentication attempts from single source within 1 hour
- Any privileged command execution outside change windows
- File changes in /etc/ not correlated with approved changes
- Any SELinux denial involving CUI-related processes

### 3.7 Audit Log Protection (AU-9)

- Audit logs on LUKS AES-256-XTS encrypted partition
- SELinux enforcing — audit logs protected by `var_log_t` context
- Only root and auditd processes may write to `/var/log/audit/`
- Log files on macOS host stored in `/var/log/` with FileVault protection
- No audit log modification or deletion except by authorized archive process

**Retention:**
- Online audit logs: 90 days
- Archived logs: 3 years minimum
- Archive location: DataStore NAS (10.10.1.100) — `/Volumes/Cyberinabox/Secure_Mac/audit-archive/`

### 3.8 Audit Record Reduction and Report Generation (AU-7)

- Wazuh SIEM provides real-time log aggregation and alerting
- Wazuh dashboards support on-demand report generation
- OpenSCAP HTML reports generated quarterly for compliance evidence
- Log search: `ausearch`, `journalctl`, and Wazuh dashboard queries

### 3.9 Time Stamps (AU-8)

- All systems synchronized to NTP
  - Rocky Linux VM: `chronyd` using pool.ntp.org
  - macOS host: macOS System Date & Time (automatic NTP)
- All audit records use system-local time with UTC offset logged
- NTP sync verified monthly: `chronyc tracking`

### 3.10 Protection of Audit Information (AU-9)

- Audit logs are read-only to all users except auditd service (SELinux enforced)
- Log rotation does not delete — rotates to compressed archive
- macOS Unified Log protected by System Integrity Protection (SIP)

### 3.11 Audit Record Retention (AU-11)

| Log Type | Online Retention | Archive Retention |
|----------|-----------------|-------------------|
| auditd (Linux) | 90 days | 3 years |
| auth.log / secure | 90 days | 3 years |
| Wazuh alerts | 90 days | 3 years |
| pf logs (macOS) | 30 days | 3 years |
| ClamAV logs | 30 days | 1 year |
| Apache access/error | 90 days | 3 years |
| Postfix/Dovecot logs | 90 days | 3 years |
| OpenVPN logs | 90 days | 3 years |

### 3.12 Audit Generation (AU-12)

- auditd on Rocky Linux VM enabled and running at all times
- CUI audit rules installed: monitoring /home/, /srv/, /etc/, /var/ossec/
- macOS pf logging enabled for WAN and LAN interfaces
- All services configured to log to syslog/journald (forwarded to Wazuh)

---

## 4. Roles and Responsibilities

### 4.1 System Owner / ISSO (Donald E. Shannon)

- Review audit logs per schedule defined in Section 3.6
- Configure and maintain auditd, Wazuh, and pf logging
- Respond to and investigate audit alerts
- Archive and protect audit records
- Review and approve this policy annually

---

## 5. Implementation Details

### 5.1 auditd Configuration (services.diwai.org)

**Key audit rules (`/etc/audit/rules.d/50-cui.rules`):**
```
-w /etc/ -p wa -k config-change
-w /home/ -p rwxa -k cui-access
-w /srv/ -p rwxa -k cui-access
-w /etc/ssh/ -p wa -k sshd-config
-w /var/log/lastlog -p wa -k login
-a always,exit -F arch=b64 -S execve -k exec
-a always,exit -F arch=b64 -S open,openat -F dir=/srv/ -k cui-file
```

**Verify auditd status:**
```bash
sudo systemctl status auditd
sudo auditctl -l
```

### 5.2 Wazuh Agent Configuration

Wazuh agent on services.diwai.org:
- Monitors `/var/log/secure`, `/var/log/audit/audit.log`, `/var/log/messages`
- FIM monitors: `/etc/`, `/home/`, `/srv/`, `/usr/local/bin/`
- Sends alerts to local Wazuh manager (if deployed) or stores locally
- Status: `sudo /var/ossec/bin/wazuh-control status`

### 5.3 macOS Audit Configuration

**macOS Unified Log (pf, USB guard, system):**
```bash
# View recent security events
log show --predicate 'subsystem == "com.apple.securityd"' --last 1h
# View USB events
log show --predicate 'subsystem == "com.apple.iokit"' --last 1h
# View pf log
sudo ifconfig pflog0   # verify pf logging interface exists
sudo tcpdump -n -e -ttt -i pflog0
```

### 5.4 Log Review Commands

```bash
# Authentication failures (Rocky Linux)
sudo aureport -au --failed --summary

# Privilege escalation review
sudo aureport -x --summary | grep sudo

# Recent CUI file access
sudo ausearch -k cui-access -ts recent

# Failed SSH attempts
sudo grep "Failed password" /var/log/secure | tail -50

# Wazuh alerts review
sudo tail -f /var/ossec/logs/alerts/alerts.log
```

---

## 6. Compliance Mapping

| NIST SP 800-171 Control | Implementation |
|-------------------------|----------------|
| **AU-1** Policy and Procedures | This document |
| **AU-2** Event Logging | Section 3.2 |
| **AU-3** Content of Audit Records | Section 3.3 |
| **AU-4** Audit Log Storage Capacity | Section 3.4 |
| **AU-5** Response to Audit Failures | Section 3.5 |
| **AU-6** Audit Review and Reporting | Section 3.6 |
| **AU-7** Audit Reduction and Report Generation | Section 3.8 |
| **AU-8** Time Stamps | Section 3.9 |
| **AU-9** Protection of Audit Information | Section 3.10 |
| **AU-11** Audit Record Retention | Section 3.11 |
| **AU-12** Audit Record Generation | Section 3.12 |

---

## 7. Policy Review and Updates

- **Review Frequency:** Annually or upon significant system changes
- **Approval Authority:** System Owner / ISSO (Donald E. Shannon)

---

## 8. Approval Signatures

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
