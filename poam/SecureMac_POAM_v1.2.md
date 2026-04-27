# PLAN OF ACTION AND MILESTONES (POA&M)
## SecureMac Reference System — diwai.org

**Document Control:**

| Field | Value |
|-------|-------|
| **System Name** | SecureMac — diwai.org CyberInABox Reference System #2 |
| **System Owner** | Donald Shannon |
| **Organization** | diwai.org (Do It With AI) |
| **Classification** | Controlled Unclassified Information (CUI) |
| **Version** | 1.2 |
| **Date** | April 26, 2026 |
| **SSP Reference** | System_Security_Plan_v1.2.md (v1.2, 2026-04-23) |
| **SPRS Score** | 101 / 110 |
| **Compliance Framework** | NIST SP 800-171 Rev 2 / FIPS 140-2 |

---

## DOCUMENT REVISION HISTORY

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-24 | D. Shannon | Extracted from SSP v1.2 as standalone document. All items current as of extraction date. |
| 1.1 | 2026-04-24 | D. Shannon | Added POAM-010 (Recovery Lock) identified during mSCP compliance scan of macOS host. Added risk-accepted items from mSCP scan (POAM-011 through POAM-013). Updated summary dashboard. |
| 1.2 | 2026-04-26 | D. Shannon | Closed POAM-007: Ollama AI inference confirmed deployed (v0.21.2 via Homebrew, Metal GPU, localhost:11434; 4 models installed). Open Web UI also deployed (pip venv, port 3000, since 2026-04-14). Summary dashboard updated: Open 7→6, Closed 1→2. |

---

## PURPOSE

This Plan of Action and Milestones (POA&M) documents all open, closed, deferred, and risk-accepted security findings for the SecureMac Reference System. It is maintained as a living document and reviewed quarterly in conjunction with the SSP. Findings are tracked from identification through remediation or formal risk acceptance.

**Relationship to SSP:** The SSP (System_Security_Plan_v1.0.md) references this document as the authoritative POA&M. The SPRS scorecard in the SSP reflects the current status of items listed here.

---

## POA&M ITEMS

| POA&M ID | Control | Finding | Status | Opened | Target Date |
|----------|---------|---------|--------|--------|-------------|
| SecureMac-POAM-001 | 3.5.3 / 3.7.5 | Multi-factor authentication not implemented (SSH key only) | **Closed** | 2026-04-10 | 2026-04-10 |
| SecureMac-POAM-002 | 3.11.1 | Formal risk assessment not conducted | Open | 2026-04-10 | 2026-07-01 |
| SecureMac-POAM-003 | 3.2.1 / 3.2.2 | Security awareness training not formally documented | Open | 2026-04-10 | 2026-07-01 |
| SecureMac-POAM-004 | 3.6.3 | Incident response tabletop exercise not conducted | Open | 2026-04-10 | 2026-09-30 |
| SecureMac-POAM-005 | 3.14.2 / 3.14.4 | ClamAV non-operational (FIPS incompatibility) | Risk Accepted | 2026-04-10 | 2026-10-01 |
| SecureMac-POAM-006 | — | Kingston IronKey secure config vault not configured | Open | 2026-04-10 | 2026-06-30 |
| SecureMac-POAM-007 | — | Ollama AI inference not yet deployed | **Closed** | 2026-04-10 | 2026-04-26 |
| SecureMac-POAM-008 | — | SuperDuper! bootable clone deferred (Tahoe beta bug) | Deferred | 2026-04-10 | When fixed |
| SecureMac-POAM-009 | 3.5.3 / 3.7.5 | MFA partial after lockout recovery (2026-04-14): smartcard enforcement disabled; SSH to VM uses RSA key only. Requires Slot 9A regeneration, re-pairing, SSH MFA restoration, and enforcement enable. | Open | 2026-04-23 | 2026-05-31 |
| SecureMac-POAM-010 | 3.1.5 / AC-6 | Recovery Lock not enabled on macOS host (M4 Pro Apple Silicon). mSCP rule os_recovery_lock_enable requires MDM SetRecoveryLock command — cannot be set on standalone Mac without MDM. Recovery Mode and Startup Manager are accessible without a password. | Open | 2026-04-24 | 2026-09-30 |
| SecureMac-POAM-011 | 3.13.6 / SC-7 | os_firewall_default_deny_require — macOS app firewall not in block-all mode. Compensating control: pf packet filter enforces default-deny at perimeter. | Risk Accepted | 2026-04-24 | 2026-10-01 |
| SecureMac-POAM-012 | 3.4.2 / CM-6 | os_gatekeeper_enable / system_settings_gatekeeper_identified_developers_allowed — Gatekeeper IS enabled (spctl assessments enabled); mSCP check fails due to MDM enforcement verification gap on standalone Mac. No remediation required. | Risk Accepted | 2026-04-24 | 2026-10-01 |
| SecureMac-POAM-013 | 3.5.3 / IA-2 | Four mSCP screensaver enforcement rules deferred pending YubiKey Slot 9A regeneration and smartcard enforcement (POAM-009). Screensaver lock without a reliable unlock mechanism creates lockout risk. | Deferred → POAM-009 | 2026-04-24 | 2026-05-31 |

