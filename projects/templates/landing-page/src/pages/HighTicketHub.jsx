import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Rocket, Target, DollarSign, ExternalLink, ShieldCheck, Briefcase } from 'lucide-react';

export default function HighTicketHub() {
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPartners = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/api/affiliates/high-ticket`);
        const data = await res.json();
        setPartners(data);
      } catch (e) {
        console.error("Failed to load partners", e);
      } finally {
        setLoading(false);
      }
    };
    fetchPartners();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-16 text-center">
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-5xl font-black tracking-tighter mb-4"
          >
            HIGH-TICKET <span className="text-primary">AFFILIATE HUB</span>
          </motion.h1>
          <p className="text-gray-400 text-xl max-w-2xl mx-auto">
            Strategic partnerships with world-class creators. Optimized for high-volume sales and maximum commission yield.
          </p>
        </header>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {partners.map((p, i) => (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.05 }}
                className="bg-gray-900/50 border border-gray-800 rounded-3xl p-8 hover:border-primary/50 transition-all group"
              >
                <div className="flex justify-between items-start mb-6">
                  <div className="p-3 bg-primary/10 rounded-2xl">
                    <Briefcase className="w-6 h-6 text-primary" />
                  </div>
                  <div className="text-[10px] font-mono text-primary bg-primary/5 px-2 py-1 rounded border border-primary/20 uppercase">
                    {p.niche}
                  </div>
                </div>

                <h3 className="text-2xl font-bold mb-2 group-hover:text-primary transition-colors">{p.name}</h3>
                <p className="text-gray-500 text-sm mb-4">by {p.creator}</p>
                <p className="text-gray-400 text-sm mb-6 leading-relaxed">
                  {p.description}
                </p>

                <div className="space-y-3 mb-8">
                  <div className="flex items-center gap-2 text-sm">
                    <Target className="w-4 h-4 text-gray-600" />
                    <span className="text-gray-500">Ticket Price:</span>
                    <span className="text-white font-medium">{p.price}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <DollarSign className="w-4 h-4 text-primary" />
                    <span className="text-gray-500">Commission:</span>
                    <span className="text-primary font-bold">{p.commission}</span>
                  </div>
                </div>

                <a 
                  href={p.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full py-4 bg-white text-black font-black rounded-xl hover:bg-primary transition-colors"
                >
                  ACQUIRE AFFILIATE LINK <ExternalLink className="w-4 h-4" />
                </a>
              </motion.div>
            ))}
          </div>
        )}

        <div className="mt-20 p-12 bg-primary/5 border border-primary/20 rounded-3xl text-center">
          <ShieldCheck className="w-12 h-12 text-primary mx-auto mb-6" />
          <h2 className="text-3xl font-bold mb-4">SWARM INTEGRATION</h2>
          <p className="text-gray-400 max-w-xl mx-auto mb-8 italic">
            "The High-Ticket Hub is now indexed in the Sovereign Memory. Agents are authorized to leverage these partnerships during autonomous outreach sequences to maximize TMR."
          </p>
          <div className="flex justify-center gap-4">
            <div className="px-6 py-2 bg-black border border-gray-800 rounded-full text-xs font-mono">ENCRYPTION: ACTIVE</div>
            <div className="px-6 py-2 bg-black border border-gray-800 rounded-full text-xs font-mono">SYNC: 100%</div>
          </div>
        </div>
      </div>
    </div>
  );
}
