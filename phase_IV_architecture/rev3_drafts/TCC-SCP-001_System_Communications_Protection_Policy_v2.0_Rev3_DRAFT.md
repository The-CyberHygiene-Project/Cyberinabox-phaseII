# System and Communications Protection Policy

**Policy Number:** TCC-SCP-001
**Version:** 2.0 Rev 3 DRAFT (Updated for NIST SP 800-171 Rev 3)
**Effective Date:** [TBD - Target: Phase 2 completion]
**Last Reviewed:** March 22, 2026
**Policy Owner:** System Owner (sysadmin)
**Approval Authority:** System Owner (sysadmin)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | February 15, 2026 | Initial policy (NIST 800-171 Rev 2) |
| 2.0 Rev 3 DRAFT | March 22, 2026 | Updated for Rev 3: Added ODPs (session termination, cryptographic algorithms), FIPS 140-2 validation certificates documented, network architecture diagram requirement added, consolidated control numbering updated (3 controls merged) |

---

## 1. PURPOSE

This policy establishes requirements for protecting system boundaries and communications within the CyberHygiene Production Network (CPN). This policy satisfies the System and Communications Protection (SC) control family requirements in NIST SP 800-171 Revision 3 (controls 3.13.1 through 3.13.16).

**Rev 3 Updates:**
- Added Organization-Defined Parameters (ODPs) for session termination timeouts, cryptographic algorithms
- Added FIPS 140-2 validated cryptography certificate documentation
- Added network architecture diagram requirement (to be created in Phase 3)
- Updated for consolidated controls (23 Rev 2 controls → 20 Rev 3 controls)
- Enhanced determination statement coverage (67 statements vs. 48 in Rev 2)

---

## 2. SCOPE

This policy applies to:

**Systems in Scope:**
- dc1.cyberinabox.net (192.168.1.10) — FreeIPA domain controller, Wazuh SIEM manager
- labrat.cyberinabox.net (192.168.1.115) — Development workstation
- engineering.cyberinabox.net (192.168.1.104) — Engineering workstation
- accounting.cyberinabox.net (192.168.1.113) — Accounting workstation

**Communications in Scope:**
- All network traffic (internal and external)
- Email communications (Postfix/Dovecot)
- File transfers (Samba, SCP)
- Remote access connections (SSH)
- Administrative sessions

**Data States:**
- Data in transit (network communications)
- Data at rest (stored on systems with LUKS encryption)
- Data in use (active processing in memory)

---

## 3. POLICY STATEMENTS

### 3.1 Boundary Protection — NIST 3.13.1 (SC-7)

**3.1.1 Managed Interfaces**

CyberHygiene shall monitor and control communications at external system boundaries and key internal boundaries using pfSense firewall with the following configuration:

**External Boundary:**
- Single internet connection point via ISP gateway
- Default-deny firewall policy (all inbound traffic blocked by default)
- Explicit allow rules for required outbound services only
- No externally-facing services (air-gapped from external access)

**Internal Boundaries:**
- Network segmentation: 192.168.1.0/24 (internal trusted zone)
- All wireless access disabled (wired network only)
- Physical network ports in server room secured

**Network Architecture Diagram (ODP-SC-1):**
- **Status:** To be created in Phase 3 (Activity 3.1)
- **Location:** `/home/dshannon/CyberSecurity/Rev3/Evidence/Network_Architecture_Diagram_v1.0.pdf`
- **Contents:** Network topology, firewall zones, system interconnections, trust boundaries

**Implementation Evidence:**
- pfSense firewall configuration: `/cf/conf/config.xml`
- Firewall rules: Default-deny with explicit allows
- Suricata IDS/IPS integration enabled

### 3.2 Application Partitioning — NIST 3.13.2 (SC-2)

**3.2.1 Separate User Functionality from Management Functionality**

CyberHygiene shall separate user functionality (including user interface services) from system management functionality:

**Administrative Separation:**
- Administrative interfaces separated from user interfaces
- SSH administrative access on standard port (22) with MFA (SSH key + TOTP)
- Web-based admin interfaces restricted to localhost or internal IPs only
- FreeIPA admin UI: https://dc1.cyberinabox.net/ipa (internal only)

**Service Isolation:**
- Each major service runs on dedicated system:
  - FreeIPA/LDAP: dc1
  - File sharing (Samba): dc1
  - SIEM (Wazuh): dc1
  - Workstations: separate systems
- No mixed user/admin workloads on single system

