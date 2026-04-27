# Backup Procedures v1.0
**System:** SecureMac — diwai.org Reference System #2  
**Owner:** Don Shannon  
**Effective Date:** April 11, 2026  
**Review Cycle:** Annual  
**NIST Controls:** CP-6, CP-7, CP-9, CP-10, MP-4, MP-5  

---

## 1. Purpose and Scope

This document describes the backup and recovery architecture for the SecureMac reference system. It covers the Mac mini M4 Pro host, the Rocky Linux 9.7 FIPS VM (diwai-services), security configuration data, and operational log archives. These procedures support NIST SP 800-171 R2 requirements for contingency planning and media protection.

**In scope:**
- Mac mini M4 Pro host (macOS Tahoe 26)
- Rocky Linux 9.7 FIPS VM (`diwai-services`, 10.10.1.10, hosted on UTM)
- Security configuration vault (Kingston IronKey — planned)
- Wazuh log archives (operational)

**Out of scope:** Synology NAS internal backup (managed by Synology DSM independently); HP mini PCs and servers in CyberInABox Ref System #1 (covered by separate SSP).

---

## 2. Backup Architecture Overview

| Component | Method | Destination | Frequency | Retention |
|---|---|---|---|---|
| Mac mini host (macOS) | Time Machine | "Secure Mac" external SSD | Continuous (hourly incremental) | 1 TB capacity |
| Rocky Linux FIPS VM | UTM snapshot | Mac mini internal storage | Weekly (Sunday 23:00) | 4 snapshots (~30 days) |
| Rocky Linux FIPS VM | UTM full export (.utm/.qcow2) | "Secure Mac" external SSD | Monthly | 2 copies |
| Security config vault | Kingston IronKey USB | Offline, locked rack | On change | Manual |
| Wazuh log archives | AES-256 encrypted .enc files | Synology NAS (10.10.1.100) | Daily (03:00) | 90 days |

---

## 3. Mac Mini Host Backup — Time Machine

### 3.1 Configuration

Time Machine backs up the entire Mac mini M4 Pro host to a dedicated external SSD physically labeled **"Secure Mac"**. The SSD is stored in the locked rack enclosure.

- **Backup destination:** "Secure Mac" external SSD (USB-C, directly attached to Mac mini)
- **Format:** APFS encrypted (Time Machine encryption enabled)
- **Schedule:** Hourly incremental; daily/weekly consolidation (macOS-managed)
- **Exclusions:** `/private/tmp`, `/private/var/vm` (swap), system caches — macOS default exclusions apply

### 3.2 What Is Covered

Time Machine captures:
- macOS system files, applications, and user data
- `/Users/dshannon/` (home directory, scripts, certificates, project docs)
- `/usr/local/sbin/` (nas-archive-push and other operational scripts)
- `/Library/LaunchDaemons/` (launchd plists)
- `/etc/pf.conf` and firewall rules (via `/etc/`)
- VPN client config (`~/diwai/dshannon-diwai.ovpn`)
- S/MIME CA certificate (`~/diwai/smime/ca/ca.crt`)

**Note:** The S/MIME private key for donald@diwai.org is stored exclusively on the YubiKey 5C Nano FIPS (PIV slot 9c). It is NOT on disk and is NOT backed up by Time Machine. The private key cannot be extracted from the YubiKey — this is by design (FIPS hardware key protection). If the YubiKey is lost, a new S/MIME certificate must be issued from the internal diwai.org CA.

### 3.3 Verification

Time Machine backup status is visible via System Settings → General → Time Machine. Verify:
1. Last backup timestamp is current (within the last 2 hours during normal operation)
2. "Secure Mac" SSD appears as the active backup destination
3. Free space on "Secure Mac" SSD is > 20% of capacity

Quarterly: perform a test restore of a sample file (`~/diwai/` directory) to verify backup integrity.

---

## 4. Rocky Linux FIPS VM Backup — UTM Snapshots and Export

### 4.1 VM Snapshots (Weekly)

UTM/QEMU snapshots capture the running state of `diwai-services` including all service configurations, LDAP data, and the FIPS environment.

**Manual snapshot procedure (until automation is implemented):**

1. SSH into Mac mini or use UTM GUI
2. Suspend the VM briefly or use live snapshot:
   ```
   # From Mac mini terminal (UTM AppleScript or qmp socket)
   # GUI method: UTM → diwai-services → Snapshots → Take Snapshot
   ```
3. Name the snapshot: `diwai-services-YYYY-MM-DD`
4. Retain the 4 most recent snapshots; delete older ones

**Snapshot retention:** 4 snapshots (~30 days rolling). Snapshots are stored on the Mac mini internal SSD alongside the VM disk image.

**Snapshot schedule:** Every Sunday at 23:00.  
**POA&M status:** Snapshot automation (cron/launchd trigger) is pending — currently manual (POA&M-009, target 2026-05-31).

### 4.2 Full VM Export (Monthly)

A full export of the UTM VM package to the "Secure Mac" external SSD provides an offline, bootable backup independent of the Mac mini internal disk.

**Monthly export procedure:**

