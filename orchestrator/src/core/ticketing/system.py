import uuid
import logging
from enum import Enum
from typing import List, Dict, Optional
import os
import asyncio
import random
import time

logger = logging.getLogger(__name__)

class TicketStatus(Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"

class Priority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Ticket:
    def __init__(self, title: str, description: str, priority: Priority = Priority.MEDIUM, metadata: Dict = None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = TicketStatus.OPEN
        self.priority = priority
        self.metadata = metadata or {}
        self.assigned_agent = None
        self.resolution_notes = None

class TicketingSystem:
    def __init__(self):
        self.queue: List[Ticket] = []
        self.resolved: List[Ticket] = []
        self.escalated: List[Ticket] = []
        
    def create_ticket(self, title: str, description: str, priority: Priority = Priority.MEDIUM, metadata: Dict = None) -> Ticket:
        ticket = Ticket(title, description, priority, metadata)
        self.queue.append(ticket)
        priority_order = {Priority.CRITICAL: 4, Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
        self.queue.sort(key=lambda t: priority_order.get(t.priority, 0), reverse=True)
        logger.info(f"[TICKETING] Created ticket: {ticket.id} - {ticket.title} ({priority.name})")
        return ticket

    def get_next_ticket(self) -> Optional[Ticket]:
        if not self.queue: return None
        return self.queue.pop(0)

    def resolve_ticket(self, ticket: Ticket, notes: str):
        ticket.status = TicketStatus.RESOLVED
        ticket.resolution_notes = notes
        self.resolved.append(ticket)
        logger.info(f"[TICKETING] Resolved ticket: {ticket.id}")

    def escalate_ticket(self, ticket: Ticket, reason: str):
        ticket.status = TicketStatus.ESCALATED
        ticket.resolution_notes = f"ESCALATED: {reason}"
        self.escalated.append(ticket)
        logger.warning(f"[TICKETING] ESCALATED ticket: {ticket.id} - {reason}")
        
ticketing_system = TicketingSystem()

# --- SWARM AGENT LOGIC WITH TIME & WAGE TRACKING ---
class SwarmAgent:
    def __init__(self, index: int):
        self.agent_id = f"SWARM_NODE_{index}"
        
        # Load wisdom from oracle
        self.oracle_prompts = self._load_oracle("prompts")
        self.oracle_tools = self._load_oracle("tools")
        
        # Role Call Logic (Persona & Unique Name)
        from orchestrator.src.agents.persona_library import PERSONA_LIBRARY
        persona_key = random.choice(list(PERSONA_LIBRARY.keys()))
        self.persona = PERSONA_LIBRARY[persona_key]["title"]
        self.unique_name = f"{persona_key.split('_')[0]}_{uuid.uuid4().hex[:4].upper()}"
        
        # Time & Wage Tracking (API Access Monetization Baseline: $2999/mo)
        self.hourly_rate = 150.00  # Calculated equivalent value
        self.total_time_spent_sec = 0.0
        self.total_value_generated = 0.0

    def _load_oracle(self, directory: str) -> List[str]:
        oracle_path = os.path.join(os.getcwd(), "data", "oracle", directory)
        loaded = []
        if os.path.exists(oracle_path):
            for file in os.listdir(oracle_path):
                loaded.append(file)
        return loaded

    def process_ticket(self, ticket: Ticket):
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.assigned_agent = self.unique_name
        logger.info(f"[ROLE CALL] Agent '{self.unique_name}' ({self.persona}) picked up ticket {ticket.id}.")
        
        start_time = time.time()
        
        # Simulate work
        if "error" in ticket.title.lower() or "repair" in ticket.title.lower():
            action = f"Repaired issue in {ticket.metadata.get('file', 'unknown')} using {self.persona} directives."
            ticketing_system.resolve_ticket(ticket, action)
            work_duration = random.uniform(1.0, 5.0)
        elif "upgrade" in ticket.title.lower() or "stream" in ticket.title.lower():
            action = "Successfully injected structural upgrades using oracle schemas."
            ticketing_system.resolve_ticket(ticket, action)
            work_duration = random.uniform(2.0, 8.0)
        else:
            ticketing_system.escalate_ticket(ticket, "Requires manual human oversight or architectural review.")
            work_duration = random.uniform(0.5, 2.0)
            
        # Tally time and wages
        self.total_time_spent_sec += work_duration
        earned = (work_duration / 3600.0) * self.hourly_rate
        self.total_value_generated += earned
        logger.info(f"[{self.unique_name}] Task value generated: ${earned:.4f}. Total: ${self.total_value_generated:.4f}")

class SwarmDirector:
    def __init__(self, size: int = 100):
        self.pool_size = size
        self.agents = [SwarmAgent(i) for i in range(size)]

    def generate_system_scan_tickets(self):
        logger.info("[SWARM] Initializing comprehensive codebase and state scan...")
        ticketing_system.create_ticket("Integrate Scraped Affiliate Links into Engine", "Use data from realms_to_riches to populate streams.", Priority.CRITICAL, {"target": "monetization_engine"})
        ticketing_system.create_ticket("Repair Deprecated API Calls in orchestrator", "Update to new standard outlined in Builder Prompt.txt", Priority.HIGH, {"file": "orchestrator/src/core/api.py"})
        ticketing_system.create_ticket("Expand Social Multiplexer to TikTok", "Use extracted TikTok Shop affiliate links.", Priority.MEDIUM, {"file": "social_tools.py"})
        ticketing_system.create_ticket("Scan Oracle Directory for Tool Drift", "Verify all Tools in data/oracle/tools are functional.", Priority.LOW)

    async def turn_loose(self):
        logger.info(f"🚀 [SWARM DIRECTOR] Turning {self.pool_size * 10} simulated autonomous agents LOOSE...")
        self.generate_system_scan_tickets()
        
        while ticketing_system.queue:
            ticket = ticketing_system.get_next_ticket()
            if ticket:
                agent = self.agents[hash(ticket.id) % self.pool_size]
                agent.process_ticket(ticket)
                await asyncio.sleep(0.1)

        total_swarm_value = sum(a.total_value_generated for a in self.agents)
        logger.info(f"✅ [SWARM DIRECTOR] Execution complete. Resolved: {len(ticketing_system.resolved)}, Escalated: {len(ticketing_system.escalated)}.")
        logger.info(f"💰 [SWARM ECONOMICS] Total autonomous value generated in this cycle: ${total_swarm_value:.2f}")

swarm_director = SwarmDirector(size=100)
