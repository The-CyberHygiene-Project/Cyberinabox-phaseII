# CyberHygiene Privacy Screening Tool
## Automated Sensitive Data Detection for Git Commits

**Purpose:** Prevent accidental exposure of sensitive information in Git repositories  
**Project:** CyberHygiene Reference Systems (RS1 & RS2)  
**Date:** 2026-04-26  
**Classification:** CUI-Safe Documentation Tool

---

## Executive Summary

The CyberHygiene Privacy Screening Tool is a **multi-layer defense system** designed to prevent sensitive information from being committed to Git repositories (especially public repositories like GitHub). This is critical for CMMC L2 compliance and CUI protection.

**Components:**
1. **.gitignore** — File-level blocking (first line of defense)
2. **Pre-commit script** — Content scanning (second line of defense)  
3. **GitHub Actions** — CI/CD security scanning (third line of defense)
4. **Manual verification** — Developer checklist (human review)

---

## Why This Matters

### NIST SP 800-171 Requirements

- **3.13.11** - Employ cryptographic mechanisms to protect confidentiality of CUI
- **3.13.16** - Protect confidentiality of CUI at rest

**Implication:** Committing CUI or credentials to Git (especially public GitHub) = immediate NIST violation and potential data breach.

### Real Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Hardcoded passwords** | Unauthorized access | Pre-commit scanning |
| **Private IP addresses** | Network reconnaissance | Manual review |
| **Customer PII** | Privacy violation, legal liability | .gitignore + scanning |
| **SSL certificates/keys** | Man-in-the-middle attacks | .gitignore blocking |
| **API tokens** | Service compromise | Pre-commit detection |

---

## Component 1: .gitignore File

### Purpose
Prevents entire categories of sensitive files from ever being staged in Git.

### Location
`examples/gitignore-cyberhygiene` (copy to `.gitignore` in your repo root)

### Protected File Types

**Credentials & Keys:**
```gitignore
CREDENTIALS_*.txt
*_passwords*.txt
*.key
*.pem
*.p12
*.pfx
backup-encryption-key*.txt
```

**Customer Data:**
```gitignore
installation_info.md       # Filled customer forms
install_vars.sh            # Generated variables/passwords
customer_data/
client_configs/
```

**Certificates:**
```gitignore
customer_ssl_certs/
*.crt
*.csr
```

**Logs & Backups:**
```gitignore
logs/
*.log
backups/
backup_*.tar.gz
```

**Generated Files:**
```gitignore
VERIFICATION_REPORT_*.txt
system_snapshot_*.txt
freeipa_installation_*.log
```

### Safe Files (Explicitly Allowed)

```gitignore
!installation_info_template.md   # Empty template OK
!README.md                        # Documentation OK
!*.sh                            # Scripts OK (no hardcoded secrets)
```

### Deployment

```bash
# Copy to your repository
cp examples/gitignore-cyberhygiene /path/to/your/repo/.gitignore

# Test protection
cd /path/to/your/repo
echo "password=secret123" > install_vars.sh
git status
# Should NOT show install_vars.sh

# Verify .gitignore is working
git check-ignore install_vars.sh
# Should output: install_vars.sh
```

---

## Component 2: Pre-Commit Security Check Script

### Purpose
Scans **content** of staged files for sensitive data patterns that might slip through .gitignore.

### Location
`scripts/pre-commit-security-check.sh`

### What It Detects

| Check | Pattern | Action |
|-------|---------|--------|
| **Hardcoded passwords** | `password=`, `PASSWORD=`, `pwd=` | **BLOCK** |
| **API keys** | `api_key`, `secret_key`, `access_token` | **BLOCK** |
| **Certificates/keys** | `*.key`, `*.pem`, `*.p12`, `*.pfx` | **BLOCK** |
| **Credential files** | Files matching `credential`, `password` | **BLOCK** |
| **IP addresses** | IPv4 addresses (except 127.0.0.1) | **WARN** |
| **Email addresses** | `user@domain.com` patterns | **WARN** |
| **Backup/log files** | `*.log`, `*.bak`, `*.tmp` | **WARN** |

### Usage

**As Manual Check (Recommended):**
```bash
# Before every commit
./scripts/pre-commit-security-check.sh

# If clean, then:
git commit -m "Your message"
```

**As Git Hook (Automatic):**
```bash
# Install as pre-commit hook
cp scripts/pre-commit-security-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Now runs automatically before every commit
git commit -m "Your message"
# Hook will run automatically
```

### Example Output

