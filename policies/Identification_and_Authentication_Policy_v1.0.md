# Identification and Authentication Policy

**Document ID:** DIWAI-IAP-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** CUI

---

## 1. Purpose

This policy establishes diwai.org (Do It With AI) requirements for identification and authentication on the SecureMac Production Network (SPN). It ensures only authorized individuals and processes can access SPN systems and CUI, in compliance with NIST SP 800-171 Rev 2 (IA-1 through IA-13) and CMMC Level 2.

---

## 2. Scope

This policy applies to:

- **All SPN Systems:**
  - Mac mini M4 Pro (securemac.diwai.org) — macOS Tahoe host
  - Rocky Linux 9.7 VM (services.diwai.org, 10.10.1.10)
    - 389 Directory Server — identity and authentication services
    - SSH daemon — administrative access
    - Apache HTTPD — web services
    - OpenVPN — remote access
    - Postfix/Dovecot — email services

- **All User Types:**
  - Organizational users (Donald E. Shannon)
  - Contractors and authorized temporary users
  - Service accounts and automated processes

---

## 3. Policy Statements

### 3.1 Identification and Authentication Policy and Procedures (IA-1)

diwai.org shall maintain this policy and review it annually. Compliance verified through quarterly OpenSCAP scans and periodic account audits.

### 3.2 Identification and Authentication — Organizational Users (IA-2)

**All organizational users must be uniquely identified before accessing SPN systems.**

1. **Unique User Accounts:**
   - Each user has a unique 389-DS LDAP account (no shared accounts)
   - Unique SSH keys per user (ECDSA-521)
   - No generic or service accounts used for interactive login

2. **Authentication Methods:**
   - SSH public key authentication (primary method for Linux VM)
   - LDAP bind password (for directory services access)
   - macOS local account (for host administration)
   - All passwords meet complexity requirements (Section 3.5)

3. **Multi-Factor Authentication (IA-2(1), IA-2(2)):**

   **Status: MET — POA&M-001 CLOSED 2026-04-10**
   - **Implementation:** YubiKey 5C Nano FIPS (FIDO2 ECDSA-SK, `verify-required`)
   - **Factor 1 (have):** YubiKey 5C Nano FIPS hardware token (serial 34246645, FIPS 140-2 Level 1)
   - **Factor 2 (know):** FIDO2 PIN enforced on every authentication via `verify-required` key flag
   - **Presence confirmation:** Physical touch of YubiKey required per session
   - **Key type:** `ecdsa-sk` (ECDSA P-256 with FIDO2 hardware binding) — FIPS 140-2 approved
   - **SSH key is resident on YubiKey** — recoverable with `ssh-keygen -K` using PIN
   - **Evidence:** DIWAI-EV-MFA-001 (`MFA_YubiKey_Deployment.md`)

### 3.3 Device Identification and Authentication (IA-3)

- SSH host key verification required for all administrative connections
- SSH host keys: ECDSA-521, generated at initial setup
- `StrictHostKeyChecking yes` enforced in client SSH configurations
- Known hosts file maintained and protected

### 3.4 Identifier Management (IA-4)

**User Identifier Requirements:**
- Unique identifiers assigned and never reused
- Naming convention: `firstname.lastname` (LDAP) or `dshannon` (system)
- Contractor accounts: `contractor.lastname` format
- Account expiration required for contractor accounts

**Identifier Lifecycle:**
- Account creation requires ISSO approval
- Inactive accounts disabled after 45 days of inactivity (reviewed monthly)
- Terminated user accounts disabled within 24 hours of separation (per DIWAI-PS-001)
- Disabled accounts retained 90 days then deleted
- Account audit conducted quarterly

### 3.5 Authenticator Management (IA-5)

**Password Requirements (enforced by 389-DS password policy):**
- Minimum length: 14 characters
- Complexity: uppercase, lowercase, digits, special characters
- Maximum age: 90 days
- Password history: Last 5 passwords remembered (no reuse)
- Lockout: 5 failed attempts → 30-minute lockout

**SSH Key Requirements:**
- Algorithm: ECDSA-521 (preferred) or Ed25519 for standard keys; `ecdsa-sk` (ECDSA P-256, FIDO2) for hardware-bound MFA keys
- Key passphrase required (minimum 20 characters) for standard keys; FIDO2 keys use PIN + touch via YubiKey
- Private keys stored with 600 permissions
- No passphrase-less keys permitted on production systems
- FIDO2 resident keys stored on YubiKey hardware; recoverable via `ssh-keygen -K`

**Initial Credential Distribution:**
- Temporary passwords issued in person or via secure encrypted channel
- User must change temporary password on first login
- SSH keys generated locally by user; public key submitted to ISSO for installation

**Credential Storage:**
- Passwords stored in KeePass vault (Passwords.kdbx) — per TCC-IAP-001 key management
- KeePass database protected with strong master password + key file
- KeePass database backed up to DataStore NAS (encrypted)

