import hashlib
from typing import List, Dict
from orchestrator.src.validation.schemas import AgentConfig
from orchestrator.src.agents.prompts import SOFTWARE_ENGINEER_PROMPT

# Meta-Departments for the 1000-Agent Fleet
META_DEPARTMENTS = {
    "Cybernetic_Engineering": 200,
    "Visual_Intelligence": 150,
    "Global_Market_Force": 200,
    "Integrity_Shield": 150,
    "Strategic_Operations": 100,
    "Revenue_Systems": 100,
    "Fallback_Optimization": 100
}

def generate_grand_fleet() -> List[AgentConfig]:
    fleet = []
    # Pre-cache common prompt parts
    eng_prompt = SOFTWARE_ENGINEER_PROMPT
    
    for meta_dept, count in META_DEPARTMENTS.items():
        base_prompt = eng_prompt if meta_dept in ["Cybernetic_Engineering", "Strategic_Operations", "Fallback_Optimization"] else ""
        
        for i in range(count):
            agent_id = f"agent_{meta_dept.lower()}_{i+1}"
            identity_hash = hashlib.sha256(agent_id.encode()).hexdigest()[:8]
            
            # Using bulk-friendly initialization
            fleet.append(AgentConfig(
                id=agent_id,
                name=f"{meta_dept.replace('_', ' ')} Specialist Unit {i+1}",
                role=f"Deep Specialization in {meta_dept}",
                description=f"Unit {identity_hash}",
                system_prompt=f"{base_prompt}\nIDENTITY: {identity_hash} of {meta_dept} Grand Fleet.",
                allowed_tool_ids=["universal_action_multiplexer"],
                handoff_targets=["forge_orchestrator"],
                governance_level="critical"
            ))
    return fleet
