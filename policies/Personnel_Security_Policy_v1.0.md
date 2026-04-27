# Personnel Security Policy

**Document ID:** DIWAI-PS-001
**Version:** 1.0
**Effective Date:** April 10, 2026
**Review Schedule:** Annually
**Next Review:** April 2027
**Owner:** Donald E. Shannon, ISSO/System Owner
**Distribution:** Authorized personnel only
**Classification:** CUI

---

## 1. Purpose

This policy establishes diwai.org (Do It With AI) requirements for personnel security on the SecureMac Production Network (SPN). It ensures individuals with access to SPN resources and CUI are appropriately screened, trained, and managed throughout their association with diwai.org, in compliance with NIST SP 800-171 Rev 2 (PS-1 through PS-9) and CMMC Level 2.

---

## 2. Scope

This policy applies to:

- **All Personnel:**
  - Donald E. Shannon (System Owner / ISSO / System Administrator)
  - Any contractors, subcontractors, or temporary personnel with:
    - Physical access to SPN hardware (Mac mini, LAN)
    - Logical access to SPN systems (SSH, LDAP, web services)
    - Access to CUI or FCI data

---

## 3. Policy Statements

### 3.1 Personnel Security Policy and Procedures (PS-1)

diwai.org shall maintain this policy and review it annually. Personnel security requirements communicated to all personnel before access is granted.

### 3.2 Position Categorization (PS-2)

**Position Risk Levels:**

| Position | Risk Level | Rationale |
|----------|-----------|-----------|
| System Owner / ISSO (Donald E. Shannon) | High | Full administrative access to all SPN systems; CUI custodian |
| System Administrator | High | Same as above (concurrent role) |
| IT Contractor with admin access | High | Privileged account with CUI access |
| Contractor with limited access | Moderate | Limited LDAP account; restricted CUI scope |
| Physical access only | Low | No logical CUI access |

### 3.3 Personnel Screening (PS-3)

**Pre-Access Screening:**

1. **System Owner / ISSO (Donald E. Shannon):**
   - Active/prior DoD security clearance (TS/SCI eligible, per background)
   - Background investigation completed via DCSA

2. **Contractors and Subcontractors:**
   - Basic background check required before access to CUI
   - Minimum: Identity verification and employment history
   - High-risk positions: Criminal background check
   - Verify no disqualifying factors under FAR 52.204-21

3. **Screening Documentation:**
   - Record of screening maintained in `~/Documents/SecureMac Project Docs/Personnel/`
   - Background check results retained per legal requirements (not retained longer than necessary)

### 3.4 Personnel Termination (PS-4)

**Upon termination or separation (all actions within 24 hours):**

1. **Immediate Logical Access Revocation:**
   ```bash
   # Disable LDAP account
   ldapmodify -x -D "cn=Directory Manager" -W \
     -H ldap://services.diwai.org << EOF
   dn: uid=username,ou=People,dc=diwai,dc=org
   changetype: modify
   replace: nsAccountLock
   nsAccountLock: true
   EOF

   # Remove SSH authorized_keys
   sudo sed -i '/terminated_user_key/d' /home/username/.ssh/authorized_keys

   # Revoke OpenVPN certificate (if issued)
   cd /etc/openvpn/easy-rsa
   ./easyrsa revoke username
   ./easyrsa gen-crl
   ```

2. **Additional Actions:**
   - Change any shared passwords or secrets the individual knew
   - Revoke any API tokens or application-specific credentials
   - Retrieve any physical access keys, badges, or access devices
   - Conduct exit briefing on CUI obligations (ongoing post-employment)

3. **Account Retention:**
   - Disabled account retained for 90 days then deleted
   - Audit logs for terminated user account retained per retention policy (3 years)

4. **Post-Separation CUI Obligations:**
   - Terminated individuals advised that CUI obligations continue post-separation
   - NDA provisions remain in effect

### 3.5 Personnel Transfer (PS-5)

**When personnel role changes (e.g., contractor scope change):**

1. Review and update LDAP group memberships to reflect new role
2. Remove access to resources no longer required
3. Update access list documentation
4. Notify ISSO within 48 hours of role change

### 3.6 Access Agreements (PS-6)

**Required Agreements Before Access:**

All personnel with SPN or CUI access must sign:

