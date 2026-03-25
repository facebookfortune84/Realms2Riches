import os
import requests
import unittest
import sys
import time
import socket

sys.path.append(os.getcwd())

class SovereignFinalAudit(unittest.TestCase):
    BASE_URL = "https://api.realms2riches.com"

    def setUp(self):
        print("   -> Waiting for API Port (localhost:8000)...")
        port_open = False
        for _ in range(60): # 60 seconds initial port wait
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', 8000)) == 0:
                    port_open = True
                    break
            time.sleep(1)
        
        if not port_open: self.fail("API Port failed to open.")

        print("   -> Polling for Matrix Readiness (10 min max)...")
        for i in range(300):
            try:
                res = requests.get(f"{self.BASE_URL}/health", timeout=2)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == "ok":
                        print(f"   -> Matrix ONLINE (Agents: {data.get('agents')}).")
                        return
                    else:
                        if i % 10 == 0:
                            print(f"   -> Initializing Swarm... Current Units: {data.get('agents', 0)}")
            except: pass
            time.sleep(2)
        self.fail("Orchestrator failed to initialize in time.")

    def test_01_core(self):
        res = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(res.status_code, 200)
        print("✅ TRACK 1: Core Online.")

    def test_02_revenue(self):
        res = requests.get(f"{self.BASE_URL}/products")
        self.assertGreater(len(res.json()), 0)
        print("✅ TRACK 2: Revenue Matrix Verified.")

    def test_03_multi_funnel_monetization(self):
        print("   -> Testing Social Funnel...")
        post_res = requests.post(f"{self.BASE_URL}/api/admin/test-dispatch")
        data = post_res.json()
        task_id = data.get("task_id")
        
        if not task_id: self.fail(f"Dispatch Rejected: {data}")
        
        task_success = False
        for _ in range(60): 
            state_res = requests.get(f"{self.BASE_URL}/api/admin/dispatch-status/{task_id}")
            if state_res.json().get("status") == "completed":
                task_success = True
                break
            time.sleep(5)
            
        self.assertTrue(task_success, "Social dispatch track timed out.")
        print("✅ TRACK 3: Social Monetization Live.")

    def test_04_workforce(self):
        res = requests.get(f"{self.BASE_URL}/api/workforce/role-call")
        self.assertEqual(res.status_code, 200)
        print("✅ TRACK 4: Workforce Synchronized.")

if __name__ == "__main__":
    print("\n👑 SOVEREIGN MASTER AUDIT v6.3 👑")
    unittest.main()

