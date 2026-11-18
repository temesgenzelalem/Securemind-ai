# SecureMind AI — System Architecture Document (SAD)

**Document ID:** SMAI-SAD-001  
**Version:** 1.0  
**Status:** Architecture Baseline  
**Based on:** SRS (`SMAI-SRS-001`) & Project Overview (`SecureMind_AI_Overview.pdf`)  

---

## 1. Executive Summary & Architectural Philosophy

SecureMind AI is an **Agentic AI-driven Web Application Security and Remediation Platform**. Rather than acting as a simple conversational wrapper or replacing existing security scanners, SecureMind AI couples proven security engines (**OWASP ZAP** and **Nuclei**) with a structured multi-agent AI system (**1 Central Orchestrator + 6 Specialized Agents**).

### Core Design Tenets
1. **Deterministic Gates Over AI Decisions:** Scan authorization, target scope boundary checks, and SSRF restrictions are strictly enforced by deterministic backend code and network firewalls. AI agents never have the final say on whether a target is authorized.
2. **Invisible Multi-Agent Orchestration:** Users interact with a clean, cohesive SaaS dashboard (Next.js). The 6 agents operate autonomously within an asynchronous Celery pipeline, surfacing their reasoning as structured metadata, confidence scores, and remediation code.
3. **Evidence-Based Finding Verification:** No finding is marked as confirmed unless corroborated by raw HTTP traffic logs (request/response evidence). The Verification Agent's primary mission is the elimination of false positives.
4. **Actionable Developer Remediation:** The platform translates abstract CVEs and CWEs into framework-specific, copy-pasteable patches and defensive configurations tailored to the detected tech stack.

---

## 2. High-Level System Architecture

The system is separated into seven decoupled layers to guarantee security, fault tolerance, and independent scaling:

```mermaid
flowchart TD
    subgraph ClientLayer ["1. Presentation Layer (Next.js / TypeScript)"]
        UI["Web Dashboard, Scan Monitors, Vulnerability Center, Remediation UI"]
    end

    subgraph APILayer ["2. Application & API Layer (Django / DRF)"]
        API["REST API Endpoints (/api/v1/)"]
        AuthRBAC["Auth, Org Management & RBAC"]
        ScopeEngine["Deterministic Scope & Authorization Engine"]
    end

    subgraph QueueLayer ["3. Background Task Queue (Celery + Redis)"]
        Broker[("Redis Message Broker")]
        Workers["Celery Background Task Workers"]
    end

    subgraph OrchestrationLayer ["4. AI Orchestration Layer (Python)"]
        Orchestrator["Central AI Orchestrator"]
        Agents["6 Specialized Agents (Auth, Recon, Scan, Verify, Risk, Remed)"]
        LLMProvider["Configurable LLM Provider / Local Model Interface"]
    end

    subgraph ScannerLayer ["5. Isolated Scanner Workers (Docker Containers)"]
        ZAPWorker["OWASP ZAP Dynamic Engine"]
        NucleiWorker["Nuclei Template Engine"]
        EgressGuard["Egress Firewall & SSRF Guard"]
    end

    subgraph DataLayer ["6. Persistence Layer (PostgreSQL)"]
        DB[("PostgreSQL Database")]
    end

    UI <-->|HTTPS / REST API| API
    API --> AuthRBAC
    API --> ScopeEngine
    API -->|Dispatch Jobs| Broker
    Broker --> Workers
    Workers <--> Orchestrator
    Orchestrator <--> Agents
    Agents <--> LLMProvider
    Workers -->|Spawn Isolated Scans| ScannerLayer
    ScannerLayer -.->|Strict Scope Only| Target["Authorized Target Web App"]
    API <--> DB
    Workers <--> DB
```

---

## 3. Database Schema & Data Model (ER Design)

