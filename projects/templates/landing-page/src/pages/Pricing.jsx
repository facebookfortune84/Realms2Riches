import { useState, useEffect } from 'react';

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
      
      if (!res.ok) throw new Error("Stripe session creation failed");
      
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      } else {
        alert("Failed to initiate secure checkout.");
      }
    } catch (e) {
      console.error(e);
      alert("Billing gateway currently unavailable. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-10">
      <h2 className="text-4xl font-bold text-center mb-4">Plans & Pricing</h2>
      <p className="text-center text-gray-400 mb-12 max-w-2xl mx-auto">Scale your development with our autonomous agent swarm.</p>
      
      {loading && <div className="text-center">Loading live catalog...</div>}
      {error && <div className="text-center text-red-500">{error}</div>}
      
      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {products.map((p, i) => {
             const price = p.prices && p.prices.length > 0 ? p.prices[0] : null;
             if (!price) return null; // Skip invalid products

             return (
              <div key={i} className="bg-card-bg p-8 rounded-xl border border-gray-800 hover:border-primary transition-all hover:scale-105 flex flex-col">
                <h3 className="text-2xl font-bold mb-2">{p.name}</h3>
                <div className="text-4xl font-bold text-primary mb-4">
                  ${price.price}<span className="text-base text-gray-500 font-normal">/{price.interval || 'mo'}</span>
                </div>
                <p className="text-gray-400 mb-8 flex-grow">{p.description || "Full access to agent swarm features."}</p>
                <button 
                  onClick={() => handleCheckout(price.product_id)} // Using product_id as proxy for price_id key in simplified DB
                  className="w-full bg-white text-black py-3 rounded font-bold hover:bg-gray-200 transition-colors"
                >
                  Choose Plan
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
