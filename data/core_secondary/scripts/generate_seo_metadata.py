import os
import json
import logging

logger = logging.getLogger("SEO_Generator")

def generate_sitemap():
    """Generates a dynamic sitemap.xml for all programmatic niches."""
    base_url = "https://api.realms2riches.com"
    niche_dir = "data/store/niches"
    
    if not os.path.exists(niche_dir):
        logger.warning("No niches found. Skipping sitemap.")
        return

    sitemap_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    # Add main pages
    routes = ["/", "/blog", "/metrics"]
    for route in routes:
        sitemap_content.append(f"  <url><loc>{base_url}{route}</loc><priority>1.0</priority></url>")

    # Add all niche pages
    for niche_file in os.listdir(niche_dir):
        if niche_file.endswith(".json"):
            slug = niche_file.replace(".json", "")
            sitemap_content.append(f"  <url><loc>{base_url}/niche/{slug}</loc><priority>0.8</priority></url>")

    sitemap_content.append("</urlset>")
    
    with open("data/store/sitemap.xml", "w") as f:
        f.write("\n".join(sitemap_content))
    
    logger.info(f"✅ SEO: Generated sitemap with {len(os.listdir(niche_dir))} niche pages.")

def update_niche_schemas():
    """Injects JSON-LD schema into niche configurations."""
    niche_dir = "data/store/niches"
    if not os.path.exists(niche_dir): return

    for niche_file in os.listdir(niche_dir):
        path = os.path.join(niche_dir, niche_file)
        with open(path, "r") as f:
            data = json.load(f)
        
        # Add Schema.org metadata
        data["schema"] = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": data["title"],
            "description": data["description"],
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "offers": {
                "@type": "Offer",
                "price": "2999.00",
                "priceCurrency": "USD"
            }
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    update_niche_schemas()
    generate_sitemap()

