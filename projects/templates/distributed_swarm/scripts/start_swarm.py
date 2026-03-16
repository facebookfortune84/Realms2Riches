import sys
import os
import asyncio

# Add current dir to path
sys.path.append(os.path.join(os.getcwd(), 'orchestrator'))

from main import Orchestrator

async def main():
    print("🚀 Starting Sovereign Distributed Swarm...")
    orchestrator = Orchestrator()
    while True:
        task = input("Enter directive (or 'exit'): ")
        if task.lower() == 'exit':
            break
        results = await orchestrator.execute(task)
        print(f"Results: {results}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Swarm stopped.")