```mermaid
erDiagram
    ORGANIZATION ||--o{ USER : contains
    ORGANIZATION ||--o{ PROJECT : owns
    PROJECT ||--o{ ASSET : groups
    ASSET ||--o{ AUTHORIZATION_CHALLENGE : verifies
    ASSET ||--o{ SCOPE_RULE : defines
    ASSET ||--o{ SCAN : targets
    SCAN ||--o{ SCANNER_EXECUTION : runs
    SCAN ||--o{ AGENT_EXECUTION : logs
    SCAN ||--o{ FINDING : produces
    FINDING ||--o{ EVIDENCE : substantiates
    FINDING ||--o| RISK_ASSESSMENT : evaluated_by
    FINDING ||--o| REMEDIATION : resolved_by
    SCAN ||--o{ REPORT : generates
    ORGANIZATION ||--o{ AUDIT_LOG : tracks

    ORGANIZATION {
        uuid id PK
        string name
        string slug
        string plan_type
        jsonb settings
        timestamp created_at
    }

    USER {
        uuid id PK
        string email
        string hashed_password
        string role
        uuid organization_id FK
        boolean is_active
        timestamp created_at
    }

    ASSET {
        uuid id PK
        uuid organization_id FK
        string domain
        string base_url
        string verification_status
        timestamp verified_at
        timestamp authorization_expires_at
    }

    AUTHORIZATION_CHALLENGE {
        uuid id PK
        uuid asset_id FK
        string challenge_type
        string challenge_token
        string verification_target
        boolean is_verified
        timestamp expires_at
    }

    SCOPE_RULE {
        uuid id PK
        uuid asset_id FK
        string rule_type
        string pattern
        integer port
        boolean is_exclusion
    }

    SCAN {
        uuid id PK
        uuid asset_id FK
        string scan_type
        string status
        jsonb config_overrides
        timestamp started_at
        timestamp completed_at
    }

    SCANNER_EXECUTION {
        uuid id PK
        uuid scan_id FK
        string scanner_type
        string status
        jsonb raw_output_ref
        jsonb execution_stats
    }

    AGENT_EXECUTION {
        uuid id PK
        uuid scan_id FK
        string agent_name
        string status
        jsonb input_payload
        jsonb output_payload
        string model_used
        integer tokens_used
        timestamp created_at
    }

    FINDING {
        uuid id PK
        uuid scan_id FK
        uuid asset_id FK
        string title
        string cwe_id
        string cvss_vector
        float cvss_score
        string severity
        string verification_status
        float confidence_score
        string affected_url
        string http_method
        string parameter
    }

    EVIDENCE {
        uuid id PK
        uuid finding_id FK
        text raw_http_request
        text raw_http_response
        string payload_used
        string evidence_type
    }

    RISK_ASSESSMENT {
        uuid id PK
        uuid finding_id FK
        string business_impact
        string exploitability
        string priority
        text rationale
    }

    REMEDIATION {
        uuid id PK
        uuid finding_id FK
        string status
        text explanation
        text recommended_patch
        jsonb code_snippets
        text references
    }
```

---

## 4. Orchestrator State Machine & Workflow

Every assessment transitions through an immutable state machine managed by the Central Orchestrator:

```mermaid
stateDiagram-v2
    [*] --> Pending : Scan Requested
    Pending --> AuthorizationCheck : Orchestrator validates request
    AuthorizationCheck --> ScopeValidation : Auth Agent confirms valid challenge
    AuthorizationCheck --> Rejected : Authorization invalid or expired
    ScopeValidation --> Reconnaissance : Scope boundaries compiled
    ScopeValidation --> Rejected : Prohibited scope or SSRF violation
    Reconnaissance --> ActiveScanApproval : Recon completed
    ActiveScanApproval --> Queued : Passive profile OR Human Approved
    ActiveScanApproval --> AwaitingApproval : Intrusive profile requiring approval
    AwaitingApproval --> Queued : Approved by user
    AwaitingApproval --> Cancelled : Denied / Timed out
    Queued --> Scanning : Dispatched to Celery / Scanner Workers
    Scanning --> Verification : Raw ZAP & Nuclei logs normalized
    Verification --> RiskAssessment : Findings validated against HTTP evidence
    RiskAssessment --> Remediation : Severity & priority calculated
    Remediation --> Consolidation : Framework-specific fixes generated
    Consolidation --> Completed : Assessment summary & reports generated
    Scanning --> Failed : Scanner timeout / error
    Verification --> Failed : Fatal parsing / orchestration error
    Completed --> [*]
    Rejected --> [*]
    Failed --> [*]
    Cancelled --> [*]
```