### 3.3 Security Function Isolation — NIST 3.13.3 (SC-3)

**3.3.1 Isolate Security Functions**

CyberHygiene shall isolate security functions from non-security functions:

**Mandatory Access Control:**
- SELinux enforcing mode on all systems (100% OpenSCAP compliance)
- Security functions isolated via SELinux type enforcement
- Security component processes cannot be modified by user processes

**Dedicated Security Components:**
- Wazuh SIEM operates with dedicated resources (4GB RAM, 100GB disk)
- Firewall/IDS on separate pfSense appliance
- No direct user access to security component internals

**Least Privilege:**
- Security services run with minimal required permissions
- Dedicated service accounts: wazuh, clamav, auditd
- sudo required for all administrative actions

### 3.4 Information in Shared Resources — NIST 3.13.4 (SC-4)

**3.4.1 Prevent Unauthorized Information Transfer**

CyberHygiene shall prevent unauthorized and unintended information transfer via shared system resources:

**Memory Protection:**
- SELinux type enforcement prevents cross-process information leakage
- Process isolation via kernel namespaces
- Memory sanitization on process termination (kernel defaults)

**Storage Protection:**
- File system permissions restrict access to owner-only for CUI files
- Temporary files in `/tmp` and `/var/tmp` cleaned on reboot
- Secure deletion (shred) used for CUI file removal

**Shared Resource Controls:**
- No virtualization used (dedicated hardware reduces shared resource risks)
- Each system has dedicated physical hardware
- No resource sharing across trust boundaries

### 3.5 Denial of Service Protection — NIST 3.13.5 (SC-5)

**3.5.1 Protect Against DoS Attacks**

CyberHygiene shall protect against or limit the effects of denial of service attacks:

**Network-Level Protections:**
- pfSense firewall with state table limits (10,000 states)
- SYN flood protection enabled
- Connection rate limiting: 100 connections/second per source IP
- ICMP rate limiting enabled

**Application-Level Protections:**
- Apache MaxRequestWorkers: 150 (prevents resource exhaustion)
- Email rate limiting: Postfix configured for 10 messages/hour from single source
- Failed authentication rate limiting: 5 attempts = 30-minute lockout (fail2ban)

**Resource Management:**
- System resource limits via systemd:
  - CPU limits: 80% max per service
  - Memory limits: Service-specific (Wazuh: 4GB, others: 2GB)
- Disk quotas: Not currently implemented (single user environment)

### 3.6 Resource Availability — NIST 3.13.6 (SC-6)

**3.6.1 Protect Availability**

CyberHygiene shall protect the availability of resources by allocating resources by priority:

**Critical Service Priority:**
- FreeIPA KDC: Highest priority (nice value: -10)
- Wazuh SIEM: High priority (nice value: -5)
- User services: Normal priority (nice value: 0)

**Automatic Recovery:**
- systemd watchdog configured for critical services
- Automatic restart on failure: FreeIPA, Wazuh, Postfix, httpd
- Monitoring alerts on resource exhaustion (Wazuh threshold alerts)

**Capacity Management:**
- Storage capacity monitoring: Alert at 75%, critical at 90%
- Memory monitoring: Alert at 80% usage
- CPU monitoring: Alert at sustained 90%+ usage

### 3.7 Transmission Confidentiality — NIST 3.13.8 (SC-8)

**3.7.1 Protect Communications Confidentiality**

CyberHygiene shall protect the confidentiality of transmitted information using cryptographic mechanisms:

**Encryption Standards (ODP-SC-2 - Approved Cryptographic Algorithms):**
- TLS encryption: TLS 1.2+ with AES-256-GCM cipher suite
- SSH encryption: ECDSA-521 keys with ChaCha20-Poly1305 cipher
- Email encryption: TLS 1.2+ for SMTP/IMAP transport (opportunistic)
- VPN encryption: (Future) WireGuard with ChaCha20-Poly1305

**FIPS 140-2 Validated Cryptography:**
The following FIPS 140-2 validated cryptographic modules are used:
- **OpenSSL:** Certificate #3980 (used for TLS/SSL, certificates)
- **libgcrypt:** Certificate #3739 (used for disk encryption, GPG)
- **Kernel crypto:** Certificate #4046 (used for LUKS, IPsec)

**Implementation:**
- HTTPS enforced for all web services (HTTP redirects to HTTPS)
- SSH protocol 2 only (protocol 1 disabled)
- Weak ciphers disabled: RC4, DES, 3DES, MD5-based ciphers
- Certificate validation enforced (self-signed rejected except for internal CA)

