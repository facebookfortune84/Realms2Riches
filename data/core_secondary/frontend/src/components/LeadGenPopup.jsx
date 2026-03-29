import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, Sparkles, Download } from 'lucide-react';

export default function LeadGenPopup() {
  const [isOpen, setIsOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [guideUrl, setGuideUrl] = useState('');

  // Use the verified ngrok backend as fallback
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://api.realms2riches.com";

  useEffect(() => {
    const isClosed = localStorage.getItem('leadGenClosed');
    if (!isClosed) {
      const timer = setTimeout(() => setIsOpen(true), 15000); // 15 seconds delay
      return () => clearTimeout(timer);
    }
  }, []);

  const handleClose = () => {
    setIsOpen(false);
    localStorage.setItem('leadGenClosed', 'true');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (email) {
      try {
        const response = await fetch(`${BACKEND_URL}/api/leads`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, source: 'popup' })
        });
        const data = await response.json();
        console.log("LEAD CAPTURE RESPONSE:", data);
        if (data.guide_url) {
            console.log("SETTING GUIDE URL:", data.guide_url);
            setGuideUrl(data.guide_url);
        }
        setSubmitted(true);
        localStorage.setItem('leadGenClosed', 'true');
      } catch (err) {
        console.error("Lead submission failed", err);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0, y: 100 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 100 }}
        className="fixed bottom-6 right-6 z-50 w-full max-w-sm"
      >
        <div className="bg-black border border-primary/30 rounded-2xl p-6 shadow-[0_0_50px_rgba(0,255,136,0.2)] relative overflow-hidden">
          <div className="absolute inset-0 bg-primary/5 pointer-events-none" />
          <button onClick={handleClose} className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors">
            <X size={16} />
          </button>

          {!submitted ? (
            <>
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-primary/20 p-2 rounded-lg text-primary shadow-[0_0_15px_rgba(0,255,136,0.4)]">
                  <Sparkles size={20} />
                </div>
                <div>
                  <h3 className="text-white font-black text-sm uppercase tracking-tighter italic">Sovereign Strategy</h3>
                  <p className="text-[10px] text-primary font-bold tracking-widest uppercase">Guide Access</p>
                </div>
              </div>
              <p className="text-[11px] text-gray-400 mb-4 leading-relaxed">Secure the <span className="text-white font-bold underline">Sovereign Strategy Guide</span> and join the autonomous elite.</p>
              <form onSubmit={handleSubmit} className="space-y-3">
                <input 
                  type="email" 
                  placeholder="Enter your email..."
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-xs focus:outline-none focus:border-primary transition-all placeholder:text-gray-600 focus:ring-1 focus:ring-primary/20"
                  required
                />
                <button type="submit" className="w-full bg-primary text-black font-black text-[10px] py-4 rounded-xl hover:bg-white transition-all uppercase tracking-[0.2em] shadow-[0_5px_20px_rgba(0,255,136,0.2)]">
                  Initialize Transmission
                </button>
              </form>
            </>
          ) : (
            <div className="text-center py-6 flex flex-col items-center">
              <motion.div initial={{ scale: 0.5 }} animate={{ scale: 1 }} className="text-primary text-5xl mb-4">⚡</motion.div>
              <h3 className="text-white font-black text-sm uppercase tracking-tighter italic">Transmission Sent</h3>
              <p className="text-[10px] text-gray-500 mt-2 mb-6 uppercase tracking-widest">Guide arriving in sub-60s.</p>
              
              {guideUrl && (
                <motion.a 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  href={guideUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 bg-white text-black font-black text-[10px] py-3 px-6 rounded-xl hover:bg-primary transition-all uppercase tracking-widest shadow-[0_5px_15px_rgba(255,255,255,0.1)]"
                >
                  <Download size={14} />
                  Download Guide Now
                </motion.a>
              )}
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

