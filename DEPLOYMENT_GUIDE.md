# SecureMind AI — Production Deployment Guide

**Document ID:** `SMAI-DEP-001`  
**Version:** 1.0.0  
**Target Environments:** Multi-Tenant SaaS & Enterprise Self-Hosted  

---

## 1. Introduction & Deployment Models

SecureMind AI supports two official deployment models:

### Model A: Multi-Tenant SaaS
In this mode, a centralized cloud cluster hosts multiple independent organizations with complete tenant boundary enforcement at both the API layer (`TenantObjectPermission`) and database foreign-key queries. Scanning workers share a queue with per-organization rate limits.

### Model B: Self-Hosted Enterprise
In this mode, an enterprise deploys SecureMind AI entirely inside its own virtual private cloud (VPC) or on-premise infrastructure. This ensures all target IP addresses, vulnerability reports, and raw HTTP evidences never leave the customer's perimeter. Private IP scanning can optionally be enabled via `ALLOW_PRIVATE_IP_SCANS=True` for internal pre-production testing.

---

## 2. Infrastructure Requirements

| Component | Minimum Specification (Development / PoC) | Recommended Specification (Production) |
|---|---|---|
| **CPU** | 4 vCPU Cores | 8–16 vCPU Cores (Dedicated) |
| **Memory (RAM)** | 8 GB RAM | 16–32 GB RAM (ZAP + Celery Workers) |
| **Storage (Disk)** | 40 GB SSD | 200+ GB NVMe SSD (PostgreSQL + PDF Reports) |
| **Operating System** | Ubuntu 22.04 LTS / Debian 12 / RHEL 9 | Ubuntu 22.04 LTS (Kernel 6.x+) |
| **Container Engine** | Docker Engine 24.0+ & Compose v2.20+ | Docker Engine 26.0+ with Docker Compose v2.26+ |
| **Networking** | 100 Mbps Public / Private | 1 Gbps with static egress IP for whitelist verification |

---

## 3. Container Topology & Architecture

The deployment topology consists of 8 containerized services communicating over an isolated Docker network (`securemind_network`):

```
                                  [ Internet / User Traffic ]
                                               │
                                       [ Reverse Proxy ]
                                    (Nginx / Traefik / Caddy)
                                    TLS 1.3 / Port 80 & 443
                                               │
                     ┌─────────────────────────┴─────────────────────────┐
                     ▼                                                   ▼
       ┌───────────────────────────┐                       ┌───────────────────────────┐
       │     Next.js Frontend      │                       │       Django Backend      │
       │    (Container: Port 3000) │                       │   (Gunicorn: Port 8000)   │
       └───────────────────────────┘                       └─────────────┬─────────────┘
                                                                         │
                                         ┌───────────────────────────────┴───────────────────────────────┐
                                         ▼                                                               ▼
                           ┌───────────────────────────┐                                   ┌───────────────────────────┐
                           │    PostgreSQL 16 DB       │                                   │       Redis 7.2 Broker    │
                           │   (Port 5432 - Internal)  │                                   │    (Port 6379 - Internal) │
                           └───────────────────────────┘                                   └─────────────┬─────────────┘
                                                                                                         │
                                         ┌───────────────────────────────────────────────────────────────┴─────────────────┐
                                         ▼                                                                                 ▼
                           ┌───────────────────────────┐                                                     ┌───────────────────────────┐
                           │   Celery Async Worker     │                                                     │   Celery Beat Scheduler   │
                           │(ZAP API + Nuclei Scanner) │                                                     │   (Recurring Audits)      │
                           └─────────────┬─────────────┘                                                     └───────────────────────────┘
                                         │
                                         ▼
                           ┌───────────────────────────┐
                           │   OWASP ZAP Daemon        │
                           │   (Port 8080 - Internal)  │
                           └───────────────────────────┘
```

> [!CAUTION]
> **Privilege Escalation Warning:** Never mount `/var/run/docker.sock` into any application container. Scanning processes run inside the isolated worker environment using static binaries and HTTP APIs without host socket access.

---

## 4. Step-by-Step Production Setup

### Step 1: Repository & Environment Initialization
```bash
# Clone the repository
git clone https://github.com/securemind-ai/securemind-platform.git /opt/securemind
cd /opt/securemind

# Create dedicated service user
sudo useradd -r -s /bin/false securemind
sudo chown -R securemind:securemind /opt/securemind
```

