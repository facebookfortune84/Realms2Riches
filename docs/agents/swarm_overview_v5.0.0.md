# Sovereign Swarm Overview v5.0.0

This document describes the structure and organization of the agentic swarm in Realms2Riches.

## Fleet Composition
The swarm consists of approximately **1000 autonomous agents**, categorized into **7 specialized departments**. Each department is designed to handle a critical aspect of the company's operations.

| Department | Agent Count | Responsibilities |
|------------|-------------|------------------|
| **Cybernetic Engineering** | 200 | Backend development, logic kernels, and database management. |
| **Visual Intelligence** | 150 | UI/UX design, brand alchemy, and video content creation. |
| **Global Market Force** | 200 | SEO, viral sharding, and social media engagement. |
| **Integrity Shield** | 150 | Cybersecurity, compliance, and legal integrity (GDPR). |
| **Strategic Operations** | 100 | Workflow orchestration and project generation. |
| **Revenue Systems** | 100 | Fintech, Stripe integration, and pricing optimization. |
| **Fallback Optimization** | 100 | Self-healing, performance auditing, and CRO. |

## Agent Definition & Configuration
Agents are dynamically generated via the `generate_grand_fleet()` function in `orchestrator/src/agents/fleet.py`. Their personas and system prompts are based on their assigned department, ensuring deep specialization.

- **Definitions**: `orchestrator/src/agents/fleet.py`
- **Identity Hash**: Every agent has a unique 8-character hash for traceability.
- **Tool Access**: All agents have access to the `Universal Action Multiplexer` for cross-platform execution.
