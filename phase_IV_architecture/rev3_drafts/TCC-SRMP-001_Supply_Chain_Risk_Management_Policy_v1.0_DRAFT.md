# Supply Chain Risk Management Policy

**Policy Number:** TCC-SRMP-001
**Version:** 1.0 DRAFT
**Effective Date:** [TBD - Target: Phase 2 completion]
**Last Reviewed:** March 18, 2026
**Policy Owner:** System Owner (sysadmin)
**Approval Authority:** System Owner (sysadmin)

---

## 1. PURPOSE

This policy establishes requirements for identifying, assessing, and mitigating supply chain risks within the CyberHygiene Production Network (CPN). This policy satisfies the Supply Chain Risk Management (SR) control family requirements in NIST SP 800-171 Revision 3, focusing on protecting the integrity of software and hardware throughout the supply chain.

---

## 2. SCOPE

This policy applies to:
- All software components used in CPN systems (operating systems, applications, libraries, dependencies)
- All hardware components (servers, workstations, network equipment, storage)
- Software repositories and update sources (Rocky Linux repos, EPEL, upstream sources)
- Hardware and software vendors and suppliers
- The Software Bill of Materials (SBOM) documenting all components

**In Scope:**
- 4 CPN systems: dc1 (.10), workstation1 (.115), workstation2 (.104), workstation3 (.113)
- 5,626 software packages tracked in SBOM v2.4 (to be enhanced to v3.0)
- Hardware: Dell/HP servers, workstations; network equipment (pfSense appliance, switches)
- Supply chain: Red Hat → Rocky Linux → CyberHygiene (software provenance)

**Out of Scope:**
- Office supplies and non-IT equipment
- Services not involving software/hardware supply chain (e.g., internet connectivity)

---

## 3. POLICY STATEMENTS

### 3.1 Supply Chain Risk Management Plan — NIST 3.13.1 (SR-2)

**3.1.1 Supply Chain Risk Management Strategy**

CyberHygiene shall manage supply chain risks through:

a) **Software Bill of Materials (SBOM):**
   - Maintain comprehensive inventory of all software components
   - Track package names, versions, sources, and signatures
   - Update SBOM quarterly or upon significant system changes
   - **Current:** SBOM v2.4 (5,626 packages across 6 systems)
   - **Planned:** SBOM v3.0 with supply chain provenance (Phase 3)

b) **Component provenance tracking:**
   - Document source of all software (upstream developer, repository, distributor)
   - Verify authenticity via digital signatures (RPM GPG signatures)
   - Track trust chain: Upstream → Distributor → CyberHygiene

c) **Vulnerability monitoring:**
   - Monitor CVE databases for vulnerabilities in SBOM components
   - Wazuh vulnerability detection scans daily
   - OpenSCAP scans weekly for known vulnerabilities
   - Subscribe to security advisories from vendors

d) **Vendor assessment:**
   - Evaluate vendor security posture before acquisition (per TCC-SAP-001)
   - Prefer trusted vendors with strong security track records
   - Document vendor security certifications and practices

e) **Supply chain controls:**
   - Cryptographic verification of software (GPG signatures)
   - FIPS 140-2 validated cryptographic modules
   - Secure update mechanisms (HTTPS, signed repos)
   - Immutable audit logs of software installations/updates

**3.1.2 Supply Chain Risk Assessment Frequency (ODP-SR-1)**

Supply chain risk assessment shall be conducted:

a) **Annually** — Formal assessment integrated with annual risk assessment
   - Review SBOM for high-risk components
   - Assess vendor security postures
   - Evaluate supply chain threats (e.g., compromised repos, malicious packages)
   - Document findings and mitigation strategies
   - **Target:** April each year (aligned with 3.11.1 risk assessment per POA&M)

b) **Event-driven assessments:**
   - Upon discovery of major supply chain incidents (e.g., SolarWinds, Log4Shell)
   - Upon addition of new vendors or software sources
   - Upon significant SBOM changes (>10% of packages updated)
   - Upon vendor security incident affecting our components

**Documentation:** Supply chain risk assessment documented in annual Risk Assessment Report (Section on Supply Chain Risks)

---

### 3.2 Supply Chain Risk Management Controls — NIST 3.13.2 (SR-3)

**3.2.1 Software Integrity Verification**

All software installations and updates shall be cryptographically verified:

a) **RPM Package Signature Verification:**
   - All RPM packages verified with GPG signatures before installation
   - Rocky Linux GPG keys: `/etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9`
   - EPEL GPG keys: `/etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-9`
   - **Verification command:** `rpm --checksig <package>`
   - dnf/yum automatically verify signatures (enabled by default via `gpgcheck=1` in repo configs)

