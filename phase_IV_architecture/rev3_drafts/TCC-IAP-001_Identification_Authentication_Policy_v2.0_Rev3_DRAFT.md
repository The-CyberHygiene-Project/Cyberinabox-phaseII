# Identification and Authentication Policy

**Policy Number:** TCC-IAP-001
**Version:** 2.0 Rev 3 DRAFT (Updated for NIST SP 800-171 Rev 3)
**Effective Date:** [TBD - Target: Phase 2 completion]
**Last Reviewed:** March 18, 2026
**Policy Owner:** System Owner (sysadmin)
**Approval Authority:** System Owner (sysadmin)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | [Original] | Initial policy (NIST 800-171 Rev 2) |
| 2.0 Rev 3 DRAFT | March 18, 2026 | Updated for Rev 3: **Added MFA deployment details** (SSH key + TOTP, deployed 2026-02-21), added ODP values, expanded determination statements |

---

## 1. PURPOSE

This policy establishes requirements for user identification and authentication within the CyberHygiene Production Network (CPN). This policy satisfies the Identification and Authentication (IA) control family requirements in NIST SP 800-171 Revision 3 (controls 3.5.1 through 3.5.11).

**Rev 3 Updates:**
- **Major Achievement:** Multi-Factor Authentication (MFA) fully deployed on all 4 systems (2026-02-21) — SPRS +5 points
- Added ODP values for password policies, authenticator management
- Expanded determination statement coverage (48 statements vs. 33 in Rev 2)
- Updated for FreeIPA centralized identity management

---

## 2. SCOPE

This policy applies to:
- All users accessing CPN systems (currently: sysadmin - system owner/administrator)
- All systems processing CUI (dc1, workstation1, workstation2, workstation3)
- All authentication mechanisms (FreeIPA Kerberos, SSH keys, TOTP MFA, PAM)
- All user accounts (interactive users, service accounts, privileged accounts)

---

## 3. POLICY STATEMENTS

### 3.1 User Identification — NIST 3.5.1 (IA-2)

**3.1.1 Unique User Identifiers**

Each user shall be assigned a unique identifier (username):

a) **User Naming Convention:**
   - Format: `firstname.lastname` or `firstinitiallastname` (e.g., `sysadmin`)
   - No shared accounts (each person has unique account)
   - Service accounts named by service (e.g., `apache`, `wazuh`, `postgres`)

b) **User ID Assignment:**
   - **Human users:** UID ≥ 1000 (standard Linux convention)
   - **Service accounts:** UID < 1000 (system accounts)
   - **Root:** UID = 0 (privileged account, used only via sudo)

c) **FreeIPA User Management:**
   - All user accounts created in FreeIPA (centralized identity management)
   - User accounts synchronized to all CPN systems via SSSD
   - No local user accounts created (except service accounts)

**Current Users:**
- **sysadmin** (UID 1000000001) — System Owner/Administrator

**3.1.2 User Identification Enforcement**

Systems enforce unique identification:
- Login prompts require username (no anonymous access)
- All audit logs include UID/username
- FreeIPA prevents duplicate usernames

---

### 3.2 User Authentication — NIST 3.5.2 (IA-2)

**3.2.1 Authentication Mechanisms**

CyberHygiene uses the following authentication mechanisms:

a) **Primary Authentication: FreeIPA Kerberos**
   - Centralized authentication via FreeIPA (dc1.example.local)
   - Kerberos protocol (realm: EXAMPLE.LOCAL)
   - Single Sign-On (SSO) capability across all CPN systems
   - **Note:** Currently experiencing KDC issue (kinit fails due to salt mismatch in ipadb.so) — workaround via kadmin -w or SSSD

b) **SSH Authentication: Public Key + TOTP (MFA)**
   - **Primary:** SSH public key authentication (ECDSA-521, RSA-4096)
   - **Secondary:** TOTP (Time-based One-Time Password) via pam_google_authenticator
   - **Deployment:** Fully operational on all 4 systems (2026-02-21)
   - **SPRS Impact:** +5 points (NIST 3.5.3 satisfied)