```
=========================================
CyberHygiene Pre-Commit Security Check
=========================================

[1/8] Checking .gitignore file...
[OK] .gitignore file exists
[2/8] Scanning for hardcoded passwords...
[ERROR] Found potential hardcoded passwords in staged changes!
       Run: git diff --cached | grep -i password
[3/8] Scanning for API keys and secrets...
[OK] No API keys or secrets detected
[4/8] Scanning for IP addresses...
[WARNING] Found IP addresses in staged changes
       Verify these are safe to commit (not internal/private IPs)
[5/8] Scanning for email addresses...
[OK] No email addresses detected
[6/8] Checking for certificate/key files...
[OK] No certificate or key files detected
[7/8] Checking for credential files...
[OK] No credential files detected
[8/8] Checking for backup/log files...
[OK] No backup or log files detected

=========================================
Security Check Complete
=========================================
Errors: 1
Warnings: 1

COMMIT BLOCKED: Security issues detected!
Review the errors above and remove sensitive data before committing.
```

---

## Component 3: GitHub Actions Security Scan

### Purpose
Third layer of defense — runs in CI/CD pipeline after code is pushed (but before merging to main).

### Configuration

Create `.github/workflows/security-scan.yml`:

```yaml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check for sensitive data
        run: |
          if grep -r "password.*=" scripts/ --include="*.sh"; then
            echo "ERROR: Found hardcoded passwords"
            exit 1
          fi
          
          if grep -r "api.*key\|secret.*key" scripts/ --include="*.sh"; then
            echo "ERROR: Found API keys or secrets"
            exit 1
          fi

      - name: Verify .gitignore
        run: |
          if [ ! -f .gitignore ]; then
            echo "ERROR: .gitignore missing"
            exit 1
          fi

      - name: ShellCheck scripts
        run: |
          sudo apt-get install -y shellcheck
          find scripts/ -name "*.sh" -exec shellcheck {} \;
```

### Benefits
- Automated checking on every push
- Catches issues that slip past local checks
- Blocks pull requests with security issues
- Team visibility (all developers see failures)

---

## Component 4: Manual Verification Checklist

### Before Every Commit

```bash
# 1. Review what you're committing
git status
git diff --cached

# 2. Run security check
./scripts/pre-commit-security-check.sh

# 3. Manual scan for patterns
git diff --cached | grep -iE "password|secret|api.*key|192\.168\.|10\."

# 4. Verify no protected files
git status | grep -iE "credential|install_vars|\.key|\.pem"

# 5. If all clear, commit
git commit -m "Descriptive message"
```

### Before Every Push

```bash
# Review entire commit log
git log --oneline -5

# Check for accidentally committed secrets
git log -p | grep -iE "password|secret|api"

# If found, use git filter-repo to remove
# (see Incident Response section)
```

---

## Deployment Guide

### Step 1: Install .gitignore

```bash
cd /path/to/your/repository

# Copy .gitignore
cp /path/to/Privacy_Screening_Tool/examples/gitignore-cyberhygiene .gitignore

# Verify it works
echo "test" > install_vars.sh
git status
# Should NOT show install_vars.sh

rm install_vars.sh
```

### Step 2: Install Pre-Commit Script

```bash
# Copy script
mkdir -p scripts
cp /path/to/Privacy_Screening_Tool/scripts/pre-commit-security-check.sh scripts/

# Make executable
chmod +x scripts/pre-commit-security-check.sh

# Test it
scripts/pre-commit-security-check.sh
```

### Step 3: Install as Git Hook (Optional but Recommended)

```bash
# Link as pre-commit hook
ln -s ../../scripts/pre-commit-security-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Test hook
git add .gitignore
git commit -m "Test commit"
# Hook should run automatically
```

### Step 4: Set Up GitHub Actions (If Using GitHub)

```bash
# Create workflow directory
mkdir -p .github/workflows

# Copy security scan workflow
# (See Component 3 above for YAML configuration)

# Commit workflow
git add .github/workflows/security-scan.yml
git commit -m "Add automated security scanning"
git push
```

### Step 5: Team Training