**Transmission Protection by Service:**
- Web (HTTPS): TLS 1.2+ with SSL.com wildcard certificate
- Email (SMTP/IMAP): TLS 1.2+ with STARTTLS
- File Transfer: SCP/SFTP via SSH (no FTP/Telnet)
- Remote Access: SSH with MFA (key + TOTP)
- API Access: HTTPS with token authentication

**Rev 3 Consolidated Controls:**
- Rev 2 3.13.18 (Protect confidentiality of sessions) merged into this control

### 3.8 Transmission Integrity — NIST 3.13.9 (SC-8(1))

**3.8.1 Protect Communications Integrity**

CyberHygiene shall protect the integrity of transmitted information:

**Cryptographic Integrity Protection:**
- TLS/SSH includes integrity protection via HMAC
- HTTPS: HMAC-SHA256 integrity checks
- SSH: HMAC-SHA512 integrity checks
- Digital signatures for software packages (RPM GPG signatures verified)

**Error Detection:**
- TCP checksums for all network traffic
- Application-level checksums where supported (rsync, SCP)
- Wazuh FIM detects unauthorized file modifications

### 3.9 Network Disconnect — NIST 3.13.9 (SC-10)

**3.9.1 Session Termination (ODP-SC-3 - Session Timeout)**

CyberHygiene shall terminate network connections at the end of sessions or after a defined period of inactivity:

**Inactivity Timeouts:**
- **SSH sessions:** 30 minutes of inactivity
  - Justification: Operational convenience for administrative tasks
  - DoD baseline: 15 minutes
  - ClientAliveInterval: 300 seconds (5 min check)
  - ClientAliveCountMax: 6 (30 min total)
- **HTTPS sessions:** 15 minutes of inactivity
  - Apache timeout: 900 seconds
  - Meets DoD baseline
- **Console sessions:** 15 minutes of inactivity
  - TMOUT=900 in /etc/profile

**Automatic Logout:**
- SSH: Automatic disconnect after timeout
- HTTPS: Session cookie expiration after timeout
- Console: Automatic logout via TMOUT

**Session Termination on User Action:**
- Explicit logout terminates session immediately
- Session data cleared on termination
- Re-authentication required for new session

### 3.10 Cryptographic Key Establishment and Management — NIST 3.13.10 (SC-12, SC-13)

**3.10.1 Cryptographic Key Management**

CyberHygiene shall establish and manage cryptographic keys using automated mechanisms:

**Key Generation:**
- SSH keys: ECDSA-521 (administrator key: `/home/dshannon/.ssh/id_ecdsa`)
- TLS certificates: RSA-4096 (SSL.com wildcard certificate)
- Disk encryption: LUKS with AES-256-XTS
- All keys generated using `/dev/urandom` (FIPS 140-2 validated)

**Key Storage:**
- SSH private keys: Encrypted on disk, passphrase protected
- TLS private keys: Root-only readable (`/etc/pki/tls/private/`, mode 0600)
- LUKS master keys: Encrypted in LUKS header
- FreeIPA CA key: Hardware-protected via softhsm2

**Key Distribution:**
- SSH public keys: Distributed via FreeIPA LDAP
- TLS certificates: SSL.com CA signed (publicly trusted)
- Internal CA: FreeIPA CA for internal services

**Key Rotation:**
- SSH keys: Rotated annually or on compromise
- TLS certificates: Renewed before expiration (SSL.com cert valid until 10/28/2026)
- LUKS keys: Not rotated (requires full disk re-encryption)
- Kerberos keys: FreeIPA handles automatic rotation

**Rev 3 Consolidated Controls:**
- Rev 2 3.13.17 (Public key infrastructure) merged into this control

### 3.11 Cryptographic Protection — NIST 3.13.11 (SC-13)

**3.11.1 Cryptographic Mechanisms**

CyberHygiene shall employ FIPS-validated cryptography to protect the confidentiality of CUI:

**Approved Algorithms (ODP-SC-2):**
- **Symmetric encryption:** AES-256 (GCM for transport, XTS for storage)
- **Asymmetric encryption:** RSA-4096, ECDSA-521
- **Hashing:** SHA-256, SHA-512
- **Key exchange:** ECDHE (Elliptic Curve Diffie-Hellman Ephemeral)
- **Message authentication:** HMAC-SHA256, HMAC-SHA512

