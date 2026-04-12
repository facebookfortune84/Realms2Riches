# PRD: Realms2Riches Company-in-a-Box Swarm v1
 
**Status:** Draft  
**Date:** 2026-04-12  
**Owner:** Product
 
---
 
## Problem
 
Running a digital game-economy business (Realms2Riches) requires continuous coordination across API services, code maintenance, content publishing, and outreach — tasks currently handled manually or not at all. There is no unified automation layer orchestrating these operations, leading to developer bottlenecks, stale content, and missed growth touchpoints.
 
---
 
## Target User
 
| Persona | Description |
|---|---|
| **Internal Operator** | Solo founder or small technical team managing the R2R platform day-to-day |
| **Developer Contributor** | Part-time devs who submit PRs and need automated review/merge pipelines |
| **Business Stakeholder** | Non-technical owner who needs content and outreach running without manual input |
 
---
 
## Core Features
 
### 1. API Swarm Agent
- Monitors the existing Python backend for health, latency, and error-rate anomalies
- Auto-restarts degraded IIS-hosted endpoints via PowerShell/IIS management APIs
- Surfaces alerts and remediation logs to a lightweight dashboard
- Manages subdomain routing sanity checks (e.g., `api.realms2riches.com`, `admin.*`)
 
### 2. Repo Maintenance Swarm
- Scheduled agent that triages open GitHub issues and PRs: labels, prioritizes, closes stale
- Runs automated dependency audits (`pip-audit`, `npm audit`) and opens patch PRs
- Enforces branch hygiene: flags long-lived branches, draft PRs past SLA
- Executes CI smoke tests on WSL2 dev environment before promoting to Windows Server 2025 / IIS staging
 
### 3. Content & Outreach Automation
- Pulls game economy data / product updates from the backend API
- Generates and schedules social posts, newsletters, and blog drafts on a configurable cadence
- Routes drafts to operator approval queue before publish; auto-publishes on approval timeout
- Tracks basic engagement metrics and feeds summary reports back into the swarm context
 
---
 
## Non-Goals (v1)
 
- No autonomous code deployment to production without human sign-off
- No customer support / ticketing automation
- No mobile app or native desktop interface
- No multi-tenant / white-label packaging
- No real-time game-engine integration or in-game event hooks
- No replacement of the existing Python backend or frontend — swarm operates alongside them
 
---
 
## Success Metrics
 
| Metric | Target (90-day) |
|---|---|
| API uptime maintained by swarm (no manual restart required) | ≥ 99.5 % |
| Repo issues triaged within 24 h of open | ≥ 90 % |
| Content pieces published per week without manual authoring | ≥ 3 |
| Dependency vulnerabilities remediated within 7 days of disclosure | 100 % |
| Operator time spent on routine maintenance tasks | ↓ 60 % vs. baseline |
 
---
 
## Constraints
 
| Area | Constraint |
|---|---|
| **Hosting** | Windows Server 2025 + IIS; no Docker in production (WSL2 for dev only) |
| **Dev environment** | WSL2 on dev machines; scripts must be dual-path (bash + PowerShell) |
| **Networking** | Subdomain-per-service architecture; agents must not hard-code IPs |
| **Backend** | Existing Python service is the source of truth — swarm is read/write via its API only |
| **Frontend** | Existing frontend unchanged in v1; swarm dashboard is a separate lightweight UI or CLI |
| **Auth** | All agent-to-service calls authenticated via existing token scheme (no new auth infra) |
| **Cost** | LLM calls budgeted; prefer local/cheap models for high-frequency tasks, GPT-4-class only for drafting |
| **Compliance** | No PII stored in swarm logs; outreach content must pass operator review before external publish |