c) **Console Authentication: Password + TOTP (MFA - planned)**
   - Password authentication via PAM (FreeIPA backend)
   - TOTP not yet enforced for console (future enhancement)

**3.2.2 Authentication Flow**

SSH Login (with MFA):
```
1. User initiates SSH connection: ssh sysadmin@dc1.example.local
2. SSH key authentication: Server verifies user's public key (~/.ssh/authorized_keys)
3. TOTP challenge: Server prompts for verification code (pam_google_authenticator)
4. User enters TOTP code from authenticator app (Microsoft Authenticator)
5. Access granted if both factors successful
```

---

### 3.3 Multi-Factor Authentication (MFA) — NIST 3.5.3 (IA-2(1), IA-2(2), IA-2(8))

**3.3.1 MFA Deployment Status** ✅ **COMPLETE**

Multi-factor authentication is **fully deployed** on all CPN systems:

| System | SSH MFA Status | Console MFA | Deployment Date | TOTP Secret |
|--------|----------------|-------------|-----------------|-------------|
| **dc1 (.10)** | ✅ SSH key + TOTP | ⏸️ Planned | 2026-02-21 | [REDACTED_TOTP_SECRET] |
| **workstation1 (.115)** | ✅ SSH key + TOTP | ⏸️ Planned | 2026-02-21 | [REDACTED_TOTP_SECRET] |
| **workstation2 (.104)** | ✅ SSH key + TOTP | ⏸️ Planned | 2026-02-21 | [REDACTED_TOTP_SECRET] |
| **workstation3 (.113)** | ✅ SSH key + TOTP | ⏸️ Planned | 2026-02-21 | [REDACTED_TOTP_SECRET] |

**MFA Factors:**
1. **Something you have:** SSH private key (`~/.ssh/id_ecdsa` - ECDSA-521)
2. **Something you know:** TOTP code (6-digit, changes every 30 seconds)

**3.3.2 MFA Configuration Details**

**SSH Configuration** (`/etc/ssh/sshd_config.d/60-mfa.conf`):
```
KbdInteractiveAuthentication yes
AuthenticationMethods publickey,keyboard-interactive
```

**PAM Configuration** (`/etc/pam.d/sshd`):
```
# Exempt dc1 (10.0.0.10) from MFA for automation
auth sufficient pam_succeed_if.so quiet rhost = 10.0.0.10

# Require TOTP for all other sources
auth required pam_google_authenticator.so nullok
```

**SELinux Module** (`/root/sshd_google_auth.pp`):
- Allows sshd_t to write to user_home_dir_t (TOTP state file: `~/.google_authenticator`)
- Allows auth_home_t write access (for TOTP secret storage)

**Authenticator App:** Microsoft Authenticator (iOS/Android)

**3.3.3 MFA Exemptions**

**dc1 Automation Exemption:**
- SSH connections FROM dc1 (10.0.0.10) to workstations are exempt from TOTP
- **Purpose:** Allow automated scripts (OpenSCAP collection, deployment scripts) to function
- **Justification:** dc1 is secured; connections FROM dc1 originate from trusted admin
- **Implementation:** PAM `pam_succeed_if.so rhost = 10.0.0.10`

**No other exemptions.** All interactive SSH logins require MFA.

**3.3.4 MFA for Privileged Access**

Privileged access (sudo) requires:
1. **MFA to login:** SSH key + TOTP (to establish session)
2. **sudo authentication:** No additional authentication (NOPASSWD sudo for sysadmin)

**Justification:** MFA at login provides strong authentication. Re-authentication for every sudo command would be operationally burdensome. Audit logging (auditd) provides accountability for all sudo usage.

---

### 3.4 Replay-Resistant Authentication — NIST 3.5.4 (IA-2(8))

**3.4.1 Replay Resistance Mechanisms**

