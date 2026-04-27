# OpenSCAP Compliance Report Reference

**Document ID:** DIWAI-EV-SCAP-001
**Version:** 2.0
**Date:** April 24, 2026
**Prepared By:** Donald E. Shannon, ISSO
**System:** services.diwai.org (Rocky Linux 9.7 VM)
**Classification:** CUI

---

## Purpose

This document provides reference information for OpenSCAP compliance scanning on the SecureMac Production Network (SPN), linking to existing scan results and documenting scanning procedures. It supports NIST SP 800-171 controls 3.11.2 (vulnerability scanning), 3.11.3 (remediation), and CMMC Level 2 RA-5 requirements.

---

## 1. Scanning Tool Information

**Tool:** OpenSCAP (oscap-scanner) with SCAP Security Guide (SSG)
**Profile:** NIST 800-171 CUI — `xccdf_org.ssgproject.content_profile_cui`
**Content:** `/usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml` (Rocky Linux 9)
**System:** services.diwai.org (Rocky Linux 9.7, kernel 5.14.0-611.45.1.el9_7.aarch64)

**Installed versions:**
- openscap: 1.3.13-1.el9_7.rocky.0.1.aarch64
- openscap-scanner: 1.3.13-1.el9_7.rocky.0.1.aarch64
- scap-security-guide: 0.1.80-1.el9_7.rocky.1.2.noarch

---

## 2. Scan History

| Scan Date | Kernel | Pass | Fail | Error | Report File | Notes |
|-----------|--------|------|------|-------|-------------|-------|
| 2026-04-09 | 5.14.0-611.41.1 | 102 | 0 | 0 | oscap-report-2.html (~/diwai/) | Baseline scan at initial deployment |
| 2026-04-24 | 5.14.0-611.45.1 | 102 | 0 | 0 | oscap-20260424.html (Evidence/) | Quarterly scan — post YubiKey PIV deployment |

**Current report:** `Evidence/oscap-20260424.html` (1.5 MB)  
**Result:** 102 pass / 0 fail / 0 errors — **FULLY COMPLIANT**

---

## 3. Quarterly Scan Procedure

**Frequency:** Quarterly (target: first week of April, July, October, January)
**Last scan:** April 24, 2026
**Next scan due:** July 2026

**Scan Command:**
```bash
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cui \
  --results /root/oscap-$(date +%Y%m%d).xml \
  --report /root/oscap-$(date +%Y%m%d).html \
  /usr/share/xml/scap/ssg/content/ssg-rl9-ds.xml
```

**Copy to evidence archive (from macOS host):**
```bash
scp -i ~/.ssh/diwai_rsa \
  dshannon@10.10.1.10:/root/oscap-$(date +%Y%m%d).html \
  "/Users/dshannon/Documents/SecureMac Project Docs/Evidence/OpenSCAP/oscap-$(date +%Y%m%d).html"

# Also copy to DataStore
cp "/Users/dshannon/Documents/SecureMac Project Docs/Evidence/OpenSCAP/oscap-$(date +%Y%m%d).html" \
  "/Volumes/Cyberinabox/Secure_Mac/oscap-$(date +%Y%m%d).html"
```

---

## 4. Known Finding Categories

Based on the initial assessment and SPRS scoring (103/110), the following categories of findings exist:

### 4.1 MFA Not Implemented (3.5.3) — SPRS -5 points
- **Finding:** SSH public key only; TOTP second factor not deployed
- **POA&M:** POA&M-001, target 2026-07-01
- **Expected OpenSCAP findings:** Rules related to PAM MFA configuration will fail

### 4.2 Formal Risk Assessment Not Completed (3.11.1) — SPRS -3 points
- **Finding:** No formal documented risk assessment completed
- **POA&M:** POA&M-002, target 2026-04-30
- **Expected OpenSCAP findings:** Administrative/procedural; may not appear in automated scan

### 4.3 IR Tabletop Exercise Not Conducted (3.6.3) — SPRS -1 point
- **Finding:** No tabletop exercise conducted
- **POA&M:** POA&M-003, target 2026-06-30
- **Expected OpenSCAP findings:** Administrative/procedural; does not appear in automated scan

### 4.4 ClamAV FIPS Incompatibility
- **Finding:** ClamAV bytecode verification disabled due to FIPS/OpenSSL incompatibility
- **Status:** Accepted risk — documented in Risk Acceptance memo
- **Compensating controls:** Wazuh FIM, SELinux, auditd, pf firewall

---

## 5. Expected Passing Controls (from initial scan)

Based on system configuration verified on April 10, 2026:

| SCAP Rule Category | Expected Result |
|--------------------|----------------|
| FIPS mode enabled | PASS |
| SELinux enforcing | PASS |
| SSH PermitRootLogin no | PASS |
| SSH PasswordAuthentication no | PASS |
| auditd enabled | PASS |
| auditd CUI rules loaded | PASS |
| LUKS encryption | PASS |
| Firewall enabled | PASS |
| NTP configured (chrony) | PASS |
| Separate /var/log/audit partition | PASS |
| dnf-automatic security updates | PASS |
| Session timeout (SSH) | PASS |
| No unnecessary services | PASS |

---

## 6. Remediation Tracking

OpenSCAP failures are tracked via the POA&M process:
- Location: `~/Documents/SecureMac Project Docs/` (POA&M document — to be created)
- Each failing rule generates a POA&M item with target remediation date
- Remediation timelines per DIWAI-RA-001:
  - Critical (CVSS 9.0-10.0): 7 days
  - High (CVSS 7.0-8.9): 30 days
  - Medium (CVSS 4.0-6.9): 90 days

---

## 7. Evidence Retention

| Artifact | Retention | Location |
|----------|-----------|----------|
| OpenSCAP HTML report | 3 years | Evidence/OpenSCAP/ + DataStore |
| OpenSCAP XML/ARF | 3 years | Evidence/OpenSCAP/ |
| Scan command log | 3 years | Evidence/OpenSCAP/ |

---

## 8. Future Scan Schedule

| Quarter | Target Date | Notes |
|---------|-------------|-------|
| Q2 2026 | July 2026 | First quarterly re-scan post-initial |
| Q3 2026 | October 2026 | Post-MFA deployment (expect POA&M-001 resolved) |
| Q4 2026 | January 2027 | Annual review cycle |
| Q1 2027 | April 2027 | Annual |

---

**Prepared By:** Donald E. Shannon, ISSO
**Date:** April 24, 2026

---

**CLASSIFICATION:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)
