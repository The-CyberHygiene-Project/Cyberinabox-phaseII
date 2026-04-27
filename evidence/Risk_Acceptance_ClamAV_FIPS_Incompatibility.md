# Risk Acceptance Memorandum — ClamAV FIPS Incompatibility

**Document ID:** DIWAI-RA-MEMO-001
**Version:** 1.0
**Date:** April 10, 2026
**Prepared By:** Donald E. Shannon, ISSO
**Approved By:** Donald E. Shannon, System Owner
**System:** services.diwai.org (Rocky Linux 9.7 VM)
**Classification:** CUI

---

## 1. Risk Description

**Risk Title:** ClamAV Bytecode Verification Disabled Due to FIPS 140-2 / OpenSSL 3 Incompatibility

**Risk ID:** RISK-2026-004

**Affected System:** services.diwai.org (Rocky Linux 9.7, FIPS 140-2 mode enabled)

**ClamAV Version:** 1.4.3

**Root Cause:**

ClamAV 1.4.3 uses OpenSSL for cryptographic operations including bytecode signature verification. Under FIPS 140-2 mode (OpenSSL 3.x with FIPS provider enabled on Rocky Linux 9.7), certain cryptographic algorithms required by ClamAV's bytecode verification process are not available as FIPS-approved primitives. Specifically, the FIPS provider rejects non-FIPS algorithm requests even when these operations are internal to ClamAV's signature verification pipeline.

**Symptom:**

When bytecode verification is enabled, freshclam downloads the `bytecode.cvd` signature database file, but ClamAV fails with:

```
ERROR: LibClamAV Error: Can't allocate memory
```

This error occurs during the bytecode verification step and is caused by OpenSSL refusing to allocate memory for non-FIPS algorithm contexts, not an actual memory shortage. The error prevents both freshclam and clamd from functioning correctly.

**Technical Detail:**

The incompatibility is a known upstream issue between ClamAV's use of OpenSSL and Red Hat/Rocky Linux's strict FIPS provider enforcement in OpenSSL 3.x. ClamAV upstream has not yet provided a FIPS-compatible build configuration for all verification operations.

---

## 2. Risk Assessment

**Threat:** Malware that could be detected by ClamAV's bytecode-analyzed signatures escapes detection

**Likelihood:** Low

- Bytecode signatures augment (not replace) the primary CVD signature database
- Primary virus signatures (main.cvd + daily.cvd) remain fully operational
- The Rocky Linux VM has limited attack surface (no direct user-accessible file uploads; services face internal LAN only, not public internet)
- FIPS mode itself provides strong cryptographic protection against many attack vectors

**Impact:** Low-Medium

- Some advanced/behavioral malware signatures unavailable
- No complete loss of antivirus capability — signature-based scanning remains active
- CUI files on the VM are protected by LUKS encryption, SELinux, and auditd
- The VM is not a general-purpose workstation; attack paths are narrow

**Risk Score:** 3 (Likelihood Low × Impact Medium = 3)

**Residual Risk Level:** Low

---

## 3. Current Configuration

The following configuration changes have been made to restore ClamAV functionality:

**`/etc/clamd.d/scan.conf`:**
```
Bytecode no
BytecodeUnsigned no
LogFile /var/log/clamd.scan
LogTime yes
```

**`/etc/systemd/system/clamd@scan.service.d/wait-for-db.conf`:**
```ini
[Unit]
ConditionPathExists=/var/lib/clamav/main.cvd
ConditionPathExists=/var/lib/clamav/daily.cvd

[Service]
Restart=on-failure
RestartSec=60
```

**`/etc/systemd/system/clamav-freshclam.service.d/tmpdir.conf`:**
```ini
[Service]
Environment=TMPDIR=/var/lib/clamav/tmp
```

**Result:** With bytecode disabled, freshclam successfully downloads and verifies main.cvd and daily.cvd using standard SHA-256 verification (FIPS-approved). clamd will start automatically when both databases are present.

**freshclam Service Status:** Active (running) — confirmed April 10, 2026.

---

## 4. Compensating Controls

The following compensating controls are in place and collectively provide equivalent or superior protection:

### 4.1 Wazuh File Integrity Monitoring (FIM)

- Wazuh agent monitors SHA-256 hashes of all files in `/etc/`, `/boot/`, `/usr/bin/`, `/usr/sbin/`, `/usr/local/bin/`, `/usr/local/sbin/`
- Any unauthorized file modification generates an immediate alert
- 12-hour scan interval with real-time modification detection
- **Addresses:** Detection of malware that modifies system files after initial infection

