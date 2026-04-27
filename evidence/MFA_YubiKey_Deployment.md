# MFA Deployment Evidence — YubiKey 5C Nano FIPS

**Document ID:** DIWAI-EV-MFA-001  
**Version:** 2.0  
**Date:** April 23, 2026  
**Deployed By:** Donald E. Shannon, ISSO  
**System:** securemac.diwai.org (macOS Tahoe host)  
**Compliance:** NIST SP 800-171 § 3.5.3  
**Classification:** CUI  

---

## Revision History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2026-04-10 | Initial deployment — FIDO2-SK (`ecdsa-sk`) for SSH to services.diwai.org. POA&M-001 closed. |
| 2.0 | 2026-04-23 | **v1.0 implementation rolled back** after 2026-04-14 lockout incident (third-party PAM with VM network dependency). Re-implemented 2026-04-15 using native macOS CryptoTokenKit PIV (Slot 9C). SSH MFA pending Slot 9A regeneration. 3.5.3 status revised to PARTIAL. |

---

## 1. Summary

YubiKey 5C Nano FIPS (PIV smartcard) is deployed for multi-factor authentication on the macOS host (securemac.diwai.org) via native macOS CryptoTokenKit. No third-party PAM modules are used.

**Current MFA coverage:**

| Auth Path | Factor 1 (Have) | Factor 2 (Know) | Status |
|-----------|-----------------|-----------------|--------|
| macOS screen lock/unlock | YubiKey hardware token | PIV PIN | ✅ Operational |
| macOS sudo (pam_smartcard.so) | YubiKey hardware token | PIV PIN (ONCE policy) | ✅ Operational |
| SSH to services.diwai.org | RSA key only | — | ⚠ MFA not active (post-rollback) |
| macOS login (enforcement) | — | — | ⚠ Not enforced (password fallback active) |

**NIST 800-171 § 3.5.3 Status: PARTIAL**  
MFA is operational for local macOS authentication. Network access to the service VM (SSH) does not currently require MFA. Smartcard enforcement is not yet enabled. See §7 for remediation path.

---

## 2. Hardware

**Device:** YubiKey 5C Nano FIPS  
**Serial Number:** 34246645  
**Firmware:** 5.4.3  
**Form Factor:** Nano (USB-C) — permanently installed in Mac mini USB-C port  
**FIPS Validation:** FIPS 140-2 Level 1 (YubiKey 5 FIPS Series)  
**Tools:** `ykman 5.9.0`, `yubico-piv-tool` (Homebrew)

---

## 3. PIV Configuration

### Slot 9C — Digital Signature (current auth pairing)

| Attribute | Value |
|-----------|-------|
| Subject | Certificate For Digital Signature (Don Shannon) |
| Issuer | diwai.org Email CA |
| Algorithm | ECDSA P-256 (FIPS 140-2 approved) |
| Hash | `3CE899BDDF09EA91986C3DB41BC24DA030EB2159` |
| Valid | 2026-04-13 → 2028-04-12 |
| PIN Policy | ONCE (PIN cached for session) |
| Touch Policy | NEVER |

**Note:** Slot 9C (Digital Signature) is being used for auth pairing because Slot 9A (PIV Authentication) has incorrect policies that are incompatible with a rack-mounted, permanently-installed key (Touch Policy: ALWAYS requires physical touch on every operation — not feasible when the device is inside a rack enclosure). Slot 9A will be regenerated with correct policies.

### Slot 9A — PIV Authentication (pending regeneration)

| Attribute | Value |
|-----------|-------|
| Status | **Incorrect policies — not in use** |
| PIN Policy | NEVER (should be ONCE) |
| Touch Policy | ALWAYS (should be NEVER — key is rack-mounted) |
| Action required | Regenerate with `--pin-policy once --touch-policy never` when diwai.org CA is online |

---

## 4. macOS Integration

### CryptoTokenKit Pairing

Slot 9C certificate paired to `dshannon` user account:

```bash
sc_auth pair -h 3CE899BDDF09EA91986C3DB41BC24DA030EB2159 -u dshannon
```

Verify pairing:
```bash
sc_auth identities
# Output: 3CE899BDDF09EA91986C3DB41BC24DA030EB2159  dshannon
```

### sudo — pam_smartcard.so

macOS native `pam_smartcard.so` is configured for sudo. PIN is cached per ONCE policy — user enters PIN on first sudo invocation, subsequent sudo calls within the session do not re-prompt.

```bash
# Verify sudo MFA
sudo whoami
# Prompts: PIN for YubiKey... then caches for session
```

