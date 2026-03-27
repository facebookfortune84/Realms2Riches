import os
import json
import datetime

def generate_seo_assets():
    with open("data/affiliates/click_funnels/campaigns.json", "r") as f:
        campaigns = json.load(f)

    # 1. Generate Metadata for React Pages
    seo_meta = {}
    for camp in campaigns:
        seo_meta[camp['id']] = {
            "title": f"{camp['name']} | Realms2Riches Sovereign Partner",
            "description": f"Launch your business with {camp['name']}. Access the exclusive bridge page and bonus assets from Realms2Riches.",
            "canonical": camp['bridge_page_url'],
            "robots": "index, follow"
        }

    with open("frontend/src/seo_config.json", "w") as sf:
        json.dump(seo_meta, sf, indent=2)

    # 2. Generate Sitemap.xml for Search Console
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for camp in campaigns:
        sitemap_content += f"""  <url>
    <loc>{camp['bridge_page_url']}</loc>
    <lastmod>{datetime.date.today().isoformat()}</lastmod>
    <priority>1.0</priority>
  </url>\n"""
    sitemap_content += "</urlset>"

    with open("frontend/public/sitemap.xml", "w") as sm:
        sm.write(sitemap_content)

    print("✅ SEO Engine Updated: Sitemap and Metadata generated for ClickFunnels Campaigns.")

if __name__ == "__main__":
    generate_seo_assets()