---

## 5. Agent Input/Output JSON Contracts

To prevent untrusted data from causing prompt injection or invalid state transitions, each agent operates on strict, schema-validated JSON.

### 5.1 Authorization Agent (`SMAI-AI-AGT-001`)
* **Input Contract:**
```json
{
  "asset_id": "8f3e2b11-9a4c-4d3b-bf88-75c123abc456",
  "target_domain": "example.com",
  "requested_scan_type": "controlled_active",
  "verification_records": [
    {
      "method": "DNS_TXT",
      "token": "securemind-verify-xyz789",
      "verified": true,
      "verified_at": "2026-11-18T08:00:00Z"
    }
  ],
  "defined_scope": {
    "allowed_hosts": ["example.com", "api.example.com"],
    "allowed_ports": [80, 443],
    "excluded_paths": ["/admin/reset-db", "/logout"]
  }
}
```
* **Output Contract:**
```json
{
  "authorization_valid": true,
  "scope_validated": true,
  "requires_human_approval": true,
  "rejection_reason": null,
  "normalized_scope": {
    "include": ["https://example.com/*", "https://api.example.com/*"],
    "exclude": ["https://example.com/admin/reset-db", "https://example.com/logout"]
  }
}
```

### 5.2 Verification Agent (`SMAI-AI-AGT-004`)
* **Input Contract:**
```json
{
  "raw_finding": {
    "scanner": "Nuclei",
    "template_id": "cve-2023-xxxx",
    "title": "Reflected Cross-Site Scripting in search query",
    "target_url": "https://example.com/search?q=%3Cscript%3Ealert(1)%3C/script%3E",
    "http_request": "GET /search?q=%3Cscript%3Ealert(1)%3C/script%3E HTTP/1.1\nHost: example.com...",
    "http_response": "HTTP/1.1 200 OK\nContent-Type: text/html\n\nSearch results for <script>alert(1)</script>..."
  }
}
```
* **Output Contract:**
```json
{
  "verification_status": "Confirmed",
  "confidence_score": 0.95,
  "is_false_positive": false,
  "evidence_analysis": "The probe payload was reflected unescaped directly into the response DOM with a text/html content-type. No sanitization was observed.",
  "verification_notes": "Payload confirmed executing in browser context."
}
```

### 5.3 Remediation Agent (`SMAI-AI-AGT-006`)
* **Input Contract:**
```json
{
  "finding_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "title": "SQL Injection in User Search",
  "cwe": "CWE-89",
  "tech_stack": {
    "language": "Python",
    "framework": "Django"
  },
  "affected_component": "/api/users/search?filter=..."
}
```
* **Output Contract:**
```json
{
  "explanation": "The endpoint concatenates user input directly into a raw SQL query string instead of utilizing Django's parameterized ORM queries.",
  "recommended_strategy": "Migrate from RawSQL to Django ORM parameterized filtering or use params list.",
  "code_examples": [
    {
      "language": "python",
      "file_hint": "views.py",
      "vulnerable_pattern": "User.objects.raw(f'SELECT * FROM users WHERE name = {user_input}')",
      "secure_replacement": "User.objects.filter(name=user_input) # Automatically parameterized by Django ORM"
    }
  ],
  "references": [
    "https://docs.djangoproject.com/en/stable/topics/security/#sql-injection-protection",
    "https://cwe.mitre.org/data/definitions/89.html"
  ]
}
```

---

## 6. Scanner Isolation & Network Security Architecture