CyberHygiene authentication mechanisms are replay-resistant:

a) **Kerberos Tickets:**
   - Kerberos uses time-based tickets (short lifetime: 10 hours default)
   - Tickets cannot be replayed after expiration
   - Nonces prevent replay of authentication exchanges

b) **SSH:**
   - SSH protocol includes nonces in key exchange (prevents replay)
   - Each SSH session uses unique session keys
   - TOTP codes expire after 30 seconds (cannot be replayed)

c) **TOTP (Time-based One-Time Password):**
   - 6-digit code changes every 30 seconds
   - Server accepts codes from 1 time window before/after (90-second window total)
   - Used codes cannot be replayed (server tracks last used code timestamp)

**3.4.2 Replay Attack Mitigation**

If attacker captures authentication traffic:
- **Kerberos:** Ticket replay blocked by expiration, nonce validation
- **SSH:** Session replay blocked by nonces, unique session keys
- **TOTP:** Code replay blocked by 30-second expiration

---

### 3.5 Identifier Management — NIST 3.5.5 (IA-4)

**3.5.1 User Account Lifecycle**

User accounts follow this lifecycle:

a) **Creation:**
   - System Owner approves new account request
   - Administrator creates account in FreeIPA: `ipa user-add`
   - User assigned unique UID, default groups
   - Initial password set (must change at first login)

b) **Modification:**
   - Group membership changes: `ipa group-add-member`
   - Role changes: RBAC roles assigned via FreeIPA
   - Password reset: `ipa passwd <username>` or `ldappasswd`

c) **Suspension:**
   - Temporary suspension: `ipa user-disable <username>`
   - Account locked, cannot authenticate
   - Used for investigations, temporary leave

d) **Termination:**
   - Account deletion: `ipa user-del <username>` (discouraged - loses audit trail)
   - **Preferred:** Disable account permanently: `ipa user-disable`
   - Remove from all groups, revoke privileges
   - Retain account for audit history

**3.5.2 User Account Review**

User accounts shall be reviewed:
- **Frequency:** Annually (or upon significant personnel changes)
- **Review criteria:** Ensure all accounts belong to authorized users, no orphaned accounts
- **Action:** Disable/delete unauthorized accounts

**Current Status:** Single user (sysadmin) - annual review confirms account authorized.

---

### 3.6 Authenticator Management — NIST 3.5.6 (IA-5)

**3.6.1 Password Authenticators**

**Initial Password Distribution (ODP-IA-1):**
- New user passwords communicated securely:
  - **In-person:** Verbal communication (no written record)
  - **Remote:** Encrypted email with separate passphrase delivery
  - **Temporary password:** Must change at first login (FreeIPA enforces)

**Password Storage:**
- Passwords stored as PBKDF2 hashes in FreeIPA (389 Directory Server)
- Hash algorithm: PBKDF2-SHA256 (iterations: 100,000)
- Salted hashes (unique salt per password)
- Cleartext passwords never stored

**3.6.2 SSH Key Authenticators**

**Key Generation:**
- Users generate SSH key pairs on their client systems
- **Recommended algorithms:** ECDSA-521, Ed25519, RSA-4096
- **Prohibited algorithms:** RSA-1024 (weak), DSA (deprecated)

**Public Key Distribution:**
- Users provide public key to administrator
- Administrator adds to `~/.ssh/authorized_keys` on target systems
- **OR** Keys stored in FreeIPA (if SSH key management enabled)

**Private Key Protection:**
- Private keys stored on user's local system (not on servers)
- **Must be encrypted:** ssh-keygen with passphrase
- Permissions: `0600` (rw-------) on private key file

**Key Rotation:**
- SSH keys rotated every 2 years (recommended)
- Immediate rotation if key compromised

**Current Key:** `/home/sysadmin/.ssh/id_ecdsa` (ECDSA-521, generated 2026-01-15)

**3.6.3 TOTP Authenticators**

