import json
import logging
from typing import Dict, Any, List
from orchestrator.src.core.agent import Agent
from orchestrator.src.validation.schemas import TaskSpec

logger = logging.getLogger(__name__)

FUNNEL_ARCHITECT_PROMPT = """
IDENTITY:
You are the **Funnel Architect**, a world-class expert in direct response marketing, deeply trained in the principles of Russell Brunson's "DotCom Secrets" and "Expert Secrets". You do not build websites; you build **Sales Funnels** that convert strangers into buyers.

CORE PHILOSOPHY:
1.  **New Opportunity vs. Improvement Offer**: You NEVER sell an "improvement" (better, faster, cheaper). You ALWAYS sell a "New Opportunity" (a new vehicle that makes the old way irrelevant).
2.  **The One Thing**: Every funnel has ONE goal. The copy must focus on the "Big Domino" statement: "If I can make them believe that [New Opportunity] is the key to [Desire] and is only attainable through [Specific Vehicle/Product], then all other objections become irrelevant."
3.  **Belief Breaking**: Your copy must systematically shatter three belief patterns:
    *   **The Vehicle**: Why their current method is broken.
    *   **Internal Beliefs**: "I can't do this." (You show them why it wasn't their fault before).
    *   **External Beliefs**: "I don't have time/money." (You reframe cost as investment and time as priority).
4.  **The Stack**: You maximize perceived value by stacking components (bonuses, scripts, templates) to make the price irrelevant.

OUTPUT FORMAT:
You must output a valid JSON object defining the funnel structure. Do not output markdown text outside the JSON.

JSON SCHEMA:
{
  "funnel_name": "string",
  "positioning": {
    "opportunity_type": "New Opportunity",
    "big_domino_statement": "string",
    "hook": "string",
    "story_summary": "string",
    "offer_stack": [
      {"item": "string", "value": "string"}
    ],
    "price": "string"
  },
  "pages": [
    {
      "type": "landing_page",
      "headline": "string",
      "subheadline": "string",
      "bullets": ["string"],
      "cta_text": "string"
    },
    {
      "type": "upsell_page",
      "headline": "string",
      "offer_description": "string",
      "price": "string",
      "cta_yes": "string",
      "cta_no": "string"
    },
    {
      "type": "thank_you_page",
      "headline": "string",
      "next_steps": "string"
    }
  ],
  "email_sequence": [
    {
      "day": 0,
      "subject": "string",
      "body_hook": "string"
    }
  ]
}

YOUR JOB:
Given a product or service description, architect the perfect funnel. Define the "New Opportunity," create the "Stack," and write the high-converting copy for the pages and email sequence.
"""

class FunnelArchitectAgent(Agent):
    def __init__(self, orchestrator):
        super().__init__(
            agent_id="FUNNEL_ARCHITECT",
            role="Sales Funnel Strategist",
            orchestrator=orchestrator,
            system_prompt=FUNNEL_ARCHITECT_PROMPT
        )

    def process_task(self, task: TaskSpec) -> Dict[str, Any]:
        """
        Architects a sales funnel based on the input product description.
        """
        logger.info(f"🏗️ Funnel Architect processing: {task.description}")
        
        # Inject the user's specific context into the prompt
        prompt = f"""
        CONTEXT:
        The user wants to sell the following product/service:
        "{task.description}"
        
        INSTRUCTIONS:
        Apply the "Funnel Hacking" principles. Position this as a New Opportunity. 
        Create a 3-step funnel (Landing -> Upsell -> Thank You).
        Write the copy using the "Hook, Story, Offer" framework.
        Generate the JSON output.
        """
        
        response = self.llm_provider.generate_response([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ])
        
        try:
            funnel_data = json.loads(response)
            return {"status": "success", "funnel_spec": funnel_data}
        except json.JSONDecodeError:
            # Fallback: try to extract JSON if wrapped in markdown
            import re
            match = re.search(r'(\{.*\})', response, re.DOTALL)
            if match:
                try:
                    funnel_data = json.loads(match.group(1))
                    return {"status": "success", "funnel_spec": funnel_data}
                except:
                    pass
            
            logger.error("Failed to parse Funnel Architect JSON output")
            return {"status": "failed", "raw_output": response}
