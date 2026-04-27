# OpenClaw AI Security Architecture Synopsis

**Document Version:** 1.0
**Last Updated:** 2026-02-02
**Classification:** CUI // SP-NOFORN
**System:** dc1.cyberinabox.net (192.168.1.10)
**Compliance Framework:** NIST 800-171 Rev 2 / CMMC Level 2

---

## Executive Summary

This document describes the security architecture for the AI-assisted system administration capability deployed on dc1.cyberinabox.net, a NIST 800-171 compliant Rocky Linux 9 Domain Controller. The implementation provides human-in-the-loop (HITL) controlled AI assistance for system administration tasks while maintaining strict security boundaries and audit compliance.

**Key Security Principle:** The AI agent operates under a zero-trust model where all privileged operations require cryptographically verified human approval through an external process that exists outside the agent's trust boundary.

---

## 1. Architecture Overview

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           User Interface Layer                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  SysAdmin Agent Dashboard          │  CPM Dashboard (Approval UI)           │
│  https://dc1/sysadmin              │  https://dc1/dashboard                 │
│  Port 8501 (Streamlit)             │  Port 5000 (Flask)                     │
│  - AI chat interface               │  - System monitoring                   │
│  - Task execution UI               │  - Sudo approval modal                 │
│  - Compliance reporting            │  - Log viewer                          │
└───────────────────┬─────────────────────────────────┬───────────────────────┘
                    │                                 │
                    ▼                                 │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI Gateway Layer                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  OpenClaw Gateway (Port 18789 - Loopback Only)                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Token Auth      │  │ Citadel Guard   │  │ Request Router  │              │
│  │ (Bearer Token)  │  │ (Injection Def) │  │ (Chat/Execute)  │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Citadel Guard Injection Patterns:                                    │    │
│  │ - Direct instruction overrides (ignore previous instructions)        │    │
│  │ - Role manipulation (you are now, act as, pretend to be)            │    │
│  │ - System prompt extraction attempts                                  │    │
│  │ - Privilege escalation keywords (sudo, as root, bypass approval)    │    │
│  │ - DC-specific attack patterns (ipa user-mod, kadmin, ldapmodify)    │    │
│  │ - Encoding evasion (base64 decode, eval, exec)                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└───────────────────┬─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LLM Backend (Air-Gapped)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Ollama Server: 192.168.1.7:11434 (Mac Mini M4 Pro)                         │
│  Model: llama3.3:70b-instruct-q4_K_M                                        │
│  Network: 192.168.1.0/24 only (no internet access)                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      Privilege Execution Layer                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  Sudo Approval Proxy (EXTERNAL TRUST BOUNDARY)                              │
│  Socket: /run/sudo-proxy/sudo-proxy.sock                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Command         │  │ Dashboard       │  │ HMAC Signature  │              │
│  │ Allowlist       │  │ Webhook         │  │ Verification    │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                              │
│  Security Properties:                                                        │
│  - Runs as separate process (not inside AI agent)                           │
│  - Validates structured commands (no raw shell strings)                     │
│  - Requires cryptographically signed approval                               │
│  - 120-second timeout = automatic denial                                    │
│  - Comprehensive audit logging                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

1. **User Input** → SysAdmin Agent Dashboard (Streamlit)
2. **AI Request** → OpenClaw Gateway (token authenticated)
3. **Injection Scan** → Citadel Guard (sanitize & flag)
4. **LLM Query** → Ollama (local network only)
5. **Response Scan** → Citadel Guard (detect indirect injection)
6. **Command Request** → shell_tool.py (validate against allowlist)
7. **Privileged Command** → Sudo Proxy (external trust boundary)
8. **Approval Request** → CPM Dashboard (WebSocket push)
9. **Human Decision** → Approve/Deny with HMAC signature
10. **Execution** → Sudo Proxy executes if approved
11. **Audit Log** → All steps logged for compliance

---

## 2. Security Controls

