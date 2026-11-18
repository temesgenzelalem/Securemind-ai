# SecureMind AI

> **Agentic AI-Powered Web Application Security Analysis and Remediation Platform**  
> Document ID: `SMAI-SRS-001` | Baseline Version: `1.0`

---

## 🌟 Overview

**SecureMind AI** is a production-oriented cybersecurity SaaS platform. It combines industry-proven security scanners (**OWASP ZAP** and **Nuclei**) with a coordinated multi-agent AI system (**1 Central Orchestrator + 6 Specialized Agents**) to provide automated, evidence-verified vulnerability assessments and actionable developer remediation.

### The 1 + 6 Agent Architecture
- **Central AI Orchestrator:** Workflow supervisor, task delegator, and assessment consolidator.
- **01 Authorization Agent:** Validates ownership challenges (DNS TXT / HTTP token) and enforces target boundaries.
- **02 Reconnaissance Agent:** Passively gathers tech stack details, headers, and endpoints.
- **03 Vulnerability Scanning Agent:** Orchestrates OWASP ZAP and Nuclei runs in isolated environments.
- **04 Verification Agent:** Examines raw HTTP evidence to eliminate false positives.
- **05 Risk Assessment Agent:** Evaluates contextual risk and prioritizes vulnerabilities.
- **06 Remediation Agent:** Produces developer-friendly explanations and framework-specific code fixes.

---

## 🏗️ Technology Stack

| Component | Technology |
|---|---|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Lucide Icons |
| **Backend API** | Python 3.12, Django 5, Django REST Framework, SimpleJWT |
| **Persistence** | PostgreSQL 16 |
| **Task Queue** | Celery 5, Redis 7 |
| **Security Engines** | OWASP ZAP, Nuclei |
| **Containerization** | Docker, Docker Compose |

---

## 📁 Repository Structure

```
SECUREMIND AI/
├── .env.example                # Environment variables template
├── .gitignore
├── docker-compose.yml          # Unified multi-service orchestration
├── README.md
├── backend/                    # Django REST Framework application
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── core/                   # Root Django configuration & Celery app
│   └── apps/
│       ├── core/               # Base models & DB health checks
│       ├── authentication/     # Custom User, JWT auth & RBAC
│       ├── organizations/      # Multi-tenant Orgs, Projects & Memberships
│       ├── assets/             # Asset registration & verification challenges
│       ├── scans/              # Scan lifecycles & ScannerExecutions
│       ├── findings/           # Normalized findings & HTTP evidence
│       ├── orchestrator/       # AI Orchestrator, Agents & JSON contracts
│       ├── remediation/        # Interactive remediation & code patches
│       ├── reports/            # Assessment PDF report generators
│       └── audit/              # Security audit logging
├── frontend/                   # Next.js web application
│   ├── Dockerfile.dev
│   ├── package.json
│   ├── tsconfig.json
│   └── src/app/                # App router, pages, and components
└── scanners/                   # Scanner worker configurations & isolation docs
```

---

## 🚀 Getting Started

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (v24+)
- [Docker Compose](https://docs.docker.com/compose/) (v2+)

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env to set your GEMINI_API_KEY, SECRET_KEY, and passwords
```

### 3. Launch Services
```bash
docker compose up -d --build
```

### 4. Access Platform
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **Django REST API:** [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
- **API Swagger Documentation:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **OWASP ZAP Daemon:** [http://localhost:8080](http://localhost:8080)
