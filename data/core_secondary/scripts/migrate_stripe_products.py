import os
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
stripe.api_key = os.getenv('STRIPE_API_KEY')

products_data = [
    {
        "name": "Jarvis 3.5 Basic Monthly",
        "description": "Launch your startup with lean AI firepower. Includes up to 5,000 API calls/month, 1 GB secure data storage, and access to core Jarvis features.",
        "price": 29.99,
        "type": "recurring",
        "image_url": "https://www.realmstoriches.xyz/img/bannerimage(3)-600.webp"
    },
    {
        "name": "Jarvis 3.5 Custom Monthly",
        "description": "Tailored automation for growing teams. Includes 25,000 API calls/month, 10 GB data storage, custom dashboard branding, and priority support.",
        "price": 79.99,
        "type": "recurring",
        "image_url": "https://www.realmstoriches.xyz/img/bannerimage(3)-600.webp"
    },
    {
        "name": "Jarvis 3.5 Premium Monthly",
        "description": "Full-stack AI orchestration for scale. Includes 100,000 API calls/month, 50 GB data storage, dedicated onboarding, conversion funnel templates, and early access to all new tools.",
        "price": 199.99,
        "type": "recurring",
        "image_url": "https://www.realmstoriches.xyz/img/bannerimage(3)-600.webp"
    },
    {
        "name": "Business Management Consultation",
        "description": "Strategic guidance to streamline your business operations and growth.",
        "price": 300.00,
        "type": "one_time",
        "image_url": "https://www.realmstoriches.xyz/img/service-consultation-300.webp"
    },
    {
        "name": "Basic Brand Kit",
        "description": "Essential branding elements including logo design, color palette, and typography.",
        "price": 450.00,
        "type": "one_time",
        "image_url": "https://www.realmstoriches.xyz/img/service-brandkitdesign-300.webp"
    },
    {
        "name": "Marketing Campaign Management",
        "description": "Expert setup and initial management of your marketing campaign (ad spend not included).",
        "price": 700.00,
        "type": "one_time",
        "image_url": "https://www.realmstoriches.xyz/img/service-marketing-300.webp"
    },
    {
        "name": "Website Design (Basic)",
        "description": "Professional, responsive website design for small businesses.",
        "price": 1500.00,
        "type": "one_time",
        "image_url": "https://www.realmstoriches.xyz/img/service-webdesignbasic-300.webp"
    },
    {
        "name": "Website Design (Advanced)",
        "description": "Advanced website design with custom features and integrations for growing businesses.",
        "price": 3000.00,
        "type": "one_time",
        "image_url": "https://www.realmstoriches.xyz/img/service-webdesignadvanced-300.webp"
    },
    {
        "name": "E-commerce Website Development",
        "description": "Full-featured online store development with payment gateway integration.",
        "price": 5000.00,
        "type": "one_time",
        "image_url": "https://www.realmstoriches.xyz/img/service-ecommercewebdesign-300.webp"
    },
    {
        "name": "SEO Optimization Package",
        "description": "Comprehensive search engine optimization to improve your online visibility.",
        "price": 800.00,
        "type": "one_time",
        "image_url": "https://www.realmstoriches.xyz/img/service-seo-300.webp"
    },
    {
        "name": "Social Media Management",
        "description": "Professional management of your social media presence to engage your audience.",
        "price": 600.00,
        "type": "one_time",
        "image_url": "https://www.realmstoriches.xyz/img/service-contentcreation-300.webp"
    },
    {
        "name": "Realms to Riches Elite Support",
        "description": "Priority support, monthly strategic coaching, and a curated library of resources.",
        "price": 250.00,
        "type": "recurring",
        "image_url": "https://www.realmstoriches.xyz/img/service-monthlyelite-300.webp"
    },
    {
        "name": "Startup Accelerator Bundle",
        "description": "Strategic guidance, essential branding, and a professional basic website.",
        "price": 1999.00,
        "type": "one_time",
        "image_url": "https://www.realmstoriches.xyz/img/service-monthlystartup-600.webp"
    },
    {
        "name": "Digital Domination Package",
        "description": "Advanced website, comprehensive marketing, and robust SEO/social media strategies.",
        "price": 4499.00,
        "type": "one_time",
        "image_url": "https://www.realmstoriches.xyz/img/service-digitaldomination-300.webp"
    },
    {
        "name": "Digital Growth Monthly",
        "description": "Continuous optimization, monthly reports, and strategic adjustments.",
        "price": 400.00,
        "type": "recurring",
        "image_url": "https://www.realmstoriches.xyz/img/service-digitalgrowthmonthly-300.webp"
    }
]

def main():
    print("Starting Stripe product migration...")
    
    # Get existing products to avoid duplicates
    existing_products = stripe.Product.list(limit=100)
    existing_names = [p.name for p in existing_products.data]

    for item in products_data:
        if item["name"] in existing_names:
            print(f"Skipping '{item['name']}' - already exists.")
            continue
            
        print(f"Creating Product: {item['name']}")
        product = stripe.Product.create(
            name=item["name"],
            description=item["description"],
            images=[item["image_url"]]
        )
        
        print(f"Creating Price for: {item['name']}")
        price_kwargs = {
            "product": product.id,
            "unit_amount": int(item["price"] * 100), # amount in cents
            "currency": "usd",
        }
        if item["type"] == "recurring":
            price_kwargs["recurring"] = {"interval": "month"}
            
        price = stripe.Price.create(**price_kwargs)
        
        print(f"Creating Payment Link for: {item['name']}")
        payment_link = stripe.PaymentLink.create(
            line_items=[
                {
                    "price": price.id,
                    "quantity": 1,
                }
            ],
            after_completion={
                "type": "hosted_confirmation"
            }
        )
        
        print(f"Created successfully. Link: {payment_link.url}")
        print("-" * 40)

if __name__ == "__main__":
    main()
