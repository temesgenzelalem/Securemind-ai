# SecureMind AI — User Guide

**Document ID:** `SMAI-USR-001`  
**Version:** 1.0.0  
**Target Audience:** Developers, Security Analysts, and Organization Administrators  

---

## 1. Introduction

Welcome to **SecureMind AI**, the Agentic AI-powered Web Application Security Analysis and Remediation Platform. SecureMind AI helps you evaluate the security posture of your web applications with real cybersecurity scanning tools (**OWASP ZAP** and **Nuclei**) while using six specialized AI agents to filter false positives and provide actionable code remediation guidance.

---

## 2. Roles & Permissions

SecureMind AI enforces strict Role-Based Access Control (RBAC):

| Role | Scope | Permitted Actions |
|---|---|---|
| **Platform Administrator** | System-wide | Manage all organizations, configure AI LLM providers, view system-wide audit logs. |
| **Organization Administrator** | Organization | Invite and remove team members, register assets, initiate verification challenges, configure scan schedules. |
| **Security Analyst** | Organization | Review and sign off on active scans, initiate passive and controlled active assessments, verify findings, generate PDF reports. |
| **Developer** | Organization | View assigned findings, read remediation guidance and code diffs, update remediation statuses (`In Progress`, `Fixed`). |
| **Viewer** | Organization | Read-only access to vulnerability dashboards and generated PDF reports. |

---

## 3. Step-by-Step Workflow Walkthrough

