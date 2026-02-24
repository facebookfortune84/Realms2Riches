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

logger = get_logger(__name__)

class Agent:
    """
    Sovereign Intelligence Unit.
    Implements recursive RAG context and safe tool-invocation protocols.
    """
    def __init__(self, config: AgentConfig, tools: List[BaseTool], memory: VectorStore, llm_provider: BaseLLMProvider):
        self.config = config
        self.tools = {t.config.tool_id: t for t in tools}
        self.memory = memory
        self.llm_provider = llm_provider
        self.history: List[Dict[str, str]] = []

    def process_task(self, task: TaskSpec) -> Dict[str, Any]:
        # FIXED: Ensure task.id is used for traceability
        trace_id = hashlib.sha256(f"{task.id}{time.time()}".encode()).hexdigest()[:12]
        span = telemetry.start_span("process_task", self.config.id, trace_id)
        
        logger.info(f"Agent {self.config.name} initiated trace {trace_id}")
        
        try:
            # 1. RAG Context Injection
            context_docs = self.memory.search(task.description, limit=5)
            context_text = "\n".join([f"- {doc['text']}" for doc in context_docs])
            
            # 2. Planning Phase
            plan = self._formulate_plan(task.description, context_text)
            
            # 3. Execution Phase
            results = []
            for step in plan.get("steps", []):
                tool_id = step.get("tool_id")
                if tool_id in self.tools:
                    tool_span = telemetry.start_span(f"tool_exec_{tool_id}", self.config.id, trace_id)
                    
                    invocation = ToolInvocation(
                        tool_id=tool_id,
                        agent_id=self.config.id,
                        input_data=step.get("inputs", {})
                    )
                    
                    result = self.tools[tool_id].run(invocation)
                    
                    # Cryptographic Signature
                    result.integrity_hash = hashlib.sha256(result.model_dump_json().encode()).hexdigest()
                    results.append(result.model_dump(mode="json"))
                    
                    telemetry.end_span(tool_span, status="SUCCESS")
                else:
                    logger.warning(f"UNAUTHORIZED TOOL CALL: {tool_id} rejected for {self.config.id}")

            # 4. Success Completion
            telemetry.end_span(span, status="SUCCESS", metadata={"steps_count": len(results)})
            
            # Recursive Learning
            self.memory.add(f"Task result for '{task.description}': {plan.get('reasoning')}", {"type": "recursive_memory"})

            return {
                "status": "completed", 
                "results": results, 
                "reasoning": plan.get("reasoning"),
                "agent_id": self.config.id,
                "trace_id": trace_id
            }
            
        except Exception as e:
            telemetry.end_span(span, status="ERROR", metadata={"error": str(e)})
            logger.error(f"Trace {trace_id} failed: {e}")
            return {"status": "failed", "error": str(e), "trace_id": trace_id}

    def _formulate_plan(self, prompt: str, context: str) -> Dict[str, Any]:
        tools_list = "\n".join([f"- {t.config.tool_id}: {t.config.description}" for t in self.tools.values()])
        
        system_prompt = f"""{self.config.system_prompt}
        TOOLS:
        {tools_list}
        
        OUTPUT SCHEMA (STRICT JSON):
        {{
          "reasoning": "thought process",
          "steps": [ {{ "tool_id": "id", "inputs": {{}} }} ]
        }}
        
        CONTEXT:
        {context}
        """
        
        response = self.llm_provider.generate_response([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        
        try:
            # Robust JSON extraction
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                return json.loads(response[start:end+1])
            return {"reasoning": "No JSON found in response.", "steps": []}
        except Exception as e:
            logger.error(f"Plan formulation parsing failed: {e}")
            return {"reasoning": f"Plan parsing failure: {str(e)}", "steps": []}