**Current Configuration:**
```
/etc/yum.repos.d/rocky.repo:
[baseos]
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9

/etc/yum.repos.d/epel.repo:
[epel]
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-9
```

b) **Repository Trust Chain:**
   - **Tier 1: Upstream (Red Hat)** — Source code from upstream projects (kernel.org, gnu.org, etc.)
   - **Tier 2: Enterprise Linux (RHEL)** — Red Hat Enterprise Linux packages (signed by Red Hat)
   - **Tier 3: Rocky Linux** — Rebuilt from RHEL sources (signed by Rocky Enterprise Software Foundation)
   - **Tier 4: CyberHygiene** — Deployed on CPN systems (signature verified at install time)

**Trust Assumption:** Rocky Linux is a downstream rebuild of RHEL, maintained by a community with strong security practices. Rocky Linux signs all packages with their GPG keys, providing chain of trust from RHEL → Rocky → CyberHygiene.

c) **Repository Security:**
   - All repository connections use HTTPS (encrypted)
   - Repository metadata signed (repomd.xml.asc)
   - Repository mirrors validated against Rocky Linux CDN
   - No third-party or untrusted repositories enabled

**Repository URLs (HTTPS only):**
- Rocky Linux: `https://download.rockylinux.org/pub/rocky/9/`
- EPEL: `https://dl.fedoraproject.org/pub/epel/9/`

---

**3.2.2 FIPS 140-2 Cryptographic Validation**

All cryptographic operations use FIPS 140-2 validated modules:

a) **Validated Cryptographic Modules:**
   - **OpenSSL FIPS module:** Certificate #3980
   - **libgcrypt FIPS module:** Certificate #3739
   - **Kernel crypto API:** Certificate #4046

b) **FIPS Mode Enforcement:**
   - Kernel booted with `fips=1` parameter
   - `/proc/sys/crypto/fips_enabled` = 1
   - OpenSSL configured for FIPS mode: `/etc/pki/tls/openssl.cnf`
   - Cryptographic self-tests run at boot

c) **Supply Chain Benefit:**
   - FIPS-validated modules provide assurance that cryptographic implementations are not backdoored or weakened
   - Validation includes source code review, known-answer tests, and vendor affirmations
   - Reduces supply chain risk of compromised cryptography

**Verification:**
```bash
cat /proc/sys/crypto/fips_enabled  # Should output: 1
openssl version  # Should include "fips"
```

---

**3.2.3 Secure Update Mechanism**

Software updates are delivered securely:

a) **Automated Security Updates (dnf-automatic):**
   - Daily checks for security updates (4:00 AM)
   - Security updates auto-applied (non-kernel)
   - Kernel updates reviewed manually before applying
   - Configuration: `/etc/dnf/automatic.conf`

b) **Update Integrity:**
   - Updates downloaded over HTTPS
   - Package signatures verified before installation
   - Failed signature verification blocks installation
   - Update logs: `/var/log/dnf.log`, monitored by Wazuh

c) **Rollback Capability:**
   - Previous kernel versions retained (rollback if update causes issues)
   - Configuration files versioned in Git (rollback configs if needed)
   - Snapshots before major updates (optional, if using LVM snapshots)

---

### 3.3 Supply Chain Protection — NIST 3.13.3 (SR-3 continued)

**3.3.1 Tamper Detection**

Unauthorized changes to software are detected via:

a) **File Integrity Monitoring (FIM) — Wazuh:**
   - Monitors critical files and directories for changes
   - Generates alerts on modifications
   - Monitored paths:
     - `/etc/` — Configuration files
     - `/usr/bin/`, `/usr/sbin/` — System binaries
     - `/boot/` — Kernel and boot files
     - `/lib/modules/` — Kernel modules
   - FIM alerts sent to Wazuh dashboard in real-time

b) **RPM Verification:**
   - Verify installed package integrity: `rpm -Va`
   - Detects modified files (compared to package manifest)
   - Run monthly via cron or on-demand
   - Alerts on unexpected modifications

c) **Audit Logging:**
   - auditd logs all software installations/removals
   - Rule: `-w /usr/bin/ -p wa -k software_mgmt`
   - Logs centralized to Wazuh SIEM

---

**3.3.2 Anti-Malware Scanning**

Detect malicious code in software supply chain:

a) **ClamAV Antivirus:**
   - Daily signature updates via freshclam
   - Weekly full system scans
   - On-access scanning for critical directories (optional)
   - Detects known malware, trojans, backdoors

