import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, Sparkles } from 'lucide-react';

export default function LeadGenPopup() {
  const [isOpen, setIsOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsOpen(true), 15000); // 15 seconds delay
    return () => clearTimeout(timer);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email) {
      setSubmitted(true);
      // In real app, POST to backend/CRM
      setTimeout(() => setIsOpen(false), 3000);
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
          <button onClick={() => setIsOpen(false)} className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors">
            <X size={16} />
          </button>

          {!submitted ? (
            <>
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-primary/20 p-2 rounded-lg text-primary">
                  <Sparkles size={20} />
                </div>
                <div>
                  <h3 className="text-white font-bold text-sm uppercase tracking-wide">Early Access</h3>
                  <p className="text-[10px] text-gray-400">Join the sovereign elite.</p>
                </div>
              </div>
              <form onSubmit={handleSubmit} className="space-y-3">
                <input 
                  type="email" 
                  placeholder="Enter your email..."
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white text-xs focus:outline-none focus:border-primary transition-colors placeholder:text-gray-600"
                  required
                />
                <button type="submit" className="w-full bg-primary text-black font-bold text-xs py-3 rounded-lg hover:bg-primary/90 transition-colors uppercase tracking-widest">
                  Secure Spot
                </button>
              </form>
            </>
          ) : (
            <div className="text-center py-6">
              <div className="text-primary text-4xl mb-2">✓</div>
              <h3 className="text-white font-bold text-sm uppercase">Access Granted</h3>
              <p className="text-[10px] text-gray-500">Check your inbox for directives.</p>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