### 3.1 Account Creation & Workspace Selection
1. Navigate to the SecureMind AI dashboard at `http://localhost:3000` (or your company's domain).
2. Click **Create an Account**, enter your email, password, and full name.
3. Upon registration, you are automatically assigned a personal workspace. If you were invited to an enterprise organization, select the organization dropdown in the top navigation bar to switch your active context.

---

### 3.2 Asset Registration
Before testing any web service, you must register it as an **Asset**:

1. In the sidebar, click **Assets** and choose **+ Register Web Application**.
2. Provide a descriptive **Name** (e.g., `Customer Payment Portal`).
3. Enter the **Base URL** (e.g., `https://portal.mycompany.com`).
4. SecureMind AI automatically normalizes the domain name and applies deterministic SSRF checks to ensure the target is a valid external destination.

---

### 3.3 Verifying Domain Ownership & Authorization
To prevent unauthorized scanning, SecureMind AI requires cryptographic proof of ownership:

1. Click on the pending asset and select **Generate Verification Challenge**.
2. Choose one of two verification methods:

#### Method A: DNS TXT Record Verification (Recommended for Production)
- SecureMind AI provides a challenge token: `securemind-verify=a8b3c9f...`
- Log into your DNS provider (Cloudflare, Route53, GoDaddy) and add a TXT record for `@` or your subdomain with the exact value provided.
- Click **Check Verification**. SecureMind AI queries authoritative nameservers to confirm the record.

#### Method B: HTTP Well-Known Token File (Recommended for Web Developers)
- SecureMind AI generates a unique verification token file.
- Place the file on your web server so it is publicly accessible at:
  ```
  https://yourdomain.com/.well-known/securemind-challenge.txt
  ```
- Click **Check Verification**. SecureMind AI fetches the file and validates the token hash.

> [!IMPORTANT]
> Once verified, an asset is granted a **90-day authorization window**. After 90 days, authorization expires automatically and must be refreshed to continue active assessments.

---

### 3.4 Configuring Scan Scope Rules
Prevent scanners from logging out sessions or touching sensitive administrative endpoints:

1. Open your asset's details and scroll to **Scope Rules**.
2. Click **+ Add Scope Rule**.
3. Select **Excluded / Out-of-Scope** and define a pattern:
   - `/admin/logout` (Prevents terminating test sessions)
   - `/api/v1/billing/delete-account` (Protects sensitive destructive actions)
   - `/oauth/*` (Excludes third-party identity providers)

---

### 3.5 Launching a Security Assessment

SecureMind AI offers three assessment profiles:

1. **Passive Reconnaissance & Header Audit (`passive`):**
   - Safe for live production environments.
   - Spiders public pages, analyzes HTTP security headers (HSTS, CSP, X-Frame-Options), and fingerprints technologies without sending aggressive attack payloads.
   - Executes immediately without requiring human review.

2. **Controlled Active Assessment (`controlled_active`):**
   - Sends non-destructive DAST payloads to identify SQL Injection, Cross-Site Scripting (XSS), and SSRF.
   - **Human-in-the-Loop Safeguard:** Automatically placed in `Authorization Review` status. An Organization Administrator or Security Analyst must review the target scope and click **Approve Scan** before execution begins.

3. **Comprehensive Template Scan (`comprehensive`):**
   - Combines OWASP ZAP active attack rules with Nuclei v3.3.5 community vulnerability templates.
   - Also requires formal analyst sign-off prior to execution.

---

### 3.6 Navigating Findings & Technical Evidence

When an assessment completes:

1. Navigate to **Findings** in the sidebar.
2. Filter vulnerabilities by **Severity** (Critical, High, Medium, Low) or **Verification Status**:
   - **Confirmed:** Technical evidence proves the payload executed or reflected in the application DOM (Confidence $\ge 0.90$).
   - **Likely:** Anomaly or header misconfiguration strongly suggests a vulnerability.
   - **Unverified:** Potential issue flagged by scanner heuristics requiring further review.
   - **False Positive:** Filtered out by the AI Verification Agent based on response patterns.
3. Click any finding to inspect its **Raw Evidence Transcript**:
   - Exact HTTP Request sent.
   - Exact HTTP Response received.
   - Specific parameter and payload utilized.

---

### 3.7 Remediation Center & Code Diffs

Developers can fix vulnerabilities directly using AI-generated guidance:

1. Click on a finding and open the **Remediation** tab.
2. Review the **Developer Explanation** written in clear engineering terms.
3. Review the **Code Diff**:
   - **Before (Vulnerable):** Highlights flawed code (e.g., raw SQL string interpolation).
   - **After (Secure):** Demonstrates the parameterized ORM query or escaping method for your detected framework (e.g., Django, Express, FastAPI).
4. Update the lifecycle status:
   - Mark as **In Progress** while writing your patch.
   - Mark as **Fixed** once deployed to staging.
   - Enter your developer notes for compliance audit tracking.

---

### 3.8 Continuous Monitoring & Scan Scheduling

Set up automated recurring audits to maintain security over time:

1. Navigate to **Monitoring** in the dashboard.
2. Click **+ New Recurring Schedule**.
3. Select your verified asset, scan profile (`passive` or `controlled_active`), and frequency:
   - **Daily** (Recommended for staging / CI environments)
   - **Weekly** (Recommended for active production web services)
   - **Monthly** (Recommended for compliance baselines)
4. Celery Beat automatically queues assessments when due and triggers email and dashboard notifications.

---

### 3.9 Assessment Comparison & Historical Diffs

Track how your security posture evolves between releases:

1. Open **Assessments** and select a completed scan.
2. Click **Compare Assessment**.
3. Choose a baseline scan (or default to the previous audit).
4. SecureMind AI calculates SHA-256 fingerprint diffs:
   - **New Vulnerabilities:** Newly introduced security flaws.
   - **Resolved Vulnerabilities:** Confirmed remediations.
   - **Recurring Vulnerabilities:** Persistent unpatched flaws.
   - **Posture Trend:** Displays whether your security posture is **Improved**, **Degraded**, or **Unchanged**.

---

### 3.10 Generating & Downloading PDF Reports

1. From any completed scan, click **Export Report**.
2. Select your report format:
   - **Executive Summary:** High-level metrics, CVSS breakdown, risk distribution.
   - **Full Technical Audit:** Complete evidence transcripts, scanner execution logs, and developer code diffs.
3. SecureMind AI compiles an audit-grade PDF (`%PDF-1.4`) using ReportLab.
4. Click **Download PDF** to save the encrypted artifact for compliance auditors.
