# USB Guard Configuration Evidence

**Document ID:** DIWAI-EV-USB-001
**Version:** 1.0
**Date Collected:** April 10, 2026
**Collected By:** Donald E. Shannon, ISSO
**Systems:** securemac.diwai.org (macOS Tahoe host) + services.diwai.org (Rocky Linux VM)
**Classification:** CUI

---

> **STATUS NOTE — April 24, 2026**
>
> The macOS-host portion of this document (Section 1) describes a state that **is no longer present on `securemac.diwai.org`**. A system lockout followed by a Time Machine recovery between this document's capture date (April 10, 2026) and the April 24, 2026 host harvest resulted in the loss of the files listed in Section 1.1 — none of `/usr/local/sbin/usb-guard`, `/usr/local/sbin/usb-guard-monitor`, `/Library/LaunchDaemons/org.diwai.usb-guard.plist`, `/var/lib/usb-guard/mode`, or `/var/log/usb-guard.log` exist on the host as of April 24, 2026, and `launchctl list` shows no matching daemon label.
>
> This document is retained unchanged as a historical record of the pre-recovery implementation and as the reference for redeployment. The Rocky VM portion (Section 2) has not been re-verified post-recovery and should be confirmed separately.
>
> Evidence-gap discussion and SSP/POA&M implications are documented at `archive/reference_system_2_mac/configuration/README.md` ("Evidence gap — custom USB-Guard daemon").

---

## Purpose

This document provides evidence of USB device access controls on the SecureMac Production Network (SPN). It supports NIST SP 800-171 controls 3.8.7 (Control use of removable media on system components) and 3.8.8 (Prohibit use of portable storage without identifiable owner), and CMMC Level 2 MP controls.

---

## 1. macOS Host — USB Guard Daemon

**Control:** NIST SP 800-171 § 3.8.7, 3.8.8 / MP-7 (Media Use)

### 1.1 Daemon Architecture

The macOS host uses a custom USB Guard implementation (LaunchDaemon) since USBGuard is a Linux-only package. The daemon operates using `diskutil` to detect and eject unauthorized USB mass storage devices.

**Component Files:**

| File | Purpose |
|------|---------|
| `/usr/local/sbin/usb-guard` | Toggle script (on/off/status commands) |
| `/usr/local/sbin/usb-guard-monitor` | LaunchDaemon polling monitor |
| `/Library/LaunchDaemons/org.diwai.usb-guard.plist` | LaunchDaemon definition |
| `/var/lib/usb-guard/mode` | State file ("on" or "off") |
| `/var/log/usb-guard.log` | Audit trail |

### 1.2 Current State

**Command:** `cat /var/lib/usb-guard/mode`
**Date:** April 10, 2026

```
off
```

**Note:** USB Guard is currently set to `off` to allow backup NAS operations. It will be set to `on` when production backup work is complete.

**Operational mode verification:**
```bash
sudo /usr/local/sbin/usb-guard status
# Returns: USB Guard is OFF (mode file: off)
```

### 1.3 USB Guard Log (audit trail)

**File:** `/var/log/usb-guard.log` (exists — confirmed)

Log format example when mode=on and USB drive connected:
```
2026-04-10 08:23:14 [WARN] USB disk detected: disk4 (SABRENT External SSD)
2026-04-10 08:23:14 [ACTION] Ejecting disk4 — USB Guard mode: on
2026-04-10 08:23:14 [INFO] USB Guard ejected disk4 successfully
```

### 1.4 LaunchDaemon Configuration

**File:** `/Library/LaunchDaemons/org.diwai.usb-guard.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>org.diwai.usb-guard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/sbin/usb-guard-monitor</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/usb-guard.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/usb-guard.log</string>
</dict>
</plist>
```

**Daemon Status:** Running (verified via `launchctl list | grep usb-guard`)

### 1.5 Toggle Script Behavior

**`/usr/local/sbin/usb-guard` commands:**

| Command | Action |
|---------|--------|
| `sudo usb-guard on` | Writes "on" to mode file; monitor starts ejecting USBs |
| `sudo usb-guard off` | Writes "off" to mode file; USB devices allowed |
| `sudo usb-guard status` | Reports current mode and daemon state |

**Monitor behavior (when mode=on):**
- Polls `diskutil list` every 5 seconds
- Any new USB mass storage device detected → immediately ejected
- Ejection logged to `/var/log/usb-guard.log`

### 1.6 Authorized USB Devices

| Device | Description | Authorization |
|--------|------------|---------------|
| SABRENT USB SSD | External backup drive | Authorized — backup operations (guard set to off during use) |
| Kingston IronKey 64GB | Secure config vault (planned) | POA&M-006, target 2026-04-30 |

---

## 2. Rocky Linux VM — USBGuard (Linux)

**Control:** NIST SP 800-171 § 3.8.7, 3.8.8 / MP-7 (Media Use)

### 2.1 USBGuard Service Status

**Command:** `sudo systemctl status usbguard --no-pager`
**Date:** April 10, 2026

```
● usbguard.service - USBGuard daemon
     Loaded: loaded (/usr/lib/systemd/system/usbguard.service; enabled; preset: disabled)
     Active: active (running) since Fri 2026-04-10 10:48:09 MDT; 1h 59min ago
       Docs: man:usbguard-daemon(8)
   Main PID: 1923 (usbguard-daemon)
     Tasks: 3 (limit: 99788)
```

**Result:** PASS — USBGuard daemon active and running since VM boot.

### 2.2 USBGuard Policy

**Default Policy:** `ImplicitPolicyTarget=block`

The Rocky Linux VM's USBGuard is configured to block any USB device not explicitly allowed by policy. This is the default secure state.

Toggle script deployed at `/usr/local/sbin/usb-guard` on the VM:

| Command | Action |
|---------|--------|
| `sudo usb-guard on` | Sets `ImplicitPolicyTarget=block`; restarts usbguard |
| `sudo usb-guard off` | Sets `ImplicitPolicyTarget=allow`; restarts usbguard |
| `sudo usb-guard status` | Reports current policy target |

### 2.3 VM USB Context

The Rocky Linux VM runs under UTM (QEMU ARM64). Physical USB devices are not passed through to the VM by default. USBGuard on the VM provides defense-in-depth for any USB devices that may be explicitly passed through for administrative purposes.

---

## 3. Compliance Summary

| Control | Requirement | macOS Host | Rocky Linux VM |
|---------|-------------|-----------|----------------|
| 3.8.7 | Control use of removable media | ✅ USB Guard daemon (custom) | ✅ USBGuard service |
| 3.8.8 | Prohibit unidentified portable storage | ✅ Eject unauthorized devices | ✅ Block by default policy |
| MP-2 | Media access controls | ✅ Mode-controlled | ✅ Implicit block |
| MP-4 | Media storage controls | ✅ Guard log maintained | ✅ Policy enforced |

---

## 4. Operational Procedures

**Before connecting a USB device (macOS host):**
```bash
# Disable USB Guard
sudo /usr/local/sbin/usb-guard off
# Connect device
# Perform required operations
# Re-enable USB Guard when done
sudo /usr/local/sbin/usb-guard on
```

**Verify USB Guard is re-enabled:**
```bash
cat /var/lib/usb-guard/mode  # Should return: on
```

**Review USB Guard audit log:**
```bash
sudo tail -50 /var/log/usb-guard.log
```

---

**Verified By:** Donald E. Shannon, ISSO
**Date:** April 10, 2026
**Next Verification:** July 2026 (quarterly)

---

**CLASSIFICATION:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)
