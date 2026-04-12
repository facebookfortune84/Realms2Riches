import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Download, Zap, ShieldCheck, Link as LinkIcon } from 'lucide-react';

import { getApiBase } from '../lib/apiBase';

// Placeholder for dynamically fetched offers
// In a real app, this would be fetched from the backend API.
// For now, we'll use static data structure, but ensure the fetch logic is there.
const DUMMY_OFFERS = [
  { id: 'ht_001', name: 'Authority Hacker Pro', creator: 'Gael Breton & Mark Webster', niche: 'SEO & Authority Sites', price: '997.00', currency: 'USD', interval: 'one_time', description: 'The ultimate course for building profitable authority websites.', link: '/affiliates/auth_hacker', unique_code: 'AHPRO-R2R', image_url: '/assets/affiliates/authority_hacker_pro.png' },
  { id: 'ht_002', name: 'SaaS Academy', creator: 'Dan Martell', niche: 'SaaS Growth', price: '4999.00', currency: 'USD', interval: 'one_time', description: 'Comprehensive program for scaling SaaS businesses.', link: '/affiliates/saas_academy', unique_code: 'SAASMAX-R2R', image_url: '/assets/affiliates/saas_academy.png' },
  { id: 'ht_003', name: 'Fintech Innovators Mastermind', creator: 'AI Finance Group', niche: 'Fintech & AI', price: '2500.00', currency: 'USD', interval: 'monthly', description: 'Exclusive mastermind for fintech leaders leveraging AI.', link: '/affiliates/fintech_ai', unique_code: 'FINTECHAI-R2R', image_url: '/assets/affiliates/fintech_ai.png'}
];

export default function HighTicketHub() {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOffers = async () => {
      try {
        const response = await fetch(`${getApiBase()}/api/affiliates/high-ticket`);
        if (response.ok) {
          const data = await response.json();
          // Ensure offers have unique codes for tracking
          const offersWithUniqueCodes = data.map(offer => ({
            ...offer,
            unique_code: offer.unique_code || `AFF_${offer.id}_R2R` // Generate if missing
          }));
          setOffers(offersWithUniqueCodes);
        } else {
          console.error("Failed to fetch offers:", response.statusText);
          setOffers(DUMMY_OFFERS); // Fallback to dummy offers if API fails
        }
      } catch (error) {
        console.error("Error fetching high-ticket offers:", error);
        setOffers(DUMMY_OFFERS); // Fallback to dummy offers on network error
      } finally {
        setLoading(false);
      }
    };
    fetchOffers();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white font-mono p-10">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-black text-primary italic tracking-tighter uppercase">High-Ticket Affiliate Nexus</h1>
          <p className="text-gray-500 mt-4 text-lg">Leveraging premium partnerships for exponential revenue growth.</p>
        </div>

        {loading && (
          <div className="text-center py-20">
            <div className="w-20 h-20 border-4 border-primary/20 border-t-primary rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-500 text-sm">Loading premium offers...</p>
          </div>
        )}

        {!loading && offers.length === 0 && (
          <div className="text-center py-20">
            <p className="text-gray-500 text-lg">No premium offers available at this time. Please check back later.</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
          {offers.map(offer => (
            <motion.div 
              key={offer.id}
              whileHover={{ scale: 1.02, y: -5 }}
              transition={{ type: "spring", stiffness: 300, damping: 15 }}
              className="bg-[#0D0D0D] border border-white/5 rounded-[2rem] p-8 relative overflow-hidden shadow-[0_0_50px_rgba(0,255,136,0.1)]"
            >
              {offer.image_url && (
                 <img src={offer.image_url} alt={offer.name} className="absolute inset-0 w-full h-full object-cover opacity-15 rounded-[2rem]" />
              )}
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-30 rounded-[2rem]" />
              
              <div className="relative z-10 flex flex-col justify-between h-full">
                <div>
                    <h3 className="text-2xl font-black text-white mb-3 uppercase tracking-tight">{offer.name}</h3>
                    <p className="text-xs text-gray-400 mb-6">{offer.niche}</p>
                    
                    <div className="text-sm text-gray-300 space-y-2 mb-6">
                      <p><strong>Creator:</strong> {offer.creator}</p>
                      <p><strong>Price Point:</strong> {offer.price} {offer.currency} / {offer.interval.toUpperCase()}</p>
                    </div>
                    
                    <p className="text-gray-300 text-xs leading-relaxed mb-8">{offer.description}</p>
                </div>

                <a 
                  href={`${offer.link}?ref=${offer.unique_code}`} // Append unique code for tracking
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-block bg-primary text-black py-4 px-8 rounded-xl font-black text-sm uppercase tracking-[0.2em] hover:bg-white hover:scale-[1.02] transition-all shadow-[0_10px_30px_rgba(0,255,136,0.2)] flex items-center justify-center"
                >
                  Explore Offer <ArrowRight size={16} className="ml-2" />
                </a>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

