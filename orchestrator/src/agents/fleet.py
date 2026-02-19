import hashlib
from typing import List, Dict
from orchestrator.src.validation.schemas import AgentConfig

# Meta-Departments for the 1000-Agent Fleet
META_DEPARTMENTS = {
    "Cybernetic_Engineering": 250,  # Compiler Devs, Kernel Optimizers, AI Logic
    "Visual_Intelligence": 150,     # UX/UI, 3D Renderers, Brand Alchemists
    "Global_Market_Force": 200,     # SEO Dominators, Viral Growth, Funnel Architects
    "Integrity_Shield": 150,        # Penetration Testers, Legal Architects, Ethics Auditors
    "Strategic_Operations": 150,    # Project Quantifiers, Workflow Engineers, SREs
    "Revenue_Systems": 100          # Fintech Architects, Pricing Game Theorists
}

def generate_grand_fleet() -> List[AgentConfig]:
    fleet = []
    
    # Core Expert Base (from previous 100)
    # Plus new programmatically generated specializations
    for meta_dept, count in META_DEPARTMENTS.items():
        for i in range(count):
            # Unique Specialization Generation
            spec_name = f"{meta_dept}_{i+1}"
            agent_id = f"agent_{meta_dept.lower()}_{i+1}"
            
            # Deterministic hash for identity verification
            identity_hash = hashlib.sha256(agent_id.encode()).hexdigest()[:8]
            
            fleet.append(AgentConfig(
                id=agent_id,
                name=f"{meta_dept} Specialist Unit {i+1}",
                role=f"Deep Specialization {i+1} in {meta_dept}",
                description=f"Unit {identity_hash} of the {meta_dept} Grand Fleet.",
                system_prompt=f"You are Sovereign Unit {identity_hash}. Mission: Hyper-specialized execution in {meta_dept}.",
                allowed_tool_ids=["universal_action_multiplexer"],
                handoff_targets=["forge_orchestrator"],
                governance_level="critical"
            ))
    return fleet