### 2.1 NIST 800-171 Control Mapping

| Control Family | Control ID | Implementation |
|----------------|------------|----------------|
| **Access Control** | 3.1.1 | Token-based authentication for OpenClaw gateway |
| | 3.1.2 | Loopback-only binding (127.0.0.1:18789) |
| | 3.1.5 | Least privilege - agent user has no direct sudo |
| | 3.1.7 | Network confinement to 192.168.1.0/24 |
| **Audit & Accountability** | 3.3.1 | Comprehensive logging at all layers |
| | 3.3.2 | Audit events include user, timestamp, command, result |
| | 3.3.4 | Alerts on Citadel Guard detections |
| **Configuration Management** | 3.4.1 | Baseline configs in /opt/openclaw/config/ |
| | 3.4.2 | Security settings enforced by systemd |
| | 3.4.5 | Tool allowlist/denylist enforcement |
| **Identification & Auth** | 3.5.1 | Service accounts with nologin shells |
| | 3.5.2 | HMAC-signed approval responses |
| **Incident Response** | 3.6.1 | Injection detection triggers alerts |
| | 3.6.2 | Audit logs for forensic analysis |
| **System & Comm Protection** | 3.13.1 | TLS for external communications |
| | 3.13.5 | Cryptographic signature verification |
| | 3.13.8 | No data leaves 192.168.1.0/24 network |

### 2.2 Defense in Depth Layers

```
Layer 1: Network Confinement
├── nftables egress rules (/etc/nftables/openclaw-egress.nft)
├── UID-based filtering for openclaw-svc (UID 379)
├── Allowed: 127.0.0.1, 192.168.1.0/24, Ollama (192.168.1.7:11434)
└── Blocked: All external internet access

Layer 2: Authentication & Authorization
├── OpenClaw Gateway: Bearer token (256-bit)
├── Sudo Proxy: HMAC-SHA256 signed responses
├── Dashboard: Session-based authentication
└── Service accounts: No interactive login

Layer 3: Input Validation
├── Citadel Guard: Prompt injection detection (20+ patterns)
├── Command allowlist: Structured commands only
├── Path validation: Restricted to allowed directories
└── Service validation: Only approved services can be managed

Layer 4: Trust Boundary Isolation
├── AI Agent: Runs as unprivileged user (dshannon)
├── Sudo Proxy: Separate process, validates all requests
├── Approval: External dashboard, cryptographic verification
└── Execution: Only after human approval with valid signature

Layer 5: Audit & Monitoring
├── OpenClaw logs: /opt/openclaw/logs/openclaw.log
├── Sudo Proxy audit: /opt/sudo-proxy/logs/audit.log
├── Agent audit: /data/ai-workspace/sysadmin-agent/logs/agent_audit.log
└── System audit: /var/log/audit/audit.log (auditd)
```

### 2.3 Human-in-the-Loop (HITL) Enforcement

**Why External HITL is Critical:**

The AI agent's built-in approval prompts run *inside* the agent's process. A compromised or manipulated agent could potentially bypass its own internal approval checks. The Sudo Approval Proxy addresses this by:

1. **External Trust Boundary**: Runs as a completely separate process
2. **No Raw Shell Access**: Only accepts structured command requests
3. **Cryptographic Verification**: Approvals must be HMAC-signed
4. **Timeout Protection**: Unanswered requests auto-deny after 120 seconds
5. **Audit Trail**: Every request/response is logged

**Approval Flow:**

```
Agent Process                    External Process
     │                                │
     │  1. Request approval           │
     │ ────────────────────────────► │
     │    (command_type, args,        │
     │     reason, source)            │
     │                                │
     │                           2. Validate against allowlist
     │                           3. Send to dashboard
     │                                │
     │                           4. Wait for human decision
     │                              (max 120 seconds)
     │                                │
     │  5. Return result              │
     │ ◄──────────────────────────── │
     │    (approved, HMAC signature,  │
     │     execution result)          │
     │                                │
```

