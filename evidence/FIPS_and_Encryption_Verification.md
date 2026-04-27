# FIPS 140-2 and Encryption Verification Evidence

**Document ID:** DIWAI-EV-FIPS-001
**Version:** 1.0
**Date Collected:** April 10, 2026
**Collected By:** Donald E. Shannon, ISSO
**System:** services.diwai.org (Rocky Linux 9.7 VM) + securemac.diwai.org (macOS Tahoe host)
**Classification:** CUI

---

## Purpose

This document provides evidence of FIPS 140-2 compliance, disk encryption, SELinux enforcement, and related security controls on the SecureMac Production Network (SPN). It supports NIST SP 800-171 controls 3.13.8 (FIPS cryptography), 3.13.10 (encryption at rest), and CMMC Level 2 requirements.

---

## 1. FIPS 140-2 Mode Verification — Rocky Linux VM

**Control:** NIST SP 800-171 § 3.13.8 / SC-13 (Cryptographic Protection)

**Command:** `fips-mode-setup --check`
**Date:** April 10, 2026

```
FIPS mode is enabled.
```

**OpenSSL Version (FIPS-validated library):**
```
OpenSSL 3.5.1 1 Jul 2025 (Library: OpenSSL 3.5.1 1 Jul 2025)
```

**Result:** PASS — FIPS 140-2 mode confirmed enabled on services.diwai.org.

---

## 2. SELinux Enforcement — Rocky Linux VM

**Control:** NIST SP 800-171 § 3.1.3, 3.13.3 / SC-3 (Security Function Isolation)

**Command:** `getenforce` and `sestatus`
**Date:** April 10, 2026

```
Enforcing

SELinux status:                 enabled
SELinuxfs mount:                /sys/fs/selinux
SELinux root directory:         /etc/selinux
Loaded policy name:             targeted
Current mode:                   enforcing
```

**Result:** PASS — SELinux enforcing mode confirmed on services.diwai.org.

---

## 3. LUKS Full-Disk Encryption — Rocky Linux VM

**Control:** NIST SP 800-171 § 3.13.16 / SC-28(1) (Cryptographic Protection at Rest)

**Command:** `lsblk -f` (root partition)
**Date:** April 10, 2026

```
NAME                                          FSTYPE      FSVER    UUID
└─vda3                                        crypto_LUKS 2        5ec294f8-2077-42df-a717-9f5aa50d5d3e
```

**LUKS Volume Mapper (dmsetup ls):**
```
luks-5ec294f8-2077-42df-a717-9f5aa50d5d3e    (253:0)
vg0-home                                      (253:4)
vg0-opt                                       (253:3)
vg0-root                                      (253:1)
vg0-swap                                      (253:2)
vg0-tmp                                       (253:5)
vg0-var                                       (253:8)
vg0-var_log                                   (253:7)
vg0-var_log_audit                             (253:6)
```

**LUKS Configuration:**
- Type: LUKS2
- Cipher: AES-256-XTS (aes-xts-plain64)
- Key Size: 512 bits (AES-256)
- UUID: 5ec294f8-2077-42df-a717-9f5aa50d5d3e

**Volume Groups Encrypted:**

| Logical Volume | Mount Point | Purpose |
|----------------|-------------|---------|
| vg0-root | / | Root filesystem |
| vg0-home | /home | User home directories |
| vg0-var | /var | System data |
| vg0-var_log | /var/log | System logs |
| vg0-var_log_audit | /var/log/audit | Audit logs (separate partition) |
| vg0-tmp | /tmp | Temporary files |
| vg0-opt | /opt | Optional packages |
| vg0-swap | [SWAP] | Swap (encrypted) |

**Result:** PASS — All partitions protected by single LUKS2 container on vda3. All filesystems within encrypted LVM volume group. Separate encrypted partition for audit logs meets AU-9 requirements.

---

## 4. FileVault Encryption — macOS Host

**Control:** NIST SP 800-171 § 3.13.16 / SC-28(1) (Cryptographic Protection at Rest)

**Command:** `fdesetup status`
**Date:** April 10, 2026

```
FileVault is On.
```

**Hardware:** Mac mini M4 Pro
- FileVault uses Apple M4 hardware Secure Enclave for key protection
- AES-256-XTS encryption of internal NVMe SSD
- Recovery key stored in KeePass vault (Passwords.kdbx)

**Result:** PASS — FileVault confirmed enabled on securemac.diwai.org macOS host.

---

## 5. Audit Logging — Rocky Linux VM

**Control:** NIST SP 800-171 § 3.3.1, 3.3.2 / AU-2, AU-12

**auditd Service Status:**
```
● auditd.service - Security Auditing Service
     Loaded: loaded (/usr/lib/systemd/system/auditd.service; enabled; preset: enabled)
     Active: active (running) since Fri 2026-04-10 10:48:08 MDT; 1h 57min ago
   Main PID: 1838 (auditd)
     Memory: 7.2M
```

