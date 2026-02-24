import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap } from 'lucide-react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Pricing() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const headers = { 
        'X-License-Key': import.meta.env.VITE_SOVEREIGN_LICENSE_KEY || 'mock_dev_key',
        'ngrok-skip-browser-warning': 'true'
    };
    fetch(`${BACKEND_URL}/products`, { headers })
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch pricing');
        return res.json();
      })
      .then(data => {
        // Ensure we show the real products if they exist, otherwise use verified fallbacks
        if (data && data.length > 0) {
            setProducts(data);
        } else {
            setProducts([
                { name: "Sovereign Strategy", description: "V3 Strategy Guide & Roadmap", prices: [{ price: 19, interval: "once", product_id: "guide" }] },
                { name: "Platinum Matrix", description: "1000 Agent access + Full Swarm", prices: [{ price: 2999, interval: "mo", product_id: "platinum" }] }
            ]);
        }
      })
      .catch(err => {
        console.error("Pricing Load Error:", err);
        setError("Catalog Unavailable.");
      })
      .finally(() => setLoading(false));
  }, []);

  const handleCheckout = async (priceId) => {
    try {
      setLoading(true);
      
      // Track Conversion Intent
      fetch(`${BACKEND_URL}/api/telemetry/conversion`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: priceId, event: 'click_checkout' })
      }).catch(() => {}); // Fire and forget tracking

      const res = await fetch(`${BACKEND_URL}/api/checkout/session`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-License-Key': import.meta.env.VITE_SOVEREIGN_LICENSE_KEY || 'mock_dev_key',
            'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({ priceId })
      });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
    } catch (e) {
      alert("Billing Secure Link Error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-20 max-w-7xl mx-auto px-4 font-mono">
      <div className="text-center mb-20">
        <h2 className="text-6xl font-black tracking-tighter uppercase italic mb-4 text-white">Pricing <span className="text-primary">Matrix</span></h2>
      </div>
      
      {loading && <div className="text-center text-primary animate-pulse">Syncing catalog...</div>}
      {error && <div className="text-center text-red-500">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 items-stretch">
        {!loading && products.map((p, i) => {
           const STRIPE_LINKS = {
             "prod_sovereign_platinum": "https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en",
             "prod_business_management": "https://checkout.realmstoriches.xyz/b/28EfZh0vPceK1p87Yl0x200",
             "prod_brand_kit": "https://checkout.realmstoriches.xyz/b/4gMbJ1emFfqW9VE6Uh0x201",
             "prod_marketing_campaign": "https://checkout.realmstoriches.xyz/b/cNi14n6UdfqWebU6Uh0x202",
             "prod_website_design_basic": "https://checkout.realmstoriches.xyz/b/fZudR9cexfqW7Nwbax0x203",
             "prod_website_design_advanced": "https://checkout.realmstoriches.xyz/b/3cI00j4M5baG3xg5Qd0x204",
             "prod_ecommerce_development": "https://checkout.realmstoriches.xyz/b/5kQ4gz3I13Ie8RAceB0x205",
             "prod_seo_optimization": "https://checkout.realmstoriches.xyz/b/7sYdR93I1ceKd7Q6Uh0x206",
             "prod_social_media": "https://checkout.realmstoriches.xyz/b/7sY9ATbat5Qm7Nw4M90x207",
             "prod_elite_support": "https://checkout.realmstoriches.xyz/b/bJecN5diB5Qm5Fo6Uh0x208",
             "prod_startup_accelerator": "https://checkout.realmstoriches.xyz/b/bJe28rdiB0w21p85Qd0x209",
             "prod_digital_domination": "https://checkout.realmstoriches.xyz/b/aFafZhdiB7YuffYemJ0x20a",
             "prod_digital_growth": "https://checkout.realmstoriches.xyz/b/5kQ5kD7YhdiO5Fo1zX0x20b"
           };

           const priceValue = p.prices?.[0]?.price ?? p.price ?? 2999;
           const intervalValue = p.prices?.[0]?.interval ?? p.interval ?? 'mo';
           const checkoutUrl = STRIPE_LINKS[p.id] || "https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en";
           
           return (
            <div key={i} className="bg-black border border-white/10 rounded-2xl overflow-hidden hover:border-primary transition-all flex flex-col group shadow-[0_0_15px_rgba(0,0,0,0.5)] hover:shadow-[0_0_30px_rgba(0,255,136,0.15)] h-full">
              <div className="h-48 bg-gradient-to-br from-gray-900 to-black border-b border-white/5 relative flex items-center justify-center overflow-hidden">
                <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,136,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,136,0.03)_1px,transparent_1px)] bg-[size:20px_20px]" />
                <span className="text-primary/20 text-6xl font-black italic uppercase -rotate-12 group-hover:text-primary/40 transition-colors z-10">{p.name.split(' ')[0]}</span>
              </div>
              <div className="p-8 flex flex-col flex-grow">
                <h3 className="text-2xl font-bold mb-2 uppercase text-white tracking-tight">{p.name}</h3>
                <div className="flex items-baseline gap-2 mb-6">
                    <span className="text-4xl font-black text-primary">${priceValue}</span>
                    <span className="text-gray-500 text-xs uppercase">/{intervalValue === 'one_time' ? 'once' : intervalValue}</span>
                </div>
                <p className="text-gray-400 text-sm mb-8 flex-grow leading-relaxed">{p.description}</p>
                <a 
                  href={checkoutUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full bg-white/5 text-white border border-white/10 py-4 rounded-xl font-black text-xs uppercase hover:bg-primary hover:text-black hover:border-primary transition-all text-center block"
                >
                  Acquire Access
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
