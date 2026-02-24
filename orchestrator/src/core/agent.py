from typing import List, Dict, Any, Optional
import json
import hashlib
import time
from datetime import datetime
from orchestrator.src.validation.schemas import AgentConfig, TaskSpec, ToolInvocation
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.core.llm_provider import BaseLLMProvider
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.logging.telemetry import telemetry
from orchestrator.src.agents.persona_library import PERSONA_LIBRARY

logger = get_logger(__name__)

class Agent:
    def __init__(self, config: AgentConfig, tools: List[BaseTool], memory: VectorStore, llm_provider: BaseLLMProvider):
        self.config = config
        self.tools = {t.config.tool_id: t for t in tools}
        self.memory = memory
        self.llm_provider = llm_provider
        self.active_persona = None

    def adopt_persona(self, persona_id: str):
        """Switches the agent's internal DNA to match a library persona."""
        if persona_id in PERSONA_LIBRARY:
            self.active_persona = PERSONA_LIBRARY[persona_id]
            logger.info(f"Agent {self.config.id} has adopted persona: {persona_id}")
        else:
            logger.warning(f"Persona {persona_id} not found. Maintaining base logic.")

    def process_task(self, task: TaskSpec) -> Dict[str, Any]:
        trace_id = hashlib.sha256(f"{task.id}{time.time()}".encode()).hexdigest()[:12]
        span = telemetry.start_span("process_task", self.config.id, trace_id)
        
        # Merge Persona Mandates with Base Config
        effective_system_prompt = self.config.system_prompt
        if self.active_persona:
            effective_system_prompt = f"{self.active_persona['mandates']}\n\n# BASE IDENTITY:\n{self.config.system_prompt}"

        try:
            # 1. Retrieval
            context_docs = self.memory.search(task.description, limit=5)
            context_text = "\n".join([f"- {doc['text']}" for doc in context_docs])
            
            # 2. Planning (Passing effective_prompt)
            plan = self._formulate_plan(task.description, context_text, effective_system_prompt)
            
            # 3. Execution
            results = []
            for step in plan.get("steps", []):
                tool_id = step.get("tool_id")
                if tool_id in self.tools:
                    res = self.tools[tool_id].run(ToolInvocation(
                        tool_id=tool_id, agent_id=self.config.id, input_data=step.get("inputs", {})
                    ))
                    results.append(res.model_dump(mode="json"))
            
            telemetry.end_span(span, status="SUCCESS")
            return {"status": "completed", "results": results, "persona": self.active_persona["title"] if self.active_persona else "BASE"}
            
        except Exception as e:
            telemetry.end_span(span, status="ERROR")
            return {"status": "failed", "error": str(e)}

    def _formulate_plan(self, prompt: str, context: str, system_prompt: str) -> Dict[str, Any]:
        tools_list = "\n".join([f"- {t.config.tool_id}: {t.config.description}" for t in self.tools.values()])
        full_prompt = f"{system_prompt}\n\nTOOLS:\n{tools_list}\n\nCONTEXT:\n{context}"
        
        response = self.llm_provider.generate_response([
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": prompt}
        ])
        
        try:
            start = response.find('{')
            end = response.rfind('}')
            return json.loads(response[start:end+1])
        except:
            return {"reasoning": "Fallback to basic execution.", "steps": []}
