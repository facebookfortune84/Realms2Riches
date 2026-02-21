from typing import List, Dict, Any, Optional
import json
import hashlib
from datetime import datetime
from orchestrator.src.validation.schemas import AgentConfig, TaskSpec, ToolInvocation
from orchestrator.src.tools.base import BaseTool
from orchestrator.src.memory.vector_store import VectorStore
from orchestrator.src.core.llm_provider import BaseLLMProvider
from orchestrator.src.logging.logger import get_logger

logger = get_logger(__name__)

class Agent:
    def __init__(self, config: AgentConfig, tools: List[BaseTool], memory: VectorStore, llm_provider: BaseLLMProvider):
        self.config = config
        self.tools = {t.config.tool_id: t for t in tools}
        self.memory = memory
        self.llm_provider = llm_provider
        self.history: List[Dict[str, str]] = []

    def process_task(self, task: TaskSpec) -> Dict[str, Any]:
        logger.info(f"Agent {self.config.name} processing task: {task.description}")
        
        try:
            # 1. RAG Context Injection
            context_docs = self.memory.search(task.description, limit=3)
            context_text = "\n".join([f"- {doc['text']}" for doc in context_docs]) if context_docs else "No specific context found."
            
            # Record this task in RAG for future recursive learning
            self.memory.add(f"Task: {task.description}", {"agent": self.config.id, "type": "task_log"})

            # 2. Formulate plan with injected context
            plan = self._call_llm(task.description, context_text)
            reasoning = plan.get("reasoning", "Executing swarm logic...")
            
            # 3. Execute tools based on plan
            results = []
            for step in plan.get("steps", []):
                tool_id = step.get("tool_id")
                if tool_id in self.tools:
                    invocation = ToolInvocation(
                        tool_id=tool_id,
                        agent_id=self.config.id,
                        input_data=step.get("inputs", {})
                    )
                    result = self.tools[tool_id].run(invocation)
                    
                    # Cryptographic Integrity: Hash the output
                    result_data = result.model_dump_json()
                    result.integrity_hash = hashlib.sha256(result_data.encode()).hexdigest()
                    
                    results.append(result.model_dump(mode="json"))
                else:
                    if tool_id:
                        logger.warning(f"Tool {tool_id} not found or allowed for {self.config.name}")

            return {
                "status": "completed", 
                "results": results, 
                "reasoning": reasoning,
                "agent_id": self.config.id,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Agent {self.config.name} failed task: {e}")
            return {"status": "failed", "error": str(e), "agent_id": self.config.id}

    def _call_llm(self, prompt: str, context: str) -> Dict[str, Any]:
        # Build Tool Definition Block
        tools_desc = "\n".join([f"- {t.config.tool_id}: {t.config.description}" for t in self.tools.values()])
        
        system_msg = f"""{self.config.system_prompt}

You have access to the following tool IDs:
{tools_desc}

RULES:
1. If the user asks to create a file or project, YOU MUST use the 'file' tool.
2. If the user asks to post social media, YOU MUST use the 'social' tool.
3. If the user asks to generate images, YOU MUST use the 'image_gen' tool.
4. If the user asks to generate videos, YOU MUST use the 'video' tool.
5. Output ONLY valid JSON with the following schema:
{{
  "reasoning": "explanation of plan",
  "steps": [
    {{
      "tool_id": "tool_id_from_list_above",
      "inputs": {{ "param_name": "value" }}
    }}
  ]
}}

Context:
{context}"""
        
        user_msg = f"Task: {prompt}"
        
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
        
        response_text = self.llm_provider.generate_response(messages)
        
        try:
            # Robust JSON extraction
            # Find the first { and last }
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx : end_idx + 1]
                return json.loads(json_str)
            else:
                # Basic cleanup in case of markdown blocks if not caught above
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                return json.loads(response_text)
        except Exception as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}. Raw: {response_text}")
            return {"steps": [], "reasoning": "Failed to parse plan."}