---

## ITEM DETAIL

### SecureMac-POAM-001 — MFA Not Implemented
**Control:** NIST SP 800-171 § 3.5.3, 3.7.5  
**Finding:** No multi-factor authentication in place; remote access used SSH RSA key only.  
**Status:** **Closed 2026-04-10**  
**Resolution:** YubiKey 5C Nano FIPS FIDO2-SK deployed for SSH to services.diwai.org. SPRS +5 recovered.  
**Note:** FIDO2-SK implementation subsequently rolled back (see POAM-009); MFA re-implemented via PIV.  
**Evidence:** DIWAI-EV-MFA-001 v1.0 (superseded by v2.0)

---

### SecureMac-POAM-002 — Formal Risk Assessment Not Conducted
**Control:** NIST SP 800-171 § 3.11.1  
**Finding:** No formal risk assessment has been conducted. The SSP documents the security posture but does not constitute a formal risk assessment per NIST methodology.  
**Status:** Open  
**SPRS Impact:** -3  
**Target:** 2026-07-01  
**Remediation plan:** Conduct formal risk assessment using NIST SP 800-30 methodology. Document threat sources, likelihood, impact, and risk level for each identified threat. Produce formal Risk Assessment Report.

---

### SecureMac-POAM-003 — Security Awareness Training Not Documented
**Control:** NIST SP 800-171 § 3.2.1, 3.2.2  
**Finding:** No formal security awareness training program documented for users or privileged users. System is a single-administrator reference build; practical knowledge demonstrated but no training records exist.  
**Status:** Open  
**SPRS Impact:** -2 (training gap, not reflected in technical SPRS score)  
**Target:** 2026-07-01  
**Remediation plan:** Develop and document security awareness training program appropriate for VSB audience. Record administrator training completion. Create annual training schedule.

---

### SecureMac-POAM-004 — IR Tabletop Exercise Not Conducted
**Control:** NIST SP 800-171 § 3.6.3  
**Finding:** No formal incident response tabletop exercise has been conducted.  
**Status:** Open  
**SPRS Impact:** -1  
**Target:** 2026-09-30  
**Remediation plan:** Conduct tabletop exercise based on documented IR procedures. Test at least two scenarios (e.g., ransomware, unauthorized access). Document outcomes and lessons learned.

---

### SecureMac-POAM-005 — ClamAV Non-Operational (FIPS Incompatibility)
**Control:** NIST SP 800-171 § 3.14.2, 3.14.4  
**Finding:** ClamAV 1.4.3 cannot verify database signatures under OpenSSL 3 FIPS mode. Error: "Can't allocate memory" — a misleading message masking a cryptographic algorithm incompatibility with bytecode verification.  
**Status:** Risk Accepted  
**SPRS Impact:** 0 (compensating controls adequately mitigate; risk level assessed as LOW with compensating controls)  
**Review Date:** 2026-10-01  
**Compensating controls:**

| Control | Implementation |
|---------|---------------|
| Network IDS | Suricata 7.0.13 — 49,521 ET rules, real-time traffic inspection |
| File Integrity Monitoring | Wazuh syscheck on /etc, /bin, /sbin, /usr/bin, /usr/sbin, /boot |
| SELinux | Enforcing mode — prevents unauthorized code execution |
| USBGuard | Blocks unauthorized USB media on both Mac and VM |
| Audit Logging | auditd + Wazuh — detects anomalous process execution |
| Patch Management | Weekly updates eliminate known-vulnerable packages |

**Resolution path:** Evaluate FIPS-compatible AV solution in FY2026 budget cycle. Reassess if ClamAV releases a FIPS-compatible version.  
**Evidence:** `Evidence/Risk_Acceptance_ClamAV_FIPS_Incompatibility.md`

---

