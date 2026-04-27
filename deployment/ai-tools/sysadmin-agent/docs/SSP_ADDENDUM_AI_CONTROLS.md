# System Security Plan Addendum
## AI-Assisted System Administration Controls

**Document ID:** SSP-ADD-AI-001
**Version:** 1.0
**Effective Date:** 2026-02-02
**System Name:** dc1.cyberinabox.net
**Classification:** CUI // SP-NOFORN

---

## 1. Purpose

This addendum documents the security controls implemented for the AI-assisted system administration capability on dc1.cyberinabox.net. It supplements the main System Security Plan (SSP) and should be incorporated into Section 13 (System and Communications Protection) and related control family sections.

---

## 2. System Description Update

### 2.1 New Components

The following components have been added to the system boundary:

| Component | Function | Location | Boundary |
|-----------|----------|----------|----------|
| OpenClaw Gateway | AI request gateway with security controls | dc1 (127.0.0.1:18789) | Internal |
| Citadel Guard | Prompt injection defense | Integrated in OpenClaw | Internal |
| Sudo Approval Proxy | External HITL enforcement | dc1 (Unix socket) | Internal |
| SysAdmin Agent Dashboard | AI chat interface | dc1 (127.0.0.1:8501) | Internal |
| Ollama LLM Server | Local AI inference | 192.168.1.7:11434 | Internal |

### 2.2 Data Flow Update

```
User → HTTPS → SysAdmin Dashboard → OpenClaw Gateway → Ollama LLM
                                  ↓
                            Citadel Guard (scan)
                                  ↓
                         Sudo Approval Proxy
                                  ↓
                         Human Approval (Dashboard)
                                  ↓
                         Command Execution
```

### 2.3 Network Diagram Update

Add the following to the network diagram:

- OpenClaw Gateway: 127.0.0.1:18789 (loopback only)
- Sudo Proxy: /run/sudo-proxy/sudo-proxy.sock (Unix socket)
- SysAdmin Agent: 127.0.0.1:8501 (proxied via httpd)
- Ollama connection: dc1 → 192.168.1.7:11434 (internal only)

---

## 3. NIST 800-171 Control Implementation Details

### 3.1 Access Control (3.1.x)

#### 3.1.1 - Limit System Access to Authorized Users

**Implementation:**
- OpenClaw Gateway requires Bearer token authentication
- Token: 256-bit cryptographically random value
- Stored in: `/opt/openclaw/config/openclaw.json`
- Dashboard access requires session authentication

**Evidence:**
```python
# From openclaw-gateway.py
auth_header = self.headers.get('Authorization', '')
expected = f"Bearer {self.config.auth_token}"
if not hmac.compare_digest(auth_header, expected):
    self.send_error(401, 'Unauthorized')
```

#### 3.1.2 - Limit System Access to Authorized Functions

**Implementation:**
- AI gateway binds to loopback interface only (127.0.0.1)
- External network access impossible
- Tool allowlist restricts AI capabilities to read-only by default

**Configuration:**
```json
{
  "gateway": {
    "bind": "loopback",
    "port": 18789
  },
  "agents": {
    "defaults": {
      "tools": {
        "allowlist": ["read"],
        "denylist": ["exec", "write", "process", "browser"]
      }
    }
  }
}
```

#### 3.1.5 - Employ Principle of Least Privilege

**Implementation:**
- AI service account (openclaw-svc) has no sudo access
- Sudoers explicitly denies all sudo: `openclaw-svc ALL=(ALL) !ALL`
- All privileged operations require human approval through external proxy

**Evidence:**
```
# /etc/sudoers.d/90-openclaw-proxy
openclaw-svc ALL=(ALL) !ALL
```

#### 3.1.7 - Prevent Non-Privileged Users from Executing Privileged Functions

**Implementation:**
- Three-tier command classification:
  1. ALLOWED_COMMANDS: Safe, no approval needed
  2. APPROVAL_REQUIRED_COMMANDS: Requires HITL approval
  3. FORBIDDEN_COMMANDS: Always blocked
- Sudo proxy validates all privileged requests
- Commands must match structured allowlist (no raw shell)

---

