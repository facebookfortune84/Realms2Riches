import os
import sys

sys.path.append(os.getcwd())

from orchestrator.src.core.catalog.models import ProductModel
from orchestrator.src.memory.sql_store import SQLStore

def update_product_images():
    store = SQLStore()
    session = store.Session()
    
    # Mapping based on prod_ prefixes found in CSV
    products = {
        'prod_jarvis_basic': 'jarvis_basic.png',
        'prod_jarvis_custom': 'jarvis_custom.png',
        'prod_jarvis_premium': 'jarvis_premium.png',
        'prod_svc_domination': 'digital_domination.png',
        'prod_svc_startup': 'startup_accelerator.png',
        'prod_svc_mgmt': 'business_consultation.png',
        'prod_svc_elite': 'elite_support.png',
        'prod_svc_brand': 'brand_kit.png'
    }
    
    found_count = 0
    for pid, img in products.items():
        p = session.query(ProductModel).filter_by(id=pid).first()
        if p:
            p.image_url = f"/assets/{img}"
            found_count += 1
            print(f"✅ Updated {pid} image path to /assets/{img}")
        else:
            print(f"⚠️ Product {pid} not found in database.")
            
    session.commit()
    session.close()
    print(f"🚀 {found_count} product images mapped to industrial directory.")

if __name__ == "__main__":
    update_product_images()