### SecureMac-POAM-006 — Kingston IronKey Vault Not Configured
**Control:** CM / MP (configuration and media protection)  
**Finding:** Kingston IronKey 64GB hardware-encrypted USB drive has not been configured as the secure configuration vault for certificates, keys, and VPN profile.  
**Status:** Open  
**Target:** 2026-06-30  
**Remediation plan:** Configure IronKey with hardware AES-256 encryption. Store: TLS private key, VPN PKI, LUKS passphrase backup, SSH keys, and YubiKey PIN. Document in system state.

---

### SecureMac-POAM-007 — Ollama AI Inference Not Deployed
**Control:** Configuration management / system completeness  
**Finding:** Ollama + local AI inference (planned for macOS host, Metal GPU) not yet installed or configured.  
**Status:** **Closed 2026-04-26**  
**Resolution:** Ollama v0.21.2 confirmed deployed via Homebrew, running as a LaunchAgent on localhost:11434 with Metal GPU acceleration. Four models installed: codestral:latest (12 GB), mistral:latest (4.4 GB), nomic-embed-text:latest (274 MB), all-minilm:latest (45 MB). Open Web UI deployed separately (pip venv at /opt/local/open-webui-venv/, port 3000, active since 2026-04-14). AI governance controls documented in SBOM v2.1 (local-only inference, no CUI processing, human oversight required). Live-state capture evidence: RS2_Live_State_20260426_101158.txt.  
**Closed:** 2026-04-26  
**Evidence:** SBOM v2.1 AI Inference section; RS2_Live_State_20260426_101158.txt

---

### SecureMac-POAM-008 — SuperDuper! Bootable Clone Deferred
**Control:** CP / backup and recovery  
**Finding:** SuperDuper! bootable clone of macOS host cannot be completed due to a known bug in macOS Tahoe beta affecting bootable clone creation.  
**Status:** Deferred  
**Target:** When Tahoe / SuperDuper! bug resolved  
**Remediation plan:** Monitor SuperDuper! release notes and macOS Tahoe updates. Complete bootable clone to Sabrent 250GB SSD when bug is fixed. Test boot from clone before considering resolved.

---

### SecureMac-POAM-009 — MFA Partial (Post-Lockout Recovery)
**Control:** NIST SP 800-171 § 3.5.3, 3.7.5  
**Finding:** Following a lockout incident on 2026-04-14 (caused by third-party PAM module with VM network dependency) and recovery via Time Machine rollback, MFA was re-implemented using native macOS CryptoTokenKit PIV (Slot 9C). Current gaps:
1. Smart card enforcement not enabled — password fallback active
2. SSH to services.diwai.org uses RSA key only (FIDO2-SK key file lost in rollback)
3. YubiKey Slot 9A has incorrect policies (PIN:NEVER, Touch:ALWAYS) — incompatible with rack-mounted key  

**Status:** Open  
**Opened:** 2026-04-23  
**SPRS Impact:** -5  
**Target:** 2026-05-31  
**Evidence:** DIWAI-EV-MFA-001 v2.0  

**Remediation steps (in order):**

| Step | Action | Prerequisite |
|------|--------|--------------|
| 1 | Regenerate Slot 9A (`--pin-policy once --touch-policy never`) | diwai.org CA online (VM .10) |
| 2 | Issue cert from diwai.org CA; import to Slot 9A; re-pair `dshannon` | Step 1 |
| 3 | Unpair Slot 9C cert | Step 2 |
| 4 | Optionally pair Slot 9A cert to `sysadmin` (break-glass Option B) | Step 2 |
| 5 | Restore SSH MFA to services.diwai.org (`ssh-keygen -K` to recover FIDO2-SK from YubiKey) | Step 2 |
| 6 | Enable enforcement: `sudo defaults write /Library/Preferences/com.apple.security.smartcard enforceSmartCard -bool true` | Steps 1–5 tested |

---

### SecureMac-POAM-010 — Recovery Lock Not Enabled
**Control:** NIST SP 800-171 § 3.1.5 / NIST AC-6 / CCE-95277-0  
**Finding:** macOS Recovery Lock is not set on the M4 Pro host. Without Recovery Lock, an attacker with physical access can boot into Recovery Mode, access Startup Manager, or use single-user mode tools to bypass OS-level security controls.  
**Status:** Open  
**Opened:** 2026-04-24  
**SPRS Impact:** 0 (not a scored NIST 800-171 deficiency — documented as defense-in-depth gap)  
**Target:** 2026-09-30  
**Constraint:** Recovery Lock (`SetRecoveryLock` MDM command) is an Apple Silicon-only feature that can only be set via MDM. The `profiles install` CLI and Apple Configurator 2 (cfgutil) do not support this command for Mac. Physical security of the locked rack enclosure is the primary compensating control.  
**Remediation path:** Evaluate lightweight MDM options for standalone VSB deployment (e.g., Apple Business Manager + free MDM tier, or Micromdm open-source). Once MDM is enrolled, issue `SetRecoveryLock` command. Document as SSP architectural enhancement.  
**Compensating control:** Mac mini is in a locked rack enclosure with physical access limited to system owner. PE-2/PE-3 physical security controls provide compensating protection against the physical attack vector Recovery Lock is designed to address.