### Smart Card Enforcement

**Current state: NOT enabled** — YubiKey removal or disconnection falls back to password authentication.

```bash
# Check current enforcement state
sudo defaults read /Library/Preferences/com.apple.security.smartcard enforceSmartCard
# Returns: 0 (not enforced)
```

Enforcement will be enabled after Slot 9A is regenerated and tested:
```bash
sudo defaults write /Library/Preferences/com.apple.security.smartcard enforceSmartCard -bool true
```

---

## 5. Incident History — 2026-04-14 Lockout

### Root Cause

The v1.0 implementation (FIDO2-SK via `pam_yubico`/`pam_u2f`) set the PAM module as `required` in the authentication stack. The module had a network dependency on the Rocky Linux VM (10.10.1.10) for OTP/FIDO2 validation. The VM does not autostart with the Mac mini.

When the YubiKey was removed for testing, combined with the VM being unreachable, the `required` PAM module caused authentication to fail completely — including the local console login prompt.

### Recovery

1. Booted into macOS Recovery Mode
2. Restored from Time Machine snapshot dated 2026-04-12
3. macOS state reverted to pre-MFA baseline

### Lessons Learned

- All authentication on securemac.diwai.org must be **local to the Mac** — zero VM/network dependency
- Third-party PAM modules that depend on external services must be configured `sufficient` (not `required`) to prevent total lockout
- Native macOS CryptoTokenKit PIV has zero network dependency — all validation is local hardware

### Break-Glass Account

`sysadmin` local account: strong 16-character password (upper/lower/number/special).  
Password stored in sealed envelope in locked cabinet.  
No smartcard paired to `sysadmin` — emergency access only.  
Will add Slot 9A certificate as secondary pairing when 9A is regenerated (Option B).

---

## 6. Previous Implementation (v1.0 — Superseded)

The original implementation used FIDO2-SK (`ecdsa-sk`, ECDSA P-256) for SSH authentication to services.diwai.org:

- Key type: `sk-ecdsa-sha2-nistp256@openssh.com` with `verify-required` and `resident` flags
- Fingerprint: `SHA256:E1PsNvufFcC4VQCiwGY9FkAY7cquizb27lNVR0WEdDA`
- sshd config: `/etc/ssh/sshd_config.d/49-fido2.conf` (prepended sk- type before crypto-policy)

This implementation was rolled back with the Time Machine restore on 2026-04-14. The key file (`~/.ssh/id_ecdsa_sk`) was lost with the rollback; as a resident key, it can be recovered from the YubiKey using `ssh-keygen -K` when restoring SSH MFA.

---

## 7. Remediation Path (Open Items)

The following steps are required to bring 3.5.3 to fully MET:

| Step | Action | Prerequisite |
|------|--------|--------------|
| 1 | Regenerate Slot 9A with correct policies (`--pin-policy once --touch-policy never`) | diwai.org CA online (VM .10) |
| 2 | Issue cert from diwai.org CA for Slot 9A; import and re-pair to `dshannon` | Step 1 |
| 3 | Unpair Slot 9C cert | Step 2 |
| 4 | Optionally pair Slot 9A cert to `sysadmin` (break-glass Option B) | Step 2 |
| 5 | Restore SSH MFA to services.diwai.org (recover FIDO2-SK via `ssh-keygen -K`, or configure PIV SSH) | Step 2 |
| 6 | Enable smart card enforcement (`enforceSmartCard -bool true`) | Steps 1–5 tested |

**Target date:** 2026-05-31  
**POA&M reference:** SecureMac-POAM-009

---

## 8. Compliance Status

| Control | Requirement | Status |
|---------|-------------|--------|
| 3.5.3 / IA-2(1) | MFA for privileged local access | ⚠ PARTIAL — PIV operational, enforcement not enabled |
| 3.5.3 / IA-2(2) | MFA for network access to privileged accounts | ⚠ PARTIAL — SSH to VM uses RSA key only |
| FIPS-compatible | ECDSA P-256 (not Ed25519) | ✅ PASS — Slot 9C cert is ECDSA P-256 |
| Hardware token | FIPS 140-2 validated device | ✅ PASS — YubiKey 5 FIPS Series |

**POA&M-009:** Open — Target 2026-05-31  
**SPRS Impact:** 3.5.3 assessed as PARTIAL — -5 points applied until enforcement and SSH MFA are operational.

---

**Verified By:** Donald E. Shannon, ISSO  
**Date:** April 23, 2026  

---

**CLASSIFICATION:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)
