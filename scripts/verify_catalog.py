import requests

BACKEND_URL = "https://api.realms2riches.com"
HEADERS = {
    "X-License-Key": "mock_dev_key", # Should match env
    "": "true"
}

def test_catalog_integrity():
    print("--- CATALOG INTEGRITY TEST ---")
    try:
        res = requests.get(f"{BACKEND_URL}/products", headers=HEADERS, timeout=10)
        res.raise_for_status()
        products = res.json()
        
        count = len(products)
        print(f"Total Products Found: {count}")
        
        if count != 18:
            print(f"❌ FAIL: Expected 18 products, found {count}")
        else:
            print("✅ PASS: Product count is 18.")

        missing_images = []
        for p in products:
            if not p.get("image_url") or "realmstoriches.xyz" not in p.get("image_url"):
                missing_images.append(p.get("id"))
        
        if missing_images:
            print(f"❌ FAIL: Products missing valid images: {missing_images}")
        else:
            print("✅ PASS: All products have valid images.")

        # Check unique names/ids
        ids = [p['id'] for p in products]
        if len(set(ids)) != len(ids):
            print("❌ FAIL: Duplicate IDs detected.")
        else:
            print("✅ PASS: All IDs are unique.")

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_catalog_integrity()

