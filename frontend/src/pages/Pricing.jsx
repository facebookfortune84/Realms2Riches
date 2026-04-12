import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, Zap, ShoppingCart, Info, ShieldAlert, Filter } from 'lucide-react';
import { trackEvent } from '../lib/analytics';
import { CMS_COPY } from '../lib/cms';
import { Testimonials, TrustBadges } from '../components/TrustElements';
import { getApiBase } from '../lib/apiBase';

const TABS = [
  { id: 'all', label: 'ALL_MATRIX' },
  { id: 'entry', label: 'ENTRY_NODES' },
  { id: 'foundation', label: 'FOUNDATION' },
  { id: 'growth', label: 'GROWTH' },
  { id: 'scale', label: 'SCALE' },
  { id: 'enterprise', label: 'ENTERPRISE' }
];

export default function Pricing() {
  const [allProducts, setAllProducts] = useState([]);
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    trackEvent('page_view', { page: 'pricing' });
    
    const headers = {
        'X-License-Key': import.meta.env.VITE_SOVEREIGN_LICENSE_KEY || 'mock_dev_key',
    };
    
    const fetchCatalog = async () => {
        try {
            const res = await fetch(`${getApiBase()}/products`, { headers });
            if (!res.ok) throw new Error('Failed to fetch pricing');
            const data = await res.json();
            if (data && data.length > 0) {
                setAllProducts(data);
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

  const filteredProducts = useMemo(() => {
    if (activeTab === 'all') return allProducts;
    return allProducts.filter(p => p.funnel_stage === activeTab);
  }, [allProducts, activeTab]);

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    trackEvent('tab_switch', { tab: tabId });
  };

  const handleAcquisition = (product) => {
    trackEvent('start_checkout', { product_id: product.id, price: product.price });
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.05 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
    exit: { opacity: 0, scale: 0.95, transition: { duration: 0.2 } }
  };

  return (
    <div className="py-32 max-w-7xl mx-auto px-6 font-mono bg-black min-h-screen">
      <div className="text-center mb-24">
        <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-block p-6 bg-primary/5 rounded-[2.5rem] border-2 border-primary/20 mb-8"
        >
            <img src={`${BACKEND_URL}/assets/branding/forge_logo.png`} alt="Forge" className="h-24 w-auto" />
        </motion.div>
        <motion.h2 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-7xl md:text-8xl font-black tracking-tighter uppercase italic mb-6 text-white"
        >
          {CMS_COPY.pricing.title} <span className="text-primary">Matrix</span>
        </motion.h2>
        <p className="text-primary/40 uppercase tracking-[0.8em] text-[11px] font-black mb-8">{CMS_COPY.pricing.tagline}</p>
        <p className="max-w-2xl mx-auto text-gray-500 text-sm leading-relaxed uppercase font-bold tracking-widest opacity-80">
          {CMS_COPY.pricing.description}
        </p>
      </div>

      <TrustBadges />

      {/* Tabs */}
      <div className="flex flex-wrap justify-center gap-2 mb-20" role="tablist" aria-label="Offer categories">
        {TABS.map(tab => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            onClick={() => handleTabChange(tab.id)}
            className={`px-6 py-3 rounded-xl text-[10px] font-black tracking-widest uppercase transition-all duration-300 border-2 ${
              activeTab === tab.id 
                ? 'bg-primary text-black border-primary' 
                : 'bg-white/5 text-gray-500 border-white/5 hover:border-white/10'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      
      {loading && (
        <div className="flex flex-col items-center justify-center py-32 gap-8" aria-live="polite">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            <div className="text-primary text-[10px] font-black uppercase tracking-widest animate-pulse">Decrypting Economics...</div>
        </div>
      )}
      
      {error && (
        <div className="max-w-md mx-auto text-center border-2 border-red-500/30 bg-red-500/5 p-12 rounded-[3rem]" role="alert">
            <ShieldAlert size={48} className="text-red-500 mx-auto mb-6" />
            <div className="text-red-500 font-black uppercase tracking-widest">{error}</div>
            <p className="text-gray-600 text-[10px] mt-4 uppercase tracking-widest text-center">Uplink verification failed. Engage local bypass.</p>
        </div>
      )}

      <motion.div 
        layout
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
      >
        <AnimatePresence mode='popLayout'>
          {filteredProducts.map((p) => {
             const priceValue = p.price ?? "0.00";
             const intervalValue = p.interval ?? 'once';
             
             return (
              <motion.div 
                layout
                key={p.id} 
                variants={itemVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                whileHover={{ scale: 1.02 }}
                className="bg-[#030303] border-2 border-white/5 rounded-[2.5rem] overflow-hidden hover:border-primary/30 transition-all duration-500 flex flex-col group relative"
              >
                {p.primary_entry_offer && (
                  <div className="absolute top-6 right-6 z-20 bg-primary text-black px-3 py-1 rounded-full text-[8px] font-black tracking-widest uppercase flex items-center gap-1 shadow-[0_0_15px_rgba(0,255,136,0.4)]">
                    <Zap size={8} fill="currentColor" /> RECOMMENDED
                  </div>
                )}

                <div className="aspect-[16/10] bg-[#080808] border-b-2 border-white/5 flex items-center justify-center p-6">
                  <img 
                      src={p.image_url.startsWith('http') ? p.image_url : `${BACKEND_URL}${p.image_url}`} 
                      alt={p.name}
                      className="w-full h-full object-contain grayscale group-hover:grayscale-0 transition-all duration-700"
                      onError={(e) => e.target.src = "https://www.realmstoriches.xyz/img/bannerimage(3)-600.webp"}
                  />
                </div>

                <div className="p-10 flex flex-col flex-grow">
                  <div className="mb-8">
                      <h3 className="text-xl font-black text-white tracking-tighter uppercase italic mb-4">{p.name}</h3>
                      <div className="flex items-baseline gap-2">
                          <span className="text-4xl font-black text-primary italic">${priceValue}</span>
                          <span className="text-gray-700 text-[10px] font-black uppercase tracking-widest">
                              {intervalValue === 'one_time' || intervalValue === 'once' ? '/SECURE' : `/${intervalValue.toUpperCase()}`}
                          </span>
                      </div>
                  </div>

                  <p className="text-gray-500 text-[10px] mb-10 flex-grow leading-relaxed font-bold uppercase tracking-widest opacity-60 group-hover:opacity-100 transition-all">
                      {p.description}
                  </p>

                  <div className="mt-auto pt-6 border-t border-white/5">
                      <motion.a 
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        href={p.checkout_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={() => handleAcquisition(p)}
                        aria-label={`Acquire ${p.name} for ${priceValue} dollars`}
                        className="w-full bg-primary text-black py-5 rounded-2xl font-black text-[10px] uppercase tracking-widest flex items-center justify-center gap-3 hover:bg-white transition-all shadow-xl shadow-primary/10"
                      >
                        <ShoppingCart size={14} strokeWidth={3} />
                        INITIATE_ACQUISITION
                      </motion.a>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </motion.div>

      <Testimonials />

      <div className="mt-32 p-12 border-2 border-dashed border-white/10 rounded-[3rem] text-center bg-white/[0.01]">
        <h3 className="text-2xl font-black text-white uppercase italic tracking-tighter mb-4">{CMS_COPY.pricing.risk_reversal}</h3>
        <p className="text-gray-600 text-[9px] font-bold uppercase tracking-[0.3em] max-w-xl mx-auto leading-relaxed">
          All digital assets are cryptographically signed and delivered instantly upon confirmation of industrial transaction.
        </p>
      </div>
    </div>
  );
}

