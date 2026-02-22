from typing import Dict, List, Any, Optional
import asyncio
import os
import random
from orchestrator.src.core.agent import Agent
from orchestrator.src.core.llm_provider import GroqProvider
from orchestrator.src.core.config import settings
from orchestrator.src.validation.schemas import TaskSpec, AgentConfig, ToolConfig
from orchestrator.src.tools.git_tools import GitTool
from orchestrator.src.tools.file_tools import FileTool
from orchestrator.src.tools.social_tools import FacebookPostTool, LinkedInPostTool, SocialMediaMultiplexer
from orchestrator.src.tools.web_tools import WebSearchTool, WebScraperTool
from orchestrator.src.tools.project_tools import ProjectGeneratorTool
from orchestrator.src.tools.content_sharder import ContentSharderTool
from orchestrator.src.tools.media_tools import ImageGenerationTool, VideoGenerationTool
from orchestrator.src.tools.revenue_tools import PaymentTool
from orchestrator.src.tools.seo_tools import SEOTool
from orchestrator.src.tools.universal_tools import get_multiplexer_tool
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.memory.sql_store import SQLStore
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.agents.fleet import generate_grand_fleet

# Voice Adapters
from orchestrator.src.core.voice.interfaces import STTAdapter, TTSAdapter
from orchestrator.src.core.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from orchestrator.src.core.voice.real_adapters import OpenAIWhisperAdapter, ElevenLabsAdapter

logger = get_logger(__name__)

class SovereignCell:
    def __init__(self, cell_id: str, agents: List[Agent]):
        self.cell_id = cell_id
        self.agent_pool = agents
        self.active_tasks = 0
        self.task_queue = asyncio.Queue()

    async def execute(self, task: TaskSpec):
        self.active_tasks += 1
        await self.task_queue.put(task)
        
        # Select an available agent (simple random load balancing for now)
        agent = random.choice(self.agent_pool) 
        
        try:
            # Run CPU-bound agent logic in a separate thread to avoid blocking the asyncio loop
            # This allows the 'Social Scheduler' and 'Autonomous Loop' to keep ticking 
            # while this agent 'thinks'.
            result = await asyncio.to_thread(agent.process_task, task)
            return result
        finally:
            self.active_tasks -= 1
            await self.task_queue.get()

