# SecureMind AI — Scanner Worker Subsystem

This directory contains container definitions and orchestration scripts for the external scanning engines:

## 1. OWASP ZAP (Zed Attack Proxy)
- **Role:** Dynamic Application Security Testing (DAST), passive analysis, active spidering, safe active vulnerability checks.
- **Access Method:** Communicates with the backend Celery workers via the ZAP REST API daemon.
- **Port:** `8080` (Internal Docker network only).

## 2. Nuclei
- **Role:** Fast, template-based vulnerability detection across standard CVEs, misconfigurations, and exposed panels.
- **Execution:** Invoked via controlled CLI/Docker workers with rate-limiting and target scope enforcement.

## 3. Network Isolation & SSRF Guardrails
- Scanners run in dedicated Docker network bridges with egress filtering rules.
- Localhost (`127.0.0.1`), private RFC1918 ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), and Cloud Metadata Services (`169.254.169.254`) are blocked unless `ALLOW_PRIVATE_IP_SCANS=True` is explicitly configured for self-hosted enterprise internal deployments.
