import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, Rocket, Shield } from 'lucide-react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Pricing() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${BACKEND_URL}/products`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch pricing');
        return res.json();
      })
      .then(data => setProducts(data))
      .catch(err => {
        console.error("Failed to load products", err);
        setError("Could not load latest pricing. Please try again.");
      })
      .finally(() => setLoading(false));
  }, []);

  const handleCheckout = async (priceId) => {
    try {
      setLoading(true);
      const res = await fetch(`${BACKEND_URL}/api/checkout/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priceId })
      });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
    } catch (e) {
      console.error(e);
      alert("Secure gateway currently syncing. Please wait.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-20 max-w-7xl mx-auto px-4 font-mono">
      <div className="text-center mb-20">
        <h2 className="text-6xl font-black tracking-tighter uppercase italic mb-4">Pricing <span className="text-primary">Matrix</span></h2>
        <p className="text-gray-500 uppercase tracking-widest text-xs">Invest in the autonomous future.</p>
      </div>
      
      {loading && (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="w-12 h-12 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="text-[10px] text-gray-600 uppercase tracking-[0.3em]">Syncing Catalog...</span>
        </div>
      )}

      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {products.map((p, i) => {
             const price = p.prices && p.prices.length > 0 ? p.prices[0] : null;
             if (!price) return null;

             return (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="bg-black border-2 border-white/5 p-10 rounded-3xl hover:border-primary/30 transition-all flex flex-col relative group"
              >
                {i === 1 && <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-black text-[10px] font-black px-4 py-1 rounded-full uppercase tracking-widest">Most Popular</div>}
                
                <h3 className="text-2xl font-bold mb-2 uppercase text-white">{p.name}</h3>
                <div className="flex items-baseline gap-2 mb-8">
                    <span className="text-5xl font-black text-primary">${price.price}</span>
                    <span className="text-gray-600 text-xs uppercase">/{price.interval}</span>
                </div>
                
                <p className="text-gray-400 text-sm mb-10 leading-relaxed">{p.description}</p>
                
                <div className="space-y-4 mb-12 flex-grow">
                    {[
                        "1000 Specialized Agents",
                        "Voice Barge-In Access",
                        "Real-time Neural Telemetry",
                        "Sovereign Legal Protection"
                    ].map((feat, j) => (
                        <div key={j} className="flex items-center gap-3 text-xs text-gray-500">
                            <Check size={14} className="text-primary" />
                            {feat}
                        </div>
                    ))}
                </div>

                <button 
                  onClick={() => handleCheckout(price.product_id)}
                  className="w-full bg-white text-black py-4 rounded-xl font-black text-xs uppercase tracking-widest hover:bg-primary transition-colors active:scale-95"
                >
                  Acquire License
                </button>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
