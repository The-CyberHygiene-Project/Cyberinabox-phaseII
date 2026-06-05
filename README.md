# CyberInABox — Phase IV (SecureMac Reference System)

**Version:** Phase IV — Apr 2026
**Reference System:** SecureMac / diwai.org
**Status:** Operational reference system for academic / research use

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-ff69b4?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/dshannon46-jpg)

## ⚠️ Disclaimer

**ACADEMIC RESEARCH PROJECT** — This repository contains documentation,
configurations, and supporting materials from an academic research project
demonstrating NIST SP 800-171 technical control implementation on a unified
appliance (Mac mini + Rocky Linux service VM) using open-source tools.

**NOT COMPLIANCE CERTIFICATION** — OpenSCAP scan results, mSCP baselines,
and technical configurations validate control implementation but do not
constitute CMMC certification, third-party assessment, or legal compliance
advice. Organizations must pursue formal assessment through authorized C3PAOs.

**NO WARRANTY** — This documentation is provided "as-is" without warranty
of any kind. Use at your own risk. See `LICENSE` for full terms.

**PROFESSIONAL GUIDANCE REQUIRED** — Implementation requires cybersecurity
expertise. This is not a substitute for professional assessment, qualified
legal counsel, or C3PAO evaluation.

**NO CONSULTING SERVICES** — The author does not provide cybersecurity
consulting services. This project is an academic exercise demonstrating
what is achievable using AI-assisted administration and open-source tools.

---

## What this repository is

The Phase IV evolution of the CyberHygiene Project — a single-appliance
NIST SP 800-171-aligned reference system built on a Mac mini M4 Pro
running a FIPS-validated Rocky Linux 9.7 service VM. SecureMac
(reachable at diwai.org) consolidates firewall, domain controller,
mail, VPN, IDS/IPS, SIEM, and monitoring into one host.

This is a companion to:
- **[diwai](https://github.com/The-CyberHygiene-Project/diwai)** — Governance artifacts for this system: Policies, Procedures, SSP, POAM, Assessments, and Training.
- **[cyberhygiene-documentation](https://github.com/The-CyberHygiene-Project/cyberhygiene-documentation)** — Phase I & II documentation (Rocky Linux RS1).
- **[cyberhygiene-evolution](https://github.com/The-CyberHygiene-Project/cyberhygiene-evolution)** — Manuscript, incident narratives, predecessor publications.

## Repository history

This repository was previously named `Cyberinabox-phaseII` and held the
Phase II Rocky Linux installer. That installer remains available at the
tag `legacy-phase-II-installer-v1.0` and on the branch
`legacy/phase-II-installer`. The canonical maintained Phase II material
moved to `cyberhygiene-documentation/Phase-II/` in April 2026; this repo
was renamed and repurposed for the Phase IV evolution at the same time.

To check out the legacy Phase II installer:

```bash
git checkout legacy-phase-II-installer-v1.0
# or:
git checkout legacy/phase-II-installer
```

## What's in here

Governance artifacts (Policies, Procedures, SSP, POAM, Assessments, Training) are
maintained in the companion **[diwai](https://github.com/The-CyberHygiene-Project/diwai)** repo.

```
sbom/                    Software Bill of Materials v2.1 + history
configuration/           pf, USBGuard, launchd, scripts, Rocky VM setup
mscp/diwai_phase1_baseline/   Custom mSCP baseline for the Mac host
evidence/                Compliance evidence (OpenSCAP, FIPS, MFA, etc.)
deployment/              Deployment package: apache configs, AI tools, dashboards, scripts
phase_IV_architecture/   Unified-appliance architecture material + Rev 3 drafts
build_evidence/          Documented build sequence (Apr 8, 2026)
tools/                   Privacy Screening Tool (CMMC L2 / CUI safety for Git commits)
```

## Redactions

Materials in this repository have been redacted for public release per
the project's privacy screening process:

- **GRUB2 PBKDF2 password hashes** in OpenSCAP HTML reports replaced
  with `[REDACTED-PBKDF2-HASH]`.
- **Hardcoded demo password** in `deployment/ai-tools/dashboard-deployment/web/app.py`
  replaced with `os.environ.get('DEMO_PASSWORD', '<unset>')`.

The unredacted versions remain in the project's private working library.
For real deployment, set `DEMO_PASSWORD` via environment (or implement
proper FreeIPA authentication as the TODO in `app.py` indicates).

## License

MIT — see `LICENSE`.

## Contact

This is an academic research project. The author does not provide
consulting services. Issues for technical clarification are welcome;
business inquiries are not the project's purpose.
