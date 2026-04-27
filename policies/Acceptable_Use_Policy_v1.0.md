# Acceptable Use Policy

**Document ID:** DIWAI-AUP-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** CUI

---

## 1. Purpose

This policy establishes diwai.org (Do It With AI) acceptable use requirements for the SecureMac Production Network (SPN). It defines authorized and prohibited uses of SPN resources to protect Controlled Unclassified Information (CUI) in compliance with NIST SP 800-171 Rev 2 and CMMC Level 2.

---

## 2. Scope

This policy applies to:

- **All SPN Systems and Resources:**
  - Mac mini M4 Pro (securemac.diwai.org) — gateway appliance running macOS Tahoe
  - Rocky Linux 9.7 VM (services.diwai.org, 10.10.1.10) — identity, mail, web, VPN services
  - Network infrastructure (pf firewall, LAN 10.10.1.0/24)
  - Remote access (OpenVPN)
  - Email services (Postfix/Dovecot, diwai.org domain)

- **All Personnel:** Donald E. Shannon (System Owner/ISSO) and any contractors or authorized users granted access to SPN resources

---

## 3. Authorized Use

### 3.1 Permitted Activities

SPN resources are authorized for:

1. **Business Operations:**
   - Processing and storing CUI related to DoD contracts and government work
   - Email communications for authorized business purposes
   - Remote access to SPN via OpenVPN from authorized locations

2. **System Administration:**
   - System configuration, maintenance, and monitoring
   - Security scanning (OpenSCAP, Wazuh)
   - Software updates and patch management

3. **Development and Testing:**
   - AI/ML workloads on the macOS host (Ollama, local inference)
   - Security research and tooling development
   - diwai.org product development (CyberInABox reference system)

### 3.2 Conditions of Use

All authorized users must:

- Access SPN resources only for authorized business purposes
- Protect CUI using approved methods (LUKS encryption, TLS, HTTPS)
- Report suspected security incidents immediately
- Complete security awareness training before accessing CUI
- Comply with all policies in the diwai.org security policy suite

---

## 4. Prohibited Activities

### 4.1 Security Violations

Users shall NOT:

1. Disable or circumvent security controls (SELinux, FIPS mode, USB Guard, auditd)
2. Share credentials, SSH keys, or LDAP passwords
3. Install unauthorized software on production systems
4. Open unnecessary network ports or disable firewall rules
5. Attempt to access systems or data beyond authorized privileges
6. Use CPN resources to conduct unauthorized scanning or attacks against external systems

### 4.2 Data Handling Violations

Users shall NOT:

1. Store CUI on unencrypted media (USB drives without LUKS/VeraCrypt)
2. Transmit CUI over unencrypted channels (HTTP, Telnet, FTP, plain SMTP)
3. Copy CUI to personal devices or unauthorized cloud storage
4. Share CUI with unauthorized individuals
5. Remove CUI from SPN without approved transfer procedures

### 4.3 Software and Content

Users shall NOT:

1. Install peer-to-peer file sharing software
2. Install unauthorized remote access tools
3. Use SPN resources for personal business activities
4. Access inappropriate or illegal content
5. Download software from untrusted repositories

### 4.4 Remote Access

Remote access via OpenVPN is subject to:

1. MFA required for VPN authentication (target 2026-07-01 — POA&M-001)
2. No split tunneling — all traffic routes through VPN
3. VPN session terminates after 15 minutes of inactivity
4. VPN credentials not shared
5. Personal devices used for VPN access must meet minimum security baseline

---

## 5. Email Usage

### 5.1 Authorized Email Use

- Business communications using diwai.org email addresses
- SMTPS/IMAPS only (TLS required — no plain text connections)
- Encrypted attachments for CUI transmission

### 5.2 Prohibited Email Use

- Sending CUI via unencrypted email
- Clicking suspicious links or attachments without verification
- Auto-forwarding email to personal accounts
- Using diwai.org email for personal communications

---

## 6. Physical Security

Users must:

- Lock workstations when unattended (15-minute screen lock enforced)
- Not leave CUI documents visible in public areas
- Report lost or stolen devices immediately
- Ensure server room / home office access is secured when not occupied
- Not bring unauthorized devices into the server area

---

## 7. Monitoring Acknowledgment

**All users are notified that:**

- SPN systems are monitored continuously for security purposes
- All activity on SPN systems is subject to audit logging
- Audit logs may be reviewed by the ISSO and System Owner
- There is no expectation of privacy on SPN systems for any purpose
- Monitoring data may be used in disciplinary or legal proceedings

This policy constitutes notice that monitoring is in effect.

---

## 8. Reporting Violations

Users must immediately report:
- Suspected unauthorized access or data breaches
- Lost or stolen devices with CUI access
- Malware infections or suspicious system behavior
- Violations of this policy by themselves or others

**Reporting Contact:** Donald E. Shannon (ISSO)
- Method: Direct contact (in-person or secure email)

---

## 9. Consequences of Violations

Violations of this policy may result in:

1. Immediate suspension of system access
2. Formal security incident investigation
3. Termination of employment or contract
4. Civil or criminal prosecution where applicable
5. Notification to contracting officers for CUI-related violations

---

## 10. Policy Review and Updates

- **Review Frequency:** Annually or upon significant changes
- **Approval Authority:** System Owner / ISSO (Donald E. Shannon)

---

## 11. Acknowledgment

All users with access to SPN resources must sign an acknowledgment that they have read, understand, and agree to comply with this Acceptable Use Policy before being granted access.

---

## 12. Approval Signatures

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