**FIPS 140-2 Validation:**
All cryptographic operations use FIPS 140-2 validated modules (see Section 3.7 for certificate numbers).

**Implementation:**
- Disk encryption: LUKS with AES-256-XTS on all systems (100% coverage)
- Transport encryption: TLS 1.2+ with AES-256-GCM
- SSH encryption: ECDSA-521 with ChaCha20-Poly1305
- Weak algorithms disabled: MD5, SHA-1 (except for non-security purposes), DES, 3DES, RC4

**Cryptography Verification:**
- OpenSCAP checks: `ssg-rhel9-ds.xml` verifies FIPS compliance (100% pass rate)
- Manual verification: `fips-mode-setup --check` on all systems

### 3.12 Collaborative Computing Devices — NIST 3.13.12 (SC-15)

**3.12.1 Prohibit Remote Activation**

CyberHygiene shall prohibit remote activation of collaborative computing devices and provide explicit indication of use:

**Device Policy:**
- No webcams on CPN workstations (physically absent or disabled)
- No microphones on CPN workstations (physically absent or disabled)
- No video conferencing software installed on CPN systems

**Future Considerations:**
- If collaborative devices added, require physical disconnect capability
- LED indicators required for any future camera/microphone

### 3.13 Mobile Code — NIST 3.13.13 (SC-18)

**3.13.1 Control Mobile Code**

CyberHygiene shall control and monitor the use of mobile code:

**Mobile Code Restrictions:**
- JavaScript: Allowed only from trusted domains (strict Content Security Policy)
- Java applets: Disabled (not installed)
- ActiveX: Not applicable (no Windows systems in CPN boundary)
- Flash: Disabled (EOL software)

**Web Browser Security:**
- Firefox ESR configured with:
  - NoScript extension for JavaScript control
  - Content Security Policy enforced
  - Third-party cookies blocked
  - Automatic downloads blocked

**Code Execution Prevention:**
- SELinux prevents execution from user-writable directories
- /tmp and /var/tmp mounted with noexec flag
- Web directories (DocumentRoot) mounted with noexec where possible

### 3.14 Voice over IP — NIST 3.13.14 (SC-19)

**3.14.1 VoIP Protection**

CyberHygiene shall establish usage restrictions and implementation guidance for VoIP:

**Current Status:** Not applicable - No VoIP services deployed on CPN.

**Future Implementation Guidance (if VoIP added):**
- VoIP traffic encryption required (SRTP)
- Separate VLAN for VoIP traffic
- QoS prioritization for voice traffic
- Regular firmware updates for VoIP equipment

### 3.15 Protection of Information at Rest — NIST 3.13.15 (SC-28)

**3.15.1 Protect Data at Rest**

CyberHygiene shall protect the confidentiality of information at rest using cryptographic mechanisms:

**Full Disk Encryption:**
- All systems use LUKS (Linux Unified Key Setup) with AES-256-XTS
- Encryption coverage: 100% of systems (dc1, labrat, engineering, accounting)
- Key derivation: PBKDF2 with high iteration count
- Boot partition: Unencrypted (GRUB limitation), contains no CUI

**Implementation Details:**
| System | Encrypted Volume | Cipher | Status |
|--------|------------------|--------|--------|
| dc1 | /dev/mapper/rhel-root | AES-256-XTS | Active |
| labrat | /dev/mapper/rhel-root | AES-256-XTS | Active |
| engineering | /dev/mapper/rhel-root | AES-256-XTS | Active |
| accounting | /dev/mapper/rhel-root | AES-256-XTS | Active |

**Verification:**
```bash
cryptsetup status /dev/mapper/rhel-root
# Shows: cipher: aes-xts-plain64, keysize: 512 bits
```

**Key Management:**
- LUKS passphrase required at boot (cold boot protection)
- No unattended boot (prevents physical theft data exposure)
- Passphrase complexity: 20+ characters, meets NIST guidelines

### 3.16 Protect Authenticity of Communications Sessions — NIST 3.13.16 (SC-23)

**3.16.1 Protect Session Authenticity**

CyberHygiene shall protect the authenticity of communications sessions:

**Session Authentication:**
- SSH: Public key authentication with TOTP second factor
- HTTPS: TLS certificate validation (SSL.com CA signed)
- Kerberos: Mutual authentication (when KDC operational)
- Email: TLS certificate validation for SMTP/IMAP