1. **Non-Disclosure Agreement (NDA)**
   - Covers CUI, FCI, and proprietary information
   - Survives termination
   - Filed in `~/Documents/SecureMac Project Docs/Personnel/`

2. **Acceptable Use Policy Acknowledgment (DIWAI-AUP-001)**
   - Acknowledges monitoring, no privacy expectation, consequences of violations

3. **CUI Handling Acknowledgment**
   - Understanding of CUI categories handled by diwai.org
   - Knowledge of handling, storage, and disposal requirements

**Agreements renewed annually for active personnel.**

### 3.7 Third-Party Personnel Security (PS-7)

**Requirements for Third-Party Vendors/Contractors:**

1. Verify vendor's personnel security practices during onboarding
2. Require flow-down of CUI protection requirements via contract
3. Vendor employees accessing CUI must meet same screening requirements
4. Include in contracts:
   - FAR 52.204-21 (Basic Safeguarding)
   - DFARS 252.204-7012 (CUI/CDI protection and reporting)
   - Non-disclosure requirements
   - Right to audit

### 3.8 Personnel Sanctions (PS-8)

**Violations of security policies may result in:**

1. Formal written warning
2. Suspension of system access (immediate, pending investigation)
3. Termination of employment or contract
4. Civil legal action (for negligent or intentional CUI exposure)
5. Criminal referral (for willful CUI violations — 18 U.S.C. § 1030)
6. Notification to cognizant Contracting Officer for CDI/CUI incidents

**All violations documented in incident records (DIWAI-IRP-001).**

### 3.9 Position Risk Designation Review (PS-2 continued)

- Position risk designations reviewed annually
- Updated when position responsibilities change
- Updated after security incidents involving personnel

---

## 4. Contractor Management

### 4.1 Contractor Account Lifecycle

| Phase | Action | Timeline |
|-------|--------|----------|
| Onboarding | Background check; NDA signed; AUP acknowledged; account created | Before first access |
| Active | Quarterly access review; annual training | Ongoing |
| Scope change | Access adjusted to new role | Within 48 hours |
| Contract end | All access revoked; exit briefing | Within 24 hours of end date |

### 4.2 Contractor Account Controls

- Time-limited LDAP accounts with expiration date set at creation
- Minimum privilege — only groups required for scope of work
- No administrative/sudo access unless explicitly required and approved
- Contractor accounts reviewed quarterly: `ldapsearch -x -D "cn=Directory Manager" -W -b "ou=People,dc=diwai,dc=org"`
- Accounts with no login in 45 days automatically disabled

---

## 5. Roles and Responsibilities

| Role | Personnel Security Responsibilities |
|------|-------------------------------------|
| **System Owner (Donald E. Shannon)** | Approve personnel access; maintain access agreements; make sanctions decisions |
| **ISSO (Donald E. Shannon)** | Conduct access reviews; manage LDAP accounts; revoke access on termination; maintain personnel records |

---

## 6. Compliance Mapping

| NIST SP 800-171 Control | Implementation |
|-------------------------|----------------|
| **PS-1** Policy and Procedures | This document |
| **PS-2** Position Categorization | Section 3.2 |
| **PS-3** Personnel Screening | Section 3.3 |
| **PS-4** Personnel Termination | Section 3.4 |
| **PS-5** Personnel Transfer | Section 3.5 |
| **PS-6** Access Agreements | Section 3.6 |
| **PS-7** Third-Party Personnel Security | Section 3.7 |
| **PS-8** Personnel Sanctions | Section 3.8 |

---

## 7. Policy Review and Updates

- **Review Frequency:** Annually
- **Approval Authority:** System Owner / ISSO (Donald E. Shannon)

---

## 8. Approval Signatures

**Prepared By:**
Name: Donald E. Shannon, System Administrator
Signature: /s/ Donald E. Shannon                Date: April 10, 2026

**Reviewed By:**
Name: Donald E. Shannon, Information System Security Officer
Signature: /s/ Donald E. Shannon                Date: April 10, 2026

**Approved By:**
Name: Donald E. Shannon, System Owner
Signature: /s/ Donald E. Shannon                Date: April 10, 2026

---

**CLASSIFICATION:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)
**DISTRIBUTION:** Official Use Only - Need to Know Basis
**STATUS:** APPROVED

---

**END OF DOCUMENT**
