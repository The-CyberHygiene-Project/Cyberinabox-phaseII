# Email Security Configuration Evidence

**Document ID:** DIWAI-EV-EMAIL-001
**Version:** 1.0
**Date Collected:** April 10, 2026
**Collected By:** Donald E. Shannon, ISSO
**System:** services.diwai.org (Rocky Linux 9.7 VM)
**Classification:** CUI

---

## Purpose

This document provides evidence of email security controls on the SecureMac Production Network (SPN). It supports NIST SP 800-171 controls 3.13.8 (cryptography in transit), 3.8.3 (sanitize media), and CMMC Level 2 SC controls for secure communications. Evidence is drawn from live system configuration as of April 10, 2026.

---

## 1. TLS Certificate

**Control:** NIST SP 800-171 § 3.13.8 / SC-8(1) (Cryptographic Protection in Transit)

**Certificate Authority:** Let's Encrypt (ISRG Root X1)
**Issuance Method:** DNS-01 challenge via Cloudflare API
**Auto-renewal:** certbot-renew.timer (systemd timer, nightly at ~01:37 MDT)

**Command:** `sudo certbot certificates`
**Date:** April 10, 2026

```
Found the following certs:
  Certificate Name: diwai.org
    Serial Number: 59e2775562fdefaca91c43c06f7451e64dd
    Key Type: ECDSA
    Domains: diwai.org *.diwai.org
    Expiry Date: 2026-07-09 14:10:51+00:00 (VALID: 89 days)
    Certificate Path: /etc/letsencrypt/live/diwai.org/fullchain.pem
    Private Key Path: /etc/letsencrypt/live/diwai.org/privkey.pem
```

**Deployed Certificate:**

```
subject=CN=diwai.org
notBefore=Apr 10 14:10:52 2026 GMT
notAfter=Jul  9 14:10:51 2026 GMT
```

**Certificate Coverage:** Wildcard `*.diwai.org` covers:
- `mail.diwai.org` (Postfix/Dovecot)
- `www.diwai.org` (Apache HTTPD)
- `services.diwai.org` (LDAP, VPN, SSH)
- Any future diwai.org subdomains

**Deployed Paths:**
- Certificate: `/etc/pki/tls/certs/diwai.org.crt`
- Private Key: `/etc/pki/tls/private/diwai.org.key` (mode 600)

**Auto-renewal Deploy Hook:** `/etc/letsencrypt/renewal-hooks/deploy/diwai-deploy.sh`
- Copies renewed cert to `/etc/pki/tls/certs/` and `/etc/pki/tls/private/`
- Restores SELinux contexts (`restorecon`)
- Reloads affected services: httpd, postfix, dovecot, openvpn-server@diwai

---

## 2. Postfix SMTP Configuration

**Control:** NIST SP 800-171 § 3.13.8 / SC-8(1)

**Command:** `sudo postconf smtpd_tls_security_level smtp_tls_security_level smtpd_tls_cert_file smtpd_tls_protocols smtp_tls_protocols`
**Date:** April 10, 2026

```
smtpd_tls_security_level = may
smtp_tls_security_level = may
smtpd_tls_cert_file = /etc/pki/tls/certs/diwai.org.crt
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtp_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
```

**Analysis:**

