import stripe
import os
import json
from dotenv import load_dotenv

# Load .env.prod for the live key
load_dotenv(".env.prod")
stripe.api_key = os.getenv("STRIPE_API_KEY")

def create_products():
    new_products = [
        {
            "name": "AI Workflow Integration",
            "description": "Full-scale neural workflow automation and optimization.",
            "amount": 99900,
            "interval": "month"
        },
        {
            "name": "Business Automation Suite",
            "description": "End-to-end industrial automation for all business operations.",
            "amount": 249900,
            "interval": "month"
        },
        {
            "name": "Custom Software Development",
            "description": "Bespoke cybernetic software solutions engineered for scale.",
            "amount": 499900,
            "interval": None
        },
        {
            "name": "Enterprise Infrastructure Setup",
            "description": "Industrial-grade secure infrastructure and cloud orchestration.",
            "amount": 750000,
            "interval": None
        }
    ]

    results = []
    for p_data in new_products:
        print(f"Creating: {p_data['name']}...")
        product = stripe.Product.create(
            name=p_data['name'],
            description=p_data['description']
        )
        
        price_args = {
            "product": product.id,
            "unit_amount": p_data['amount'],
            "currency": "usd"
        }
        if p_data['interval']:
            price_args["recurring"] = {"interval": p_data['interval']}
            
        price = stripe.Price.create(**price_args)
        
        pay_link = stripe.PaymentLink.create(line_items=[{"price": price.id, "quantity": 1}])
        
        results.append({
            "product_id": product.id,
            "name": product.name,
            "description": product.description,
            "price_id": price.id,
            "amount": p_data['amount'] / 100,
            "interval": p_data['interval'] or "one_time",
            "payment_link": pay_link.url
        })
        print(f"  Success: {product.id} | {pay_link.url}")

    with open("data/catalog/new_stripe_products.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    create_products()