### 4.2 SELinux Enforcing Mode

- SELinux type enforcement prevents processes from accessing resources outside their defined security context
- Malware that gains a foothold in a confined process cannot escalate to access CUI or system files without triggering SELinux denials
- SELinux denials logged to auditd for immediate review
- **Addresses:** Lateral movement and privilege escalation post-infection

### 4.3 auditd System Call Auditing

- CUI-profile audit rules monitor all file writes to sensitive directories
- All privilege escalation (sudo) events captured
- Unauthorized command execution detected
- **Addresses:** Detection of malicious activity through audit trail analysis

### 4.4 pf Firewall (macOS Host)

- Default-deny inbound policy on WAN
- Only explicitly authorized ports open (443, 993, 587, 1194/UDP)
- Prevents most malware delivery mechanisms that require inbound connections
- **Addresses:** Reduction of malware delivery attack surface

### 4.5 ClamAV Signature-Based Scanning (Remains Active)

- Primary signature databases (main.cvd, daily.cvd) fully operational
- Daily updates via freshclam
- Detection of known virus, trojan, and malware families via hash and pattern matching
- **Addresses:** Broad-spectrum known malware detection

### 4.6 Restricted Attack Surface

- Rocky Linux VM has no graphical interface (no browser, no email client)
- No user file upload capability (no Samba file server, no writable FTP)
- Mail is transit-only (Postfix/Dovecot); files arriving via email can be scanned by clamd on demand
- Services face internal LAN (10.10.1.0/24) only — not public internet
- **Addresses:** Significantly reduces the paths by which malware could be introduced

### 4.7 Network Monitoring (Planned)

- Suricata IDS on Rocky Linux VM or macOS pf: network-level malware detection
- When deployed, provides behavioral network signature matching as additional compensating control

---

## 5. Monitoring and Review

**Ongoing monitoring of this accepted risk:**

- Monthly: Verify ClamAV freshclam and clamd status
- Quarterly: Review Wazuh FIM alerts for any anomalies that compensating controls should catch
- Semi-annual: Check ClamAV upstream and Red Hat release notes for FIPS compatibility fixes

**Expected resolution:**

This incompatibility is expected to be resolved in a future ClamAV or OpenSSL update. When a FIPS-compatible build becomes available for Rocky Linux 9.x:

1. Re-enable bytecode in `/etc/clamd.d/scan.conf`: change `Bytecode no` → `Bytecode yes`
2. Remove `BytecodeUnsigned no` line
3. Restart freshclam and clamd
4. Verify successful startup with bytecode databases
5. Update this risk acceptance memo to reflect closure
6. Update POA&M status to Closed

---

## 6. Risk Acceptance Decision

**Based on the above analysis:**

- The risk of operating ClamAV without bytecode verification is **Low** given the compensating controls in place
- The alternative (disabling FIPS mode to enable bytecode) would introduce a **High** risk by violating NIST SP 800-171 § 3.13.8 and CMMC Level 2 cryptographic requirements
- The risk of operating ClamAV without bytecode is **substantially lower** than the risk of disabling FIPS mode

**Decision:** Accept the risk of ClamAV bytecode verification being disabled on services.diwai.org while FIPS 140-2 mode is enabled, contingent on the compensating controls listed in Section 4 remaining active.

**Acceptance Conditions:**
1. Wazuh FIM must remain active
2. SELinux must remain in enforcing mode
3. auditd must remain active
4. pf firewall must remain enabled
5. ClamAV signature-based scanning (main.cvd + daily.cvd) must remain operational
6. This acceptance reviewed quarterly or upon ClamAV/OpenSSL version updates

---

## 7. Related Documents

- System Security Plan v1.0 — Section 3.14 (SI-3 Malicious Code Protection)
- Risk Management Policy (DIWAI-RA-001) — Risk Register entry RISK-2026-004
- System and Information Integrity Policy (DIWAI-SI-001) — Section 3 (Malicious Code Protection)
- FIPS and Encryption Verification (DIWAI-EV-FIPS-001)

---

## 8. Approval

**Prepared By:**
Name: Donald E. Shannon, ISSO
Signature: /s/ Donald E. Shannon
Date: April 10, 2026

**Approved By:**
Name: Donald E. Shannon, System Owner
Signature: /s/ Donald E. Shannon
Date: April 10, 2026

**Risk Acceptance Authority:** System Owner

**Next Review Date:** July 10, 2026 (quarterly review)

---

**CLASSIFICATION:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)
**DISTRIBUTION:** Official Use Only - Need to Know Basis
**STATUS:** APPROVED — RISK ACCEPTED
