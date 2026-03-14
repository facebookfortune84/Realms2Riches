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
            setError("No products available.");
        }
      })
      .catch(err => {
        console.error("Pricing Load Error:", err);
        setError("Catalog Offline.");
      })
      .finally(() => setLoading(false));
  }, []);

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
           const priceValue = p.price ?? "Contact";
           const intervalValue = p.interval ?? 'once';
           const checkoutUrl = p.checkout_url || "https://buy.stripe.com/fZu9ATdSzcVM3459ezgYU06?locale=en";
           
           return (
            <motion.div 
              key={p.id || i} 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              className="bg-[#0a0a0a] border border-white/10 rounded-2xl overflow-hidden hover:border-primary/50 transition-all flex flex-col group shadow-[0_0_30px_rgba(0,0,0,0.8)] hover:shadow-[0_0_40px_rgba(0,255,136,0.1)] h-full relative"
            >
              {/* Product Image / Header */}
              <div className="h-56 bg-[#111] border-b border-white/5 relative flex items-center justify-center overflow-hidden transition-all duration-700">
                <img 
                    src={p.image_url.startsWith('http') ? p.image_url : `${BACKEND_URL}${p.image_url}`} 
                    alt={p.name}
                    className="w-full h-full object-cover opacity-80 group-hover:opacity-100 group-hover:scale-110 transition-all duration-700"
                    onError={(e) => e.target.src = "https://www.realmstoriches.xyz/img/bannerimage(3)-600.webp"}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] to-transparent opacity-60" />
                <span className="absolute bottom-4 left-6 text-primary/90 text-4xl font-black italic uppercase tracking-tighter z-10 drop-shadow-lg">
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
                        Verified: {p.id}
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
