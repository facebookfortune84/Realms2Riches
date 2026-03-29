import hashlib
from typing import List
from orchestrator.src.validation.schemas import AgentConfig
from orchestrator.src.agents.prompts import SOFTWARE_ENGINEER_PROMPT

# Meta-Departments for the 1000-Agent Fleet
META_DEPARTMENTS = {
    "Cybernetic_Engineering": 200,  # Logic, Databases, AI Kernels
    "Visual_Intelligence": 150,     # UI/UX, Video, Brand Alchemy
    "Global_Market_Force": 200,     # Viral Sharding, SEO, Social Pulse
    "Integrity_Shield": 150,        # Cybersecurity, Compliance, GDPR
    "Strategic_Operations": 100,    # Workflows, Genesis Forge
    "Revenue_Systems": 100,         # Fintech, Stripe, Pricing Theory
    "Fallback_Optimization": 100    # Self-Healing, CRO, System Audit
}

def generate_grand_fleet() -> List[AgentConfig]:
    fleet = []
    
    for meta_dept, count in META_DEPARTMENTS.items():
        for i in range(count):
            agent_id = f"agent_{meta_dept.lower()}_{i+1}"
            identity_hash = hashlib.sha256(agent_id.encode()).hexdigest()[:8]
            
            # Select Base Prompt
            base_prompt = ""
            if meta_dept in ["Cybernetic_Engineering", "Strategic_Operations", "Fallback_Optimization"]:
                base_prompt = SOFTWARE_ENGINEER_PROMPT
            
            system_prompt = f"""
{base_prompt}

# Specialized Identity
You are Sovereign Unit {identity_hash} of the {meta_dept} Grand Fleet. 
MISSION: Platinum execution and autonomous optimization within your department context.
            """.strip()
            
            fleet.append(AgentConfig(
                id=agent_id,
                name=f"{meta_dept.replace('_', ' ')} Specialist Unit {i+1}",
                role=f"Deep Specialization in {meta_dept}",
                description=f"Sovereign Intelligence Unit {identity_hash}.",
                system_prompt=system_prompt,
                allowed_tool_ids=["universal_action_multiplexer", "system_audit", "self_healer", "product_forge"],
                handoff_targets=["forge_orchestrator"],
                governance_level="critical"
            ))
    return fleet