1. Confirm VM is in a clean state (services running, no active writes)
2. In UTM: right-click `diwai-services` → Share/Export → save as `diwai-services-YYYY-MM.utm` 
   - Alternatively, copy the `.utm` bundle from `~/Library/Containers/com.utmapp.UTM/Data/Documents/`
3. Destination: `/Volumes/Secure Mac/VM-Backups/diwai-services-YYYY-MM.utm`
4. Retain 2 monthly exports; delete the oldest after the 3rd export is confirmed good

**LUKS note:** The VM disk (vda3, 198.4 GB) is LUKS2 encrypted. The LUKS passphrase (`REDACTED_SEE_SENSITIVE`) is required to boot the VM from any export. Store this passphrase in the Kingston IronKey config vault (see Section 5) and in a printed emergency sheet stored in the locked rack.

### 4.3 Critical VM Data — 389 Directory Server

The 389-ds LDAP database is the most operationally critical dataset on the VM. In addition to VM-level backups, export an LDAP data backup weekly:

```bash
# On diwai-services VM — run as root
# Full LDAP export (LDIF format)
dsconf diwai.org export -p 636 -Z --rootdn "cn=Directory Manager" \
    --password "SecureMac2026!LDAP" \
    --output-file /var/backups/ldap-diwai-$(date +%Y%m%d).ldif

# Copy to Mac mini staging
scp -i /root/.ssh/id_ecdsa_automation \
    /var/backups/ldap-diwai-$(date +%Y%m%d).ldif \
    dshannon@10.10.1.1:/Users/dshannon/nas-staging/
```

LDIF backup files are then pushed to the Synology NAS alongside Wazuh log archives. Retain 4 weekly LDIF exports.

**POA&M status:** LDAP backup automation is pending (POA&M-010, target 2026-05-31).

---

## 5. Security Configuration Vault — Kingston IronKey

### 5.1 Overview

A Kingston IronKey hardware-encrypted USB drive serves as the offline security configuration vault for the SecureMac reference system. The IronKey stores configuration data and credentials that are required for disaster recovery but must not be stored in cloud services or unencrypted media.

**Status:** Planned — POA&M-006, target 2026-04-30.

### 5.2 Contents of IronKey Vault

When provisioned, the IronKey vault will contain:

| Item | Description |
|---|---|
| `credentials.txt` | All service credentials (LDAP DM, MariaDB, YubiKey PIN/PUK, GRUB/LUKS passphrase) |
| `diwai-ca.crt` | Internal diwai.org Email CA certificate |
| `wazuh-archive.key` | AES-256 key for Wazuh log archive decryption |
| `diwai-services-restore.md` | Step-by-step VM restore procedure |
| `pf.conf.bak` | Mac mini firewall rules backup |
| `yubikey-mgmt-key.txt` | YubiKey AES-256 management key |
| `openvpn-server.conf.bak` | OpenVPN server configuration backup |
| `backup-manifest.txt` | Inventory of all backup locations and schedules |

### 5.3 IronKey Security Policy

- The IronKey is stored in the locked rack enclosure when not in use
- Access requires the IronKey PIN (hardware-enforced; wipes after 10 failed attempts per Kingston FIPS 140-2 specification)
- IronKey is updated whenever service credentials or configurations change
- A second IronKey (offsite copy) is planned for business continuity (POA&M-007)

---

## 6. Wazuh Log Archive — NAS (Operational)

This backup component is currently operational. See the Wazuh section of the CPM Dashboard for live status.

### 6.1 Pipeline Summary

```
diwai-services VM (02:00 daily)
  → Compress previous day's Wazuh alerts (tar.gz)
  → Encrypt: OpenSSL AES-256-CBC + PBKDF2/SHA-256, 100k iterations (FIPS 140-2)
  → SCP to Mac mini (10.10.1.1) ~/nas-staging/ via ECDSA-521 SSH
  
Mac mini (03:00 daily, LaunchDaemon)
  → Copy .enc files from ~/nas-staging/ to /Volumes/Logs/wazuh-alerts/
  → NAS applies second-layer AES-256/SHA-256 folder encryption (non-FIPS, defense in depth)
```

### 6.2 Retention

- OpenSearch (live index): 90 days (ISM policy: `wazuh-90day-retention`)
- NAS encrypted archives: 90 days (manual review and deletion; automation pending)
- Encryption key: `/etc/wazuh-archive.key` on VM (root:root, 600); copy stored in IronKey vault

### 6.3 FIPS Boundary Note

The FIPS 140-2 boundary ends at the `.enc` file produced on the Rocky Linux FIPS VM. Transfer to Mac mini uses AES-256-CTR over SSH (FIPS-compliant). The Synology NAS applies folder-level AES-256/SHA-256 encryption as a second layer — this is **not** FIPS 140-2 validated. The NAS is classified as supporting infrastructure within the physical security perimeter (locked rack). See SSP Section 3 (System Boundary) for full boundary analysis.

---

## 7. Recovery Procedures

### 7.1 Mac Mini Host Recovery (Time Machine)