**Active Audit Rules (CUI Profile — representative sample):**
```
-a always,exit -F arch=b64 -S openat,open_by_handle_at -F a2&0x3 -F path=/etc/passwd -F auid>=1000 -F auid!=-1 -F key=user-modify
-a always,exit -F arch=b64 -S openat,open_by_handle_at -F a2&0x3 -F path=/etc/shadow -F auid>=1000 -F auid!=-1 -F key=user-modify
-a always,exit -F arch=b64 -S ... -F path=/etc/group -F perm=wa -F auid>=1000 -F auid!=-1 -F key=group-modify
-a always,exit -F arch=b64 -S execve -F path=/usr/sbin/unix_chkpwd -F perm=x -F auid>=1000 -F auid!=-1 -F key=special-config-changes
```

**Audit Log Partition:** `/var/log/audit` on dedicated LVM volume (`vg0-var_log_audit`) within LUKS-encrypted container.

**Result:** PASS — auditd active, enabled at boot, CUI audit rules loaded, audit logs on separate encrypted partition.

---

## 6. SSH Hardening — Rocky Linux VM

**Control:** NIST SP 800-171 § 3.1.12, 3.5.2 / AC-17, IA-2

**Command:** `sudo sshd -T` (effective configuration)
**Date:** April 10, 2026

```
port 22
permitrootlogin no
passwordauthentication no
pubkeyauthentication yes
challengeresponseauthentication no (default)
clientaliveinterval 300
clientalivecountmax 0
x11forwarding yes
loglevel INFO
```

**Key Security Settings:**
- `PermitRootLogin no` — root cannot log in via SSH
- `PasswordAuthentication no` — password-based SSH disabled; keys required
- `ClientAliveInterval 300` — sessions disconnected after 5 minutes idle
- `ClientAliveCountMax 0` — no reconnection attempts; immediate disconnect

**MFA Status:** NOT YET DEPLOYED — POA&M-001, target 2026-07-01
- When deployed: `AuthenticationMethods publickey,keyboard-interactive` will be added
- TOTP via pam_google_authenticator planned

**Result:** PASS (within current scope) — Root login disabled, password auth disabled, key-only access enforced, session timeout active. MFA POA&M tracked.

---

## 7. pf Firewall — macOS Host

**Control:** NIST SP 800-171 § 3.13.1 / SC-7 (Boundary Protection)

**Command:** `sudo pfctl -si`
**Date:** April 10, 2026

```
Status: Enabled for 2 days 03:45:59           Debug: Urgent

State Table                          Total             Rate
  current entries                      170
  searches                        16,513,786          88.6/s
```

**Result:** PASS — pf firewall enabled on macOS host for 2+ days. Active state table with 170 current connections.

---

## 8. NTP Synchronization — Rocky Linux VM

**Control:** NIST SP 800-171 § 3.3.7 / AU-8 (Time Stamps)

**Command:** `chronyc tracking`
**Date:** April 10, 2026

```
Reference ID    : 1796297A (s2-b.time.mci1.us.rozint.net)
Stratum         : 3
Ref time (UTC)  : Fri Apr 10 18:47:52 2026
System time     : 0.001618602 seconds fast of NTP time
Last offset     : +0.000016564 seconds
```

**Result:** PASS — Time synchronized to NTP pool, stratum 3, offset < 2ms. Timestamps in audit records are accurate.

---

## 9. Automatic Security Updates — Rocky Linux VM

**Control:** NIST SP 800-171 § 3.14.1 / SI-2 (Flaw Remediation)

**Command:** `systemctl is-active dnf-automatic.timer`
**Date:** April 10, 2026

```
active
```

**Result:** PASS — `dnf-automatic.timer` active; security updates applied automatically on Rocky Linux VM.

---

## 10. OS Versions

| System | OS | Kernel |
|--------|----|-|
| services.diwai.org | Rocky Linux 9.7 (Blue Onyx) | 5.14.0-611.41.1.el9_7.aarch64 |
| securemac.diwai.org | macOS Tahoe | Darwin 25.4.0 |

---

## Summary

| Control | Requirement | Status |
|---------|-------------|--------|
| FIPS 140-2 mode | Enabled on Rocky Linux VM | ✅ PASS |
| SELinux enforcing | Enforcing on Rocky Linux VM | ✅ PASS |
| LUKS encryption (VM) | AES-256-XTS, all partitions | ✅ PASS |
| FileVault (macOS) | Enabled, M4 Secure Enclave | ✅ PASS |
| auditd / CUI audit rules | Active, enabled at boot | ✅ PASS |
| Root SSH login | Disabled | ✅ PASS |
| Password SSH | Disabled | ✅ PASS |
| SSH session timeout | 300s idle → disconnect | ✅ PASS |
| pf firewall | Enabled 2+ days | ✅ PASS |
| NTP synchronization | Synced, offset <2ms | ✅ PASS |
| Auto security updates | dnf-automatic.timer active | ✅ PASS |
| MFA (SSH + TOTP) | **NOT MET — POA&M-001** | ⚠️ Tracked |

---

**Verified By:** Donald E. Shannon, ISSO
**Date:** April 10, 2026
**Next Verification:** July 2026 (quarterly)

---

**CLASSIFICATION:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)
