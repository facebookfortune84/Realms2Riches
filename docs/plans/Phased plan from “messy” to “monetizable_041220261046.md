Phased plan from “messy” to “monetizable”
Phase 0 – Lock the vision & PRD (use Taskmaster + Workshop)
Goal: One clear PRD that all tools/agents use as the “source of truth”.

Concrete steps:

Taskmaster PRD prompt:

“You are the Product Manager for Realms2Riches. Create a concise PRD for ‘Realms2Riches Company-in-a-Box Swarm v1’. Include: problem, target user, core features (API, repo maintenance swarm, content/outreach automation), non-goals, success metrics, and constraints (Windows Server 2025 + IIS, subdomains, WSL2 dev, existing Python backend + frontend).”

Save that PRD into your repo, e.g.:

docs/product/PRD-company-in-a-box-v1.md

Also copy into Taskmaster’s PRD location.

This becomes the north star for every agent.

Phase 1 – Map the repo & existing capabilities (Cursor + Gemini CLI + Plandex)
Goal: Turn “I don’t know what’s where” into a machine-readable map.

Artifacts to produce:

docs/architecture/api_endpoints.md

docs/architecture/services_and_subdomains.md

docs/architecture/feature_map.md

Tool usage:

Cursor agent prompt (inside repo):

“Scan this repo and produce:

A list of all API endpoints (path, method, handler file, purpose).

A list of services (backend, frontend, workers, scripts) and how they interact.

A feature map: which files implement which business features.
Output as markdown files under docs/architecture/.”

Google Gemini CLI prompt (from project root):

“You are a codebase cartographer. Based on this repo, generate a high-level architecture overview for Realms2Riches, including: API, frontend, background jobs, scripts, and any infra hints (Docker, IIS, WSL2). Focus on what exists, not what should exist.”

Plandex prompt (once installed):

“Create a project plan to fully map the Realms2Riches repo. Tasks:

Enumerate API endpoints and their usage.

Identify all config files (.env, pyproject.toml, poetry.lock, package.json, docker files).

Detect test coverage and missing tests.

Output a task list with dependencies and estimated effort.
Use the existing docs folder if present.”

Phase 2 – Architecture & hosting plan (IIS + subdomains + WSL2 dev)
Goal: Decide where everything lives and how it’s hosted.

Target subdomains:

api.realms2riches.com → backend API (FastAPI or similar)

blog.realms2riches.com → blog (static or CMS)

tools.realms2riches.com → internal tools / dashboards

newsletter.realms2riches.com → email capture / campaigns

email.realms2riches.com → provider config (IONOS, etc.)

Tasks:

Define deployment targets in a doc:

docs/deployment/windows_server_2025_iis.md

Decide dev vs prod:

Dev: WSL2 + Ubuntu + Docker/Poetry

Prod: Windows Server 2025 + IIS + reverse proxy to backend services

WSL2/Ubuntu alignment (high level):

In Ubuntu (WSL2):

bash
# From /mnt/c/Realms2Riches
python3.11 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
cd frontend && npm install
Make sure env files are consistent:

.env for backend

.env.local or similar for frontend

Document in docs/env/environment_layout.md

Phase 3 – Swarm design: features, tools, agents, roles, teams
Goal: Turn your mental swarm into explicit manifests.

Create a swarm/ folder with:

swarm/features.yaml

swarm/tools.yaml

swarm/agents.yaml

swarm/roles.yaml

swarm/teams.yaml

swarm/skills.yaml

Example structure (YAML-ish):

yaml
# swarm/features.yaml
- id: repo_hygiene
  name: Repo Hygiene & Health
  outcomes:
    - Clean, linted, passing tests
    - No dead configs or unused files

- id: content_outreach
  name: Content & Outreach Automation
  outcomes:
    - Weekly blog post
    - Cross-post to LinkedIn & Facebook
yaml
# swarm/agents.yaml
- id: repo_guardian
  role: code_maintainer
  skills: [linting, testing, dependency_audit]
  tools: [cursor_agent, plandex, taskmaster]

- id: content_scribe
  role: content_creator
  skills: [blog_writing, social_snippets]
  tools: [gemini_cli, workshop]
Use Plandex to help generate these:

“You are designing an AI swarm for Realms2Riches. Based on the PRD and architecture docs, generate manifests for features, tools, agents, roles, teams, and skills in YAML. Each agent should map to concrete tasks (repo hygiene, tests, deployment, content, outreach).”

