# Physical and Media Protection Policy

**Policy Number:** TCC-PE-MP-001
**Version:** 2.0 Rev 3 DRAFT (Updated for NIST SP 800-171 Rev 3)
**Effective Date:** [TBD - Target: Phase 2 completion]
**Last Reviewed:** March 22, 2026
**Policy Owner:** System Owner (sysadmin)
**Approval Authority:** System Owner (sysadmin)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | November 2, 2025 | Initial policy (NIST 800-171 Rev 2, combined PE and MP families) |
| 2.0 Rev 3 DRAFT | March 22, 2026 | Updated for Rev 3: Added ODPs (physical access controls, media sanitization methods), updated for consolidated PE/MP families, documented home office environment, enhanced NIST SP 800-88 sanitization procedures |

---

## 1. PURPOSE

This policy establishes requirements for physical and media protection within the CyberHygiene Production Network (CPN). This policy satisfies the Physical and Environmental Protection (PE) and Media Protection (MP) control family requirements in NIST SP 800-171 Revision 3.

**Rev 3 Updates:**
- Added Organization-Defined Parameters (ODPs) for physical access controls and media sanitization
- Enhanced sanitization procedures per NIST SP 800-88 Rev 1
- Documented home office physical security environment
- Updated for Rev 3 control family consolidation

---

## 2. SCOPE

This policy applies to:

**Physical Locations:**
- Home office (primary CPN location)
- Server room (dedicated, locked)

**Systems:**
- All CPN systems (dc1, labrat, engineering, accounting)
- Backup media (encrypted USB drives, encrypted NAS)
- Removable media (USB drives, external drives)

**Media Types:**
- Digital storage: Hard drives, SSDs, USB drives
- Backup media: Encrypted external drives, ReaR backup ISOs
- Paper documents: Printed CUI requiring secure disposal

---

## 3. POLICY STATEMENTS

### 3.1 Physical Access Authorization — NIST 3.10.1 (PE-2, ODP-PE-1)

**3.1.1 Authorize Physical Access (ODP-PE-1 - Access Controls)**

CyberHygiene shall limit physical access to CPN systems and facilities:

**Physical Security Environment:**
- **Location:** Home office (single-family residence)
- **Server room:** Dedicated room, locked door (key access only)
- **Access control:** Owner/operator only (no other personnel)
- **Visitors:** Escorted at all times (rare occurrence)

**Physical Access Controls (ODP-PE-1):**
- Door locks (keyed deadbolt)
- Server room locked when unattended
- Workstations locked (screen saver timeout 15 minutes)
- No visitor CUI access permitted

**Physical Security Monitoring:**
- No physical intrusion detection system (home office environment)
- Wazuh logs all system logins (detects unauthorized logical access)
- Insurance: Homeowner's policy covers equipment theft

### 3.2 Physical Access Control — NIST 3.10.2 (PE-3)

**3.2.1 Enforce Physical Access Authorizations**

CyberHygiene shall verify physical access authorizations before granting access:

**Access Procedures:**
- **Routine access:** Owner/operator only (no verification needed)
- **Visitor access:** Escort required, no unattended access to server room
- **Vendor access:** Supervised only (rare, for equipment delivery)

**Physical Access Logs:**
- Informal tracking (visitors rare)
- System access logged via Wazuh (logical access audit trail)

### 3.3 Media Storage — NIST 3.8.1 (MP-4)

**3.3.1 Protect Media During Storage**

CyberHygiene shall protect CUI media during storage:

**Digital Media Storage:**
- All systems: Full disk encryption (LUKS AES-256-XTS)
- Backup media: Encrypted USB drives, encrypted NAS (LUKS)
- Removable media: Encrypted if contains CUI
- Storage location: Locked server room

**Paper Document Storage:**
- CUI documents: Locked file cabinet (when not in use)
- Clean desk policy: Lock documents when stepping away
- No CUI left on printers/scanners

### 3.4 Media Transport — NIST 3.8.2 (MP-5)

**3.4.1 Protect Media During Transport**

CyberHygiene shall protect CUI media during physical transport:

**Transport Procedures:**
- Encrypted media only (LUKS encryption required)
- Physical custody maintained (hand-carry, no mail/courier)
- Transport container: Locked briefcase or bag
- Avoid unnecessary transport (prefer electronic transmission over VPN)

