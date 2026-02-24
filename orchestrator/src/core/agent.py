from typing import List, Dict, Any, Optional
import json
import hashlib
import time
import random
from datetime import datetime
from orchestrator.src.validation.schemas import AgentConfig, TaskSpec, ToolInvocation
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.core.llm_provider import BaseLLMProvider
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.logging.telemetry import telemetry
from orchestrator.src.agents.persona_library import PERSONA_LIBRARY
from orchestrator.src.core.workforce import workforce
from orchestrator.src.core.lineage import lineage_registry

logger = get_logger(__name__)

class Agent:
    def __init__(self, config: AgentConfig, tools: List[BaseTool], memory: VectorStore, llm_provider: BaseLLMProvider):
        self.config = config
        self.tools = {t.config.tool_id: t for t in tools}
        self.memory = memory
        self.llm_provider = llm_provider
        self.active_persona = None
        
        # Self-Naming & Dossier
        self.agent_name = self._dream_name()
        self.dossier = workforce.onboard_agent(self.config.id, "BASE")

    def _dream_name(self) -> str:
        prefixes = ["Aether", "Cyber", "Sovereign", "Nexus", "Titan", "Zenith", "Omega", "Alpha"]
        suffixes = ["Prime", "Unit", "Architect", "Shield", "Core", "Node", "Vanguard", "Force"]
        return f"{random.choice(prefixes)}-{random.choice(suffixes)}-{random.randint(100, 999)}"

    def adopt_persona(self, persona_id: str):
        if persona_id in PERSONA_LIBRARY:
            self.active_persona = PERSONA_LIBRARY[persona_id]
            self.dossier.persona_type = persona_id

    def process_task(self, task: TaskSpec) -> Dict[str, Any]:
        start_time = time.time()
        trace_id = hashlib.sha256(f"{task.id}{time.time()}".encode()).hexdigest()[:12]
        span = telemetry.start_span("process_task", self.config.id, trace_id)
        
        effective_system_prompt = self.config.system_prompt
        if self.active_persona:
            effective_system_prompt = f"IDENTITY: {self.active_persona['title']}\n{self.active_persona['mandates']}\n\n# BASE IDENTITY:\n{self.config.system_prompt}"

        try:
            context_docs = self.memory.search(task.description, limit=5)
            context_text = "\n".join([f"- {doc['text']}" for doc in context_docs])
            
            plan = self._formulate_plan(task.description, context_text, effective_system_prompt)
            
            results = []
            artifacts = []
            for step in plan.get("steps", []):
                tool_id = step.get("tool_id")
                if tool_id in self.tools:
                    res = self.tools[tool_id].run(ToolInvocation(
                        tool_id=tool_id, agent_id=self.config.id, input_data=step.get("inputs", {})
                    ))
                    res_dict = res.model_dump(mode="json")
                    results.append(res_dict)
                    # Track physical artifacts (file paths, IDs)
                    if "path" in res_dict.get("output_data", {}):
                        artifacts.append(res_dict["output_data"]["path"])

            # Record Work & Cost
            duration_ms = int((time.time() - start_time) * 1000)
            self.dossier.record_work(duration_ms)
            
            # --- LINEAGE SIGNATURE ---
            lineage_id = lineage_registry.record_contribution(
                agent_id=self.config.id,
                tax_id=self.dossier.tax_id,
                action=task.description,
                artifacts=artifacts,
                cost=self.dossier.accrued_cost
            )
            
            telemetry.end_span(span, status="SUCCESS", metadata={"lineage_id": lineage_id})
            
            return {
                "status": "completed", 
                "agent_name": self.agent_name,
                "tax_id": self.dossier.tax_id,
                "lineage_fingerprint": lineage_id,
                "results": results
            }
            
        except Exception as e:
            telemetry.end_span(span, status="ERROR")
            return {"status": "failed", "error": str(e)}

    def _formulate_plan(self, prompt: str, context: str, system_prompt: str) -> Dict[str, Any]:
        identity_header = f"You are {self.agent_name}. Your Tax ID is {self.dossier.tax_id}."
        full_prompt = f"{identity_header}\n{system_prompt}\n\nCONTEXT:\n{context}"
        response = self.llm_provider.generate_response([{"role": "system", "content": full_prompt}, {"role": "user", "content": prompt}])
        try:
            start, end = response.find('{'), response.rfind('}')
            return json.loads(response[start:end+1])
        except: return {"reasoning": "Fallback.", "steps": []}