**Authenticator Protection:**
- SSH private keys stored in `~/.ssh/` with mode 600
- No storage of credentials in scripts, configuration files, or environment variables
- SSH agent forwarding disabled by default

### 3.6 Authenticator Feedback (IA-6)

- Password entry obscured (terminal default behavior)
- SSH authentication feedback does not reveal whether username or key is invalid
- No password hints or recovery questions implemented

### 3.7 Cryptographic Module Authentication (IA-7)

- FIPS 140-2 mode enabled on Rocky Linux VM
- Only FIPS-approved cryptographic algorithms used for authentication
- Verification: `fips-mode-setup --check`
- LDAP connections use TLS 1.2+ (FIPS-compliant cipher suites)

### 3.8 Identification and Authentication — Non-Organizational Users (IA-8)

**Non-organizational users (contractors) subject to the same authentication requirements as organizational users:**
- Unique LDAP account required
- Same password complexity and SSH key requirements
- Time-limited account expiration enforced
- MFA required when implemented (POA&M-001)
- Access restricted to minimum required resources (least privilege via LDAP groups)

### 3.9 Service Identifier Management (IA-9)

- Service accounts use non-interactive shell (`/sbin/nologin`)
- Service account passwords are long, random, stored in KeePass only
- Services authenticate to each other using certificates or service-specific credentials
- Let's Encrypt wildcard certificate (*.diwai.org) used for service TLS authentication
  - Certificate stored: `/etc/letsencrypt/live/diwai.org/`
  - Deployed to: `/etc/pki/tls/certs/diwai.org.crt`, `/etc/pki/tls/private/diwai.org.key`
  - Auto-renewal: certbot-renew.timer (nightly)
  - Expiry: 2026-07-09

### 3.10 Adaptive Authentication (IA-10)

Not implemented. Will be reviewed for implementation after POA&M-001 MFA deployment.

### 3.11 Re-Authentication (IA-11)

- SSH sessions: `ClientAliveInterval 300`, `ClientAliveCountMax 0` (disconnect after 5 minutes idle)
- macOS screen lock: 15-minute timeout
- LDAP session tokens: expire per application session configuration
- VPN sessions: Disconnect after 15 minutes idle

---

## 4. Account Management Integration

### 4.1 Account Creation

1. ISSO approves account request
2. 389-DS LDAP account created:
   ```bash
   # Add user to directory
   ldapadd -x -D "cn=Directory Manager" -W -H ldap://services.diwai.org << EOF
   dn: uid=username,ou=People,dc=diwai,dc=org
   objectClass: top
   objectClass: person
   objectClass: organizationalPerson
   objectClass: inetOrgPerson
   objectClass: posixAccount
   uid: username
   cn: First Last
   sn: Last
   uidNumber: <assigned>
   gidNumber: <assigned>
   homeDirectory: /home/username
   loginShell: /bin/bash
   EOF
   ```
3. SSH public key added to `authorized_keys`
4. User notified of account via secure channel
5. Account creation logged in audit trail

### 4.2 Account Modification

- All modifications documented in Change_Log.md
- LDAP password resets logged and require user verification
- Group membership changes require ISSO approval

### 4.3 Account Termination

- Account disabled within 24 hours of separation
- SSH authorized_keys entry removed
- Active sessions terminated
- Account retained (disabled) 90 days then deleted
- LDAP audit trail preserved

---

## 5. Compliance Mapping

| NIST SP 800-171 Control | Implementation |
|-------------------------|----------------|
| **IA-1** Policy and Procedures | This document |
| **IA-2** Identification and Authentication (Org Users) | Section 3.2 |
| **IA-2(1)** MFA for Privileged Access | Section 3.2.3 — MET (YubiKey 5C FIPS, POA&M-001 closed 2026-04-10) |
| **IA-2(2)** MFA for Non-Privileged Access | Section 3.2.3 — MET (YubiKey 5C FIPS, POA&M-001 closed 2026-04-10) |
| **IA-3** Device Identification | Section 3.3 |
| **IA-4** Identifier Management | Section 3.4 |
| **IA-5** Authenticator Management | Section 3.5 |
| **IA-6** Authenticator Feedback | Section 3.6 |
| **IA-7** Cryptographic Module Authentication | Section 3.7 |
| **IA-8** Identification and Authentication (Non-Org) | Section 3.8 |
| **IA-9** Service Identifier Management | Section 3.9 |
| **IA-11** Re-Authentication | Section 3.11 |

**SPRS Impact:**
- IA-2(1)/IA-2(2)/IA-2(3.5.3): 0 points (MET — deficit resolved 2026-04-10, +5 recovered)
- POA&M-001: **CLOSED 2026-04-10** — YubiKey 5C Nano FIPS deployed

---

## 6. Policy Review and Updates

- **Review Frequency:** Annually
- **Approval Authority:** System Owner / ISSO (Donald E. Shannon)

---

## 7. Approval Signatures

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