---

## 3. Software Bill of Materials (SBOM)

### 3.1 Core Components

| Component | Version | Source | Purpose | License |
|-----------|---------|--------|---------|---------|
| OpenClaw Gateway | 1.0.0 | Local | AI gateway with security controls | Proprietary |
| Sudo Approval Proxy | 1.0.0 | Local | External HITL enforcement | Proprietary |
| Citadel Guard | 1.0.0 | Integrated | Prompt injection defense | Proprietary |
| SysAdmin Agent | 1.0.0 | Local | Streamlit dashboard | Proprietary |

### 3.2 Python Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.0 | Web framework (CPM Dashboard) |
| Flask-SocketIO | 5.3.6 | WebSocket support |
| Flask-CORS | 4.0.0 | Cross-origin resource sharing |
| eventlet | 0.35.2 | Async networking |
| python-socketio | 5.11.0 | Socket.IO protocol |
| streamlit | 1.32.0+ | SysAdmin Agent UI |
| langchain-core | 0.1.x | LLM framework |
| langchain-ollama | 0.1.x | Ollama integration |
| langgraph | 0.0.x | Agent workflow graphs |

### 3.3 System Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.9.x | Runtime (Rocky Linux 9 default) |
| Ollama | 0.1.x | LLM inference server |
| nftables | 1.0.x | Network filtering |
| systemd | 252+ | Service management |
| auditd | 3.0.x | System audit logging |

### 3.4 LLM Model

| Model | Size | Quantization | Source |
|-------|------|--------------|--------|
| Llama 3.3 70B Instruct | 70B params | Q4_K_M (42GB) | Meta (via Ollama) |

---

## 4. Configuration Files Reference

### 4.1 OpenClaw Gateway

**Location:** `/opt/openclaw/config/openclaw.json`

```json
{
  "gateway": {
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "type": "token",
      "token": "[REDACTED - 256-bit token]"
    }
  },
  "agent": {
    "model": "ollama/llama3.3:70b-instruct-q4_K_M",
    "modelOptions": {
      "baseUrl": "http://192.168.1.7:11434/v1"
    }
  },
  "agents": {
    "defaults": {
      "tools": {
        "allowlist": ["read"],
        "denylist": ["exec", "write", "process", "browser"]
      }
    }
  },
  "plugins": {
    "citadelGuard": {
      "enabled": true,
      "sensitivity": "high",
      "action": "sanitize_and_flag"
    }
  }
}
```

### 4.2 Sudo Proxy Command Allowlist

**Location:** `/opt/sudo-proxy/bin/sudo_proxy.py` (COMMAND_ALLOWLIST)

| Command Type | Description | Sudo Required | Dangerous |
|--------------|-------------|---------------|-----------|
| systemctl_status | Check service status | No | No |
| systemctl_restart | Restart service | Yes | Yes |
| systemctl_start | Start service | Yes | Yes |
| systemctl_stop | Stop service | Yes | Yes |
| ipactl_status | FreeIPA status | Yes | No |
| ipactl_restart | FreeIPA restart | Yes | Yes |
| firewall_list | List firewall rules | Yes | No |
| firewall_reload | Reload firewall | Yes | Yes |
| journalctl | View logs | Yes | No |
| cat_log | Tail log files | Yes | No |
| clamscan | Run antivirus scan | Yes | No |
| freshclam | Update AV signatures | Yes | No |
| suricata_update | Update IDS rules | Yes | No |
| openscap_scan | Run compliance scan | Yes | No |

### 4.3 Network Confinement

**Location:** `/etc/nftables/openclaw-egress.nft`

```nft
table inet openclaw_egress {
    chain output {
        type filter hook output priority 0; policy accept;

        # Allow loopback
        oifname "lo" accept

        # Allow local subnet
        ip daddr 192.168.1.0/24 accept

        # Block all other egress for openclaw-svc (UID 379)
        meta skuid 379 counter drop
    }
}
```

---

