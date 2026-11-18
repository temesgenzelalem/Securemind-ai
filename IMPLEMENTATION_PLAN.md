# SecureMind AI — Phased Implementation Plan

**Document Version:** 1.0.0  
**Status:** Approved for Execution Pending Phase-0 Sign-off  

---

## Overview

This implementation plan outlines the prioritized sequence of engineering tasks required to transition SecureMind AI from its current baseline into a production-grade, fully functional, and verifiable MVP. Each phase has explicit tasks, acceptance criteria, and verification commands.

---

## Phase 1: Environment Hardening & Database Migrations
* **Goal:** Establish a robust container foundation and persistent relational schema.
* **Tasks:**
  1. Remove dangerous `/var/run/docker.sock` volume mount from `celery_worker` in `docker-compose.yml`.
  2. Update `backend/Dockerfile` to install `nuclei` binary and basic defensive templates.
  3. Generate all initial Django database migrations across all modular apps (`core`, `authentication`, `organizations`, `assets`, `scans`, `findings`, `orchestrator`, `remediation`, `reports`, `audit`).
  4. Implement an isolated, lightweight local test target (deliberately vulnerable test application) in Docker Compose for safe scanner testing.
* **Verification:**
  - `python manage.py makemigrations --check` exits with 0.
  - `docker compose config` validates without errors.
  - Test target container responds on dedicated internal test bridge.

---

## Phase 2: Authentication, Tenant Isolation & RBAC Testing
* **Goal:** Verify that multi-tenant security policies and role permissions are airtight.
* **Tasks:**
  1. Write Django unit and integration tests for:
     - User registration with automatic workspace creation.
     - JWT token issue, refresh, and role claim verification.
     - Cross-tenant data isolation (User A cannot access User B's organizational data).
     - RBAC restrictions (`viewer` cannot launch scans; `developer` cannot invite members).
* **Verification:**
  - Automated test runner executes `backend/tests/test_auth_rbac.py` with 100% pass rate.

---

## Phase 3: Asset Verification & Scope Enforcement Hardening
* **Goal:** Guarantee that only authorized assets can be scanned and SSRF attacks are prevented.
* **Tasks:**
  1. Implement DNS TXT and HTTP verification integration tests using mock DNS responses and local HTTP servers.
  2. Harden `TargetSafetyValidator` against DNS rebinding (pinning resolved IP during request) and IPv6 edge cases (`[::ffff:127.0.0.1]`).
  3. Implement authorization expiration checking (scans rejected if authorization > 90 days old).
* **Verification:**
  - Automated tests execute `backend/tests/test_assets_scope.py` with 100% pass rate.

---

## Phase 4: Scanner Integration (OWASP ZAP & Nuclei)
* **Goal:** Connect real scanning engines to the Celery asynchronous queue and local test target.
* **Tasks:**
  1. Ensure `ZAPScannerService` communicates with the containerized ZAP daemon over internal Docker network.
  2. Wire `NucleiScannerService` to execute reviewed templates against the local test target.
  3. Validate that scanner output is correctly parsed into raw JSON without fabrication.
  4. Ensure proper handling and failure states if a scanner engine is unreachable.
* **Verification:**
  - Run Celery task test scanning the local test target; verify raw output records created in PostgreSQL.

---

## Phase 5: AI Orchestration & Standardized Agent Architecture
* **Goal:** Refactor agents into a structured, schema-validated multi-agent pipeline.
* **Tasks:**
  1. Create `BaseAgent` abstract class with strict lifecycle hooks (`validate_input()`, `execute()`, `validate_output()`, `handle_error()`).
  2. Implement Pydantic v2 schemas for all 6 agents:
     - `AuthorizationAgent` (`SMAI-AI-AGT-001`)
     - `ReconnaissanceAgent` (`SMAI-AI-AGT-002`)
     - `VulnerabilityScanningAgent` (`SMAI-AI-AGT-003`) — encapsulated as explicit agent class.
     - `VerificationAgent` (`SMAI-AI-AGT-004`)
     - `RiskAssessmentAgent` (`SMAI-AI-AGT-005`)
     - `RemediationAgent` (`SMAI-AI-AGT-006`)
  3. Implement a multi-provider LLM abstraction layer supporting:
     - Google Gemini (`google-genai` SDK)
     - OpenAI-compatible endpoints
     - Explicit offline / unconfigured state reporting (honest fallback without pretending AI ran).
  4. Defend against prompt injection by sanitizing raw scanner and web text before LLM interpolation.
* **Verification:**
  - Run `backend/tests/test_agents.py` validating schema validation, prompt safety, and offline degradation.

---

## Phase 6: Finding Normalization, Evidence & Verification Engine
* **Goal:** Perfect the false-positive filtering pipeline using raw HTTP evidence.
* **Tasks:**
  1. Test finding deduplication logic across repeated scanner executions.
  2. Verify that `VerificationAgent` correctly flags false positives (e.g. rate-limit errors vs. real SQLi delays).
  3. Ensure raw HTTP request and response evidence is preserved verbatim for auditability.
* **Verification:**
  - Unit tests verifying normalization of sample ZAP alerts and Nuclei JSON lines.

---

## Phase 7: Remediation Center & Deterministic PDF Reporting
* **Goal:** Provide framework-specific fix guidance and generate downloadable PDF reports.
* **Tasks:**
  1. Complete the `Report` generation service using a real PDF rendering engine (ReportLab / WeasyPrint).
  2. Generate executive summaries, finding breakdowns, CVSS metrics, and developer remediation diffs.
  3. Implement secure, authorized PDF download endpoints with tenant access verification.
* **Verification:**
  - Test generating a PDF report for a completed scan; verify valid PDF bytes and file storage.

---

## Phase 8: Next.js Frontend Real API Integration
* **Goal:** Replace static React state arrays with live REST API data.
* **Tasks:**
  1. Create an API client service in `frontend/src/services/api.ts` with Axios interceptors and JWT token refresh.
  2. Implement authentication flow (Login, Register, Logout, AuthContext).
  3. Connect `OverviewView`, `AssetsView`, `AssessmentsView`, `FindingsView`, and `RemediationView` to live Django endpoints.
  4. Add loading skeletons, real-time status polling, and clear empty/error states.
* **Verification:**
  - End-to-end browser / API test verifying login, asset registration, and finding retrieval.

---

## Phase 9: Audit Trail, Monitoring & Assessment History
* **Goal:** Provide compliance traceability and assessment comparison.
* **Tasks:**
  1. Verify audit logs record every sensitive action (login, domain verification, scan launch, status update).
  2. Implement finding diffing across scans (compare new findings vs. resolved findings).
* **Verification:**
  - Automated tests verifying audit log creation on API mutation endpoints.

---

## Phase 10: End-to-End Acceptance Testing & Security Hardening
* **Goal:** Validate the complete authorized assessment lifecycle from registration to report download.
* **Tasks:**
  1. Execute full end-to-end integration test against the local test application.
  2. Verify all 13 User Acceptance Criteria from the SRS.
  3. Finalize all documentation deliverables.
* **Verification:**
  - Complete automated test suite passes with zero failures.