To meet non-functional requirements (`NFR-SEC-007`, `NFR-SEC-008`, `NFR-SEC-013`):

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DOCKER HOST SYSTEM                              │
│                                                                        │
│   ┌─────────────────────┐             ┌────────────────────────────┐   │
│   │   Celery App Node   │             │   Scanner Worker (ZAP)     │   │
│   │                     │             │   Docker Container         │   │
│   └──────────┬──────────┘             └─────────────┬──────────────┘   │
│              │                                      │                  │
│              │ Internal Docker Network              │ Isolated Bridge  │
│              ▼                                      ▼                  │
│   ┌────────────────────────────────────────────────────────────┐       │
│   │               EGRESS PROXY / IPTABLES FILTER               │       │
│   │                                                            │       │
│   │  - Blocks 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16       │       │
│   │  - Blocks 127.0.0.0/8 (Loopback)                           │       │
│   │  - Blocks 169.254.169.254 (Cloud Instance Metadata Service)│       │
│   │  - Only permits TCP ports 80, 443 to verified targets      │       │
│   └─────────────────────────────┬──────────────────────────────┘       │
│                                 │                                      │
└─────────────────────────────────┼──────────────────────────────────────┘
                                  ▼
                        PUBLIC INTERNET TARGET
```

* **SSRF Guarding:** Any target resolving to a private or loopback IP is blocked at both the API level and the egress proxy level before any scanner process is spawned.
* **Ephemeral Workspaces:** Scanner containers run with read-only root filesystems and write raw findings to a transient volume, destroyed immediately after findings are parsed and normalized.

---

## 7. REST API Route Structure

All endpoints reside under `/api/v1/` and enforce JWT authentication and RBAC:

* **Authentication & Identity:**
  - `POST /api/v1/auth/register/`
  - `POST /api/v1/auth/login/`
  - `POST /api/v1/auth/refresh/`
  - `GET /api/v1/auth/me/`
* **Organizations & Projects:**
  - `GET/POST /api/v1/organizations/`
  - `GET/POST /api/v1/organizations/{id}/members/`
  - `GET/POST /api/v1/projects/`
* **Assets & Scope Authorization:**
  - `GET/POST /api/v1/assets/`
  - `POST /api/v1/assets/{id}/challenge/` (Generates DNS TXT / HTTP challenge)
  - `POST /api/v1/assets/{id}/verify/` (Triggers backend ownership verification)
  - `GET/POST /api/v1/assets/{id}/scope-rules/`
* **Scans & AI Workflow:**
  - `GET/POST /api/v1/scans/`
  - `GET /api/v1/scans/{id}/status/` (Live polling / WebSocket stream)
  - `POST /api/v1/scans/{id}/cancel/`
  - `POST /api/v1/scans/{id}/approve/` (Human-in-the-loop sign-off)
* **Vulnerabilities & Evidence:**
  - `GET /api/v1/findings/` (Filters: severity, status, asset)
  - `GET /api/v1/findings/{id}/`
  - `GET /api/v1/findings/{id}/evidence/`
  - `PATCH /api/v1/findings/{id}/status/` (Open, In Progress, Fixed, False Positive)
* **Remediation & Reports:**
  - `GET /api/v1/findings/{id}/remediation/`
  - `POST /api/v1/reports/generate/`
  - `GET /api/v1/reports/{id}/download/`

---

## 8. Development Implementation Roadmap

Following the 12 phases outlined in the project blueprint:

1. **Phase 1: Architecture Baseline & Environment** (Complete with this SAD).
2. **Phase 2: Django Backend Foundation & Models** (PostgreSQL schema, migrations, base models).
3. **Phase 3: Auth, RBAC & Multi-Tenancy** (Custom user model, org tenant isolation).
4. **Phase 4: Asset Registration & Verification Engine** (DNS TXT & HTTP token verification).
5. **Phase 5: Secure Scanner Worker Sandbox** (Docker, Celery, SSRF egress rules).
6. **Phase 6: OWASP ZAP & Nuclei Engine Integrations** (Wrappers & output normalizers).
7. **Phase 7: Central Orchestrator & 6 Specialized Agents** (Python agent engine, prompts, JSON schemas).
8. **Phase 8: Finding Normalization, Evidence & Risk Scoring** (Deduplication, CVSS/CWE).
9. **Phase 9: AI Remediation & PDF Reporting** (Fix generation, WeasyPrint/report generation).
10. **Phase 10: Next.js Frontend Dashboard** (Interactive UI, scan status, finding explorer).
11. **Phase 11: Security Hardening & Penetration Testing** (Audit logs, rate limiting, defensive checks).
12. **Phase 12: Production Packaging** (Docker Compose for self-hosted and cloud SaaS).