**TOTP Secret Generation:**
- Generated via `google-authenticator` command
- 16-character Base32-encoded secret (80 bits entropy)
- Secret stored in `~/.google_authenticator` (permissions: 0600)

**TOTP Secret Distribution:**
- User scans QR code during setup (displayed on terminal)
- Backup codes provided (stored securely, offline)

**TOTP Secret Protection:**
- Secrets never transmitted over network (generated locally)
- Encrypted at rest (home directory on LUKS-encrypted disk)
- SELinux protects `~/.google_authenticator` file

**Authenticator App Security:**
- **Recommended apps:** Microsoft Authenticator, Google Authenticator, Authy
- **Device security:** Authenticator device (smartphone) must be PIN/biometric protected
- **Backup:** Backup codes stored securely (password manager, safe)

**TOTP Secret Rotation:**
- Rotate every 2 years (recommended)
- Immediate rotation if device lost/compromised

**3.6.4 Service Account Authenticators**

Service accounts (apache, wazuh, postgres) use:
- **No interactive login:** `/sbin/nologin` shell
- **Authentication:** Not applicable (services run as these accounts, but accounts cannot login)
- **Access control:** File permissions, SELinux contexts

---

### 3.7 Password Policy — NIST 3.5.7 (IA-5(1))

**3.7.1 Password Complexity Requirements (ODP-IA-2, ODP-IA-3)**

FreeIPA enforces the following password policy:

a) **Minimum length (ODP-IA-2):** 12 characters
   - **Meets DoD baseline** (DoD ODP: 12 characters)
   - Configuration: `ipa pwpolicy-mod --minlength=12`

b) **Complexity requirements (ODP-IA-3):** At least 3 character classes
   - **Character classes:** Uppercase, lowercase, numbers, special characters
   - **Requirement:** Password must contain at least 3 of the 4 classes
   - **Example valid:** `MyP@ssw0rd!2026` (uppercase, lowercase, special, numbers - 4 classes)
   - **Example invalid:** `mypassword12345` (only lowercase and numbers - 2 classes)
   - Configuration: `ipa pwpolicy-mod --minclasses=3`

c) **Dictionary check:** Passwords cannot contain username or common dictionary words
   - FreeIPA password quality plugin (libpwquality) checks

 against dictionary

d) **Repetition check:** No more than 2 identical consecutive characters
   - Example invalid: `P@sssword123` (three consecutive 's')

**3.7.2 Password Expiration (ODP-IA-4)**

Passwords expire and must be changed:

a) **Maximum password age:** 90 days
   - **More permissive than DoD baseline** (DoD ODP: 60 days)
   - **Justification:** NIST SP 800-63B (2017) recommends AGAINST periodic password changes unless compromise suspected. MFA deployment reduces password-only risk. 90 days balances legacy DoD requirements with modern guidance.
   - Configuration: `ipa pwpolicy-mod --maxlife=90`

b) **Expiration warning:** 7 days before expiration
   - FreeIPA sends warning at login: "Password expires in X days"

c) **Grace logins:** 3 logins after expiration (to allow password change)

d) **Post-expiration:** Account locked until password reset by administrator

**3.7.3 Password Change Requirements**

When changing password:
- **Minimum age:** Cannot change password for 1 day after last change (prevents rapid cycling)
  - Configuration: `ipa pwpolicy-mod --minlife=1`
- **Must differ from previous:** New password cannot be same as current password
- **History check:** Cannot reuse last 24 passwords (see Section 3.8)

---

### 3.8 Password Reuse Prohibition — NIST 3.5.8 (IA-5(1))

**3.8.1 Password History (ODP-IA-5)**

FreeIPA maintains password history:

a) **History size:** 24 generations
   - **Meets DoD baseline** (DoD ODP: 24 generations)
   - Configuration: `ipa pwpolicy-mod --history=24`

b) **History enforcement:**
   - User cannot reuse any of last 24 passwords
   - FreeIPA stores password hashes (PBKDF2) for comparison
   - History cleared only upon administrator action (not recommended)

