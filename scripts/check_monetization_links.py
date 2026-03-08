import requests
from typing import Dict, List

# From orchestrator/src/core/monetization/engine.py
AFFILIATE_LINKS = {
    "tiktok_shop": "https://thesuperlink.com/tiktokshop?ref=robertdemottojr&source=realmstoriches",
    "highlevel": "https://www.gohighlevel.com/?fp_ref=realmstoriches",
    "capcut": "https://capcutaffiliateprogram.pxf.io/realmstoriches",
    "clickfunnels": "https://www.plrfunnels.com/plr?aff=b227fabeecb5b9674bf510b0714f0569236d7bbd6ceb3c3ac3f92061ea372fab",
    "brand_push": "https://www.brandpush.co/?ref=57120",
    "pollo_ai": "https://pollo.ai/invitation-landing?invite_code=pIY2cF",
    "play_ht": "https://www.play.ht/?via=robert-demotto-jr",
    "vidiq": "https://vidiq.com/realmstoriches",
}

STRIPE_MONETIZATION = {
    "jarvis_basic": "https://buy.stripe.com/7sY7sLeY1aw1cEWcJJ8so0e",
    "jarvis_custom": "https://buy.stripe.com/eVqeVd17b5bHfR87pp8so0d",
    "jarvis_premium": "https://buy.stripe.com/28E6oHbLP33z6gyaBB8so0c",
    "business_consultation": "https://buy.stripe.com/eVqbJ13fj5bH48q9xx8so0b",
    "brand_kit": "https://buy.stripe.com/28E00jaHLgUp20i5hh8so0a",
    "elite_support": "https://buy.stripe.com/5kQ4gzcPTbA57kCcJJ8so09",
    "startup_accelerator": "https://buy.stripe.com/bJe4gz9DH33z5cu2558so08"
}

def verify_links(links: Dict[str, str], name: str):
    print(f"\nVerifying {name} Links...")
    for key, url in links.items():
        try:
            # Using verify=False to ignore SSL errors for quick checking, 
            # and a short timeout.
            response = requests.head(url, allow_redirects=True, timeout=5)
            status = response.status_code
            if status == 200:
                print(f"✅ [200] {key}: {url}")
            elif status == 405: # Method Not Allowed (some servers block HEAD)
                print(f"⚠️ [405] {key} (Try GET): {url}")
            elif status == 404:
                print(f"❌ [404] {key} NOT FOUND: {url}")
            else:
                print(f"⚠️ [{status}] {key}: {url}")
        except Exception as e:
            print(f"❌ [ERROR] {key}: {e}")

if __name__ == "__main__":
    verify_links(AFFILIATE_LINKS, "Affiliate")
    verify_links(STRIPE_MONETIZATION, "Stripe")
