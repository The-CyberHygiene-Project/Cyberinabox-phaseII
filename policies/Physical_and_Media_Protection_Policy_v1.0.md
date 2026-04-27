# Physical and Media Protection Policy

**Document ID:** DIWAI-PE-MP-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** CUI

---

## 1. Purpose

This policy establishes diwai.org (Do It With AI) requirements for physical security and media protection on the SecureMac Production Network (SPN). It ensures SPN hardware is physically secured and CUI media is properly controlled throughout its lifecycle, in compliance with NIST SP 800-171 Rev 2 (PE-1 through PE-20, MP-1 through MP-8) and CMMC Level 2.

---

## 2. Scope

This policy applies to:

- **All SPN Hardware:**
  - Mac mini M4 Pro (securemac.diwai.org) — primary appliance
  - SABRENT USB SSD (external backup drive)
  - Any additional USB drives used with SPN systems
  - Network cabling and switches (10.10.1.0/24 LAN)

- **All SPN Media:**
  - Internal NVMe SSD (Mac mini internal storage — FileVault encrypted)
  - Rocky Linux VM virtual disk (LUKS encrypted within UTM bundle)
  - USB storage devices
  - DataStore NAS (10.10.1.100 — SMB shares on LAN)
  - Shannon_Home NAS (Wi-Fi connected — secondary backup only)
  - Printed CUI documents

- **All Personnel:** Donald E. Shannon and any contractors with physical access

---

## 3. Physical Protection Policy

### 3.1 Physical Access Authorizations (PE-2)

**Authorized Physical Access:**
- Donald E. Shannon — unlimited access (System Owner/ISSO)
- Contractors — escorted access only, logged, limited to duration of work

**Physical Access Control:**
- Mac mini housed in dedicated home office
- Office secured when unattended (door locked)
- No unauthorized individuals permitted access to SPN hardware

### 3.2 Physical Access Control (PE-3)

**Entry Controls:**
- Home office door locked when not occupied
- Mac mini not accessible from public areas
- Physical access log maintained for any contractor or external party access

**Visitor Procedures:**
- Visitors escorted at all times in server area
- Visitor access logged: Name, purpose, date, time in/out

### 3.3 Access Control for Output Devices (PE-5)

- Printer in secure area only
- CUI documents printed only when operationally required
- Printed CUI not left unattended
- Printer not networked to SPN (standalone or air-gapped)

### 3.4 Monitoring Physical Access (PE-6)

- ISSO aware of all physical access to Mac mini and SPN hardware
- No unescorted access by contractors or third parties
- Physical access anomalies reported to ISSO immediately

### 3.5 Power Equipment and Cabling (PE-9)

- UPS (Uninterruptible Power Supply) recommended for Mac mini
- Power cabling routed and secured to prevent accidental disconnection
- Network cabling labeled and secured

### 3.6 Emergency Shutoff (PE-10)

- Graceful shutdown procedure documented: `sudo shutdown -h now` (Rocky Linux) or Apple Menu → Shut Down (macOS)
- Emergency physical power cutoff: disconnect power cable
- LUKS encryption protects data if power abruptly cut

### 3.7 Delivery and Removal (PE-16)

- All hardware additions to SPN logged in SBOM
- Hardware removal requires ISSO authorization
- Removed hardware sanitized before disposal (Section 4.6)

---

## 4. Media Protection Policy

### 4.1 Media Access (MP-2)

**Authorized Media Access:**
- Only Donald E. Shannon authorized to access SPN storage media
- CUI stored on LUKS-encrypted VM virtual disk and FileVault macOS volume
- External USB drives used with SPN require USB Guard authorization

**USB Guard Controls:**
- USB Guard daemon (`/usr/local/sbin/usb-guard-monitor`) runs on macOS host
- Mode controlled via `/var/lib/usb-guard/mode` (on/off)
- When mode=on: unauthorized USB devices automatically ejected
- Toggle: `sudo /usr/local/sbin/usb-guard [on|off|status]`
- USB Guard state logged to `/var/log/usb-guard.log`

### 4.2 Media Marking (MP-3)

**Physical Media Labeling:**
- External USB drives containing CUI marked: "CUI — ENCRYPTED — Do Not Remove from Secure Area"
- NAS volumes containing CUI: share names indicate CUI content
- Printed CUI documents marked "CONTROLLED UNCLASSIFIED INFORMATION" on each page

