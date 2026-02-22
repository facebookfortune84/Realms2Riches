import os
import sys
sys.path.append(os.getcwd())

import asyncio
import unittest
from fastapi.testclient import TestClient
from orchestrator.src.core.api import app
from orchestrator.src.core.orchestrator import Orchestrator

class TestSovereignTracks(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_track_1_asset_delivery(self):
        """Verify the Strategy Guide is available at the correct ngrok-based URL."""
        response = self.client.post("/api/leads", json={
            "email": "verification@sovereign.ai",
            "source": "live_test"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify the URL is exactly what the user provided
        expected_url = "https://glowfly-sizeable-lazaro.ngrok-free.dev/assets/sovereign_strategy_guide_v3.txt"
        self.assertEqual(data["guide_url"], expected_url)
        print(f"✅ Track 1 Passed: Guide URL is {data['guide_url']}")

    def test_track_2_static_serving(self):
        """Verify the backend actually serves the file from the local path."""
        # TestClient can hit mounted static files
        response = self.client.get("/assets/sovereign_strategy_guide_v3.txt")
        self.assertEqual(response.status_code, 200)
        self.assertIn("SOVEREIGN STRATEGY GUIDE", response.text)
        print("✅ Track 2 Passed: Static file serving verified.")

    def test_track_3_concurrent_routing(self):
        """Verify the Orchestrator can route tasks to different cells without blocking."""
        # Genesis Forge (Build) -> ALPHA
        # Social Content (Market) -> BETA
        # Audit (Revenue) -> GAMMA
        
        o = Orchestrator()
        
        async def run_parallel():
            t1 = o.submit_task_stream("Build project Chimera", "test")
            t2 = o.submit_task_stream("Post to socials", "test")
            
            # We just verify routing labels in the stream
            r1 = await t1.__anext__()
            r2 = await t2.__anext__()
            
            self.assertIn("CELL_ALPHA", r1["message"])
            self.assertIn("CELL_BETA", r2["message"])
            
        asyncio.run(run_parallel())
        print("✅ Track 3 Passed: Multi-track routing (Build & Social) verified.")

if __name__ == "__main__":
    unittest.main()