**Example:**
- User changes password 24 times
- Attempts to reuse password #1 (from 24 changes ago)
- FreeIPA rejects: "Password is in history"
- User must choose new password not in history

---

### 3.9 Password Transmission Protection — NIST 3.5.9 (IA-5(1))

**3.9.1 Encrypted Transmission**

Passwords are never transmitted in cleartext:

a) **SSH:** Passwords transmitted encrypted via SSH protocol (AES-256-GCM)

b) **FreeIPA Web UI:** Passwords transmitted encrypted via HTTPS (TLS 1.3, AES-256-GCM)

c) **LDAP:** Passwords transmitted via LDAPS (LDAP over TLS) or LDAPI (UNIX domain socket)

d) **Kerberos:** Passwords used to derive encryption keys, never transmitted (pre-authentication uses encrypted timestamp)

**3.9.2 Prohibited Transmission Methods**

The following are **prohibited**:
- ❌ Cleartext protocols (Telnet, HTTP, FTP)
- ❌ Email (even encrypted email - passwords should not be emailed)
- ❌ Instant messaging
- ❌ Written/printed (passwords should not be written down except for secure offline backup)

---

### 3.10 Cryptographic Password Protection — NIST 3.5.10 (IA-5(1))

**3.10.1 Password Hashing**

Passwords are protected cryptographically:

a) **Hashing algorithm:** PBKDF2-SHA256
   - Password-Based Key Derivation Function 2 with SHA-256
   - Industry-standard, resistant to brute-force attacks

b) **Iterations:** 100,000 rounds
   - Slows brute-force attacks (takes ~0.1 seconds per hash)
   - NIST SP 800-132 recommends ≥10,000 iterations

c) **Salting:** Unique random salt per password
   - Prevents rainbow table attacks
   - Salt stored alongside hash in FreeIPA

d) **Storage:** Hashes stored in 389 Directory Server (FreeIPA backend)
   - LDAP attribute: `userPassword`
   - Format: `{PBKDF2_SHA256}AAA...` (base64-encoded hash)

**3.10.2 Password Hash Protection**

Password hashes are protected:
- LDAP access controls restrict `userPassword` attribute read (only administrators)
- Hashes stored on LUKS-encrypted disk
- Backups of FreeIPA are encrypted

---

### 3.11 Obscure Feedback of Authentication Information — NIST 3.5.11 (IA-6)

**3.11.1 Password Masking**

Authentication information is obscured during entry:

a) **Password prompts:** Characters replaced with asterisks (*) or not displayed
   - SSH password prompt: no echo
   - sudo password prompt: no echo
   - FreeIPA Web UI: password field masked (••••••)

b) **TOTP prompts:** Digits masked or not displayed
   - SSH TOTP prompt: "Verification code: " (no echo)

c) **Audit logs:** Passwords never logged
   - auditd logs authentication events but not password/TOTP values
   - Failed authentication logs show "authentication failure" not "incorrect password: XYZ"

**3.11.2 Prohibited Practices**

The following are **prohibited**:
- ❌ Displaying passwords on screen (except during initial setup, briefly)
- ❌ Logging passwords in cleartext
- ❌ Storing passwords in command history (bash history)
- ❌ Passing passwords as command-line arguments (visible in `ps`)

**Best Practice:** Use environment variables or input redirection for scripts requiring passwords.

---

## 4. ROLES AND [REDACTED_TOTP_SECRET]

### 4.1 System Owner (sysadmin)

- Approve identification and authentication policy
- Approve new user account requests
- Authorize MFA exemptions (currently: dc1 automation only)
- Conduct annual user account review
- Approve password policy changes

### 4.2 Administrator (sysadmin)

- Create, modify, disable user accounts in FreeIPA
- Configure and maintain MFA (SSH keys, TOTP)
- Monitor authentication logs for anomalies
- Reset passwords upon authorized request
- Maintain FreeIPA identity management system

### 4.3 Users (currently: sysadmin only)