b) **YARA Custom Rules:**
   - Custom YARA rules for suspicious patterns
   - Rules detect:
     - Cryptocurrency miners
     - Backdoor shells
     - Rootkits
     - Obfuscated code
   - Rules location: `/var/lib/yara/rules/`
   - Updated as new threats identified

c) **Supply Chain Incident Response:**
   - If malware detected in SBOM component:
     1. Isolate affected system(s)
     2. Identify malicious package source
     3. Remove/quarantine package
     4. Verify other systems not affected
     5. Report to upstream vendor/repository
     6. Document in incident response log (TCC-IRP-001)

---

### 3.4 Supply Chain Provenance — NIST 3.13.4 (SR-4)

**3.4.1 Component Provenance Tracking**

For all SBOM components, document:

a) **Package Metadata:**
   - Package name (e.g., `openssl`)
   - Version and release (e.g., `3.0.7-16.el9_1`)
   - Architecture (e.g., `x86_64`)
   - Repository source (e.g., `rocky-baseos`)

b) **Provenance Information:**
   - **Upstream source:** Original developer/project (e.g., OpenSSL Project, openssl.org)
   - **Distributor:** Red Hat (RHEL) → Rocky Linux
   - **Build information:** Rocky Linux build system (koji.rockylinux.org)
   - **Signing authority:** Rocky Enterprise Software Foundation (GPG key: 0x350D275D)
   - **Installation date:** When package installed on CPN system
   - **Update history:** Previous versions, update dates

c) **Provenance Verification:**
   - RPM signature verified = authentic package from Rocky Linux
   - Rocky Linux transparency: All packages built from public RHEL SRPMs
   - Build logs publicly available (if needed for investigation)

**SBOM v3.0 Enhancement (Phase 3):**
- Add provenance columns to SBOM v2.4:
  - **Upstream Source** (project name, URL)
  - **Signing Authority** (GPG key fingerprint)
  - **Installation Date**
  - **Last Update Date**
  - **Critical Component Flag** (Yes/No per ODP-SR-2)

**3.4.2 Critical Component Designation (ODP-SR-2)**

Critical components are those that, if compromised, could significantly impact system security:

**Critical Component Criteria:**
1. **Cryptographic components:** OpenSSL, libgcrypt, GnuTLS, kernel crypto
2. **Authentication components:** PAM, FreeIPA, SSSD, pam_google_authenticator
3. **Network security:** OpenSSH, firewalld, nftables, iptables
4. **Audit & logging:** auditd, rsyslog, Wazuh agent
5. **Core system:** kernel, systemd, glibc, bash
6. **Key applications:** Apache, PostgreSQL (if used), FreeIPA server components

**Top 100 Critical Components (Examples):**
1. `kernel` — Operating system kernel
2. `openssl` — Cryptographic library (FIPS module)
3. `openssh-server` — SSH daemon
4. `pam` — Pluggable Authentication Modules
5. `audit` — auditd audit framework
6. `ipa-server` — FreeIPA identity management
7. `wazuh-agent` — Wazuh SIEM agent
8. `firewalld` — Firewall management
9. `systemd` — System and service manager
10. `glibc` — C standard library
11. `bash` — Shell
12. `sudo` — Privilege escalation
13. `rsyslog` — Syslog daemon
14. `selinux-policy` — SELinux mandatory access control
15. `cryptsetup` — LUKS disk encryption
... (Full list of 100 to be documented in SBOM v3.0)

**Critical Component Monitoring:**
- CVEs affecting critical components prioritized (remediate within 7 days)
- Wazuh vulnerability detection flags critical component CVEs
- Critical component updates tested in lab before production (if feasible)

---

### 3.5 Acquisition Strategies and Tools — NIST 3.13.5 (SR-5)

**3.5.1 Trusted Vendor Strategy**

CyberHygiene prioritizes trusted vendors with established security practices:

**Tier 1: Trusted Open-Source Foundations**
- **Rocky Enterprise Software Foundation** — Rocky Linux (RHEL rebuild)
- **Fedora Project** — EPEL (Extra Packages for Enterprise Linux)
- **Apache Software Foundation** — Apache HTTP Server
- **OpenSSH Project** — OpenSSH
- **FreeIPA Project** — Identity management
- **Wazuh, Inc.** — Wazuh SIEM

**Rationale:** Open-source projects with:
- Large, active communities (transparency, peer review)
- Responsible disclosure programs
- CVE database coverage
- Long track records (10+ years)
- No profit motive to cut security corners

**Tier 2: Commercial Vendors with Strong Security**
- **SSL.com** — TLS certificates (WebTrust audited, publicly trusted CA)
- **Dell / HP** — Hardware (established vendors with supply chain controls)

