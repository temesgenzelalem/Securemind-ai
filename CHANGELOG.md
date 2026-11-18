# SecureMind AI — Changelog

All notable changes to the SecureMind AI platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-11-18

### Initial Production Baseline Release (MVP)

#### Added
- **Core Architecture & Infrastructure:**
  - Containerized microservices topology using Docker Compose: `backend` (Django 5.0), `frontend` (Next.js 14), `postgres` (PostgreSQL 16), `redis` (Redis 7.2), `celery_worker`, `celery_beat`, `zap` (OWASP ZAP daemon), and `test_target` (safe deliberately vulnerable test application).
  - Hardened Docker configuration: eliminated dangerous `/var/run/docker.sock` volume mounts to prevent container breakouts.
  - Asynchronous background task orchestration using Celery with Redis broker and Celery Beat periodic scheduler.
  - Complete schema migrations generated and applied across all 10 Django applications.

- **Authentication, Multi-Tenancy & RBAC:**
  - Custom `User` model supporting 5 hierarchical security roles (`platform_admin`, `org_admin`, `security_analyst`, `developer`, `viewer`).
  - JWT authentication using SimpleJWT with custom organization claims and token refresh endpoints (`/api/v1/auth/`).
  - Multi-tenant architecture (`Organization`, `Project`, `Membership`) with strict cross-tenant object authorization (`TenantObjectPermission`).
  - Dynamic organization context switching in active user sessions.

- **Asset Management & Verification:**
  - Web application asset registration with RFC1035 hostname validation and normalization.
  - Cryptographic domain ownership verification supporting both DNS TXT records (`securemind-verify=<token>`) and HTTP well-known token files (`/.well-known/securemind-challenge.txt`).
  - 90-day authorization expiration window and re-verification workflows.
  - Granular in-scope and out-of-scope path rules with port restrictions.

- **Deterministic Security & SSRF Guardrails:**
  - Hardened pre-scan network validator (`TargetSafetyValidator`) blocking loopback addresses (`127.0.0.0/8`, `localhost`), RFC1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), cloud metadata services (`169.254.169.254`), and IPv6-mapped IPv4 addresses (`::ffff:127.0.0.1`).
  - Strict human-in-the-loop sign-off requirement for active/intrusive scan profiles (`controlled_active`, `comprehensive`).

- **DAST Security Scanners:**
  - Real OWASP ZAP integration via HTTP API: target spidering, passive alert inspection, and controlled active attacks.
  - Real Nuclei integration packaging static binary v3.3.5 and community vulnerability templates with rate-limiting (15 req/sec) and execution timeouts.
  - Unification and normalization of disparate scanner outputs into a standard `Finding` schema.
  - Deterministic SHA-256 fingerprint generation (`title|affected_url|parameter`) for finding deduplication.
  - Verbatim raw HTTP request and response evidence capture in `Evidence` records.

- **Agentic AI Architecture:**
  - One Central AI Orchestrator (`SMAI-AI-ORC-001`) supervising assessment execution plans and tracking workflow states (`WorkflowState`).
  - Six specialized AI agents inheriting from `BaseAgent` with strict Pydantic v2 input/output schemas:
    1. Authorization Agent (`SMAI-AI-AGT-001`)
    2. Reconnaissance Agent (`SMAI-AI-AGT-002`)
    3. Vulnerability Scanning Agent (`SMAI-AI-AGT-003`)
    4. Verification Agent (`SMAI-AI-AGT-004`)
    5. Risk Assessment Agent (`SMAI-AI-AGT-005`)
    6. Remediation Agent (`SMAI-AI-AGT-006`)
  - Multi-provider LLM abstraction layer (`LLMClient`) supporting Google Gemini (`google-genai` SDK) and an honest deterministic offline provider (`OfflineLLMProvider`).
  - Prompt injection defense using structural delimiters (`<<<UNTRUSTED_EXTERNAL_DATA>>>`) and input sanitization.
  - Agent telemetry logging in `AgentExecution` tracking input/output payloads, models used, tokens, and execution times.

- **Remediation Center:**
  - Actionable, framework-specific code diffs (Before vs. After) for detected technology stacks (Django, Express, Spring, etc.).
  - Developer remediation lifecycle tracking (`Open` -> `In Progress` -> `Fixed` -> `Accepted Risk`) with compliance audit notes.

- **PDF Report Generation:**
  - Deterministic audit-grade PDF generator built with ReportLab producing `%PDF-1.4` compliant artifacts.
  - Includes executive summaries, severity breakdown charts, finding evidence transcripts, and code remediation diffs.
  - Secure tenant-scoped report download endpoints.

- **Continuous Monitoring & Audit Logging:**
  - Recurring assessment schedules (`ScanSchedule`) supporting daily, weekly, and monthly execution frequencies.
  - Automated Celery Beat task (`run_scheduled_assessments`) evaluating due schedules.
  - Assessment comparison service (`ScanComparisonService`) calculating fingerprint diffs (new, resolved, recurring vulnerabilities) and posture trends.
  - Immutable compliance audit trail (`AuditLog`) tracking all security-sensitive actions with query filtering.
  - Alert notification dispatch (`AssessmentNotification`) for completed scans and critical vulnerabilities.

- **Frontend Integration:**
  - Modern Next.js 14 frontend using TypeScript, Tailwind CSS, and Lucide icons.
  - Authenticated Axios API client layer with JWT bearer interceptors and token refresh.
  - Connected live DRF backend endpoints to all dashboard views: `AssetsView`, `AssessmentsView`, `FindingsView`, `RemediationView`, and `OverviewView`.

- **Quality Assurance & Verification:**
  - 33 automated test cases across 7 test suites achieving a 100% pass rate.
  - Complete end-to-end acceptance test validating all 13 User Acceptance Criteria from SRS Section 12.4.
  - Verified clean Next.js 14 production build (`next build`).