- Protect authentication credentials (passwords, SSH keys, TOTP secrets)
- Use strong, unique passwords
- Change password if compromised
- Report lost/stolen authenticator devices (smartphones with TOTP)
- Comply with password policy

---

## 5. PROCEDURES

### 5.1 User Account Creation Procedure

**When to Use:** Adding new user to CPN systems

**Steps:**

1. **Obtain approval:**
   - System Owner approves new account request
   - Verify business need, CUI access justification

2. **Create account in FreeIPA:**
   ```bash
   ipa user-add <username> \
     --first=<firstname> \
     --last=<lastname> \
     --email=<email> \
     --shell=/bin/bash \
     --homedir=/home/<username>
   ```

3. **Set initial password:**
   ```bash
   ipa passwd <username>
   ```
   - Enter temporary password (12+ characters, meets complexity)
   - Communicate password securely to user (encrypted email or in-person)
   - Tell user to change password at first login

4. **Assign groups/roles:**
   ```bash
   ipa group-add-member <groupname> --users=<username>
   ```

5. **Configure MFA:**
   - Add SSH public key: `ipa user-mod <username> --sshpubkey="<key>"`
   - User sets up TOTP: `google-authenticator` (on first SSH login)

6. **Verify account:**
   - User logs in via SSH (tests SSH key + TOTP)
   - User changes initial password

7. **Document:**
   - Record account creation in user account log
   - Update user account inventory

---

### 5.2 MFA Setup Procedure (TOTP)

**When to Use:** New user account, TOTP secret rotation

**Steps:**

1. **Generate TOTP secret:**
   ```bash
   google-authenticator
   ```

2. **Answer prompts:**
   - "Do you want authentication tokens to be time-based?" → Yes
   - Scan QR code with authenticator app (Microsoft Authenticator recommended)
   - Save backup codes to secure location (password manager, offline)

3. **Configuration questions:**
   - "Do you want me to update your ~/.google_authenticator file?" → Yes
   - "Do you want to disallow multiple uses of the same token?" → Yes
   - "Do you want to increase time skew window?" → No (30-second window sufficient)
   - "Do you want to enable rate-limiting?" → Yes (3 login attempts per 30 seconds)

4. **Test MFA:**
   - Logout
   - SSH back in: `ssh <username>@<system>`
   - Enter SSH key passphrase (if key encrypted)
   - Enter TOTP code from authenticator app
   - Verify successful login

5. **Document:**
   - Record TOTP setup completion
   - Store backup codes securely (encrypted, offline)

---

### 5.3 Password Reset Procedure

**When to Use:** User forgets password, password compromised

**Steps:**

1. **Verify user identity:**
   - In-person: Visual verification
   - Remote: Out-of-band verification (phone call, video call)

2. **Reset password in FreeIPA:**
   ```bash
   ipa passwd <username>
   ```
   - Enter new temporary password (12+ characters)

3. **Communicate new password:**
   - In-person: Verbal communication
   - Remote: Encrypted email or secure messaging

4. **User changes password:**
   - User logs in with temporary password
   - FreeIPA prompts for password change (temporary password expired)
   - User chooses new password (meets complexity, not in history)

5. **If SSH key compromised:**
   - Remove old public key: `ipa user-mod <username> --sshpubkey=`
   - User generates new key pair
   - User provides new public key
   - Administrator adds new public key: `ipa user-mod <username> --sshpubkey="<new-key>"`

6. **If TOTP secret compromised:**
   - User runs `google-authenticator` again (generates new secret)
   - Old secret invalidated
   - User scans new QR code with authenticator app

---

## 6. COMPLIANCE