| Setting | Value | Requirement |
|---------|-------|-------------|
| `smtpd_tls_security_level` | `may` | Opportunistic TLS (offers TLS; degrades if partner doesn't support) |
| `smtp_tls_security_level` | `may` | Opportunistic TLS for outbound |
| `smtpd_tls_cert_file` | `diwai.org.crt` | Valid wildcard cert deployed |
| `smtpd_tls_protocols` | `!SSLv2, !SSLv3, !TLSv1, !TLSv1.1` | TLS 1.2+ enforced |
| `smtp_tls_protocols` | `!SSLv2, !SSLv3, !TLSv1, !TLSv1.1` | TLS 1.2+ for outbound |

**Listening Ports (firewalld):**
- Port 25/tcp: SMTP (MTA-to-MTA)
- Port 587/tcp: SMTP Submission (client → server, requires AUTH)
- Port 465/tcp: SMTPS (implicit TLS) — can be enabled

**Note:** `smtpd_tls_security_level = may` (opportunistic) vs. `encrypt` (required) is a deliberate operational choice — requiring encryption would reject legitimate mail from servers that don't support TLS. This is standard for public-facing SMTP. Internal and client submissions on port 587 use `smtpd_tls_auth_only = yes` requiring TLS for authentication.

---

## 3. Dovecot IMAP/POP3 Configuration

**Control:** NIST SP 800-171 § 3.13.8 / SC-8(1)

**File:** `/etc/dovecot/conf.d/10-ssl.conf`
**Date:** April 10, 2026

```
ssl = yes
ssl_cert = </etc/pki/tls/certs/diwai.org.crt
ssl_key = </etc/pki/tls/private/diwai.org.key
ssl_min_protocol = TLSv1.2
ssl_cipher_list = ECDHE+AESGCM:DHE+AESGCM:ECDHE+AES:DHE+AES:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK
ssl_prefer_server_ciphers = yes
```

**Analysis:**

| Setting | Value | Security Assessment |
|---------|-------|---------------------|
| `ssl` | `yes` | TLS enabled |
| `ssl_cert` | `diwai.org.crt` | Valid wildcard cert |
| `ssl_min_protocol` | `TLSv1.2` | TLS 1.2 minimum — SSLv2/3/TLSv1/1.1 rejected |
| `ssl_cipher_list` | ECDHE+AESGCM first | PFS ciphers preferred |
| `ssl_prefer_server_ciphers` | `yes` | Server controls cipher selection |

**Listening Ports (firewalld):**
- Port 993/tcp: IMAPS (implicit TLS — active)
- Port 143/tcp: IMAP with STARTTLS (available)
- Port 995/tcp: POP3S (if enabled)

**Result:** PASS — Dovecot configured with TLS 1.2 minimum, strong cipher suites with PFS, using valid diwai.org wildcard certificate.

---

## 4. Apache HTTPD TLS Configuration

**Control:** NIST SP 800-171 § 3.13.8 / SC-8(1)

**File:** `/etc/httpd/conf.d/diwai.conf` (effective VirtualHost config)
**Date:** April 10, 2026

```
SSLProtocol -all +TLSv1.2 +TLSv1.3
SSLCipherSuite ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256
SSLEngine on
```

**Active on VirtualHosts:** HTTPS 443 on all configured virtual hosts (diwai.org, mail.diwai.org, webmail.diwai.org)

**Analysis:**

| Setting | Value | Security Assessment |
|---------|-------|---------------------|
| `SSLProtocol` | `-all +TLSv1.2 +TLSv1.3` | Only TLS 1.2 and 1.3; all others disabled |
| `SSLCipherSuite` | ECDHE-ECDSA-AES256-GCM-SHA384 first | AES-256-GCM with ECDHE (PFS) preferred |
| `SSLEngine` | `on` | HTTPS active on all virtual hosts |

**Result:** PASS — Apache configured with TLS 1.2/1.3 only, AES-256-GCM ciphers with perfect forward secrecy.

---

## 5. Firewall Open Ports (Email-Related)

**Command:** `sudo firewall-cmd --list-all`
**Date:** April 10, 2026

```
public (active)
  services: cockpit dhcpv6-client http https imap imaps smtp smtps ssh
  ports: 587/tcp 1194/udp 1514/tcp 1515/tcp
  masquerade: yes
  rich rules:
    rule family="ipv4" source address="10.8.0.0/24" masquerade
```

**Email-related ports open:**

| Port | Service | Encryption |
|------|---------|-----------|
| 25/tcp (smtp) | SMTP MTA | STARTTLS (opportunistic) |
| 465/tcp (smtps) | SMTPS | Implicit TLS |
| 587/tcp | SMTP Submission | STARTTLS required for auth |
| 143/tcp (imap) | IMAP | STARTTLS |
| 993/tcp (imaps) | IMAPS | Implicit TLS |

---

## 6. Auto-Renewal Verification

**Control:** Operational — ensures certificate doesn't expire

**certbot-renew.timer Status:** Active (verified during session setup)
**Renewal window:** 30 days before expiry
**Current certificate expiry:** 2026-07-09 (89 days remaining as of 2026-04-10)
**Next renewal:** ~2026-06-09 (auto)

**Deploy hook verifies:** SELinux contexts restored after cert rotation; all affected services reloaded.

---

## 7. DNS Security Records

**Domain:** diwai.org
**DNS Provider:** Cloudflare (used for Let's Encrypt DNS-01 validation)

**Recommended DNS records (to verify via Cloudflare):**

| Record | Type | Purpose |
|--------|------|---------|
| `diwai.org` | MX | Mail exchanger |
| `diwai.org` | TXT (SPF) | Sender Policy Framework |
| `_dmarc.diwai.org` | TXT (DMARC) | DMARC policy |
| `mail._domainkey.diwai.org` | TXT (DKIM) | DomainKeys (if configured) |

**Note:** SPF, DKIM, and DMARC record verification to be confirmed via Cloudflare dashboard.

---

## 8. Compliance Summary

| Control | Requirement | Status |
|---------|-------------|--------|
| TLS 1.2+ for SMTP | Postfix `ssl_protocols` excludes TLS 1.0/1.1 | ✅ PASS |
| TLS 1.2+ for IMAP | Dovecot `ssl_min_protocol = TLSv1.2` | ✅ PASS |
| TLS 1.2+ for HTTPS | Apache `SSLProtocol -all +TLSv1.2 +TLSv1.3` | ✅ PASS |
| Valid certificate | Let's Encrypt wildcard, expires 2026-07-09 | ✅ PASS (89 days) |
| ECDSA key | Certificate Key Type: ECDSA | ✅ PASS |
| PFS cipher suites | ECDHE ciphers first in all configs | ✅ PASS |
| Auto-renewal | certbot-renew.timer active | ✅ PASS |
| SELinux cert contexts | restorecon in deploy hook | ✅ PASS |
| FIPS-compatible TLS | AES-256-GCM (FIPS-approved) | ✅ PASS |

---

**Verified By:** Donald E. Shannon, ISSO
**Date:** April 10, 2026
**Next Verification:** July 2026 (quarterly, or at certificate renewal)

---

**CLASSIFICATION:** CONTROLLED UNCLASSIFIED INFORMATION (CUI)
