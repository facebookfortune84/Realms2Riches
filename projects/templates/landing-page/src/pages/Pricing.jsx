import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, ShoppingCart, Info } from 'lucide-react';

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

  // Theatrical Wobble Animation
  const wobbleVariant = {
    initial: { scale: 1, rotate: 0 },
    hover: { 
      scale: 1.05, 
      rotate: [0, -1, 1, -1, 0],
      transition: { 
        rotate: { repeat: Infinity, duration: 0.5 },
        scale: { duration: 0.3 }
      }
    }
  };

  return (
    <div className="py-24 max-w-7xl mx-auto px-4 font-mono bg-black">
      <div className="text-center mb-24">
        <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-block p-4 bg-primary/10 rounded-3xl border border-primary/20 mb-6 shadow-[0_0_50px_rgba(0,255,136,0.1)]"
        >
            <img src={`${BACKEND_URL}/assets/branding/forge_logo.png`} alt="Forge" className="h-20 w-auto" />
        </motion.div>
        <motion.h2 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-7xl font-black tracking-tighter uppercase italic mb-4 text-white"
        >
          Industrial <span className="text-primary drop-shadow-[0_0_20px_rgba(0,255,136,0.4)]">Matrix</span>
        </motion.h2>
        <p className="text-gray-500 uppercase tracking-[0.5em] text-[10px] font-bold">Autonomous Provisioning Channels</p>
      </div>
      
      {loading && (
        <div className="flex flex-col items-center justify-center py-24 gap-6">
            <div className="w-16 h-16 border-4 border-primary/10 border-t-primary rounded-full animate-spin shadow-[0_0_30px_rgba(0,255,136,0.2)]" />
            <div className="text-primary text-[10px] font-black uppercase tracking-[0.4em] animate-pulse">Syncing Swarm Economics...</div>
        </div>
      )}
      
      {error && <div className="text-center text-red-500 bg-red-500/5 p-8 rounded-3xl border-2 border-red-500/20 font-black uppercase tracking-widest">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10 items-stretch">
        {!loading && products.map((p, i) => {
           const priceValue = p.price ?? "Contact";
           const intervalValue = p.interval ?? 'once';
           const checkoutUrl = p.checkout_url;
           
           return (
            <motion.div 
              key={p.id || i} 
              initial="initial"
              whileHover="hover"
              variants={wobbleVariant}
              className="bg-[#050505] border-2 border-white/5 rounded-[2.5rem] overflow-hidden hover:border-primary/40 transition-colors flex flex-col group shadow-[0_20px_50px_rgba(0,0,0,0.5)] h-full relative"
            >
              {/* Product Image Container */}
              <div className="aspect-video bg-[#111] border-b-2 border-white/5 relative flex items-center justify-center overflow-hidden">
                <img 
                    src={p.image_url.startsWith('http') ? p.image_url : `${BACKEND_URL}${p.image_url}`} 
                    alt={p.name}
                    className="w-full h-full object-contain p-4 group-hover:scale-110 transition-transform duration-700 ease-out"
                    onError={(e) => e.target.src = "https://www.realmstoriches.xyz/img/bannerimage(3)-600.webp"}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-40" />
              </div>

              <div className="p-10 flex flex-col flex-grow relative z-10">
                <div className="mb-8">
                    <div className="flex justify-between items-start mb-2">
                        <h3 className="text-xl font-black text-white tracking-tighter uppercase italic">{p.name}</h3>
                        <div className="p-2 bg-white/5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"><Info size={14} className="text-primary" /></div>
                    </div>
                    <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-black text-primary italic tracking-tighter">${priceValue}</span>
                        <span className="text-gray-600 text-[10px] font-black uppercase tracking-widest">
                            {intervalValue === 'one_time' || intervalValue === 'once' ? '/FIXED' : `/${intervalValue.toUpperCase()}`}
                        </span>
                    </div>
                </div>

                <p className="text-gray-400 text-xs mb-10 flex-grow leading-relaxed font-medium uppercase tracking-tight opacity-70 group-hover:opacity-100 transition-opacity">
                    {p.description}
                </p>

                <div className="space-y-4">
                    <a 
                      href={checkoutUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full bg-primary text-black py-5 rounded-2xl font-black text-[11px] uppercase tracking-[0.2em] hover:bg-white transition-all text-center flex items-center justify-center gap-3 shadow-[0_10px_30px_rgba(0,255,136,0.15)] group-hover:shadow-[0_15px_40px_rgba(0,255,136,0.25)]"
                    >
                      <ShoppingCart size={16} strokeWidth={3} />
                      Initialize Acquisition
                    </a>
                    <div className="flex justify-between items-center px-2">
                        <span className="text-[8px] text-gray-700 uppercase font-black tracking-[0.3em]">SECURE_LINK_ENCRYPTED</span>
                        <span className="text-[8px] text-primary font-black uppercase">{p.id.split('_').pop()}</span>
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
