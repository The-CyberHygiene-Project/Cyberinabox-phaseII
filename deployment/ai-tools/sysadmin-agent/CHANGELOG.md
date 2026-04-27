# Changelog

All notable changes to the SysAdmin Agent and OpenClaw AI platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-02

### Added

#### OpenClaw AI Gateway
- Implemented hardened AI gateway with loopback-only binding (127.0.0.1:18789)
- Added token-based authentication (256-bit Bearer tokens)
- Integrated Citadel Guard prompt injection defense with 20+ detection patterns
- Added OpenAI-compatible endpoint (`/v1/chat/completions`) for LangChain integration
- Implemented tool allowlist/denylist enforcement
- Added comprehensive audit logging

#### Sudo Approval Proxy (HITL Enforcement)
- Created external sudo approval proxy running outside AI agent's trust boundary
- Implemented structured command allowlist (no raw shell execution)
- Added HMAC-SHA256 signed approval responses
- Configured 120-second timeout with automatic denial
- Added dashboard webhook integration for approval UI
- Comprehensive audit logging for all approval requests/responses

#### Security Controls
- Network confinement via nftables (UID-based egress filtering)
- Service account isolation (openclaw-svc with nologin shell)
- Sudoers configuration denying direct sudo for AI user
- fapolicyd rules for execution control

#### SysAdmin Agent Integration
- Routed all LLM requests through OpenClaw gateway
- Integrated shell_tool.py with sudo-proxy client
- Added structured command mapping for privileged operations
- Updated config to use OpenClaw endpoint (http://127.0.0.1:18789/v1)

#### CPM Dashboard Enhancements
- Added WebSocket support via Flask-SocketIO
- Implemented sudo approval modal for HITL workflow
- Added OpenClaw status endpoint
- Integrated real-time approval notifications

#### Documentation
- Created comprehensive security architecture document
- Added CycloneDX SBOM (Software Bill of Materials)
- Documented NIST 800-171 control mappings
- Added operational procedures and verification checklist

### Security
- All privileged AI operations now require human approval through external proxy
- Prompt injection attacks detected and sanitized by Citadel Guard
- Network egress blocked for AI service account
- Cryptographic verification of approval responses

### Changed
- Deprecated cyberhygiene-ai.service in favor of integrated SysAdmin Agent Dashboard
- Updated sysadmin-agent config to route through OpenClaw instead of direct Ollama

### Deprecated
- cyberhygiene-ai.service (port 5500) - replaced by sysadmin-agent.service with OpenClaw integration

### Removed
- Direct Ollama access from SysAdmin Agent (now proxied through OpenClaw)

## [Unreleased]

### Planned
- Lobster plugin for workflow approval gates
- Custom Citadel Guard rules for DC-specific attack patterns
- Integration with Wazuh for alert correlation
- Automated security report generation

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-02-02 | Initial OpenClaw integration with full HITL enforcement |
