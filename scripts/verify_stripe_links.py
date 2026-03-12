import csv
import os
from playwright.sync_api import sync_playwright

def verify_links():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        products_file = 'data/catalog/products.csv'
        if not os.path.exists(products_file):
            print(f"Error: {products_file} not found.")
            return

        with open(products_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['checkout_url']
                p_id = row['id']
                p_name = row['name']
                
                if 'stripe.com' not in url and 'checkout.realmstoriches.xyz' not in url:
                    print(f"Skipping non-stripe URL for {p_id}")
                    continue

                print(f"Checking {p_id}: {url}")
                try:
                    page.goto(url, wait_until="networkidle", timeout=60000)
                    # Common Stripe selectors
                    # .ProductSummary-info (legacy)
                    # .Checkout-product-name (new)
                    # h1 (general fallback)
                    name_selector = ".ProductSummary-info, .Checkout-product-name, h1"
                    price_selector = ".ProductSummary-totalAmount, .Checkout-total-amount, [data-testid='total-amount-text']"
                    
                    page.wait_for_selector(name_selector, timeout=10000)
                    
                    actual_name = page.inner_text(name_selector).replace('\n', ' ').strip()
                    actual_price = page.inner_text(price_selector).strip()
                    
                    print(f"  [FOUND] Name: {actual_name} | Price: {actual_price}")
                    results.append({
                        "id": p_id,
                        "expected_name": p_name,
                        "actual_name": actual_name,
                        "actual_price": actual_price,
                        "url": url
                    })
                except Exception as e:
                    print(f"  [FAILED] {p_id}: {str(e)[:100]}")
        
        browser.close()
    
    # Save results for analysis
    with open('data/catalog/stripe_verification.json', 'w') as out:
        import json
        json.dump(results, out, indent=2)
    print("\nVerification report saved to data/catalog/stripe_verification.json")

if __name__ == "__main__":
    verify_links()