### 4.3 Media Storage (MP-4)

**Storage Requirements:**
- Encrypted external drives stored in locked desk drawer when not in use
- USB drives not left unattended in Mac mini ports
- DataStore NAS (10.10.1.100) located on secured LAN — not internet-accessible
- KeePass vault backup (Passwords.kdbx) stored on encrypted drive only

### 4.4 Media Transport (MP-5)

**Physical Transport:**
- CUI media transported in person only (no unattended mail/courier)
- Encrypted USB drives transported in locked case where possible
- Unencrypted CUI not transported on removable media

**Electronic Transfer:**
- CUI transferred via LUKS-encrypted volumes only
- Network transfer via TLS-encrypted channels (SFTP, HTTPS, VPN)
- No CUI sent via unencrypted email

### 4.5 Media Sanitization (MP-6)

**Sanitization Methods by Media Type:**

| Media Type | Method | Verification |
|-----------|--------|--------------|
| LUKS-encrypted SSD/HDD | `cryptsetup luksErase` (destroys master key) | `cryptsetup luksDump` shows empty keyslots |
| Unencrypted SSD | Manufacturer secure erase or physical destruction | Secure erase log |
| USB Flash Drive | `shred -vfz -n 3` then verify, or physical destruction | |
| FileVault macOS | `diskutil secureErase` or factory restore | `fdesetup status` |
| Printed CUI | Cross-cut shredder (minimum DIN P-4) | |
| Virtual disk (UTM) | Delete VM bundle; wipe free space on host | `rm -P diwai-services.utm` |

**Sanitization Log:**
- All media sanitization events documented in `~/Documents/SecureMac Project Docs/Evidence/Media_Sanitization_Log.md`
- Include: Date, media description, method used, verified by

### 4.6 Media Downgrading (MP-7)

- Media downgrading from CUI classification not performed without explicit ISSO review
- Default: treat all media previously containing CUI as CUI until sanitized

---

## 5. Backup Media

### 5.1 Backup Locations

| Backup | Location | Encryption | Notes |
|--------|----------|-----------|-------|
| VM bundle (primary) | DataStore NAS 10.10.1.100 | SMB on LAN; macOS FileVault | `/Volumes/home/Backup/SecureMac/` |
| VM bundle (secondary) | Shannon_Home NAS | SMB via Wi-Fi | `/Volumes/VM/SecureMac-Backups/` |
| Config docs | DataStore NAS | SMB on LAN | `/Volumes/Cyberinabox/Secure_Mac/` |
| SABRENT USB SSD | Physical drive | FileVault / LUKS | External backup drive |

### 5.2 Backup Media Controls

- Backup NAS (DataStore) on secured LAN — not internet-accessible
- NAS credentials stored in KeePass vault only
- VM bundle backup treated as CUI media
- Backup media not shared with unauthorized parties

---

## 6. Physical Security Checklist

**Monthly verification:**
- [ ] Mac mini physically secured in office
- [ ] No unauthorized USB devices connected
- [ ] USB Guard mode confirmed appropriate (on during production)
- [ ] External drives stored securely when not in use
- [ ] No printed CUI left unattended
- [ ] DataStore NAS accessible only on LAN (10.10.1.0/24)
- [ ] Physical access log reviewed for anomalies

---

## 7. Compliance Mapping

| NIST SP 800-171 Control | Implementation |
|-------------------------|----------------|
| **PE-2** Physical Access Authorizations | Section 3.1 |
| **PE-3** Physical Access Control | Section 3.2 |
| **PE-5** Access Control for Output Devices | Section 3.3 |
| **PE-6** Monitoring Physical Access | Section 3.4 |
| **PE-9** Power Equipment and Cabling | Section 3.5 |
| **PE-10** Emergency Shutoff | Section 3.6 |
| **PE-16** Delivery and Removal | Section 3.7 |
| **MP-2** Media Access | Section 4.1 |
| **MP-3** Media Marking | Section 4.2 |
| **MP-4** Media Storage | Section 4.3 |
| **MP-5** Media Transport | Section 4.4 |
| **MP-6** Media Sanitization | Section 4.5 |
| **MP-7** Media Downgrading | Section 4.6 |

---

## 8. Policy Review and Updates

- **Review Frequency:** Annually
- **Approval Authority:** System Owner / ISSO (Donald E. Shannon)

---

## 9. Approval Signatures

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
