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
      
      {loading && <div className="text-center text-gray-500 animate-pulse">Syncing catalog...</div>}
      {error && <div className="text-center text-red-500">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {!loading && products.map((p, i) => {
           const price = p.prices?.[0];
           return (
            <div key={i} className="bg-black border-2 border-white/5 p-10 rounded-3xl hover:border-primary/30 transition-all flex flex-col group">
              <h3 className="text-2xl font-bold mb-2 uppercase text-white">{p.name}</h3>
              <div className="flex items-baseline gap-2 mb-8">
                  <span className="text-5xl font-black text-primary">${price?.price}</span>
                  <span className="text-gray-600 text-xs uppercase">/{price?.interval === 'one_time' ? 'once' : price?.interval}</span>
              </div>
              <p className="text-gray-400 text-sm mb-10">{p.description}</p>
              <button 
                onClick={() => handleCheckout(price?.stripe_price_id || price?.product_id)}
                className="w-full bg-white text-black py-4 rounded-xl font-black text-xs uppercase hover:bg-primary transition-colors"
              >
                Acquire
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