## 5. Service Configuration

### 5.1 Systemd Units

| Service | User | Port/Socket | Auto-Start |
|---------|------|-------------|------------|
| openclaw.service | openclaw-svc | 127.0.0.1:18789 | Yes |
| sudo-proxy.service | root | /run/sudo-proxy/sudo-proxy.sock | Yes |
| sysadmin-agent.service | dshannon | 127.0.0.1:8501 | Yes |
| cpm-dashboard.service | apache | 127.0.0.1:5000 | Yes |

### 5.2 Service Dependencies

```
                    ┌──────────────────┐
                    │ network.target   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  openclaw   │  │ sudo-proxy  │  │    httpd    │
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ sysadmin-agent  │
                   │ cpm-dashboard   │
                   └─────────────────┘
```

---

## 6. User Accounts & Permissions

### 6.1 Service Accounts

| Account | UID | Shell | Groups | Purpose |
|---------|-----|-------|--------|---------|
| openclaw-svc | 379 | /sbin/nologin | openclaw-svc | OpenClaw gateway |
| dshannon | 1000 | /bin/bash | wheel, openclaw-svc, wazuh, suricata | SysAdmin agent |
| apache | 48 | /sbin/nologin | apache | CPM dashboard |

### 6.2 Sudoers Configuration

**File:** `/etc/sudoers.d/90-openclaw-proxy`

```sudoers
# Deny ALL sudo access for openclaw-svc
# This ensures the AI cannot bypass the sudo proxy
openclaw-svc ALL=(ALL) !ALL
```

**File:** `/etc/sudoers.d/sysadmin-agent`

```sudoers
# Limited sudo for sysadmin-agent (commands must still go through proxy)
dshannon ALL=(ALL) NOPASSWD: /usr/bin/systemctl status *
dshannon ALL=(ALL) NOPASSWD: /usr/bin/journalctl *
dshannon ALL=(ALL) NOPASSWD: /usr/bin/tail -n * /var/log/*
```

---

## 7. Logging & Audit

### 7.1 Log Locations

| Log File | Content | Retention |
|----------|---------|-----------|
| /opt/openclaw/logs/openclaw.log | Gateway requests, Citadel Guard flags | 90 days |
| /opt/sudo-proxy/logs/audit.log | All approval requests/responses | 1 year |
| /data/ai-workspace/sysadmin-agent/logs/agent_audit.log | Command execution audit | 90 days |
| /var/log/audit/audit.log | System audit events | Per auditd policy |

### 7.2 Audit Event Types

| Event | Description | Severity |
|-------|-------------|----------|
| CITADEL_INJECTION_DETECTED | Prompt injection pattern matched | High |
| APPROVAL_REQUESTED | Privileged command awaiting approval | Info |
| APPROVAL_GRANTED | Human approved command execution | Info |
| APPROVAL_DENIED | Human denied command execution | Info |
| APPROVAL_TIMEOUT | Request timed out (auto-denied) | Warning |
| COMMAND_EXECUTED | Approved command was executed | Info |
| COMMAND_BLOCKED | Command blocked by allowlist | Warning |
| SIGNATURE_INVALID | HMAC verification failed | Critical |

### 7.3 Log Forwarding

All logs are forwarded to:
- Wazuh Manager (192.168.1.10) for SIEM analysis
- Graylog Server for centralized search
- Local retention per policy

---

## 8. Operational Procedures

### 8.1 Approving a Command

1. AI agent requests privileged operation
2. Sudo proxy validates command structure
3. Approval request appears in CPM Dashboard modal
4. Review: command type, arguments, AI's reason
5. Click **Approve** or **Deny**
6. Response is cryptographically signed and sent to proxy
7. If approved, command executes; result returned to AI

### 8.2 Responding to Citadel Guard Alerts

1. Alert appears in OpenClaw logs and/or dashboard
2. Review the flagged content and pattern matched
3. Determine if legitimate or malicious
4. If malicious: investigate source, block if external
5. If false positive: consider pattern tuning (with caution)
6. Document in incident response log

