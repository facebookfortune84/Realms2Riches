import asyncio
import argparse
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from orchestrator.src.agents.builder_agent import BuilderAgent
from orchestrator.src.core.database import AsyncSessionLocal
from orchestrator.src.core.models import Project
from orchestrator.src.logging.logger import get_logger

logger = get_logger("FAMOUS_MODE")

async def run_builder(prompt: str):
    logger.info("🎨 Starting Famous Mode Builder...")
    
    # Ensure tables exist
    from orchestrator.src.core.database import init_db
    await init_db()
    
    agent = BuilderAgent()
    
    # 1. Analyze
    project_spec = await agent.analyze_prompt(prompt)
    logger.info(f"✨ Spec Generated: {project_spec['name']}")
    
    # 2. Persist
    async with AsyncSessionLocal() as session:
        new_project = Project(
            name=project_spec["name"],
            slug=project_spec["slug"],
            description=project_spec["description"],
            tech_stack=project_spec["tech_stack"]
        )
        session.add(new_project)
        await session.commit()
        await session.refresh(new_project)
        
        # 3. Generate
        try:
            path = await agent.generate_project(new_project)
            new_project.status = "generated"
            new_project.local_path = path
            await session.commit()
            
            print("\n" + "="*50)
            print(f"🚀 APP GENERATED SUCCESSFULLY")
            print("="*50)
            print(f"Name: {new_project.name}")
            print(f"Path: {path}")
            print(f"Stack: {new_project.tech_stack}")
            print("\nTo launch:")
            print(f"  cd {path}")
            print(f"  docker-compose up --build")
            print("="*50 + "\n")
            
        except Exception as e:
            logger.error(f"Build failed: {e}")
            new_project.status = "failed"
            await session.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Realms2Riches Autonomous Builder (Famous.ai Mode)")
    parser.add_argument("prompt", nargs="?", help="Describe the app you want to build", default="A simple landing page for my startup")
    
    args = parser.parse_args()
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/famous_mode.py \"Describe your app here\"")
        # Default prompt will run if nothing provided, but explicit is better for CLI help
    
    asyncio.run(run_builder(args.prompt))