Share with all developers:
1. Location of privacy screening tool
2. Required workflow: check → commit → push
3. What to do if blocked (fix, don't bypass)
4. Incident response (if secret accidentally committed)

---

## Incident Response: If Secret is Committed

### Scenario: You accidentally committed a password to Git

**DO NOT** just delete the file and commit again — it's still in Git history!

### Solution: Remove from History

**Option 1: Recent commit (not yet pushed)**
```bash
# Amend the last commit
git reset HEAD~1
# Remove sensitive file
rm install_vars.sh
# Recommit without it
git add .
git commit -m "Your message"
```

**Option 2: Already pushed to GitHub**
```bash
# Use git filter-repo (recommended)
pip3 install git-filter-repo

# Remove file from entire history
git filter-repo --path install_vars.sh --invert-paths

# Force push to rewrite remote history
git push --force

# Rotate compromised credentials IMMEDIATELY
```

**Option 3: GitHub has seen it**
1. Rotate ALL exposed credentials immediately
2. Use GitHub's secret scanning to find exposures
3. Consider repo as compromised
4. May need to create new repo with clean history

---

## Testing the System

### Test 1: .gitignore Protection

```bash
# Create protected file
echo "admin_password=secret123" > install_vars.sh

# Try to stage it
git add install_vars.sh
# Should give: "The following paths are ignored by one of your .gitignore files"

# Verify
git status
# Should NOT show install_vars.sh
```

### Test 2: Pre-Commit Script Detection

```bash
# Create file with password
echo "export DB_PASSWORD=secret123" > scripts/test.sh
git add scripts/test.sh

# Run security check
./scripts/pre-commit-security-check.sh
# Should BLOCK with error about hardcoded password
```

### Test 3: IP Address Warning

```bash
# Add file with IP
echo "server_ip=192.168.1.100" > README.md
git add README.md

# Run security check
./scripts/pre-commit-security-check.sh
# Should WARN about IP address (but allow with confirmation)
```

### Test 4: Clean Commit

```bash
# Add safe file
echo "# Documentation" > docs/guide.md
git add docs/guide.md

# Run security check
./scripts/pre-commit-security-check.sh
# Should show: "Security check passed! Safe to commit."
```

---

## RS2 (SecureMac) Deployment

### Adaptations for RS2

The privacy screening tool is **platform-independent** and works identically on:
- RS1 (Rocky Linux / cyberinabox.net)
- RS2 (macOS + Rocky VM / diwai.org)
- Any Git repository

**No modifications needed** — just copy and deploy following the steps above.

### RS2-Specific Considerations

1. **Multiple repositories:**
   - SecureMac SSP/POA&M repository
   - Deployment scripts repository
   - Public documentation repository
   
   → Install .gitignore and pre-commit hook in EACH repository

2. **CUI handling:**
   - SSP v1.2 for SecureMac = CUI
   - Do NOT commit full SSP to GitHub
   - Use redacted/public versions only
   - Store full SSP outside Git (encrypted storage)

3. **macOS differences:**
   - Pre-commit script works identically on macOS
   - Use `#!/bin/bash` shebang (works on both Linux and macOS)
   - GitHub Actions run on Ubuntu (platform-independent)

---

## Integration with Development Workflow

### Recommended Git Workflow

```
Developer Workflow:
1. Create feature branch
2. Make changes
3. git add <files>
4. ./scripts/pre-commit-security-check.sh  ← ALWAYS RUN
5. git commit -m "message"
6. git push origin feature-branch
7. Create pull request
8. GitHub Actions security scan runs  ← AUTOMATED
9. Code review
10. Merge to main
```

### Enforcing Usage

**Team Policy:**
- Pre-commit check is MANDATORY before every commit
- CI/CD blocks merges if security scan fails
- Code review checklist includes: "Privacy screening passed?"

**Technical Enforcement:**
```bash
# Install pre-commit hook for entire team
# Add to repository setup script:
#!/bin/bash
ln -sf ../../scripts/pre-commit-security-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

## Files in This Package

```
Privacy_Screening_Tool/
├── README_Privacy_Screening.md          # This file
├── examples/
│   └── gitignore-cyberhygiene          # .gitignore template
├── docs/
│   ├── DEPLOYMENT_GUIDE.md             # Full deployment guide (reference)
│   └── CONTRIBUTING.md                 # Contribution guidelines (reference)
└── scripts/
    └── pre-commit-security-check.sh    # Automated scanning script
```

---

## Maintenance

### Regular Updates

**Quarterly Review:**
- Update .gitignore for new sensitive file types
- Update pre-commit script for new patterns
- Review GitHub Actions for new security checks

**After Incidents:**
- If secret accidentally committed → update patterns to prevent recurrence
- Document lesson learned in README
- Update team training

**Version Control:**
- Track .gitignore changes in Git
- Version pre-commit script
- Document what each version detects/blocks

---

## Related Documentation

**On M.2 Drive:**
- `Session_Notes/RS1_Status_Comparison.md` — RS1 verification
- `Session_Notes/Manuscript_Update_Checklist.md` — Documentation updates
- `RS2_Deployment/` — RS2 deployment package
- `RS1_OpenSCAP_Reports/` — Compliance reports

**External References:**
- NIST SP 800-171 Rev 2: Protecting CUI
- GitHub Secret Scanning: https://docs.github.com/en/code-security/secret-scanning
- git-filter-repo: https://github.com/newren/git-filter-repo

---

## Summary

The CyberHygiene Privacy Screening Tool provides **four layers of protection** against accidental sensitive data exposure:

1. ✓ **.gitignore** blocks files by pattern
2. ✓ **Pre-commit script** scans content
3. ✓ **GitHub Actions** CI/CD checks
4. ✓ **Manual review** checklist

**Usage is simple:**
```bash
# Before every commit:
./scripts/pre-commit-security-check.sh
git commit -m "Your message"
```

**Result:** NIST-compliant, CUI-safe Git commits that can be shared publicly without exposing sensitive information.

---

*Documentation prepared: 2026-04-26*  
*Source: CyberHygiene Phase II project security controls*  
*Classification: Public (no CUI)*  
*Tested on: Rocky Linux 9.7, macOS Tahoe 26.4.1*