### 8.3 Service Recovery

```bash
# Restart all AI services
sudo systemctl restart openclaw sudo-proxy sysadmin-agent cpm-dashboard

# Check status
sudo systemctl status openclaw sudo-proxy sysadmin-agent cpm-dashboard

# View logs
sudo journalctl -u openclaw -u sudo-proxy -f
```

---

## 9. Security Considerations

### 9.1 Known Limitations

1. **LLM Unpredictability**: AI responses may vary; always verify critical information
2. **Pattern Evasion**: Sophisticated attacks may evade Citadel Guard patterns
3. **Insider Threat**: Dashboard operator with approval rights is trusted
4. **Network Dependency**: Requires connectivity to Ollama server (192.168.1.7)

### 9.2 Mitigations

1. All privileged actions require human approval (defense in depth)
2. Citadel Guard patterns updated based on threat intelligence
3. Audit logging enables forensic investigation
4. Approval timeout prevents indefinite pending states
5. Network confinement limits data exfiltration risk

### 9.3 Prohibited Actions

The AI system is explicitly prevented from:

- Executing raw shell commands (structured allowlist only)
- Accessing the internet (network confinement)
- Modifying IAM/FreeIPA users without approval
- Changing firewall rules without approval
- Installing packages without approval
- Accessing files outside allowed paths

---

## 10. Change History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-02-02 | 1.0 | SysAdmin Agent + Human | Initial architecture deployment |

---

## 11. Document Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| System Administrator | | | |
| Information Security Officer | | | |
| Authorizing Official | | | |

---

## Appendix A: File Inventory

```
/opt/openclaw/
├── bin/
│   └── openclaw-gateway.py          # Main gateway service
├── config/
│   └── openclaw.json                # Gateway configuration
├── logs/
│   └── openclaw.log                 # Gateway logs
└── venv/                            # Python virtual environment

/opt/sudo-proxy/
├── bin/
│   └── sudo_proxy.py                # Sudo approval proxy
├── keys/
│   └── approval.key                 # HMAC signing key
└── logs/
    └── audit.log                    # Approval audit log

/data/ai-workspace/sysadmin-agent/
├── app.py                           # Streamlit dashboard
├── config/
│   └── config.py                    # Agent configuration
├── tools/
│   ├── shell_tool.py                # Command execution (HITL)
│   └── sudo_proxy_client.py         # Proxy client library
├── graphs/
│   └── common.py                    # LangGraph utilities
└── logs/
    └── agent_audit.log              # Agent audit log

/opt/cpm-dashboard/
├── app.py                           # Flask dashboard
├── templates/
│   ├── dashboard.html               # Main UI
│   └── base.html                    # Base template
└── logs/
    └── access.log                   # HTTP access log

/etc/systemd/system/
├── openclaw.service
├── sudo-proxy.service
├── sysadmin-agent.service
└── cpm-dashboard.service

/etc/nftables/
└── openclaw-egress.nft              # Network confinement rules

/etc/sudoers.d/
├── 90-openclaw-proxy                # Deny sudo for openclaw-svc
└── sysadmin-agent                   # Limited sudo for agent
```

---

## Appendix B: Verification Checklist

- [ ] OpenClaw gateway responds on 127.0.0.1:18789 only
- [ ] Citadel Guard detects test injection patterns
- [ ] Sudo proxy denies commands not in allowlist
- [ ] Approval modal appears for privileged commands
- [ ] HMAC signature verification works correctly
- [ ] Timeout auto-denial functions (120 seconds)
- [ ] Network egress blocked for openclaw-svc user
- [ ] All audit logs being written
- [ ] Logs forwarded to Wazuh/Graylog
- [ ] Service auto-restart on failure
- [ ] No direct sudo access for openclaw-svc

---

*This document is classified as CUI and should be handled according to NIST 800-171 requirements for controlled unclassified information.*
