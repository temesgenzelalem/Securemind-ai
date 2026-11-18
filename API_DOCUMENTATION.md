# SecureMind AI — REST API Documentation

**Document ID:** `SMAI-API-001`  
**Version:** 1.0.0  
**Base URL:** `https://app.securemind.ai/api/v1` (or `http://localhost:8000/api/v1`)  
**Interactive Swagger UI:** `/api/docs/`  
**Interactive ReDoc:** `/api/redoc/`  
**OpenAPI 3.0 Schema:** `/api/schema/`  

---

## 1. Authentication & Security

All protected endpoints require a JSON Web Token (JWT) passed in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

Tokens are valid for 60 minutes. Use the refresh endpoint to obtain a new access token before expiration.

---

## 2. API Endpoints

### 2.1 Authentication (`/api/v1/auth/`)

| Method | Endpoint | Description | Permitted Roles |
|---|---|---|---|
| `POST` | `/register/` | Register a new user account. | Anonymous |
| `POST` | `/login/` | Authenticate and obtain JWT access & refresh tokens. | Anonymous |
| `POST` | `/refresh/` | Refresh an expired access token using a valid refresh token. | Anonymous |
| `GET` | `/me/` | Retrieve current authenticated user profile and active workspace. | Authenticated |
| `POST` | `/change-password/`| Change current account password. | Authenticated |
| `POST` | `/switch-org/` | Switch active organization context in user session. | Authenticated |

#### Example: Login Request
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "analyst@securemind.ai", "password": "SecurePassword123!"}'
```

---

### 2.2 Organizations & Members (`/api/v1/organizations/`)

| Method | Endpoint | Description | Permitted Roles |
|---|---|---|---|
| `GET` | `/` | List all organizations where user has membership. | Authenticated |
| `POST` | `/` | Create a new organization tenant. | Authenticated |
| `GET` | `/{id}/` | Retrieve organization details and settings. | Member |
| `PATCH`| `/{id}/` | Update organization profile. | Org Admin |
| `GET` | `/{id}/members/` | List members and roles in organization. | Org Admin |
| `POST` | `/{id}/members/` | Invite/add a user to the organization. | Org Admin |

---

### 2.3 Asset Management & Verification (`/api/v1/assets/`)

| Method | Endpoint | Description | Permitted Roles |
|---|---|---|---|
| `GET` | `/` | List verified and pending assets in active organization. | Authenticated |
| `POST` | `/` | Register a new web application asset. | Org Admin, Analyst |
| `GET` | `/{id}/` | Retrieve asset details and authorization status. | Authenticated |
| `POST` | `/{id}/challenge/` | Generate a cryptographic DNS or HTTP challenge. | Org Admin, Analyst |
| `POST` | `/{id}/verify/` | Trigger immediate verification check of challenge. | Org Admin, Analyst |
| `GET` | `/{id}/history/` | Chronological assessment progression and metrics. | Authenticated |
| `GET` | `/{id}/scope_rules/` | List active scope inclusion/exclusion rules. | Authenticated |
| `POST` | `/{id}/scope_rules/` | Add an in-scope or out-of-scope path pattern. | Org Admin, Analyst |

#### Example: Register Asset Request
```bash
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Portal",
    "base_url": "https://portal.example.com"
  }'