**3.5.2 COTS-Only Strategy**

CyberHygiene uses 100% Commercial Off-The-Shelf (COTS) products — no custom development.

**Supply Chain Benefits:**
- **Broad adoption:** COTS products used by thousands of organizations (vulnerabilities discovered faster)
- **Vendor support:** Commercial or community support for security updates
- **Peer review:** Open-source COTS products benefit from public code audits
- **Predictable updates:** Established release and patching cycles

**Avoidance of Custom Code:**
- No custom development = no risk of introducing vulnerabilities in-house
- No reliance on single developer (bus factor = 1)
- Easier to replace or migrate if vendor/project abandoned

**3.5.3 Open-Source Preference**

Where feasible, CyberHygiene prefers open-source over proprietary:

**Security Advantages of Open Source:**
1. **Transparency:** Source code publicly auditable (no backdoors or hidden vulnerabilities)
2. **Community vetting:** Thousands of eyes reviewing code
3. **Rapid patching:** Community can patch CVEs faster than proprietary vendors
4. **No vendor lock-in:** Can fork or migrate if project direction changes
5. **Supply chain visibility:** Can trace code provenance to original developers

**Examples:**
- Rocky Linux (open-source) vs. RHEL (proprietary, but Rocky is RHEL-compatible)
- OpenSSH (open-source) vs. commercial SSH implementations
- FreeIPA (open-source) vs. Microsoft Active Directory (proprietary)
- Wazuh (open-source) vs. commercial SIEM products

**Exception:** Proprietary software acceptable if:
- No open-source equivalent exists
- Commercial support required (e.g., SSL.com for publicly trusted certificates)
- Strong vendor security posture (security certifications, track record)

**3.5.4 Repository Restriction**

Only trusted repositories are enabled on CPN systems:

**Allowed Repositories:**
- **rocky-baseos:** Rocky Linux base operating system
- **rocky-appstream:** Rocky Linux application stream
- **rocky-extras:** Rocky Linux extras
- **epel:** Extra Packages for Enterprise Linux (Fedora Project)

**Prohibited:**
- Third-party repositories (e.g., rpmforge, remi, atrpms) — not trusted
- Personal repositories (e.g., user-maintained Copr repos) — insufficient vetting
- Unverified sources (direct RPM downloads without signature verification)

**Exception Process:**
- If package needed from non-standard repo:
  1. Evaluate repository trustworthiness (maintainer, security practices)
  2. Verify package signature with maintainer's GPG key
  3. Install package manually (not via enabled repo)
  4. Add package to SBOM with "Non-standard Source" flag
  5. Document justification and risk acceptance by System Owner

---

## 4. ROLES AND [REDACTED_TOTP_SECRET]

### 4.1 System Owner (sysadmin)

- Approve Supply Chain Risk Management Policy
- Conduct annual supply chain risk assessment (integrated with 3.11.1 risk assessment)
- Designate critical components (top 100 list)
- Approve exceptions to trusted vendor strategy
- Review SBOM quarterly for high-risk components

### 4.2 Administrator (sysadmin)

- Maintain Software Bill of Materials (SBOM)
- Update SBOM quarterly or upon significant changes
- Enhance SBOM v2.4 → v3.0 (Phase 3) with provenance
- Monitor CVE databases for SBOM component vulnerabilities
- Verify RPM signatures for all installations
- Maintain FIPS mode on all systems
- Respond to supply chain incidents per TCC-IRP-001

---

## 5. PROCEDURES

### 5.1 SBOM Maintenance Procedure

**Frequency:** Quarterly (Jan, Apr, Jul, Oct) or upon significant changes

**Steps:**

1. **Generate package list for each system:**
   ```bash
   # On each system (dc1, workstation1, workstation2, workstation3):
   rpm -qa --queryformat "%{NAME}|%{VERSION}|%{RELEASE}|%{ARCH}|%{PACKAGER}|%{INSTALLTIME:date}\n" | sort > /tmp/sbom_$(hostname)_$(date +%Y%m%d).txt
   ```

2. **Consolidate into master SBOM:**
   - Merge package lists from all 4 systems
   - Deduplicate (same package on multiple systems)
   - Add metadata columns:
     - **System(s):** Which systems have this package (e.g., "dc1, workstation1, workstation2, workstation3" or "dc1 only")
     - **Repository:** rocky-baseos, rocky-appstream, epel, etc.
     - **Upstream Source:** Project name and URL (Phase 3 enhancement)
     - **Critical Component:** Yes/No flag (Phase 3 enhancement)

