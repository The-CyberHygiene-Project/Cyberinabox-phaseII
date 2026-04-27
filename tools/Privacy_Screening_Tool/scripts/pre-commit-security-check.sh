#!/bin/bash
# Pre-Commit Security Check Script
# CyberHygiene Project - Privacy Screening Tool
#
# Purpose: Scans staged Git commits for sensitive information before allowing commit
# Usage: Can be used manually or as a Git pre-commit hook
# Date: 2026-04-26

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "CyberHygiene Pre-Commit Security Check"
echo "========================================="
echo ""

# Counter for findings
WARNINGS=0
ERRORS=0

# Function to print error
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((ERRORS++))
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((WARNINGS++))
}

# Function to print success
print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Check 1: Verify .gitignore exists
echo "[1/8] Checking .gitignore file..."
if [ ! -f .gitignore ]; then
    print_error ".gitignore file is missing!"
else
    print_success ".gitignore file exists"
fi

# Check 2: Look for hardcoded passwords in staged files
echo "[2/8] Scanning for hardcoded passwords..."
if git diff --cached | grep -iE "password\s*=|PASSWORD\s*=|pwd\s*=|passwd\s*=" > /dev/null; then
    print_error "Found potential hardcoded passwords in staged changes!"
    echo "       Run: git diff --cached | grep -i password"
else
    print_success "No hardcoded passwords detected"
fi

# Check 3: Look for API keys and secrets
echo "[3/8] Scanning for API keys and secrets..."
if git diff --cached | grep -iE "api[_-]?key|secret[_-]?key|access[_-]?token|private[_-]?key" > /dev/null; then
    print_error "Found potential API keys or secrets in staged changes!"
    echo "       Run: git diff --cached | grep -iE 'api.*key|secret'"
else
    print_success "No API keys or secrets detected"
fi

# Check 4: Look for IP addresses (may be sensitive)
echo "[4/8] Scanning for IP addresses..."
if git diff --cached | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | grep -v "127.0.0.1\|0.0.0.0" > /dev/null; then
    print_warning "Found IP addresses in staged changes"
    echo "       Verify these are safe to commit (not internal/private IPs)"
    echo "       Run: git diff --cached | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}'"
fi

# Check 5: Look for email addresses
echo "[5/8] Scanning for email addresses..."
if git diff --cached | grep -oE "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b" > /dev/null; then
    print_warning "Found email addresses in staged changes"
    echo "       Verify these are safe to commit (not personal emails)"
fi

# Check 6: Look for certificate/key files
echo "[6/8] Checking for certificate/key files..."
if git diff --cached --name-only | grep -E "\.(key|pem|p12|pfx|crt|cer)$" > /dev/null; then
    print_error "Found certificate or key files in staged changes!"
    echo "       Files: $(git diff --cached --name-only | grep -E '\.(key|pem|p12|pfx|crt|cer)$')"
else
    print_success "No certificate or key files detected"
fi

# Check 7: Look for credential files
echo "[7/8] Checking for credential files..."
if git diff --cached --name-only | grep -iE "credential|password|secret|install_vars" > /dev/null; then
    print_error "Found potential credential files in staged changes!"
    echo "       Files: $(git diff --cached --name-only | grep -iE 'credential|password|secret')"
else
    print_success "No credential files detected"
fi

# Check 8: Look for backup/log files
echo "[8/8] Checking for backup/log files..."
if git diff --cached --name-only | grep -E "\.(log|bak|backup|tmp)$|~$" > /dev/null; then
    print_warning "Found backup or log files in staged changes"
    echo "       Files: $(git diff --cached --name-only | grep -E '\.(log|bak|backup|tmp)$|~$')"
fi

echo ""
echo "========================================="
echo "Security Check Complete"
echo "========================================="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

# Exit with error if any errors found
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}COMMIT BLOCKED:${NC} Security issues detected!"
    echo "Review the errors above and remove sensitive data before committing."
    echo ""
    echo "To see what you're committing: git diff --cached"
    echo "To unstage a file: git reset HEAD <file>"
    exit 1
fi

# Warn but allow commit if only warnings
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}WARNINGS DETECTED:${NC} Review the warnings above."
    echo "If you're sure these are safe to commit, proceed."
    echo ""
    read -p "Continue with commit? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Commit cancelled by user."
        exit 1
    fi
fi

echo -e "${GREEN}Security check passed!${NC} Safe to commit."
exit 0