```

---

### 2.4 Assessments & Scans (`/api/v1/scans/`)

| Method | Endpoint | Description | Permitted Roles |
|---|---|---|---|
| `GET` | `/` | List all assessments for active organization. | Authenticated |
| `POST` | `/` | Create and launch an assessment. | Org Admin, Analyst |
| `GET` | `/{id}/` | Retrieve scan execution details, statuses, findings count. | Authenticated |
| `POST` | `/{id}/approve/` | Human-in-the-loop sign-off for active intrusive scans. | Analyst, Admin |
| `POST` | `/{id}/cancel/` | Terminate a queued or running scan. | Analyst, Admin |
| `GET` | `/{id}/compare/?with={id}` | Compare scan findings against a baseline scan (diff). | Authenticated |

#### Assessment Comparison Response Schema
```json
{
  "has_baseline": true,
  "target_scan": {"id": "uuid", "scan_type": "passive", "total_findings": 4},
  "baseline_scan": {"id": "uuid", "scan_type": "passive", "total_findings": 3},
  "summary": {
    "new_count": 1,
    "resolved_count": 0,
    "recurring_count": 3,
    "net_change": 1,
    "posture_trend": "degraded"
  },
  "new_findings": [...],
  "resolved_findings": [...],
  "recurring_findings": [...]
}
```

---

### 2.5 Vulnerability Findings (`/api/v1/findings/`)

| Method | Endpoint | Description | Filters |
|---|---|---|---|
| `GET` | `/` | List normalized findings with evidence. | `severity`, `verification_status`, `scan`, `asset`, `source_scanner`, `search` |
| `GET` | `/{id}/` | Retrieve single finding with full evidence payload. | None |

---

### 2.6 AI Agent Telemetry (`/api/v1/agents/`)

| Method | Endpoint | Description | Filters |
|---|---|---|---|
| `GET` | `/executions/` | List agent executions with input/output payloads, models, tokens. | `agent_name`, `status`, `scan` |
| `GET` | `/workflows/` | View orchestrator workflow states and stage history. | `scan` |

---

### 2.7 Remediation Center (`/api/v1/remediation/`)

| Method | Endpoint | Description | Permitted Roles |
|---|---|---|---|
| `GET` | `/` | List remediation guides and code diffs. | Authenticated |
| `GET` | `/{id}/` | Retrieve code snippets and OWASP references. | Authenticated |
| `PATCH`| `/{id}/` | Update status (`in_progress`, `fixed`, `accepted_risk`) and notes. | Developer, Analyst, Admin |

---

### 2.8 Reports (`/api/v1/reports/`)

| Method | Endpoint | Description | Permitted Roles |
|---|---|---|---|
| `GET` | `/` | List generated security reports. | Authenticated |
| `POST` | `/` | Generate a new PDF report (`executive` or `technical_full`). | Analyst, Admin |
| `GET` | `/{id}/download/` | Download ReportLab generated `%PDF-1.4` file. | Authenticated (Tenant Enforced) |

---

### 2.9 Continuous Monitoring (`/api/v1/monitoring/`)

| Method | Endpoint | Description | Permitted Roles |
|---|---|---|---|
| `GET` | `/stats/` | Real-time posture statistics and metrics. | Authenticated |
| `GET` | `/schedules/` | List recurring assessment schedules. | Authenticated |
| `POST` | `/schedules/` | Create a recurring schedule (daily/weekly/monthly). | Analyst, Admin |
| `DELETE`| `/schedules/{id}/` | Delete a recurring scan schedule. | Analyst, Admin |
| `GET` | `/notifications/` | List assessment notifications & alerts. | Authenticated |
| `POST` | `/notifications/{id}/mark_read/` | Mark notification as read. | Authenticated |

---

### 2.10 Audit Trail (`/api/v1/audit/`)

| Method | Endpoint | Description | Permitted Roles |
|---|---|---|---|
| `GET` | `/` | Query immutable audit logs. Supports filtering by `action`, `target_type`, `actor`. | Org Admin, Platform Admin |

---

## 3. Standard HTTP Response Codes

| Status Code | Meaning | Example Scenario |
|---|---|---|
| `200 OK` | Request succeeded. | Retrieved finding details or downloaded PDF. |
| `201 Created` | Resource created. | Asset registered or report compiled. |
| `400 Bad Request` | Validation failure or SSRF violation. | Target IP resolves to private RFC1918 range. |
| `401 Unauthorized` | Missing or invalid JWT. | Bearer token expired or not supplied. |
| `403 Forbidden` | Insufficient role permissions. | Developer attempted to approve an active scan. |
| `404 Not Found` | Object does not exist or cross-tenant. | Requesting a scan belonging to another organization. |
| `500 Server Error` | Unexpected backend error. | Handled gracefully with logged audit event. |