### Step 2: Configure Environment Variables
Generate cryptographically strong secrets for all sensitive keys:

```bash
# Generate secure Django secret key
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Generate secure database password
openssl rand -base64 32

# Generate ZAP API Key
openssl rand -hex 24
```

Create your production `/opt/securemind/.env`:

```ini
# Production Environment Flag
DEBUG=False
SECRET_KEY=<GENERATED_DJANGO_SECRET_KEY>
ALLOWED_HOSTS=app.securemind.ai,api.securemind.ai

# PostgreSQL Configuration
POSTGRES_DB=securemind_prod
POSTGRES_USER=securemind_app
POSTGRES_PASSWORD=<GENERATED_DB_PASSWORD>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis & Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Security Scanners
ZAP_API_URL=http://zap:8080
ZAP_API_KEY=<GENERATED_ZAP_KEY>
NUCLEI_TEMPLATES_DIR=/app/nuclei-templates
ALLOW_PRIVATE_IP_SCANS=False

# AI Model Provider
AI_PROVIDER=gemini
GEMINI_API_KEY=<YOUR_GOOGLE_AI_STUDIO_API_KEY>
AI_DEFAULT_MODEL=gemini-2.5-flash
AI_REASONING_MODEL=gemini-2.5-pro

# CORS & Frontend Origins
CORS_ALLOWED_ORIGINS=https://app.securemind.ai
NEXT_PUBLIC_API_URL=https://app.securemind.ai/api/v1
```

### Step 3: Initialize Database & Run Migrations
```bash
# Start infrastructure containers
docker compose up -d postgres redis

# Wait for healthy database status
docker compose run --rm backend python manage.py wait_for_db

# Execute schema migrations
docker compose run --rm backend python manage.py migrate

# Collect static assets
docker compose run --rm backend python manage.py collectstatic --noinput

# Create platform administrator account
docker compose run --rm backend python manage.py createsuperuser
```

### Step 4: Build & Launch Full Service Cluster
```bash
docker compose up -d --build
```

Check the health status of all running containers:
```bash
docker compose ps
```

---

## 5. Nginx Reverse Proxy & TLS Termination

Place an Nginx reverse proxy in front of the services to terminate HTTPS and route requests:

```nginx
# /etc/nginx/sites-available/securemind.conf

upstream backend_api {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream frontend_app {
    server 127.0.0.1:3000;
    keepalive 32;
}

server {
    listen 80;
    server_name app.securemind.ai;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.securemind.ai;

    ssl_certificate /etc/letsencrypt/live/app.securemind.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.securemind.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    client_max_body_size 25M;

    # API and Admin Routes -> Django Backend
    location /api/ {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    location /admin/ {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static Assets & Reports
    location /static/ {
        alias /opt/securemind/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Frontend Dashboard -> Next.js
    location / {
        proxy_pass http://frontend_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 6. Backup, Restoration & Disaster Recovery

### Automated PostgreSQL Backup Script
Create `/usr/local/bin/securemind-backup.sh`:

```bash
#!/usr/bin/env bash
set -eo pipefail
BACKUP_DIR="/var/backups/securemind"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"

docker exec -t securemind_postgres pg_dump -U securemind_app securemind_prod | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Retain backups for 30 days
find "$BACKUP_DIR" -type f -name "db_*.sql.gz" -mtime +30 -delete
echo "Backup completed: db_$TIMESTAMP.sql.gz"
```

### Database Restoration Procedure
```bash
gunzip < /var/backups/securemind/db_YYYYMMDD_HHMMSS.sql.gz | docker exec -i securemind_postgres psql -U securemind_app -d securemind_prod
```

---

## 7. Production Health Monitoring

SecureMind AI exposes several monitoring endpoints:

- **Database Connectivity:** Checked continuously via `python manage.py wait_for_db` container healthchecks.
- **REST API Health:** `GET /api/v1/auth/me/` returns HTTP 200 with user profile when active.
- **Queue Health:** Run `docker exec -it securemind_celery_worker celery -A core inspect ping` to ensure all worker threads are listening.
- **System Metrics:** `GET /api/v1/monitoring/stats/` provides real-time counts of active scans, verified assets, recurring schedules, and unread critical security alerts.
