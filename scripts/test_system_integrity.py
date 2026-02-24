import asyncio
import logging
from orchestrator.src.core.ticketing.system import swarm_director
from orchestrator.src.core.monetization.engine import monetization_engine

logging.basicConfig(level=logging.INFO)

async def main():
    print("\n--- INITIATING SWARM TICKETING SYSTEM ---")
    await swarm_director.turn_loose()
    
    print("\n--- INITIATING MONETIZATION ENGINE ---")
    results = await monetization_engine.run_all_streams()
    
    active_streams = len([r for r in results if r.get('status') == 'active'])
    print(f"\nTotal Active Streams: {active_streams}")

if __name__ == "__main__":
    asyncio.run(main())