**Scenario:** Mac mini macOS failure, disk replacement, or migration to new hardware.

1. Boot from macOS Recovery (hold power button on Apple Silicon)
2. Select "Restore from Time Machine Backup"
3. Connect "Secure Mac" external SSD
4. Select the most recent backup
5. Allow restore to complete (approximately 2–4 hours for full restore)
6. After restore, verify:
   - UTM and `diwai-services` VM start correctly
   - `pf` firewall rules load (`sudo pfctl -sr`)
   - LaunchDaemons load (`sudo launchctl list | grep diwai`)
   - NAS SMB mount re-established

**YubiKey note:** After host restore, the YubiKey 5C Nano FIPS must be re-inserted. The S/MIME private key on the YubiKey is preserved — it does not need to be re-provisioned. Re-import the S/MIME certificate from `~/diwai/smime/certs/donald.crt` into the login Keychain if needed.

### 7.2 Rocky Linux FIPS VM Recovery (UTM Snapshot)

**Scenario:** VM corruption, accidental config change, or failed update.

1. Open UTM on Mac mini
2. Select `diwai-services` → Snapshots
3. Choose the most recent clean snapshot (`diwai-services-YYYY-MM-DD`)
4. Click "Restore Snapshot"
5. Start the VM; enter LUKS passphrase when prompted (`REDACTED_SEE_SENSITIVE`)
6. Verify services:
   ```bash
   systemctl is-active dirsrv@diwai httpd postfix dovecot openvpn@server
   ```

### 7.3 Rocky Linux FIPS VM Full Rebuild (UTM Export)

**Scenario:** Snapshot unavailable or Mac mini internal disk failure.

1. Copy the most recent `.utm` export from "Secure Mac" external SSD:
   `/Volumes/Secure Mac/VM-Backups/diwai-services-YYYY-MM.utm`
2. In UTM: File → Import VM → select the `.utm` bundle
3. Start the VM; enter LUKS passphrase (`REDACTED_SEE_SENSITIVE`)
4. If using a monthly export, apply any LDIF changes made since the export:
   ```bash
   ldapadd -H ldaps://localhost -D "cn=Directory Manager" \
       -w "SecureMac2026!LDAP" -f /path/to/ldap-diwai-YYYYMMDD.ldif
   ```
5. Update Wazuh agent key on Mac mini if agent re-registration is needed

### 7.4 LDAP Data Recovery

**Scenario:** 389 Directory Server data corruption.

1. Retrieve the most recent LDIF export from NAS or nas-staging
2. Stop 389-ds: `systemctl stop dirsrv@diwai`
3. Initialize new backend and import:
   ```bash
   dsconf diwai.org backend import userRoot /path/to/ldap-diwai-YYYYMMDD.ldif
   systemctl start dirsrv@diwai
   ```
4. Verify user accounts: `ldapsearch -H ldaps://localhost -D "cn=Directory Manager" -w "SecureMac2026!LDAP" -b "ou=people,dc=diwai,dc=org" "(uid=*)" uid`

### 7.5 Wazuh Log Archive Decryption (for forensics/audit)

To decrypt an archived `.enc` file for review:

```bash
# Retrieve the archive key from /etc/wazuh-archive.key (or IronKey vault)
KEY=$(cat /etc/wazuh-archive.key)

openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 \
    -pass "pass:${KEY}" \
    -in  wazuh-alerts-YYYY-MM-DD.tar.gz.enc \
    -out wazuh-alerts-YYYY-MM-DD.tar.gz

tar -xzf wazuh-alerts-YYYY-MM-DD.tar.gz
```

---

## 8. Backup Verification Schedule

| Test | Frequency | Method |
|---|---|---|
| Time Machine backup current | Monthly | Check System Settings → Time Machine last backup time |
| Time Machine restore test | Quarterly | Restore sample file from "Secure Mac" SSD to temp location |
| VM snapshot restore test | Quarterly | Restore to snapshot, verify service health, restore back to current |
| NAS archive pipeline | Monthly | Confirm .enc files present in /Volumes/Logs/wazuh-alerts/ |
| Archive decryption test | Annually | Decrypt one .enc file, verify contents readable |
| IronKey contents current | On change | Update IronKey whenever credentials or configs change |

---

## 9. NIST SP 800-171 R2 Control Mapping

| Control | Requirement | This Document |
|---|---|---|
| CP-9 (3.6.1) | Establish and implement operational continuity and backup plans | Sections 3–6: four backup tiers |
| CP-10 (3.6.2) | Test the organizational contingency plan | Section 8: verification schedule |
| MP-4 (3.8.1) | Protect system media | IronKey FIPS hardware encryption (Section 5) |
| MP-5 (3.8.2) | Control access to CUI on portable devices | IronKey PIN-enforced access; Time Machine APFS encryption |
| SC-28 (3.13.16) | Protect the confidentiality of CUI at rest | LUKS2 on VM, AES-256 on Time Machine, AES-256 on log archives |

---

*Document maintained by: Don Shannon — SecureMac Reference System #2, diwai.org*  
*Next review: April 2027 (or upon significant architecture change)*