Phase 4 – Tests, harness, and CI/CD
Goal: Every feature has tests; every change runs through a pipeline.

Artifacts:

tests/ expanded

docs/testing/test_matrix.md

CI config: .github/workflows/ci.yml or similar

Prompts:

Cursor / Workshop prompt:

“For each API endpoint documented in docs/architecture/api_endpoints.md, generate:

Unit tests for core logic

Integration tests hitting the endpoint

A short description of expected behavior.
Place tests under tests/ following existing patterns.”

Plandex prompt:

“Create a CI/CD plan for Realms2Riches including: linting, tests, build, and deploy to Windows Server 2025 + IIS. Output as a task graph with dependencies and a suggested GitHub Actions workflow.”

Phase 5 – Deployment, lockdown, and monetization
Goal: Running in prod, versioned, and ready to sell.

Tasks:

Configure IIS sites for each subdomain and reverse proxy to:

Backend API (Python app via wfastcgi or reverse proxy to a service on WSL2/Docker)

Frontend (static build)

Tag a launch version in git:

v1.0.0-company-in-a-box

Lock down:

Branch protection

Release notes

SOPs in docs/sops/

Then:

Define offers that match swarm capabilities:

“Repo Hygiene & CI Setup Package”

“Company-in-a-Box Swarm Setup”

“Content & Outreach Automation Setup”

4️⃣ System prompts & custom instructions for your tools
Here are short, reusable system prompts you can adapt.

Workshop (system prompt)
“You are the Lead Engineer for the Realms2Riches project.

Always respect the PRD in docs/product/PRD-company-in-a-box-v1.md.

Prefer incremental, reversible changes.

Keep repo structure clean and deterministic.

When unsure, propose options and ask for clarification instead of guessing.

Always update or create documentation when you add or change behavior.”

Taskmaster (system / PRD alignment)
“You are the Project Orchestrator for Realms2Riches.

Break work into small, trackable tasks.

Always link tasks to features in swarm/features.yaml.

Maintain a clear ‘Now / Next / Later’ roadmap.

Ensure every task has a definition of done and, where relevant, tests.”

Plandex (project-level prompt)
“You are a planning agent for Realms2Riches.

Read the PRD, architecture docs, and swarm manifests.

Generate task graphs that move the project toward launch.

Prefer sequences that reduce risk early (tests, infra, env alignment).

Output tasks with dependencies and suggested tool/agent to execute each.”

Google Gemini CLI (code understanding / refactor)
“You are a senior engineer reviewing the Realms2Riches codebase.

Explain what this module does in plain language.

Identify risks, missing tests, and unclear boundaries.

Suggest refactors that improve clarity without changing behavior.”

Cursor agents (inside repo)
“You are a repo-native coding agent for Realms2Riches.

Never introduce new tech stacks without justification.

Follow existing patterns for tests, config, and logging.

When editing files, keep changes minimal and well-commented.

After changes, update or create docs under docs/.”

5️⃣ High-level setup notes (WSL2, Workshop, Plandex, Gemini CLI)
Very briefly, the order I’d use:

WSL2 + Ubuntu

Ensure WSL2 enabled, Ubuntu installed.

From Ubuntu, work in /mnt/c/Realms2Riches.

Align Python (3.11), Poetry, Node, and env files as noted above.

Workshop + Taskmaster

Install Workshop CLI.

Point it at your repo.

Configure local models (or API keys) and set the system prompt.

Add your PRD into its expected PRD location.

Plandex

Install via their instructions.

Run from project root.

First tasks: repo mapping, test coverage, CI/CD plan.

Google Gemini CLI

Configure API key.

Use it for deep code explanations and architecture docs.

Cursor

Open the repo.

Configure agents with the prompts above.

Use it for concrete refactors and test generation.

6️⃣ What I’d like to clarify before we “set in stone”
To make this truly “set in stone” and not just another big plan, I’d want to lock in:

Primary v1 offer:  
Is “Company-in-a-Box Swarm Setup” the first thing you want to sell, or “Repo Hygiene & CI Setup” as a smaller entry offer?

Backend tech:  
Are we definitely standardizing on FastAPI (or similar) for the API, or is there another framework in play?

If you answer those two, I can tighten this into a concrete, step-by-step execution roadmap (with rough ordering and milestones) that you—and your agents—can follow day by day.