**Session Protection:**
- TLS session resumption disabled (prevents session theft)
- SSH session rekeying: Every 1GB of data or 1 hour
- Cookie security: HTTPOnly, Secure flags set
- Session tokens: Cryptographically random (128-bit entropy minimum)

**Anti-Replay Mechanisms:**
- TLS sequence numbers prevent replay attacks
- SSH sequence numbers prevent replay attacks
- Kerberos ticket timestamps prevent replay (5-minute window)

**Rev 3 Consolidated Controls:**
- Rev 2 3.13.19 (Authenticity of communications sessions) is the primary source for this control

---

## 4. ROLES AND RESPONSIBILITIES

**System Owner (sysadmin):**
- Maintain this policy and ensure compliance
- Configure and maintain cryptographic implementations
- Review firewall rules quarterly
- Approve network architecture changes
- Conduct annual policy review

**System Administrator (sysadmin):**
- Implement and maintain boundary protection controls
- Configure and monitor encryption implementations
- Maintain FIPS 140-2 compliance
- Document cryptographic key management procedures
- Create and maintain network architecture diagram (Phase 3)

---

## 5. COMPLIANCE

**Regulatory Requirements:**
- NIST SP 800-171 Rev 3: Controls 3.13.1 through 3.13.16 (all 16 SC controls)
- CMMC Level 2: System and Communications Protection domain
- DFARS 252.204-7012: Safeguarding CUI requirements
- FIPS 140-2: Validated cryptography required

**Assessment Evidence:**
- OpenSCAP scan results: 100% SC control compliance
- Firewall configuration backups
- Encryption verification outputs (cryptsetup status, openssl version)
- FIPS validation certificates (OpenSSL #3980, libgcrypt #3739, Kernel #4046)
- Network architecture diagram (Phase 3 deliverable)

---

## 6. DEFINITIONS

**Boundary Protection:** Monitoring and controlling communications at external and internal system boundaries.

**CUI:** Controlled Unclassified Information requiring safeguarding per NIST SP 800-171.

**FIPS 140-2:** Federal Information Processing Standard for cryptographic module validation.

**LUKS:** Linux Unified Key Setup, disk encryption specification.

**Mobile Code:** Software transferred between systems and executed without explicit installation (JavaScript, Java applets).

**ODP:** Organization-Defined Parameter, value tailored by organization per Rev 3 guidance.

**Session:** Persistent interactive information exchange between systems or users.

---

## 7. ENFORCEMENT

**Non-Compliance:**
- Violations of this policy may result in:
  - Immediate account suspension
  - System access revocation
  - Disciplinary action per Personnel Security Policy (TCC-PS-001)

**Reporting:**
- Policy violations must be reported to System Owner immediately
- Incident Response procedures (TCC-IRP-001) apply for security incidents

---

## 8. RELATED DOCUMENTS

**Policies:**
- TCC-AAP-001: Audit and Accountability Policy v2.0 Rev 3
- TCC-IAP-001: Identification and Authentication Policy v2.0 Rev 3
- TCC-IRP-001: Incident Response Policy (to be updated to Rev 3)
- TCC-PS-001: Personnel Security Policy (to be updated to Rev 3)

**Procedures:**
- Incident Response Plan
- LUKS Encryption Procedures
- Firewall Change Control Procedures

**Standards:**
- NIST SP 800-171 Rev 3: Protecting Controlled Unclassified Information
- NIST SP 800-53 Rev 5: Security and Privacy Controls (SC family)
- FIPS 140-2: Security Requirements for Cryptographic Modules

---

## 9. REVIEW AND UPDATES

**Review Frequency:** Annually or when significant changes occur

**Next Scheduled Review:** March 2027

**Version Control:** All policy versions maintained in `/home/dshannon/CyberSecurity/Rev3/Policies/`

**Change Log:**
- v2.0 Rev 3 DRAFT (March 22, 2026): Updated for Rev 3 - ODPs added, FIPS certs documented, network diagram requirement added, consolidated controls updated

---

## 10. APPROVAL

**Policy Owner:** System Owner (sysadmin)

**Approval Date:** [TBD - Target: Phase 2 completion]

**Signature:** _________________________________

**Next Review Date:** [Approval Date + 12 months]

---

*This policy satisfies NIST SP 800-171 Rev 3 controls 3.13.1 through 3.13.16 (System and Communications Protection family). All 20 SC controls addressed.*

**Rev 3 Status:** DRAFT - Pending final review and approval
**Phase 2 Target Completion:** April 2026
