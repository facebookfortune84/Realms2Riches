import unittest
import json
import os
import sys

sys.path.append(os.getcwd())

from orchestrator.src.core.catalog.api import catalog_api
from orchestrator.src.core.self_healing import sovereign_healer

class TestPricingDelivery(unittest.TestCase):

    def test_01_null_slot_purge(self):
        """Ensure corrupt None.json is deleted by healer."""
        bad_path = "data/store/slots/None.json"
        with open(bad_path, "w") as f:
            json.dump({"id": None, "price": None}, f)
        
        sovereign_healer.execute_healing_cycle()
        self.assertFalse(os.path.exists(bad_path))
        print("✅ Test 1: Corrupt null slot purged successfully.")

    def test_02_price_normalization(self):
        """Verify flat 'price' fields are mapped to 'prices' list."""
        test_file = "data/store/slots/test_flat.json"
        with open(test_file, "w") as f:
            json.dump({"id": "test_flat", "name": "Flat Product", "price": 99}, f)
        
        products = catalog_api.get_products()
        test_prod = next((p for p in products if p.id == "test_flat"), None)
        
        self.assertIsNotNone(test_prod)
        self.assertTrue(len(test_prod.prices) > 0)
        self.assertEqual(test_prod.prices[0].price, 99)
        
        os.remove(test_file)
        print("✅ Test 2: Price normalization verified.")

    def test_03_platinum_pricing_present(self):
        """Ensure high-ticket Platinum tier is always in the feed."""
        products = catalog_api.get_products()
        ids = [p.id for p in products]
        self.assertIn("sovereign_platinum", ids)
        
        platinum = next(p for p in products if p.id == "sovereign_platinum")
        self.assertEqual(platinum.prices[0].price, 2999)
        print(f"✅ Test 3: Platinum price confirmed at ${platinum.prices[0].price}.")

if __name__ == "__main__":
    unittest.main()