---

### SecureMac-POAM-011 — App Firewall Block-All Mode (Risk Accepted)
**Control:** NIST SP 800-171 § 3.13.6 / SC-7  
**Finding:** mSCP rule `os_firewall_default_deny_require` checks that the macOS application firewall is in "block all incoming connections" mode. The app firewall is enabled and stealth mode is on, but block-all is not set.  
**Status:** Risk Accepted  
**Risk Level:** LOW (compensating control in place)  
**Compensating control:** `pf` packet filter on macOS host enforces default-deny (`block all`) at the network layer. All inbound traffic is explicitly permitted by rule only. The macOS app firewall operates at the application layer above pf — pf provides equivalent or stronger boundary protection.  
**Review Date:** 2026-10-01

---

### SecureMac-POAM-012 — Gatekeeper MDM Enforcement Gap (Risk Accepted)
**Control:** NIST SP 800-171 § 3.4.2 / CM-6  
**Finding:** mSCP rules `os_gatekeeper_enable` and `system_settings_gatekeeper_identified_developers_allowed` report failures. Gatekeeper is confirmed enabled (`spctl --status` = "assessments enabled", "developer id enabled"). Failures reflect the absence of MDM enforcement verification, not actual non-compliance.  
**Status:** Risk Accepted  
**Risk Level:** LOW — setting is correct; only MDM-enforcement attestation is absent  
**Verified state:** `spctl --status` confirms Gatekeeper operational. `com.apple.systempolicy.managed` and `com.apple.systempolicy.control` profiles installed.  
**Review Date:** 2026-10-01

---

### SecureMac-POAM-013 — Screensaver Enforcement Deferred
**Control:** NIST SP 800-171 § 3.5.3 / IA-2  
**Finding:** Four mSCP screensaver rules fail: `os_screensaver_loginwindow_enforce`, `system_settings_screensaver_ask_for_password_delay_enforce`, `system_settings_screensaver_password_enforce`, `system_settings_screensaver_timeout_enforce`. Screensaver settings are configured but MDM enforcement profiles are not active for user-level enforcement.  
**Status:** Deferred — blocked by POAM-009  
**Rationale:** Enabling screensaver lock requires a reliable unlock mechanism. YubiKey smartcard enforcement (POAM-009) is not yet enabled — enforcing screensaver lock before enforcement is tested creates lockout risk (repeat of 2026-04-14 incident). Screensaver will be enabled and validated as part of POAM-009 closure.  
**Target:** 2026-05-31 (aligned with POAM-009)

---

## SUMMARY DASHBOARD

| Status | Count | POAM IDs |
|--------|-------|----------|
| Open | 6 | 002, 003, 004, 006, 009, 010 |
| Closed | 2 | 001, 007 |
| Risk Accepted | 3 | 005, 011, 012 |
| Deferred | 2 | 008, 013 |
| **Total** | **13** | |

**SPRS impact from open technical items:** -9 (3.5.3: -5, 3.11.1: -3, 3.6.3: -1)  
**Score path to 110:** Close POAM-009 (+5) → 106; close POAM-002 (+3) → 109; close POAM-004 (+1) → **110/110**  
**Note:** POAM-010 (Recovery Lock) carries no SPRS point deduction — it is a defense-in-depth gap with physical compensating controls documented above.

---

## DOCUMENT CONTROL

**Classification:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)  
**Distribution:** Official Use Only — Need to Know Basis  
**Retention:** Current + 3 years  
**Next Review:** 2026-07-01 (Quarterly, aligned with SSP review)  
**Local Copy:** `~/Documents/SecureMac Project Docs/SecureMac_POAM_v1.0.md`  
**NAS Copy:** `DataStore:/Cyberinabox/Secure_Mac/`  

---

**END OF POA&M v1.2**

*This Plan of Action and Milestones supports NIST SP 800-171 Rev 2 compliance for the SecureMac Reference System (diwai.org). Maintained as a standalone document; referenced by SSP v1.2.*