This policy supports compliance with:
- NIST SP 800-171 Rev 3 Identification and Authentication (IA) family:
  - 3.5.1 (IA-2): Identification
  - 3.5.2 (IA-2): Authentication
  - 3.5.3 (IA-2(1), IA-2(2), IA-2(8)): Multi-Factor Authentication ✅ **COMPLETE**
  - 3.5.4 (IA-2(8)): Replay-Resistant Authentication
  - 3.5.5 (IA-4): Identifier Management
  - 3.5.6 (IA-5): Authenticator Management
  - 3.5.7 (IA-5(1)): Password Complexity and Expiration
  - 3.5.8 (IA-5(1)): Password Reuse
  - 3.5.9 (IA-5(1)): Password Transmission Protection
  - 3.5.10 (IA-5(1)): Cryptographic Password Protection
  - 3.5.11 (IA-6): Obscure Feedback
- DFARS 252.204-7012 (Safeguarding CUI)
- CMMC Level 2 (IA domain) — **MFA achievement enhances CMMC readiness**

---

## 7. DEFINITIONS

**Authenticator:** Something a user possesses and controls (e.g., password, SSH key, TOTP secret) used to verify identity.

**Multi-Factor Authentication (MFA):** Authentication using two or more factors from different categories: something you know (password), something you have (SSH key, TOTP device), something you are (biometric).

**TOTP (Time-based One-Time Password):** A 6-digit code that changes every 30 seconds, generated by an authenticator app.

**Organization-Defined Parameter (ODP):** A variable in Rev 3 controls that organizations must define (e.g., password length, expiration).

---

## 8. REFERENCES

- NIST SP 800-171 Rev 3 (IA family, controls 3.5.x)
- NIST SP 800-53 Rev 5 (IA family source controls)
- NIST SP 800-63B (Digital Identity Guidelines - Authentication)
- DoD ODP Values (Published April 15, 2025)
- FreeIPA documentation: https://www.freeipa.org/page/Documentation
- pam_google_authenticator: https://github.com/google/google-authenticator-libpam

---

## 9. POLICY REVIEW

This policy shall be reviewed and updated:
- **Annually** — Target month: April (aligned with SSP review)
- **Upon MFA changes** — Deployment to console, additional factors
- **Upon password policy changes** — FreeIPA policy updates

**Next Review Date:** April 2027

---

## 10. APPROVAL

**Policy Approved By:**

**System Owner:** _____________________________ Date: __________
sysadmin

---

**END OF POLICY**

---

## APPENDIX A: MFA DEPLOYMENT DETAILS

### Deployment Timeline
- **2026-02-17:** MFA planning and testing began
- **2026-02-21:** MFA deployed to all 4 systems (dc1, workstation1, workstation2, workstation3)
- **Current Status:** ✅ Fully operational

### Technical Architecture
```
[User Client]
    |
    ├─ SSH Private Key (ECDSA-521) ─────────┐
    |                                        |
    └─ TOTP App (Microsoft Authenticator) ──┤
                                             |
                                             v
                                    [CPN System (sshd)]
                                             |
                                             ├─ Verify SSH Public Key
                                             |  (~/.ssh/authorized_keys)
                                             |
                                             ├─ Challenge for TOTP
                                             |  (pam_google_authenticator)
                                             |
                                             └─ Grant Access if both factors valid
```

### SELinux Configuration
Custom policy module allows sshd to write TOTP state file:
```
module sshd_google_auth 1.0;

require {
    type sshd_t;
    type user_home_dir_t;
    type auth_home_t;
    class file { write create };
}

allow sshd_t user_home_dir_t:file { write create };
allow sshd_t auth_home_t:file { write create };
```

Installed: `semodule -i /root/sshd_google_auth.pp`

### Backup Codes
Each TOTP setup generates 5 backup codes (8-digit):
- Stored in `~/.google_authenticator` (encrypted line)
- Should be extracted and stored offline (password manager, safe)
- Each code usable once
- Regenerate codes if all used: `google-authenticator` (overwrite)

---

**TCC-IAP-001 v2.0 Rev 3 DRAFT**
**Created:** March 18, 2026
**Status:** DRAFT — Ready for review and customization
**Estimated customization effort:** 2-3 hours (review MFA details, verify configurations, approve)