### 3.3 Audit and Accountability (3.3.x)

#### 3.3.1 - Create and Retain System Audit Logs

**Implementation:**
- OpenClaw Gateway: `/opt/openclaw/logs/openclaw.log`
- Sudo Proxy: `/opt/sudo-proxy/logs/audit.log`
- Agent Audit: `/data/ai-workspace/sysadmin-agent/logs/agent_audit.log`
- Retention: 90 days (gateway/agent), 1 year (sudo proxy)

**Log Format (Sudo Proxy):**
```json
{
  "timestamp": "2026-02-02T12:30:00.000Z",
  "event": "APPROVAL_REQUESTED",
  "command_type": "systemctl_restart",
  "args": ["httpd"],
  "reason": "User requested service restart",
  "details": "request_id=abc123, dangerous=true"
}
```

#### 3.3.2 - Ensure Actions Can Be Traced to Individual Users

**Implementation:**
- All AI requests include source identifier
- Approval responses include approver identity
- Dashboard session tracks authenticated user
- Audit logs correlate request_id across all components

**Audit Fields:**
- timestamp, user, source, command, result, approved_by, request_id

#### 3.3.4 - Alert on Audit Logging Process Failures

**Implementation:**
- Citadel Guard detections generate immediate alerts
- Log events forwarded to Wazuh for SIEM correlation
- Systemd monitors service health with auto-restart

---

### 3.4 Configuration Management (3.4.x)

#### 3.4.1 - Establish and Maintain Baseline Configurations

**Implementation:**
- OpenClaw config: `/opt/openclaw/config/openclaw.json`
- Sudo proxy allowlist: Embedded in `/opt/sudo-proxy/bin/sudo_proxy.py`
- Agent config: `/data/ai-workspace/sysadmin-agent/config/config.py`
- All configs version controlled in Git

**Baseline Documentation:**
- See: `docs/OPENCLAW_AI_SECURITY_ARCHITECTURE.md`

#### 3.4.2 - Establish and Enforce Security Configuration Settings

**Implementation:**
- Systemd unit files enforce security settings:
  - `ProtectSystem=full`
  - `PrivateTmp=true`
  - `NoNewPrivileges=true` (where applicable)
- nftables enforces network confinement
- fapolicyd controls executable permissions

#### 3.4.5 - Define and Document Configuration Settings

**Implementation:**
- All security-relevant settings documented in architecture document
- SBOM tracks all software components and versions
- Changes tracked via CHANGELOG.md

---

### 3.5 Identification and Authentication (3.5.x)

#### 3.5.1 - Identify System Users and Processes

**Implementation:**
- Service accounts:
  - `openclaw-svc` (UID 379): OpenClaw gateway
  - `dshannon` (UID 1000): SysAdmin agent
  - `apache` (UID 48): CPM dashboard
- All accounts have defined roles and permissions

#### 3.5.2 - Authenticate Users and Processes

**Implementation:**
- OpenClaw: Bearer token authentication
- Sudo Proxy: HMAC-SHA256 signed approval responses
- Dashboard: Session-based authentication
- Inter-service: Unix socket permissions (group-based)

**HMAC Verification:**
```python
def verify_signature(self, response):
    message = f"{response.request_id}:{response.approved}:{response.approver}:{response.timestamp}"
    expected_sig = hmac.new(self.hmac_key, message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(response.signature, expected_sig)
```

---

### 3.6 Incident Response (3.6.x)

#### 3.6.1 - Establish Operational Incident-Handling Capability

**Implementation:**
- Citadel Guard triggers alerts on injection detection
- Alert categories:
  - CITADEL_INJECTION_DETECTED (High)
  - SIGNATURE_INVALID (Critical)
  - APPROVAL_TIMEOUT (Warning)
- Alerts forwarded to Wazuh SIEM

#### 3.6.2 - Track and Document Security Incidents

**Implementation:**
- All security events logged with correlation IDs
- Logs retained per policy (90 days - 1 year)
- Forensic analysis capability via audit logs

---

### 3.13 System and Communications Protection (3.13.x)

#### 3.13.1 - Monitor Communications at External Boundaries

