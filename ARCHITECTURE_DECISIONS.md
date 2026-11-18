# SecureMind AI — Architecture Decision Records (ADRs)

**Document Version:** 1.0.0  
**Status:** Active Baseline  

---

### ADR-001: 1 Central Orchestrator + 6 Specialized Agents Architecture
* **Context:** The system needs to coordinate complex security operations without confusing users with multiple chatbots or overwhelming single LLM prompts.
* **Decision:** We implement a structured multi-agent architecture comprising one Central AI Orchestrator (`SMAI-AI-ORC-001`) and six specialized agents (`SMAI-AI-AGT-001` through `006`). Users interact with a single SaaS dashboard; agent coordination occurs asynchronously in the Celery background worker tier.
* **Consequences:** Provides clear modularity, testability, and isolated failure handling, while keeping the user experience unified and professional.

---

### ADR-002: Deterministic Scope & Authorization Enforcement
* **Context:** AI models are non-deterministic and susceptible to hallucination or prompt injection. Relying on an LLM to decide if a scan is legally permitted presents severe legal and security risks.
* **Decision:** Scan authorization, target scope boundary checks, rate limits, and ownership verification must be enforced by **deterministic Python code, PostgreSQL constraints, and network firewall policies**. AI agents cannot override backend authorization.
* **Consequences:** Guarantees that scans only run against verified, authorized targets within explicit path and port boundaries.

---

### ADR-003: Two-Tier SSRF Prevention
* **Context:** Dynamic scanning engines probe web applications and follow redirects. Without controls, attackers could target internal cloud services (e.g. AWS metadata `169.254.169.254`) or private subnets (`10.0.0.0/8`, `192.168.0.0/16`, `127.0.0.1`).
* **Decision:** Implement SSRF validation at two tiers:
  1. *Application Tier:* Pre-flight validation resolving hostname and checking all IPv4/IPv6 addresses against loopback, private, and link-local ranges.
  2. *Network / Egress Tier:* Docker network isolation blocking scanner containers from communicating with private subnets in SaaS deployments, while maintaining configurable access for self-hosted enterprise deployments.
* **Consequences:** Completely prevents internal service probing and cloud credential extraction.

---

### ADR-004: Evidence-Driven Finding Verification
* **Context:** DAST scanners report high rates of false positives based on heuristic pattern matching, frustrating developers.
* **Decision:** All scanner alerts must be corroborated by raw HTTP traffic evidence (request, response, headers, timing). The Verification Agent specifically inspects whether probe payloads actually executed or were reflected unescaped, assigning confidence scores and false-positive flags.
* **Consequences:** Eliminates noise and ensures developers only spend time addressing genuine vulnerabilities.

---

### ADR-005: Multi-Provider LLM Abstraction with Honest Offline Degradation
* **Context:** SecureMind AI must support both cloud SaaS (using models like Google Gemini) and self-hosted environments that may use local models or operate in offline/restricted environments.
* **Decision:** The AI orchestration layer communicates through a unified `LLMProvider` abstraction. When no API key or model is configured, the platform reports an honest "AI Provider Unconfigured" state rather than fabricating or mocking AI output.
* **Consequences:** Code remains vendor-agnostic and maintains integrity without misleading users.

---

### ADR-006: Container Isolation & No Host Socket Mounting
* **Context:** Mounting `/var/run/docker.sock` into worker containers gives those containers root-equivalent privileges on the host, creating a critical vulnerability.
* **Decision:** Remove host Docker socket mounts. Scanners execute as dedicated networked services (`zaproxy/zap-stable`) or containerized binaries within the worker container with restricted capabilities (`CAP_DROP=ALL`).
* **Consequences:** Prevents container breakout and host compromise.
