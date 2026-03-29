# Oracle Knowledge Bank: Intelligence Patterns

This document extracts the core patterns of world-class agentic behavior from `data/oracle/`.

## 1. Interaction & Decision Patterns
- **Autonomous Resolution**: Agents must "keep going" until the task is complete, minimizing back-and-forth with the user.
- **Plan-then-Act**: For complex tasks, a discovery pass (Grep/Read) is followed by a structured plan (Todo/Backlog) before execution.
- **Intent-Driven Response**: Understanding the "why" behind garbled or incomplete inputs, especially in live environments.
- **Headline-First Communication**: Providing direct answers first, followed by supporting bullet points for clarity and skimmability.

## 2. Tool & Execution Patterns
- **Maximum Parallelism**: Batching independent tool calls (e.g., reading 5 files, searching 3 patterns) in a single turn to save time/tokens.
- **Tool-Based Verification**: Using tools (Grep, Pytest, Healthchecks) to confirm results rather than assuming success.
- **Defensive Security**: Refusing tasks that involve credential discovery, bulk harvesting, or malicious code modification.
- **SVG over Binary**: For visual asset generation, preferring SVG for scalability and editability.

## 3. Reasoning Scaffolds
- **The Discovery Pass**: Broad keyword searches followed by targeted file reads.
- **The Integrity Loop**: Each modification is followed by a build/test run; failures are fixed before completion.
- **The SOP Alignment**: Following a specific "Mandatory Procedure" for recurring business/technical tasks (e.g., `MKT_001`, `MON_002`).

## 4. Safety & Governance
- **Role Isolation**: Agents operate within Meta-Departments (Engineering, Revenue, Marketing) with specific tool access.
- **Lineage Registry**: All significant actions and artifacts are logged to a central integrity registry.
- **Sandbox Enforcement**: Untested code is run in isolated environments (Docker/Staging) before production deployment.
