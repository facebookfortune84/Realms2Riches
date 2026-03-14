import asyncio
import sys
import os
import json

# Ensure project root is in path
sys.path.append(os.getcwd())

from mcp_internal.ucp.core import ucp

async def verify_ucp():
    print("🚀 STARTING UCP VERIFICATION...")
    
    # Test Stripe MCP
    try:
        print("\n[STRIPE] Calling create_checkout...")
        result = await ucp.create_checkout("test@example.com", "prod_123")
        print(f"✅ Result: {result.content}")
    except Exception as e:
        print(f"❌ Stripe Error: {e}")

    # Test Outreach MCP
    try:
        print("\n[OUTREACH] Calling send_outreach...")
        result = await ucp.send_outreach("test@example.com", "<h1>Hello</h1>", "Test Subject")
        print(f"✅ Result: {result.content}")
    except Exception as e:
        print(f"❌ Outreach Error: {e}")

    # Test Oracle MCP
    try:
        print("\n[ORACLE] Calling consult_oracle...")
        result = await ucp.consult_oracle()
        print(f"✅ Result: {result.content}")
    except Exception as e:
        print(f"❌ Oracle Error: {e}")

    # Test Swarm MCP (requires API running)
    try:
        print("\n[SWARM] Calling dispatch_swarm...")
        result = await ucp.dispatch_swarm("Generate a revenue report.")
        print(f"✅ Result: {result.content}")
    except Exception as e:
        print(f"❌ Swarm Error (Expected if API is down): {e}")

if __name__ == "__main__":
    asyncio.run(verify_ucp())