3. **Verify signatures (sample check):**
   - Randomly select 20 packages from SBOM
   - Verify signatures: `rpm --checksig <package>`
   - All should show "signatures OK"
   - Document verification in SBOM changelog

4. **Compare to previous SBOM:**
   - Identify new packages (additions)
   - Identify removed packages (removals)
   - Identify updated packages (version changes)
   - Assess security impact of changes

5. **Update SBOM version and publish:**
   - Increment version (e.g., v2.4 → v2.5 quarterly, v2.4 → v3.0 for Phase 3 enhancement)
   - Save SBOM: `/home/sysadmin/CyberSecurity/Current/Evidence/Software_Inventory/Software_Bill_of_Materials_v2.X.md`
   - Add changelog entry (date, version, # packages, notable changes)

6. **Review for high-risk components:**
   - Scan SBOM for packages with known CVEs (Wazuh vulnerability detection)
   - Flag packages from untrusted sources (should be zero)
   - Flag unsigned packages (should be zero)
   - Document findings and remediation in POA&M if needed

---

### 5.2 Supply Chain Risk Assessment Procedure

**Frequency:** Annually (April, integrated with 3.11.1 risk assessment)

**Steps:**

1. **Identify supply chain threats:**
   - **Compromised repositories** — Attacker injects malicious packages into Rocky/EPEL repos
   - **Malicious upstream** — Upstream developer intentionally backdoors project (rare but possible, e.g., xz-utils incident)
   - **Build system compromise** — Rocky Linux build system (koji) compromised
   - **Dependency confusion** — Attacker uploads malicious package with same name to public repo
   - **Typosquatting** — Attacker creates package with similar name to legitimate package
   - **EOL/abandoned projects** — Software no longer maintained, vulnerabilities unpatched

2. **Assess likelihood and impact:**
   - For each threat, rate likelihood (High/Medium/Low) and impact (High/Medium/Low)
   - Calculate risk score (Likelihood × Impact)

3. **Identify vulnerabilities:**
   - **Dependency on single repository** — All packages from Rocky/EPEL (no diversity)
   - **Limited supply chain visibility** — Don't audit upstream source code directly
   - **Trust in GPG signatures** — Assumes GPG keys not compromised

4. **Evaluate existing controls:**
   - ✅ **GPG signature verification** — Mitigates compromised repository (unsigned packages rejected)
   - ✅ **FIPS 140-2 crypto** — Mitigates compromised cryptography
   - ✅ **File integrity monitoring (Wazuh)** — Detects tampering post-installation
   - ✅ **Anti-malware (ClamAV, YARA)** — Detects known malicious code
   - ✅ **Audit logging** — Provides forensic evidence of installations
   - ✅ **SBOM** — Enables rapid identification of affected components during incidents (e.g., Log4Shell)

5. **Document risk treatment decisions:**
   - For each high/medium risk: Accept, Mitigate, Transfer, or Avoid
   - Document justification (e.g., "Accept dependency on Rocky Linux due to strong community vetting and signature verification")

6. **Update Supply Chain Risk Assessment section in Risk Assessment Report:**
   - Add as dedicated section in annual Risk Assessment Report (GAP-001 template, Section 4 "Supply Chain Risks")
   - Document findings, controls, residual risks

7. **Update SBOM for critical components:**
   - Review top 100 critical components list
   - Add/remove components based on new threats or architecture changes
   - Flag in SBOM v3.0 (Phase 3)

---

### 5.3 Supply Chain Incident Response Procedure

**When to Use:** Discovery of supply chain compromise (e.g., SolarWinds-type incident, malicious package)

**Steps:**

1. **Detect incident:**
   - Vendor security advisory (e.g., "Package XYZ version 1.2.3 contained backdoor")
   - ClamAV/YARA detection of malware in installed package
   - Wazuh FIM alert on unexpected binary modification
   - Public disclosure (news, CVE, security mailing lists)

2. **Assess impact — Check SBOM:**
   - Is affected package in SBOM? (Search SBOM for package name/version)
   - Which systems are affected? (SBOM lists systems per package)
   - Is package a critical component? (Check critical component flag)

3. **Contain incident:**
   - If package is running: Stop service immediately
   - If exploit possible: Isolate affected systems from network
   - If CUI potentially accessed: Treat as CUI breach (DFARS 252.204-7012 reporting)

4. **Eradicate malicious component:**
   - Remove affected package: `dnf remove <package>`
   - If dependencies require package: Find alternate package or mitigate differently
   - Verify removal: Check SBOM, re-scan with ClamAV/YARA

5. **Investigate scope:**
   - Review audit logs: When was package installed? What actions occurred?
   - Review Wazuh logs: Any suspicious activity from compromised package?
   - Forensics: Preserve evidence (system snapshots, logs) for 90 days (DFARS requirement)

6. **Recover:**
   - Install patched version of package (if available)
   - Restore from backup if system integrity questionable
   - Re-scan with OpenSCAP to verify baseline compliance

7. **Report incident:**
   - Internal: Document in incident log (TCC-IRP-001)
   - External (if CUI affected):
     - US-CERT: https://www.us-cert.gov/report (within 1 hour)
     - Contracting Officer: Within 72 hours (DFARS 252.204-7012)
     - DoD: https://dibnet.dod.mil (within 72 hours if DoD contract)

8. **Lessons learned:**
   - Update TCC-SRMP-001 policy if needed
   - Add detection signatures (YARA rules for similar malware)
   - Enhance monitoring for similar incidents
   - Document in supply chain risk assessment (next annual cycle)

---

## 6. COMPLIANCE

This policy supports compliance with:
- NIST SP 800-171 Rev 3 Supply Chain Risk Management (SR) family:
  - 3.13.1 (SR-2): Supply Chain Risk Management Plan
  - 3.13.2 (SR-3): Supply Chain Risk Management Controls
  - 3.13.3 (SR-3): Supply Chain Protection (Tamper Detection, Malware Scanning)
  - 3.13.4 (SR-4): Provenance
  - 3.13.5 (SR-5): Acquisition Strategies, Tools, and Methods
- NIST SP 800-161 Rev 1 (Cybersecurity Supply Chain Risk Management Practices)
- DFARS 252.204-7012 (Safeguarding CUI — incident reporting includes supply chain)
- CMMC Level 2 (SR domain)
- Executive Order 14028 (Improving the Nation's Cybersecurity — SBOM requirements)

---

## 7. DEFINITIONS

**Critical Component:** A software or hardware component that, if compromised, could significantly impact system security (e.g., kernel, OpenSSL, SSH).

**Provenance:** The origin and history of a component, including upstream source, build process, and distribution chain.

**Software Bill of Materials (SBOM):** A comprehensive inventory of software components, including names, versions, sources, and dependencies.

**Supply Chain:** The network of entities involved in producing, distributing, and delivering software and hardware to CyberHygiene (e.g., developers, build systems, repositories, vendors).

**Supply Chain Risk:** The potential for an adversary to sabotage, maliciously introduce unwanted functionality, or otherwise subvert the design, integrity, or operation of a component through the supply chain.

**Tamper Detection:** Mechanisms to detect unauthorized modifications to software or hardware.

---

## 8. REFERENCES

- NIST SP 800-171 Rev 3 (SR family, controls 3.13.x)
- NIST SP 800-53 Rev 5 (SR family source controls)
- NIST SP 800-161 Rev 1 (Cybersecurity Supply Chain Risk Management Practices)
- Executive Order 14028 (Improving the Nation's Cybersecurity, Section 4: Enhancing Software Supply Chain Security)
- CISA Software Bill of Materials (SBOM) Resources: https://www.cisa.gov/sbom
- DFARS 252.204-7012 (Safeguarding CUI and Cyber Incident Reporting)
- Rocky Linux Security: https://wiki.rockylinux.org/rocky/security/
- CyberHygiene SBOM v2.4 (current), v3.0 (planned Phase 3)

---

## 9. POLICY REVIEW

This policy shall be reviewed and updated:
- **Annually** — Target month: April (aligned with SSP review and supply chain risk assessment)
- **Upon supply chain incidents** — Major incidents (e.g., SolarWinds-scale) trigger policy review
- **Upon significant SBOM changes** — Addition of new major software components or repositories

**Next Review Date:** April 2027

---

## 10. APPROVAL

**Policy Approved By:**

**System Owner:** _____________________________ Date: __________
sysadmin

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 DRAFT | March 18, 2026 | Claude (AI Assistant) | Initial draft created for Rev 3 transition (Phase 2) |
| 1.0 | [TBD] | sysadmin | Reviewed, customized, and approved |

---

**END OF POLICY**

---

## APPENDIX A: CRITICAL COMPONENTS LIST (TOP 100)

**Instructions:** This list identifies the top 100 critical software components in the CyberHygiene SBOM. These components are designated "critical" because compromise could significantly impact system security. Critical components receive priority patching (within 7 days for critical CVEs) and enhanced monitoring.

**Criteria for Critical Component:**
1. **Cryptographic:** Provides encryption, signing, or key management
2. **Authentication:** Provides user/system authentication or authorization
3. **Network Security:** Provides network boundary protection or secure communications
4. **Audit/Logging:** Provides security event logging or monitoring
5. **Core System:** Essential for system operation (kernel, libc, init system)
6. **High Privilege:** Runs with root or elevated privileges
7. **External Facing:** Exposed to untrusted networks (internet, remote users)

---

### Category 1: Cryptographic Components (15 components)

| # | Package Name | Description | Rationale |
|---|--------------|-------------|-----------|
| 1 | `openssl` | Cryptographic library (FIPS module) | FIPS 140-2 validated, used system-wide |
| 2 | `openssl-libs` | OpenSSL shared libraries | Runtime dependency for TLS |
| 3 | `libgcrypt` | Cryptographic library (FIPS module) | FIPS 140-2 validated, used by GnuPG |
| 4 | `gnutls` | TLS protocol implementation | Alternative TLS library |
| 5 | `nss` | Network Security Services (Mozilla crypto) | Used by Firefox, system crypto |
| 6 | `kernel` (crypto subsystem) | Kernel cryptographic API (FIPS module) | In-kernel encryption (dm-crypt, IPsec) |
| 7 | `cryptsetup` | LUKS disk encryption utility | Manages encrypted volumes |
| 8 | `gnupg2` | GPG encryption and signing | RPM signature verification |
| 9 | `openssh` | SSH cryptographic library | SSH key generation, algorithms |
| 10 | `crypto-policies` | System-wide crypto policy framework | Enforces TLS 1.2+ minimum |
| 11 | `ca-certificates` | Trusted CA certificate bundle | TLS certificate validation |
| 12 | `certmonger` | Certificate management daemon (FreeIPA) | Auto-renewal of certs |
| 13 | `p11-kit` | PKCS#11 module management | Smart card, HSM support |
| 14 | `nettle` | Low-level cryptographic library | Used by GnuTLS |
| 15 | `libssh` | SSH protocol library | Used by various SSH clients |

---

### Category 2: Authentication & Identity (12 components)

| # | Package Name | Description | Rationale |
|---|--------------|-------------|-----------|
| 16 | `pam` | Pluggable Authentication Modules | System-wide authentication |
| 17 | `ipa-server` | FreeIPA server (identity mgmt) | Centralized authentication |
| 18 | `sssd` | System Security Services Daemon | LDAP/Kerberos client |
| 19 | `krb5-libs` | Kerberos 5 libraries | Network authentication |
| 20 | `krb5-server` | Kerberos KDC server (FreeIPA) | Issues authentication tickets |
| 21 | `389-ds-base` | LDAP directory server (FreeIPA) | User/group database |
| 22 | `pam_google_authenticator` | TOTP MFA module | Multi-factor authentication |
| 23 | `authselect` | Authentication configuration tool | Manages PAM/nsswitch config |
| 24 | `shadow-utils` | User account management | passwd, useradd, usermod commands |
| 25 | `sudo` | Privilege escalation | Root access control |
| 26 | `polkit` | Policy-based privilege control | Desktop privilege management |
| 27 | `keyutils` | Kernel key management | Session keys, keyrings |

---

### Category 3: Network Security (10 components)

| # | Package Name | Description | Rationale |
|---|--------------|-------------|-----------|
| 28 | `openssh-server` | SSH daemon (sshd) | Remote access (MFA enforced) |
| 29 | `openssh-clients` | SSH client tools | Remote administration |
| 30 | `firewalld` | Firewall management daemon | Network boundary protection |
| 31 | `nftables` | Firewall backend (successor to iptables) | Packet filtering |
| 32 | `iptables` | Legacy firewall (still used) | Packet filtering |
| 33 | `httpd` (Apache) | Web server | Hosts internal dashboards |
| 34 | `mod_ssl` | Apache TLS module | HTTPS encryption |
| 35 | `bind-utils` | DNS utilities (dig, nslookup) | DNS troubleshooting |
| 36 | `iproute` | Network configuration tools (ip command) | Network management |
| 37 | `net-tools` | Legacy network tools (ifconfig, netstat) | Network diagnostics |

---

### Category 4: Audit, Logging & Monitoring (8 components)

| # | Package Name | Description | Rationale |
|---|--------------|-------------|-----------|
| 38 | `audit` | Auditd audit framework | Kernel-level audit logging |
| 39 | `audit-libs` | Audit framework libraries | Runtime audit support |
| 40 | `wazuh-agent` | Wazuh SIEM agent | Security monitoring, alerting |
| 41 | `rsyslog` | Syslog daemon | System logging |
| 42 | `logrotate` | Log rotation utility | Prevents log disk exhaustion |
| 43 | `aide` (if installed) | File integrity checker | Detects unauthorized changes |
| 44 | `chrony` | NTP client/server | Time synchronization (audit timestamps) |
| 45 | `systemd-journal` | Systemd journal logging | Core system logging |

---

### Category 5: Core System (15 components)

| # | Package Name | Description | Rationale |
|---|--------------|-------------|-----------|
| 46 | `kernel` | Linux kernel | Operating system core |
| 47 | `systemd` | Init system and service manager | System startup, process mgmt |
| 48 | `glibc` | GNU C Library | Standard C library (all binaries depend on this) |
| 49 | `bash` | Bourne Again Shell | Default shell, runs scripts |
| 50 | `coreutils` | Core utilities (ls, cp, chmod, etc.) | Essential system commands |
| 51 | `util-linux` | System utilities (mount, fdisk, etc.) | Disk/filesystem management |
| 52 | `dnf` | Package manager | Software installation/updates |
| 53 | `rpm` | RPM package manager | Low-level package management |
| 54 | `selinux-policy` | SELinux mandatory access control policy | Enforces MAC |
| 55 | `selinux-policy-targeted` | SELinux targeted policy | Default SELinux policy |
| 56 | `libselinux` | SELinux runtime library | Used by all SELinux-aware apps |
| 57 | `dbus` | D-Bus message bus | Inter-process communication |
| 58 | `systemd-udev` | Device manager | Hardware discovery, /dev management |
| 59 | `procps-ng` | /proc utilities (ps, top, etc.) | Process monitoring |
| 60 | `filesystem` | Filesystem hierarchy | Defines /usr, /etc, /var structure |

---

### Category 6: High-Privilege Services (10 components)

| # | Package Name | Description | Rationale |
|---|--------------|-------------|-----------|
| 61 | `cronie` | Cron daemon | Scheduled tasks (runs as root) |
| 62 | `at` | At/batch job scheduler | Deferred task execution |
| 63 | `postfix` (if installed) | Mail transfer agent | Email delivery (if used) |
| 64 | `tuned` | System tuning daemon | Performance profiles |
| 65 | `NetworkManager` | Network management daemon | Network config (runs as root) |
| 66 | `lvm2` | Logical Volume Manager | Disk partitioning, encryption (LUKS) |
| 67 | `device-mapper` | Device mapper kernel driver | Used by LVM, LUKS |
| 68 | `usbguard` (if installed) | USB device authorization | Prevents malicious USB |
| 69 | `fapolicyd` (if installed) | File access policy daemon | Application whitelisting |
| 70 | `pcscd` (if smart cards used) | PC/SC smart card daemon | Smart card access |

---

### Category 7: Additional Critical (30 components)

*(Abbreviated for length; full list would include 30 more packages like FreeIPA components, Apache modules, Python libraries, etc.)*

| # | Package Name | Description | Rationale |
|---|--------------|-------------|-----------|
| 71-100 | ... | (30 additional components) | ... |

**Note:** Full top 100 list will be documented in SBOM v3.0 (Phase 3). This appendix provides examples across 6 categories.

---

## APPENDIX B: SBOM v3.0 TEMPLATE (Phase 3 Enhancement)

**Enhancement Plan:** Add the following columns to SBOM v2.4 to create v3.0:

| Column | Description | Example |
|--------|-------------|---------|
| **Upstream Source** | Original project name and URL | "OpenSSL Project, https://www.openssl.org" |
| **Signing Authority** | GPG key fingerprint used to sign package | "Rocky Linux: 0x350D275D" |
| **Installation Date** | When package was first installed on system | "2026-01-15" |
| **Last Update Date** | When package was last updated | "2026-03-10" |
| **Critical Component** | Is this in top 100 critical components? | "Yes" or "No" |

**SBOM v3.0 Row Example:**
```
Package: openssl
Version: 3.0.7
Release: 16.el9_1
Arch: x86_64
Systems: dc1, workstation1, workstation2, workstation3
Repository: rocky-baseos
Upstream Source: OpenSSL Project, https://www.openssl.org
Signing Authority: Rocky Linux (GPG: 0x350D275D)
Installation Date: 2026-01-15
Last Update Date: 2026-03-10
Critical Component: Yes
```

**Estimated Effort:** 18 hours (Phase 3, Activity 3.3)

---

**TCC-SRMP-001 Policy v1.0 DRAFT**
**Created:** March 18, 2026
**Status:** DRAFT — Ready for review and customization in Phase 2
**Estimated customization effort:** 4-6 hours (review, adjust for your environment, approve)
