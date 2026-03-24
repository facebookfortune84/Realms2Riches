import os
import json
import shutil
import uuid
import zipfile
from datetime import datetime
from typing import List, Dict, Any
from orchestrator.src.validation.schemas import AgentConfig, TaskSpec, ToolInvocation
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.core.llm_provider import BaseLLMProvider
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.logging.telemetry import telemetry
from orchestrator.src.agents.persona_library import PERSONA_LIBRARY
from orchestrator.src.core.workforce import workforce
from orchestrator.src.core.lineage import lineage_registry
from orchestrator.src.core.config import settings # Assuming settings is configured to load .env.prod

logger = get_logger("GENESIS_FORGE")

class GenesisForge:
    """
    Industrial-grade swarm provisioner.
    Creates fully functional, autonomous swarm packages.
    """
    
    # CORE_FILES list will be populated dynamically based on a scan or explicit configuration
    # For now, assuming a base set from previous context.
    CORE_FILES_TEMPLATE = [
        "orchestrator",
        "agents",
        "scripts",
        "data/oracle",
        "SOVEREIGN_START.ps1",
        "requirements.txt",
        "pyproject.toml",
        "package.json",
        ".env.example",
        "Makefile"
    ]

    def __init__(self, output_dir: str = "data/generated/swarms"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_swarm(self, config: Dict[str, Any]) -> str:
        """
        Generates a complete swarm zip package.
        config: {
            "name": str,
            "industry": str,
            "agent_count": int,
            "roles": List[str], # Persona IDs
            "tools": List[str]  # Tool IDs
        }
        """
        swarm_id = f"swarm_{uuid.uuid4().hex[:8]}"
        target_path = os.path.join(self.output_dir, swarm_id)
        os.makedirs(target_path, exist_ok=True)

        logger.info(f"🚀 Generating Industrial Swarm: {config['name']} ({swarm_id}) for industry {config['industry']}")

        # 1. Copy Core Operating Files
        # Use absolute paths to ensure correct copying from the project root
        project_root = os.getcwd() # Assuming the script is run from the project root
        
        core_file_paths = []
        for item in self.CORE_FILES_TEMPLATE:
            src_path = os.path.abspath(os.path.join(project_root, item))
            core_file_paths.append(src_path)
            dst_path = os.path.join(target_path, item)
            
            if not os.path.exists(src_path):
                logger.warning(f"Source file/dir missing for swarm: {src_path}")
                continue

            try:
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '.git', 'node_modules', 'venv', '.pytest_cache', '*.pyc', '*.swp', '*.DS_Store'))
                else:
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
            except Exception as e:
                logger.error(f"Failed to copy {src_path} to {dst_path}: {e}")

        # 2. Generate Swarm Manifest (incorporating user selections)
        manifest = {
            "swarm_id": swarm_id,
            "name": config.get("name", "Unnamed Swarm"),
            "industry": config.get("industry", "generic"),
            "created_at": datetime.utcnow().isoformat(),
            "configuration": {
                "total_units": config.get("agent_count", 100),
                "specializations": config.get("roles", ["general_assistant"]),
                "active_toolsets": config.get("tools", ["Vector Memory"])
            },
            "status": "SOVEREIGN_PROVISIONED"
        }
        with open(os.path.join(target_path, "swarm_manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)
        logger.info("Swarm manifest generated.")

        # 3. Generate Custom README.md
        readme_content = self._generate_readme(config, swarm_id)
        with open(os.path.join(target_path, "README.md"), "w") as f:
            f.write(readme_content)
        logger.info("Custom README generated.")

        # 4. Create specialized .env.local for the user
        # Ensure this uses settings from .env.prod for production context where possible,
        # but allows user overrides for local setup.
        env_content = f"""# {config.get('name', 'Swarm')} - Sovereign Configuration
# Generated on {datetime.utcnow().isoformat()}

# --- CORE INFRASTRUCTURE ---
# Use localhost for local development. These will be overridden by docker-compose in prod.
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000 # Assuming frontend runs on a different port locally
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://{settings.db_config.user}:{settings.db_config.password}@{settings.db_config.host}:{settings.db_config.port}/{settings.db_config.db}

# --- AI MODELS ---
# User must provide their own keys for generation
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
# FAST_LLM_MODEL={settings.fast_llm_model} # Use defaults from project or specify
# SMART_LLM_MODEL={settings.smart_llm_model} # Use defaults from project or specify

# --- MONETIZATION ---
STRIPE_API_KEY=sk_test_your_stripe_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_test_webhook_secret

# --- AFFILIATE LINKS ---
# Add your personal affiliate links here for tracking commissions
AFFILIATE_LINK_1_NAME="Example High-Ticket Offer"
AFFILIATE_LINK_1_URL="https://example.com/affiliate/your_id"
AFFILIATE_LINK_2_NAME="Another Offer"
AFFILIATE_LINK_2_URL="https://example.com/affiliate/your_id_2"

# --- COMPANY SPECIFIC ---
COMPANY_NAME={config.get('name', 'Unnamed Company')}
INDUSTRY_SECTOR={config.get('industry', 'generic')}
"""
        with open(os.path.join(target_path, ".env.local"), "w") as f:
            f.write(env_content)
        logger.info("User .env.local generated.")

        # 5. Zip the Package
        zip_filename = f"{config['name'].lower().replace(' ', '_')}_{swarm_id}.zip"
        zip_path = os.path.join(self.output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(target_path):
                # Skip excluded directories
                if 'node_modules' in dirs: dirs.remove('node_modules')
                if '__pycache__' in dirs: dirs.remove('__pycache__')
                if '.git' in dirs: dirs.remove('.git')
                if 'venv' in dirs: dirs.remove('venv')
                
                for file in files:
                    file_abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_abs_path, target_path)
                    zipf.write(file_abs_path, rel_path)
        
        logger.info(f"Package zipped to {zip_path}")

        # 6. Cleanup temp directory
        shutil.rmtree(target_path)

        logger.info(f"✅ Swarm Compilation Complete: {zip_filename}")
        return f"/swarms/{zip_filename}" # Return URL path for download

    def _generate_readme(self, config: Dict[str, Any], swarm_id: str) -> str:
        roles_list = "
".join([f"- {role.label} ({role.id})" for role in AGENT_ROLES_DATA if role.id in config["roles"]])
        tools_list = "
".join([f"- {tool}" for tool in config["tools"]])
        
        return f"""# 🦅 {config['name']} - Sovereign AI Swarm

Welcome to your Industrial-Grade Autonomous Swarm. This package was generated by the **Realms2Riches Genesis Forge** and is configured for the **{config['industry']}** sector.

## Swarm Profile
- **ID:** {swarm_id}
- **Density:** {config.get('agent_count', 100)} Specialized Units
- **Domains:** {config['industry']}

## Included Agent Personas
{roles_list}

## Active Toolsets
{tools_list}

## Quick Start (Out of the Box)

### 1. Prerequisites
Ensure you have the following installed:
- Python 3.11+
- Node.js & npm (for any frontend assets if applicable)
- Docker Desktop (for Postgres/Redis if running locally)

### 2. Configuration
Open the `.env.local` file in this directory and provide your necessary API keys:
- **Groq API Key:** [Get here](https://console.groq.com/)
- **OpenAI API Key:** [Get here](https://platform.openai.com/api-keys)
- **Stripe API Key:** [Get here](https://dashboard.stripe.com/)
- **Other Keys:** Refer to the README in the `docs/oracle/` directory for details on other potential API requirements.

### 3. Launch Sequence
Navigate to the root directory of this swarm package and execute the primary launch script:
```powershell
.\SOVEREIGN_START.ps1
```
*Ensure Docker is running and the `POSTGRES_URL`, `REDIS_URL`, and other variables in `.env.local` are correctly set.*

### 4. Verification
Once the system is live, navigate to `http://localhost:8000/health` to confirm the swarm is SOVEREIGN and operational. Check logs for confirmation of agent initialization and tool access.

---
*Generated by Realms2Riches Industrial Matrix*
*Hash: {uuid.uuid4().hex[:16]}*
"""

genesis_forge = GenesisForge()
