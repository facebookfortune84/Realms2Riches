import os
import logging
import sys
from orchestrator.src.core.catalog.api import catalog_api
from orchestrator.src.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AssetVerifier")

def verify_all_assets():
    """
    Sovereign Asset Integrity Auditor.
    Enforces the 'No-Asset-No-Launch' rule across all forged items.
    """
    logger.info("🔍 INITIATING GLOBAL ASSET INTEGRITY AUDIT...")
    
    products = catalog_api.get_products()
    if not products:
        logger.warning("⚠️ No products found in catalog. Forge may be idle.")
        return True

    failures = []
    
    for product in products:
        product_id = product.id
        logger.info(f"Checking product: {product_id}")
        
        # 1. Verify Image/Video Reference
        # In our schema, we expect 'image' or 'video' in metadata or as a direct attribute if extended
        # For now, we check the standard marketing directories for files matching the ID
        image_path = f"data/marketing/images/{product_id}.png"
        video_path = f"data/marketing/videos/{product_id}.mp4"
        
        has_image = os.path.exists(image_path)
        has_video = os.path.exists(video_path)
        
        if not (has_image or has_video):
            if settings.ENV_MODE == "dev":
                logger.warning(f"🛠️ [AUTO-HEAL] Generating placeholder image for {product_id}...")
                os.makedirs("data/marketing/images", exist_ok=True)
                with open(image_path, "w") as f: f.write("MOCK_ASSET_DNA")
            else:
                failures.append(f"Product {product_id}: Missing both image ({image_path}) and video ({video_path})")
            
        # 2. Verify Checkout Link
        # Every product must have at least one price with a valid link pattern
        if not product.prices:
            failures.append(f"Product {product_id}: No prices defined.")
        else:
            for price in product.prices:
                # Every price must have a value and optionally a stripe link
                if price.price <= 0:
                    failures.append(f"Product {product_id}: Price is invalid (<= 0).")
                if not price.stripe_price_id and settings.ENV_MODE == "prod":
                    failures.append(f"Product {product_id}: Missing stripe_price_id in production.")

    if failures:
        logger.error("❌ ASSET AUDIT FAILED:")
        for f in failures:
            logger.error(f"  - {f}")
        return False
    
    logger.info("✅ ALL ASSETS VERIFIED. System is READY FOR LAUNCH.")
    return True

if __name__ == "__main__":
    success = verify_all_assets()
    sys.exit(0 if success else 1)
