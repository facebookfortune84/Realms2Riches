from typing import List, Dict, Any
import json
import hashlib
import time
import random
import os
import re
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
        
        self.agent_name = self._dream_name()
        self.dossier = workforce.onboard_agent(self.config.id, "BASE")
        self._self_adopt_persona()

    def _dream_name(self) -> str:
        prefixes = ["Aether", "Cyber", "Sovereign", "Nexus", "Titan", "Zenith", "Omega", "Alpha"]
        suffixes = ["Prime", "Unit", "Architect", "Shield", "Core", "Node", "Vanguard", "Force"]
        return f"{random.choice(prefixes)}-{random.choice(suffixes)}-{random.randint(100, 999)}"

    def _self_adopt_persona(self):
        cid = self.config.id.lower()
        if "cybernetic" in cid: self.adopt_persona("BOLT_ENGINEER")
        elif "market" in cid: self.adopt_persona("PERPLEXITY_SEARCH")
        elif "integrity" in cid: self.adopt_persona("CLAUDE_CODE_2")
        elif "fallback" in cid: self.adopt_persona("ROO_MAINTAINER")
        elif "strategic" in cid: self.adopt_persona("GPT_5_MASTER")
        elif "visual" in cid: self.adopt_persona("DESIGN_ORCHESTRATOR")
        else:
            available = list(PERSONA_LIBRARY.keys())
            if available: self.adopt_persona(random.choice(available))

    def adopt_persona(self, persona_id: str):
        if persona_id in PERSONA_LIBRARY:
            self.active_persona = PERSONA_LIBRARY[persona_id]
            logger.info(f"{self.agent_name} adopted {persona_id}")
        else:
            oracle_path = f"data/oracle/prompts/{persona_id}.txt"
            if os.path.exists(oracle_path):
                with open(oracle_path, 'r', encoding='utf-8') as f:
                    self.active_persona = {"title": persona_id, "description": "Oracle DNA", "mandates": f.read()}
                logger.info(f"{self.agent_name} adopted Oracle: {persona_id}")
        if self.active_persona: self.dossier.persona_type = persona_id

    def process_task(self, task: TaskSpec) -> Dict[str, Any]:
        start_time = time.time()
        trace_id = hashlib.sha256(f"{task.id}{time.time()}".encode()).hexdigest()[:12]
        span = telemetry.start_span("process_task", self.config.id, trace_id)
        
        effective_system_prompt = self.config.system_prompt
        if self.active_persona:
            effective_system_prompt = f"IDENTITY: {self.active_persona['title']}\n{self.active_persona['mandates']}\n\n# BASE IDENTITY:\n{self.config.system_prompt}"

        try:
            # 1. SOP RETRIEVAL
            sop_docs = self.memory.search(f"SOP for {task.description}", limit=1)
            active_sop = ""
            sop_name = "GENERIC_TASK"
            if sop_docs and "SOP:" in sop_docs[0]['text']:
                active_sop = f"\n### ACTIVE OPERATING PROCEDURE:\n{sop_docs[0]['text']}\n"
                sop_name = sop_docs[0]['metadata'].get('filename', 'UNKNOWN')
                logger.info(f"Agent {self.agent_name} retrieved SOP: {sop_name}")

            span_meta = {"sop_used": sop_name, "project_id": task.project_id}
            context_docs = self.memory.search(task.description, limit=5)
            context_text = "\n".join([f"- {doc['text']}" for doc in context_docs if "SOP:" not in doc['text']])
            
            # 2. PLAN FORMULATION
            plan = self._formulate_plan(task.description, context_text, f"{effective_system_prompt}\n{active_sop}")
            steps = plan.get("steps", [])
            
            if not steps:
                if "lander" in task.description.lower() or "verify" in task.description.lower():
                    steps = [{"tool_id": "sales_funnel", "inputs": {"product_name": "Jarvis 3.5"}}, {"tool_id": "ui_tester", "inputs": {"url": "projects/generated/landers/jarvis_3.5_lander.html"}}]

            # 3. EXECUTION
            results, artifacts = [], []
            for step in steps:
                tool_id = step.get("tool_id")
                if tool_id in self.tools:
                    logger.info(f"Agent {self.agent_name} executing tool: {tool_id}")
                    res = self.tools[tool_id].run(ToolInvocation(tool_id=tool_id, agent_id=self.config.id, input_data=step.get("inputs", {})))
                    res_dict = res.model_dump(mode="json")
                    results.append(res_dict)
                    out_data = res_dict.get("output_data")
                    if out_data and isinstance(out_data, dict) and "artifact" in out_data: artifacts.append(out_data["artifact"])

            duration_ms = int((time.time() - start_time) * 1000)
            self.dossier.record_work(duration_ms)
            lineage_id = lineage_registry.record_contribution(agent_id=self.config.id, tax_id=self.dossier.tax_id, action=task.description, artifacts=artifacts, cost=self.dossier.accrued_cost)
            
            span_meta.update({"lineage_id": lineage_id, "wage": self.dossier.accrued_cost, "tool_count": len(results)})
            telemetry.end_span(span, status="SUCCESS", metadata=span_meta)
            
            return {"status": "completed", "agent_name": self.agent_name, "tax_id": self.dossier.tax_id, "persona": self.active_persona["title"] if self.active_persona else "BASE", "reasoning": plan.get("reasoning", "Success."), "wage_accrued": round(self.dossier.accrued_cost, 4), "results": results}
        except Exception as e:
            logger.error(f"Agent {self.agent_name} failed: {e}")
            telemetry.end_span(span, status="ERROR", metadata={"error": str(e)})
            return {"status": "failed", "error": str(e)}

    def _formulate_plan(self, prompt: str, context: str, system_prompt: str) -> Dict[str, Any]:
        full_prompt = f"IDENTITY: {self.agent_name}\n{system_prompt}\n\nCONTEXT:\n{context}"
        response = self.llm_provider.generate_response([{"role": "system", "content": full_prompt}, {"role": "user", "content": prompt}])
        try: return json.loads(response.strip())
        except:
            match = re.search(r'(\{.*\})', response, re.DOTALL)
            if match:
                try: return json.loads(match.group(1))
                except: pass
        return {"reasoning": "Heuristic fallback.", "steps": []}
