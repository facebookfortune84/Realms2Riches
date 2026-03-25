import os
import sys
import subprocess

def setup_domain_routing():
    print("🌐 REALMS2RICHES SOVEREIGN DOMAIN SETUP")
    print("=======================================")
    
    domain = input("Enter your primary domain (e.g., realms2riches.com): ").strip()
    if not domain:
        print("❌ No domain provided. Exiting.")
        return

    # 1. Generate Nginx Configuration
    nginx_config = f"""
server {{
    listen 80;
    server_name {domain} www.{domain};

    location / {{
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /api {{
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    
    config_path = f"/etc/nginx/sites-available/{domain}"
    
    # Check if we are on Linux/VPS
    if os.name != 'posix':
        print(f"⚠️  Not running on Linux. Cannot write to {config_path} directly.")
        print("Here is your Nginx Configuration:")
        print(nginx_config)
        print("\nSave this to your Nginx sites-available directory on your VPS.")
    else:
        try:
            with open(f"nginx_{domain}.conf", "w") as f:
                f.write(nginx_config)
            
            print(f"✅ Generated Nginx config: nginx_{domain}.conf")
            print("To apply this configuration on a live server:")
            print(f"1. sudo mv nginx_{domain}.conf {config_path}")
            print(f"2. sudo ln -s {config_path} /etc/nginx/sites-enabled/")
            print("3. sudo systemctl restart nginx")
            print("4. sudo certbot --nginx -d {domain} -d www.{domain}")
        except Exception as e:
            print(f"❌ Failed to write config: {e}")

    # 2. DNS Instructions
    print("\n📡 DNS UPDATE INSTRUCTIONS (ACTION REQUIRED)")
    print("------------------------------------------")
    print(f"1. Log in to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.).")
    print(f"2. Navigate to DNS Settings for '{domain}'.")
    print(f"3. Add an 'A Record':")
    print(f"   - Type: A")
    print(f"   - Name: @")
    print(f"   - Value: [YOUR_VPS_IP_ADDRESS]")
    print(f"   - TTL: Automatic/300")
    print(f"4. Add a 'CNAME Record':")
    print(f"   - Type: CNAME")
    print(f"   - Name: www")
    print(f"   - Value: {domain}")
    print("\n✅ Once DNS propagates (1-24 hours), your sovereign funnel will be live.")

if __name__ == "__main__":
    setup_domain_routing()