**Current Transport:**
- Minimal media transport (home office environment)
- Offsite backups: Encrypted USB drives, physically transported to secure offsite location monthly

### 3.5 Media Sanitization — NIST 3.8.3 (MP-6, ODP-MP-1)

**3.5.1 Sanitize Media Before Disposal or Reuse (ODP-MP-1 - Sanitization Methods)**

CyberHygiene shall sanitize media before disposal, release, or reuse per NIST SP 800-88 Rev 1:

**Sanitization Methods (ODP-MP-1):**

**Hard Drives/SSDs (CUI Data):**
- **Method:** Clear + Purge
- **Clear:** Overwrite with zeros (3 passes minimum)
  ```bash
  shred -vfz -n 3 /dev/sdX
  ```
- **Purge:** ATA Secure Erase (preferred for SSDs)
  ```bash
  hdparm --security-erase <password> /dev/sdX
  ```
- **Destroy:** Physical destruction if drive failure prevents sanitization

**USB Drives/Removable Media (CUI Data):**
- **Method:** Purge or Destroy
- **Purge:** Overwrite 3+ passes with shred
- **Destroy:** Physical destruction (hammer, shredder)

**Paper Documents (CUI):**
- **Method:** Cross-cut shredding (minimum 5/32" x 1-1/2" particles)
- **Equipment:** Cross-cut shredder (home office)
- **Verification:** Visual inspection of shred container

**Optical Media (CD/DVD - if used):**
- **Method:** Physical destruction
- **Destroy:** Cut/shred disc into small pieces

**Sanitization Verification:**
- Test read after sanitization (verify unreadable)
- Document sanitization in disposal log
- Certificate of destruction (if third-party destruction)

**Media Disposal:**
- Sanitized media: Discard in regular waste or recycle
- Failed sanitization: Physical destruction required
- Third-party disposal: Use DOD-approved degausser/shredder (if needed)

### 3.6 Media Use — NIST 3.8.4 (MP-7)

**3.6.1 Prohibit Use of Certain Media**

CyberHygiene shall restrict the use of certain types of removable media:

**Prohibited Media:**
- Unencrypted USB drives (for CUI storage)
- Personal cloud storage (Dropbox, Google Drive, OneDrive)
- Optical media (CDs/DVDs) for CUI (deprecated)
- Floppy disks (obsolete)

**Approved Media:**
- Encrypted USB drives (LUKS-encrypted)
- Encrypted external drives (backup use only)
- SCP/SFTP (preferred over removable media)

**USB Device Controls:**
- USBGuard not implemented (single-user environment, low risk)
- Physical port security: Server room locked
- Audit logging: All USB device insertions logged (auditd)

---

## 4. ROLES AND RESPONSIBILITIES

**System Owner (sysadmin):**
- Maintain physical security of home office and server room
- Lock server room when unattended
- Sanitize media before disposal per NIST SP 800-88
- Transport encrypted media only
- Escort visitors (if any)
- Document media sanitization

---

## 5. COMPLIANCE

**Regulatory Requirements:**
- NIST SP 800-171 Rev 3: PE and MP control families
- CMMC Level 2: Physical Protection and Media Protection domains
- NIST SP 800-88 Rev 1: Media sanitization guidelines

**Assessment Evidence:**
- Physical access logs: Informal (owner-only access)
- Encryption verification: `cryptsetup status` on all systems (100% coverage)
- Sanitization logs: Media disposal documentation
- Clean desk policy: Documented in TCC-AUP-001

---

## 6. RELATED DOCUMENTS

**Policies:**
- TCC-SCP-001: System and Communications Protection Policy v2.0 Rev 3 (encryption)
- TCC-AUP-001: Acceptable Use Policy (clean desk, removable media)

**Standards:**
- NIST SP 800-171 Rev 3: Protecting Controlled Unclassified Information
- NIST SP 800-88 Rev 1: Guidelines for Media Sanitization

---

## 7. APPROVAL

**Policy Owner:** System Owner (sysadmin)

**Approval Date:** [TBD - Target: Phase 2 completion]

**Signature:** _________________________________

---

*This policy satisfies NIST SP 800-171 Rev 3 PE and MP control families.*

**Rev 3 Status:** DRAFT - Pending final review and approval
