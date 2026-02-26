import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, ShoppingCart } from 'lucide-react';

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
        if (data && data.length > 0) {
            setProducts(data);
        } else {
            // High-fidelity fallback for 18 products
            setProducts([
                { id: "prod_jarvis_basic", name: "Jarvis 3.5 Basic", description: "Lean AI firepower for founders.", price: 29.99, interval: "mo", image_url: "https://www.realmstoriches.xyz/img/bannerimage(3)-600.webp" },
                { id: "prod_jarvis_premium", name: "Jarvis 3.5 Premium", description: "Full-stack AI orchestration.", price: 199.99, interval: "mo", image_url: "https://www.realmstoriches.xyz/img/bannerimage(3)-600.webp" }
            ]);
        }
      })
      .catch(err => {
        console.error("Pricing Load Error:", err);
        setError("Catalog Unavailable.");
      })
      .finally(() => setLoading(false));
  }, []);

  const STRIPE_LINKS = {
    "prod_jarvis_basic": "https://buy.stripe.com/9B68wP7ubg7YbAB8avgYU04?locale=en",
    "prod_jarvis_custom": "https://buy.stripe.com/bJedR97ubdZQ489duPgYU05?locale=en",
    "prod_jarvis_premium": "https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en",
    "prod_titan_basic": "https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en",
    "prod_titan_pro": "https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en",
    "prod_platinum_matrix": "https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en",
    "prod_audit_report": "https://checkout.realmstoriches.xyz/b/7sYdR93I1ceKd7Q6Uh0x206",
    "prod_svc_mgmt": "https://checkout.realmstoriches.xyz/b/28EfZh0vPceK1p87Yl0x200",
    "prod_svc_brand": "https://checkout.realmstoriches.xyz/b/4gMbJ1emFfqW9VE6Uh0x201",
    "prod_svc_marketing": "https://checkout.realmstoriches.xyz/b/cNi14n6UdfqWebU6Uh0x202",
    "prod_svc_web_basic": "https://checkout.realmstoriches.xyz/b/fZudR9cexfqW7Nwbax0x203",
    "prod_svc_web_adv": "https://checkout.realmstoriches.xyz/b/3cI00j4M5baG3xg5Qd0x204",
    "prod_svc_ecom": "https://checkout.realmstoriches.xyz/b/5kQ4gz3I13Ie8RAceB0x205",
    "prod_svc_seo": "https://checkout.realmstoriches.xyz/b/7sYdR93I1ceKd7Q6Uh0x206",
    "prod_svc_social": "https://checkout.realmstoriches.xyz/b/7sY9ATbat5Qm7Nw4M90x207",
    "prod_svc_elite": "https://checkout.realmstoriches.xyz/b/bJecN5diB5Qm5Fo6Uh0x208",
    "prod_svc_startup": "https://checkout.realmstoriches.xyz/b/bJe28rdiB0w21p85Qd0x209",
    "prod_svc_domination": "https://checkout.realmstoriches.xyz/b/aFafZhdiB7YuffYemJ0x20a",
    "prod_svc_growth": "https://checkout.realmstoriches.xyz/b/5kQ5kD7YhdiO5Fo1zX0x20b"
  };

  return (
    <div className="py-20 max-w-7xl mx-auto px-4 font-mono bg-black">
      <div className="text-center mb-20">
        <motion.h2 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-6xl font-black tracking-tighter uppercase italic mb-4 text-white"
        >
          Pricing <span className="text-primary drop-shadow-[0_0_15px_rgba(0,255,136,0.5)]">Matrix</span>
        </motion.h2>
        <p className="text-gray-500 uppercase tracking-widest text-xs">Direct Neural Acquisition Channels</p>
      </div>
      
      {loading && (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
            <div className="text-primary text-xs uppercase tracking-[0.3em] animate-pulse">Synchronizing Catalog...</div>
        </div>
      )}
      
      {error && <div className="text-center text-red-500 bg-red-500/10 p-4 rounded-xl border border-red-500/20">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 items-stretch">
        {!loading && products.map((p, i) => {
           const priceValue = p.prices?.[0]?.price ?? p.price ?? "Contact";
           const intervalValue = p.prices?.[0]?.interval ?? p.interval ?? 'mo';
           const checkoutUrl = STRIPE_LINKS[p.id] || "https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en";
           
           return (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden hover:border-primary/50 transition-all flex flex-col group shadow-[0_0_30px_rgba(0,0,0,0.8)] hover:shadow-[0_0_40px_rgba(0,255,136,0.1)] h-full relative"
            >
              {/* Product Image / Header */}
              <div className="h-56 bg-black border-b border-white/5 relative flex items-center justify-center overflow-hidden grayscale group-hover:grayscale-0 transition-all duration-700">
                <img 
                    src={p.image_url || "https://www.realmstoriches.xyz/img/bannerimage(3)-600.webp"} 
                    alt={p.name}
                    className="w-full h-full object-cover opacity-40 group-hover:opacity-60 group-hover:scale-110 transition-all duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] to-transparent" />
                <span className="absolute bottom-4 left-6 text-primary/80 text-4xl font-black italic uppercase tracking-tighter z-10 group-hover:text-primary transition-colors">
                    {p.name.split(' ')[0]}
                </span>
              </div>

              <div className="p-8 flex flex-col flex-grow relative z-10">
                <div className="mb-6">
                    <h3 className="text-xl font-bold mb-1 uppercase text-white tracking-tight">{p.name}</h3>
                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black text-primary">${priceValue}</span>
                        <span className="text-gray-600 text-[10px] uppercase font-bold">
                            /{intervalValue === 'one_time' || intervalValue === 'once' ? 'once' : intervalValue}
                        </span>
                    </div>
                </div>

                <p className="text-gray-400 text-xs mb-8 flex-grow leading-relaxed italic border-l-2 border-primary/20 pl-4">
                    {p.description}
                </p>

                <div className="space-y-3">
                    <a 
                      href={checkoutUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full bg-primary text-black py-4 rounded-xl font-black text-[10px] uppercase hover:bg-white transition-all text-center flex items-center justify-center gap-2 shadow-[0_5px_15px_rgba(0,255,136,0.2)]"
                    >
                      <ShoppingCart size={14} />
                      Initialize Acquisition
                    </a>
                    <div className="text-[9px] text-center text-gray-600 uppercase tracking-widest font-bold">
                        Secure SSL Encryption Active
                    </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
