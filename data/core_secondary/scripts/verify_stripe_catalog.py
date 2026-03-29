import os
import stripe
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
stripe.api_key = os.getenv('STRIPE_API_KEY')

def main():
    print("Verifying and exporting all Stripe products...")
    
    # Get all products and their default prices
    products = stripe.Product.list(limit=100, expand=['data.default_price'])
    
    # We also need to get the payment links for these products
    # Payment links are not directly tied to products, but to prices. 
    # We'll fetch all active payment links and map them by price ID.
    payment_links = stripe.PaymentLink.list(limit=100, active=True)
    price_to_link_map = {}
    
    for link in payment_links.data:
        # A payment link can have multiple line items. We assume 1 for our products.
        line_items = stripe.PaymentLink.list_line_items(link.id, limit=10)
        for item in line_items.data:
            if item.price:
                price_to_link_map[item.price.id] = link.url

    catalog = []
    
    for p in products.data:
        price_id = None
        price_amount = None
        currency = None
        interval = None
        
        if p.default_price:
            price_id = p.default_price.id
            price_amount = p.default_price.unit_amount / 100 if p.default_price.unit_amount else None
            currency = p.default_price.currency
            if p.default_price.type == "recurring" and p.default_price.recurring:
                interval = p.default_price.recurring.interval
                
        # If no default price, search for a price
        if not price_id:
            prices = stripe.Price.list(product=p.id, limit=1)
            if prices.data:
                price_id = prices.data[0].id
                price_amount = prices.data[0].unit_amount / 100 if prices.data[0].unit_amount else None
                currency = prices.data[0].currency
                if prices.data[0].type == "recurring" and prices.data[0].recurring:
                    interval = prices.data[0].recurring.interval
                    
        payment_link = price_to_link_map.get(price_id) if price_id else None
        
        item = {
            "product_id": p.id,
            "name": p.name,
            "description": p.description,
            "images": p.images,
            "active": p.active,
            "price_id": price_id,
            "price_amount": price_amount,
            "currency": currency,
            "interval": interval,
            "payment_link": payment_link
        }
        catalog.append(item)
        
    # Ensure directory exists
    os.makedirs('data/catalog', exist_ok=True)
    
    # Write to file
    with open('data/catalog/stripe_products.json', 'w') as f:
        json.dump(catalog, f, indent=2)
        
    print(f"Exported {len(catalog)} products to data/catalog/stripe_products.json")

if __name__ == "__main__":
    main()