**Implementation:**
- AI gateway bound to loopback only (no external interface)
- nftables egress filtering blocks external connections
- All AI traffic stays within 192.168.1.0/24

#### 3.13.5 - Implement Cryptographic Mechanisms

**Implementation:**
- HMAC-SHA256 for approval response signing
- TLS for HTTPS dashboard access
- 256-bit authentication tokens

**Key Management:**
- HMAC key: `/opt/sudo-proxy/keys/approval.key`
- Key rotation: Manual, documented procedure

#### 3.13.8 - Implement Cryptographic Mechanisms for CUI

**Implementation:**
- No CUI transmitted to external networks
- AI processing occurs entirely on-premises
- LLM server (192.168.1.7) is air-gapped from internet

---

## 4. Risk Assessment Update

### 4.1 New Risks Introduced

| Risk ID | Description | Likelihood | Impact | Mitigation |
|---------|-------------|------------|--------|------------|
| AI-001 | Prompt injection attack | Medium | High | Citadel Guard, input sanitization |
| AI-002 | AI executes unauthorized command | Low | Critical | External HITL via sudo proxy |
| AI-003 | AI data exfiltration | Low | High | Network confinement, loopback binding |
| AI-004 | Approval bypass | Very Low | Critical | HMAC signatures, external trust boundary |
| AI-005 | LLM produces harmful output | Medium | Medium | Human review, response scanning |

### 4.2 Residual Risk

After implementing all controls, residual risk is assessed as **LOW** due to:
1. Multiple defense layers
2. External trust boundary for privileged operations
3. Cryptographic verification of approvals
4. Complete audit trail
5. Network isolation

---

## 5. Authorization Boundary Update

The following components are added to the authorization boundary:

**Inside Boundary:**
- OpenClaw Gateway (dc1)
- Sudo Approval Proxy (dc1)
- SysAdmin Agent Dashboard (dc1)
- Citadel Guard (integrated)
- Ollama LLM Server (192.168.1.7)
- Llama 3.3 70B model

**Outside Boundary:**
- No external AI services used
- No cloud dependencies
- No internet connectivity for AI components

---

## 6. Interconnection Update

### 6.1 Internal Interconnections

| Source | Destination | Protocol | Port | Purpose |
|--------|-------------|----------|------|---------|
| httpd | SysAdmin Agent | HTTP | 8501 | Reverse proxy |
| httpd | CPM Dashboard | HTTP | 5000 | Reverse proxy |
| SysAdmin Agent | OpenClaw | HTTP | 18789 | AI requests |
| OpenClaw | Ollama | HTTP | 11434 | LLM inference |
| SysAdmin Agent | Sudo Proxy | Unix Socket | - | Approval requests |
| CPM Dashboard | Sudo Proxy | Unix Socket | - | Approval responses |

### 6.2 External Interconnections

**None.** All AI components operate within the internal network boundary.

---

## 7. Continuous Monitoring Update

Add the following to continuous monitoring procedures:

1. **Daily:**
   - Review Citadel Guard detection logs
   - Verify sudo proxy service health
   - Check for approval timeout events

2. **Weekly:**
   - Analyze AI usage patterns for anomalies
   - Review denied approval requests
   - Validate audit log integrity

3. **Monthly:**
   - Test HITL approval flow
   - Verify network confinement rules
   - Update Citadel Guard patterns if needed

4. **Quarterly:**
   - Full security assessment of AI components
   - Review and update command allowlists
   - Penetration test prompt injection defenses

---

## 8. Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| System Owner | | | |
| ISSM | | | |
| ISSO | | | |
| Authorizing Official | | | |

---

## 9. References

- NIST SP 800-171 Rev 2, Protecting Controlled Unclassified Information
- NIST SP 800-53 Rev 5, Security and Privacy Controls
- NIST AI RMF 1.0, AI Risk Management Framework
- System Security Plan (main document)
- OpenClaw AI Security Architecture (docs/OPENCLAW_AI_SECURITY_ARCHITECTURE.md)
- Software Bill of Materials (docs/SBOM.json)

---

*This addendum is classified as CUI and must be protected according to NIST 800-171 requirements.*