class Orchestrator:
    def __init__(self):
        self.memory = VectorStore()
        self.sql_store = SQLStore()
        self.llm_provider = GroqProvider()
        self.cells: Dict[str, SovereignCell] = {}
        
        if settings.ELEVENLABS_API_KEY and len(settings.ELEVENLABS_API_KEY) > 10:
            self.tts = ElevenLabsAdapter(settings.ELEVENLABS_API_KEY)
        else: self.tts = MockTTSAdapter()
            
        if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 10:
            self.stt = OpenAIWhisperAdapter(settings.OPENAI_API_KEY)
        else: self.stt = MockSTTAdapter()

        self._initialize_sovereign_matrix()

    def _initialize_sovereign_matrix(self):
        # 1. Load Tools
        all_tools = [
            GitTool(ToolConfig(tool_id="git", name="Git", description="Git ops", parameters_schema={}, allowed_agents=["*"])),
            FileTool(ToolConfig(tool_id="file", name="File", description="File system access", parameters_schema={}, allowed_agents=["*"])),
            FacebookPostTool(ToolConfig(tool_id="facebook_post", name="Facebook Poster", description="Post content to Facebook Page", parameters_schema={"message": "string", "link": "string"}, allowed_agents=["*"])),
            LinkedInPostTool(ToolConfig(tool_id="linkedin_post", name="LinkedIn Poster", description="Post content to LinkedIn Profile/Page", parameters_schema={"message": "string", "link": "string"}, allowed_agents=["*"])),
            SocialMediaMultiplexer(ToolConfig(tool_id="social_multiplexer", name="Social Media Multiplexer", description="Post to all channels simultaneously", parameters_schema={"message": "string", "link": "string"}, allowed_agents=["*"])),
            WebSearchTool(ToolConfig(tool_id="search", name="Search", description="Search web", parameters_schema={}, allowed_agents=["*"])),
            WebScraperTool(ToolConfig(tool_id="scrape", name="Scrape", description="Scrape web", parameters_schema={"url": "string"}, allowed_agents=["*"])),
            ProjectGeneratorTool(ToolConfig(tool_id="scaffold", name="Scaffold", description="Build companies", parameters_schema={"name": "string", "industry": "string"}, allowed_agents=["*"])),
            ContentSharderTool(ToolConfig(tool_id="shard", name="Shard", description="Fragment content", parameters_schema={"text": "string"}, allowed_agents=["*"])),
            ImageGenerationTool(ToolConfig(tool_id="image_gen", name="ImageGen", description="Generate images", parameters_schema={"prompt": "string"}, allowed_agents=["*"]), stability_key=settings.STABILITY_API_KEY),
            VideoGenerationTool(ToolConfig(tool_id="video", name="Video", description="Video logic", parameters_schema={}, allowed_agents=["*"])),
            PaymentTool(ToolConfig(tool_id="payments", name="Payments", description="Manage fiscal transmissions", parameters_schema={}, allowed_agents=["*"]), stripe_key=settings.STRIPE_API_KEY),
            SEOTool(ToolConfig(tool_id="seo", name="SEO_Master", description="Optimize content for organic reach", parameters_schema={}, allowed_agents=["*"])),
            get_multiplexer_tool()
        ]

        fleet = generate_grand_fleet()
        
        # 2. Case-Insensitive Cell Partitioning
        # ids in fleet are e.g. agent_cybernetic_engineering_1 (all lowercase)
        self.cells["ALPHA"] = SovereignCell("ALPHA_CORE", [
            Agent(c, all_tools, self.memory, self.llm_provider) 
            for c in fleet if any(k in c.id.lower() for k in ["engineering", "cybernetic"])
        ])
        self.cells["BETA"] = SovereignCell("BETA_GROWTH", [
            Agent(c, all_tools, self.memory, self.llm_provider) 
            for c in fleet if any(k in c.id.lower() for k in ["market", "force"])
        ])
        self.cells["GAMMA"] = SovereignCell("GAMMA_OPS", [
            Agent(c, all_tools, self.memory, self.llm_provider) 
            for c in fleet if any(k in c.id.lower() for k in ["strategic", "legal", "revenue", "integrity"])
        ])

        self.agents = {a.config.id: a for cell in self.cells.values() for a in cell.agent_pool}
        
        if not self.agents:
            logger.error("MATRIX INITIALIZATION FAILED: 0 Agents detected. Checking fleet generation...")
            # Fallback: take all agents if filter failed
            alpha_fallback = [Agent(c, all_tools, self.memory, self.llm_provider) for c in fleet[:333]]
            beta_fallback = [Agent(c, all_tools, self.memory, self.llm_provider) for c in fleet[333:666]]
            gamma_fallback = [Agent(c, all_tools, self.memory, self.llm_provider) for c in fleet[666:]]
            self.cells["ALPHA"] = SovereignCell("ALPHA_CORE", alpha_fallback)
            self.cells["BETA"] = SovereignCell("BETA_GROWTH", beta_fallback)
            self.cells["GAMMA"] = SovereignCell("GAMMA_OPS", gamma_fallback)
            self.agents = {a.config.id: a for cell in self.cells.values() for a in cell.agent_pool}

        logger.info(f"PLATINUM SOVEREIGN MATRIX ONLINE: {len(self.agents)} Agents across 3 Specialized Cells.")

    async def submit_task_stream(self, task_description: str, project_id: str):
        task = TaskSpec(project_id=project_id, description=task_description)
        desc = task_description.lower()
        
        if any(k in desc for k in ["build", "code", "fix", "logic", "infrastructure"]): cell_key = "ALPHA"
        elif any(k in desc for k in ["post", "market", "shard", "outreach", "seo"]): cell_key = "BETA"
        else: cell_key = "GAMMA"

        yield {"status": "routing", "message": f"Diverting directive to CELL_{cell_key}..."}
        
        try:
            result = await self.cells[cell_key].execute(task)
            yield {"status": "completed", "result": result}
        except Exception as e:
            logger.error(f"Cell Execution Failed: {e}")
            yield {"status": "failed", "message": str(e)}

    def get_matrix_status(self):
        return {name: {"active": c.active_tasks, "queued": c.task_queue.qsize(), "units": len(c.agent_pool)} for name, c in self.cells.items()}
