# Wazuh Agent Installation Guide
## CyberHygiene Project - NIST 800-171 Compliance

This guide explains how to install Wazuh agents on workstations for Security Configuration Assessment (SCA) compliance scanning.

---

## Overview

Once installed, Wazuh agents will:
- Run CIS Benchmark compliance scans every 12 hours
- Report results to the Wazuh Dashboard on dc1
- Provide continuous security monitoring
- Map findings to NIST 800-53 and CMMC 2.0 controls

**No SSH required from the dashboard** - agents maintain their own secure connection to the manager.

---

## Installation Scripts

| Workstation | Script | Download |
|-------------|--------|----------|
| Rocky Linux 9 | install_wazuh_agent_rocky9.sh | [Download](https://dc1.cyberinabox.net/scripts/install_wazuh_agent_rocky9.sh) |
| macOS (Mac Mini) | install_wazuh_agent_macos.sh | [Download](https://dc1.cyberinabox.net/scripts/install_wazuh_agent_macos.sh) |

---

## Rocky Linux Workstations

**Applies to:** engineering, accounting, labrat

### Option A: Download and Run (Recommended)
```bash
# On the workstation, run:
curl -O https://dc1.cyberinabox.net/scripts/install_wazuh_agent_rocky9.sh
chmod +x install_wazuh_agent_rocky9.sh
sudo ./install_wazuh_agent_rocky9.sh
```

### Option B: Copy via SCP
```bash
# From dc1:
scp /var/www/cyberhygiene/scripts/install_wazuh_agent_rocky9.sh user@workstation:~/

# On workstation:
chmod +x install_wazuh_agent_rocky9.sh
sudo ./install_wazuh_agent_rocky9.sh
```

---

## macOS (Mac Mini / ai.cyberinabox.net)

### Option A: Download and Run
```bash
# On the Mac:
curl -O https://dc1.cyberinabox.net/scripts/install_wazuh_agent_macos.sh
chmod +x install_wazuh_agent_macos.sh
sudo ./install_wazuh_agent_macos.sh
```

### Option B: Copy via SCP
```bash
# From dc1:
scp /var/www/cyberhygiene/scripts/install_wazuh_agent_macos.sh ITAdminHelp@192.168.1.7:~/

# On Mac:
chmod +x install_wazuh_agent_macos.sh
sudo ./install_wazuh_agent_macos.sh
```

---

## Verification

After installation, verify the agent is connected:

### On the Workstation
```bash
# Rocky Linux:
sudo systemctl status wazuh-agent
sudo grep "Connected" /var/ossec/logs/ossec.log

# macOS:
sudo /Library/Ossec/bin/wazuh-control status
sudo grep "Connected" /Library/Ossec/logs/ossec.log
```

### On the Manager (dc1)
```bash
# List connected agents:
sudo /var/ossec/bin/agent_control -l

# Check agent info:
sudo /var/ossec/bin/agent_control -i <AGENT_ID>
```

### In Wazuh Dashboard
1. Open https://dc1.cyberinabox.net:5601
2. Navigate to **Agents** in the left menu
3. Verify new agent appears with "Active" status
4. Click on agent > **Security Configuration Assessment**

---

## SCA Policies Enabled

| Policy | OS | Controls Mapped |
|--------|----|--------------------|
| cis_rocky_linux_9.yml | Rocky Linux 9 | NIST 800-53, CMMC 2.0, PCI-DSS, ISO 27001 |
| cis_apple_macOS_15.x.yml | macOS 15+ | NIST 800-53, CMMC 2.0, CIS Controls |

---

## Scan Schedule

- **Initial scan:** Runs immediately when agent starts
- **Recurring scans:** Every 12 hours
- **Manual trigger:** Restart agent to force immediate scan

---

## Troubleshooting

### Agent Not Connecting

1. **Check firewall on workstation:**
   ```bash
   # Rocky Linux:
   sudo firewall-cmd --list-ports | grep -E "1514|1515"

   # If missing, add:
   sudo firewall-cmd --permanent --add-port=1514/tcp
   sudo firewall-cmd --permanent --add-port=1515/tcp
   sudo firewall-cmd --reload
   ```

2. **Check DNS resolution:**
   ```bash
   ping dc1.cyberinabox.net
   # Should resolve to 192.168.1.10
   ```

3. **Check agent logs:**
   ```bash
   # Rocky Linux:
   sudo tail -50 /var/ossec/logs/ossec.log

   # macOS:
   sudo tail -50 /Library/Ossec/logs/ossec.log
   ```

### SCA Results Not Appearing

1. **Force a scan:**
   ```bash
   # Rocky Linux:
   sudo systemctl restart wazuh-agent

   # macOS:
   sudo /Library/Ossec/bin/wazuh-control restart
   ```

2. **Check SCA is enabled in agent config:**
   ```bash
   grep -A5 "<sca>" /var/ossec/etc/ossec.conf  # Rocky
   grep -A5 "<sca>" /Library/Ossec/etc/ossec.conf  # macOS
   ```

---

## Network Ports

| Port | Protocol | Direction | Purpose |
|------|----------|-----------|---------|
| 1514 | TCP | Agent → Manager | Event/log transmission |
| 1515 | TCP | Agent → Manager | Agent registration |

---

## File Locations

### Rocky Linux
| Component | Path |
|-----------|------|
| Agent binary | /var/ossec/bin/ |
| Configuration | /var/ossec/etc/ossec.conf |
| Logs | /var/ossec/logs/ossec.log |
| SCA policies | /var/ossec/ruleset/sca/ |

### macOS
| Component | Path |
|-----------|------|
| Agent binary | /Library/Ossec/bin/ |
| Configuration | /Library/Ossec/etc/ossec.conf |
| Logs | /Library/Ossec/logs/ossec.log |
| SCA policies | /Library/Ossec/ruleset/sca/ |

---

## Support

- **Wazuh Dashboard:** https://dc1.cyberinabox.net:5601
- **Documentation:** https://documentation.wazuh.com/
- **SCA Reference:** https://documentation.wazuh.com/current/user-manual/capabilities/sec-config-assessment/

---

**Last Updated:** January 29, 2026
