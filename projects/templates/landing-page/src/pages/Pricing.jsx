import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, ShoppingCart, Info, ShieldAlert } from 'lucide-react';

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
    
    const fetchCatalog = async () => {
        try {
            const res = await fetch(`${BACKEND_URL}/products`, { headers });
            if (!res.ok) throw new Error('Failed to fetch pricing');
            const data = await res.json();
            if (data && data.length > 0) {
                setProducts(data);
            } else {
                setError("No products available.");
            }
        } catch (err) {
            console.error("Pricing Load Error:", err);
            setError("Catalog Offline.");
        } finally {
            setLoading(false);
        }
    };

    fetchCatalog();
  }, []);

  // Aggressive Theatrical Animations
  const cardVariants = {
    initial: { scale: 1, rotateY: 0, z: 0 },
    hover: { 
      scale: 1.05, 
      rotateY: 5,
      z: 50,
      transition: { duration: 0.4, ease: "easeOut" }
    }
  };

  const imageVariants = {
    initial: { scale: 1, rotate: 0, filter: "brightness(0.7) contrast(1.2)" },
    hover: { 
      scale: 1.15, 
      rotate: [0, -2, 2, -2, 0],
      filter: "brightness(1.1) contrast(1.1)",
      transition: { 
        rotate: { repeat: Infinity, duration: 0.6, ease: "easeInOut" },
        scale: { duration: 0.5, ease: "circOut" },
        filter: { duration: 0.3 }
      }
    }
  };

  return (
    <div className="py-32 max-w-7xl mx-auto px-6 font-mono bg-black min-h-screen perspective-1000">
      <div className="text-center mb-32">
        <motion.div
            initial={{ opacity: 0, scale: 0.5, rotate: -10 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 100 }}
            className="inline-block p-6 bg-primary/5 rounded-[2.5rem] border-2 border-primary/20 mb-8 shadow-[0_0_80px_rgba(0,255,136,0.15)]"
        >
            <img src={`${BACKEND_URL}/assets/branding/forge_logo.png`} alt="Forge" className="h-24 w-auto" />
        </motion.div>
        <motion.h2 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-8xl font-black tracking-[ -0.05em] uppercase italic mb-6 text-white"
        >
          Industrial <span className="text-primary drop-shadow-[0_0_30px_rgba(0,255,136,0.6)]">Matrix</span>
        </motion.h2>
        <p className="text-primary/40 uppercase tracking-[0.8em] text-[11px] font-black animate-pulse">Sovereign Asset Allocation Protocol v5.8.2</p>
      </div>
      
      {loading && (
        <div className="flex flex-col items-center justify-center py-32 gap-8">
            <div className="relative w-20 h-20">
                <div className="absolute inset-0 border-8 border-primary/10 rounded-full" />
                <div className="absolute inset-0 border-8 border-primary rounded-full animate-spin border-t-transparent shadow-[0_0_40px_rgba(0,255,136,0.3)]" />
            </div>
            <div className="text-primary text-xs font-black uppercase tracking-[0.5em] animate-pulse">Decrypting Economics...</div>
        </div>
      )}
      
      {error && (
        <div className="max-w-md mx-auto text-center border-2 border-red-500/30 bg-red-500/5 p-12 rounded-[3rem] shadow-[0_0_50px_rgba(239,68,68,0.1)]">
            <ShieldAlert size={48} className="text-red-500 mx-auto mb-6 animate-bounce" />
            <div className="text-red-500 font-black uppercase tracking-[0.2em]">{error}</div>
            <p className="text-gray-600 text-[10px] mt-4 uppercase">Uplink verification failed. Engage local bypass.</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12 items-stretch">
        {!loading && products.map((p, i) => {
           const priceValue = p.price ?? "0.00";
           const intervalValue = p.interval ?? 'once';
           const checkoutUrl = p.checkout_url;
           
           return (
            <motion.div 
              key={p.id || i} 
              variants={cardVariants}
              initial="initial"
              whileHover="hover"
              className="bg-[#030303] border-2 border-white/5 rounded-[3rem] overflow-hidden hover:border-primary/50 transition-all duration-500 flex flex-col group shadow-[0_30px_100px_rgba(0,0,0,0.8)] h-full relative transform-gpu"
            >
              {/* Product Image Container */}
              <div className="aspect-[16/10] bg-[#080808] border-b-2 border-white/5 relative flex items-center justify-center overflow-hidden p-6">
                <motion.img 
                    variants={imageVariants}
                    src={p.image_url.startsWith('http') ? p.image_url : `${BACKEND_URL}${p.image_url}`} 
                    alt={p.name}
                    className="w-full h-full object-contain relative z-10 drop-shadow-[0_10px_30px_rgba(0,0,0,0.5)]"
                    onError={(e) => e.target.src = "https://www.realmstoriches.xyz/img/bannerimage(3)-600.webp"}
                    loading="eager"
                />
                {/* Visual Depth Gradients */}
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,255,136,0.05),transparent)] opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-60" />
              </div>

              <div className="p-12 flex flex-col flex-grow relative z-10 bg-gradient-to-b from-[#050505] to-black">
                <div className="mb-10">
                    <div className="flex justify-between items-start mb-4">
                        <h3 className="text-2xl font-black text-white tracking-tighter uppercase italic leading-none group-hover:text-primary transition-colors duration-500">{p.name}</h3>
                        <div className="p-2.5 bg-white/5 rounded-xl opacity-0 group-hover:opacity-100 transition-all translate-x-4 group-hover:translate-x-0"><Info size={16} className="text-primary" /></div>
                    </div>
                    <div className="flex items-baseline gap-3">
                        <span className="text-5xl font-black text-primary italic tracking-tighter drop-shadow-[0_0_15px_rgba(0,255,136,0.3)]">${priceValue}</span>
                        <span className="text-gray-700 text-[11px] font-black uppercase tracking-[0.2em]">
                            {intervalValue === 'one_time' || intervalValue === 'once' ? '/SECURE_OWN' : `/${intervalValue.toUpperCase()}`}
                        </span>
                    </div>
                </div>

                <p className="text-gray-500 text-[11px] mb-12 flex-grow leading-relaxed font-bold uppercase tracking-widest opacity-50 group-hover:opacity-100 group-hover:text-gray-300 transition-all duration-500 border-l-2 border-primary/10 pl-6">
                    {p.description}
                </p>

                <div className="space-y-5">
                    <motion.a 
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      href={checkoutUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full bg-primary text-black py-6 rounded-[1.5rem] font-black text-xs uppercase tracking-[0.3em] flex items-center justify-center gap-4 shadow-[0_15px_40px_rgba(0,255,136,0.2)] hover:bg-white hover:shadow-[0_20px_60px_rgba(255,255,255,0.15)] transition-all duration-500"
                    >
                      <ShoppingCart size={18} strokeWidth={3} />
                      INITIATE_ACQUISITION
                    </motion.a>
                    <div className="flex justify-between items-center px-4">
                        <div className="flex gap-1">
                            {[1,2,3].map(bit => <div key={bit} className="w-1 h-1 bg-primary/20 rounded-full animate-pulse" style={{animationDelay: `${bit*0.2}s`}} />)}
                        </div>
                        <span className="text-[9px] text-gray-800 uppercase font-black tracking-[0.4em] italic">NODE_SIG: {p.id.split('_').pop().toUpperCase()}</span>
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
