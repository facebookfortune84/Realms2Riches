from typing import List, Dict, Any
from orchestrator.src.validation.schemas import AgentConfig

DEPARTMENTS = {
    "Engineering": [
        "Cloud Infrastructure Architect", "Cybersecurity Analyst", "Site Reliability Engineer", 
        "Database Administrator", "Performance Optimization Specialist", "Mobile App Developer (iOS)",
        "Mobile App Developer (Android)", "Full-Stack Integrator", "API Design Specialist",
        "Legacy Code Refactorer", "Embedded Systems Engineer", "Machine Learning Engineer",
        "Data Engineer", "Frontend Performance Guru", "Backend Scalability Expert",
        "Blockchain Developer", "AR/VR Experience Dev", "Quality Assurance Automator",
        "Penetration Tester", "DevSecOps Specialist"
    ],
    "Creative": [
        "UI Visual Designer", "UX Research Lead", "Brand Identity Strategist", 
        "Motion Graphics Designer", "3D Asset Illustrator", "User Empathy Specialist",
        "Interactive Prototype Builder", "Typography Expert", "Color Theory Consultant",
        "Design Systems Maintainer"
    ],
    "Marketing": [
        "SEO Strategy Lead", "PPC Campaign Manager", "Growth Hacker", 
        "Social Media Engagement Agent", "Email Funnel Architect", "Content Distribution Specialist",
        "Affiliate Network Manager", "Influencer Outreach Coordinator", "Market Sentiment Analyst",
        "Conversion Rate Optimizer", "Public Relations Officer", "Event Marketing Planner",
        "Viral Loop Strategist", "Brand Voice Consistency Agent", "Ad Creative Copywriter"
    ],
    "Data_Research": [
        "Quantitative Market Analyst", "Competitive Intelligence Agent", "User Behavior Scientist",
        "Trend Forecasting Bot", "Data Visualization Expert", "Academic Research Liaison",
        "NLP Model Tuner", "Computer Vision Specialist", "Statistical Auditor",
        "A/B Testing Coordinator", "Sentiment Mining Agent", "Data Privacy Officer"
    ],
    "Operations": [
        "Agile Scrum Master", "Workflow Automation Engineer", "Resource Allocation Planner",
        "Project Timeline Auditor", "Logistics Coordinator", "Internal Process Optimizer",
        "Agent Performance Monitor", "Documentation Governance Lead", "Knowledge Base Manager"
    ],
    "Finance": [
        "SaaS Pricing Strategist", "Revenue Forecasting Analyst", "Tax Compliance Agent",
        "Billing Logic Auditor", "Investor Relations Liaison", "Risk Management Specialist",
        "Stripe Integration Expert", "Expense Optimization Bot", "Procurement Coordinator"
    ],
    "Legal_Compliance": [
        "Terms of Service Architect", "Privacy Policy Specialist", "GDPR Compliance Officer",
        "Intellectual Property Scout", "Contract Review Agent", "Ethical AI Auditor",
        "Security Governance Lead", "Licensing Compliance Officer"
    ],
    "Sales_Support": [
        "Technical Sales Engineer", "Customer Success Architect", "User Onboarding Specialist",
        "High-Ticket Closer Agent", "Lead Qualification Bot", "Support Tier-3 Resolver",
        "Community Management Lead", "Customer Feedback Synthesizer"
    ],
    "Product": [
        "Product Roadmap Visionary", "Feature Prioritization Bot", "User Story Architect",
        "Market Fit Validator", "UX Friction Finder", "Product Analytics Lead"
    ],
    "Executive": [
        "Chief Strategy Agent", "Crisis Management Lead", "Partnership Ecosystem Scout",
        "AI Alignment Director", "Innovation Lab Lead"
    ]
}

def generate_fleet_configs() -> List[AgentConfig]:
    fleet = []
    for dept, agents in DEPARTMENTS.items():
        for agent_name in agents:
            agent_id = agent_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
            fleet.append(AgentConfig(
                id=agent_id,
                name=agent_name,
                role=agent_name,
                description=f"Specialized {agent_name} within the {dept} department.",
                system_prompt=f"You are the {agent_name}. Your mission is to provide world-class expertise in {agent_name} tasks. Cooperate with the Forge Orchestrator.",
                allowed_tool_ids=["universal_search", "universal_writer", "universal_analyst"],
                handoff_targets=["pm", "forge_orchestrator"],
                governance_level="high"
            ))
    return fleet
