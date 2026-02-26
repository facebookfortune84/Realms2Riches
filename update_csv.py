import pandas as pd

products_csv_path = 'F:/Realms2Riches/data/catalog/products.csv'
df = pd.read_csv(products_csv_path)

links = {
    "prod_jarvis_basic": "https://buy.stripe.com/9B68wP7ubg7YbAB8avgYU04?locale=en",
    "prod_jarvis_custom": "https://buy.stripe.com/bJedR97ubdZQ489duPgYU05?locale=en",
    "prod_jarvis_premium": "https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en",
    "prod_svc_mgmt": "https://checkout.realmstoriches.xyz/b/28EfZh0vPceK1p87Yl0x200",
    "prod_svc_brand": "https://checkout.realmstoriches.xyz/b/4gMbJ1emFfqW9VE6Uh0x201",
    "prod_svc_marketing": "https://checkout.realmstoriches.xyz/b/cNi14n6UdfqWebU6Uh0x202",
    "prod_svc_web_basic": "https://checkout.realmstoriches.xyz/b/fZudR9cexfqW7Nwbax0x203",
    "prod_svc_web_adv": "https://checkout.realmstoriches.xyz/b/3cI00j4M5baG3xg5Qd0x204",
    "prod_svc_ecom": "https://checkout.realmstoriches.xyz/b/5kQ4gz3I13Ie8RAceB0x205",
    "prod_svc_seo": "https://checkout.realmstoriches.xyz/b/7sYdR93I1ceKd7Q6Uh0x206",
    "prod_svc_social": "https://checkout.realmstoriches.xyz/b/7sY9ATbat5Qm7Nw4M90x207",
    "prod_svc_elite": "https://checkout.realmstoriches.xyz/b/bJecN5diB5Qm5Fo6Uh0x208",
}

# Add default for existing products
df['checkout_url'] = df['id'].apply(lambda x: links.get(x, f"https://checkout.realmstoriches.xyz/b/{x}"))

df.to_csv(products_csv_path, index=False)
print("Updated products.csv with checkout_urls.")
