import { useState, useEffect } from 'react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Pricing() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BACKEND_URL}/products`)
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(err => {
        console.error("Failed to load products", err);
        // Fallback data
        setProducts([
          { name: "Starter Plan", price: 29, interval: "month", description: "Perfect for individuals." },
          { name: "Pro Plan", price: 99, interval: "month", description: "For small teams shipping fast." },
          { name: "Enterprise", price: 499, interval: "month", description: "Full swarm power & support." }
        ]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h2 className="text-3xl font-bold text-center mb-10">Pricing Plans</h2>
      {loading ? (
        <div className="text-center">Loading catalog...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {products.map((p, i) => {
             const price = p.prices ? p.prices[0] : p;
             return (
              <div key={i} className="bg-card-bg p-8 rounded-xl border border-gray-800 hover:border-primary transition-colors flex flex-col">
                <h3 className="text-2xl font-bold mb-2">{p.name}</h3>
                <div className="text-4xl font-bold text-primary mb-4">
                  ${price.price}<span className="text-base text-gray-500 font-normal">/{price.interval || 'mo'}</span>
                </div>
                <p className="text-gray-400 mb-8 flex-grow">{p.description}</p>
                <button className="w-full bg-white text-black py-3 rounded font-bold hover:bg-gray-200">
                  Select Plan
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
