import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, Rocket, ShieldCheck, Users, ArrowRight, Check } from 'lucide-react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function CompanyWizard({ isOpen, onClose }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState({
    name: '',
    industry: 'Software',
    scale: '100 Agents',
    focus: 'Rapid Growth'
  });

  const handleLaunch = async () => {
    setLoading(true);
    try {
      await fetch(`${BACKEND_URL}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: `INITIALIZE COMPANY BLUEPRINT: Name: ${config.name}, Industry: ${config.industry}, Scale: ${config.scale}, Strategy: ${config.focus}. Generate file structure, agent roles, and 12-month roadmap.`
        })
      });
      setStep(3);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm font-mono">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-2xl bg-black border-2 border-primary/20 rounded-3xl p-8 relative overflow-hidden shadow-[0_0_100px_rgba(0,255,136,0.1)]"
      >
        <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-black text-white italic tracking-tighter">COMPANY_GENESIS_v1</h2>
            <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">ESC</button>
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="s1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
                <div className="space-y-2">
                    <label className="text-[10px] text-gray-500 uppercase tracking-widest">Company Identity</label>
                    <input 
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-primary focus:outline-none focus:border-primary transition-colors"
                        placeholder="e.g. CyberDyne Systems"
                        value={config.name}
                        onChange={e => setConfig({...config, name: e.target.value})}
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <label className="text-[10px] text-gray-500 uppercase tracking-widest">Industry Domain</label>
                        <select 
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none"
                            value={config.industry}
                            onChange={e => setConfig({...config, industry: e.target.value})}
                        >
                            <option>Software</option>
                            <option>Finance</option>
                            <option>Biotech</option>
                            <option>Manufacturing</option>
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] text-gray-500 uppercase tracking-widest">Swarm Scale</label>
                        <select 
                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none"
                            value={config.scale}
                            onChange={e => setConfig({...config, scale: e.target.value})}
                        >
                            <option>10 Agents</option>
                            <option>100 Agents</option>
                            <option>1000 Agents</option>
                        </select>
                    </div>
                </div>
                <button 
                    onClick={() => setStep(2)}
                    disabled={!config.name}
                    className="w-full bg-primary text-black py-4 rounded-xl font-black flex items-center justify-center gap-2 hover:scale-[1.02] transition-transform disabled:opacity-50"
                >
                    PROCEED TO VALIDATION <ArrowRight size={18} />
                </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="s2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
                <div className="bg-primary/5 p-6 rounded-2xl border border-primary/20 space-y-4">
                    <div className="flex items-center gap-3 text-primary">
                        <ShieldCheck size={20} />
                        <span className="font-bold text-sm uppercase">Verification Complete</span>
                    </div>
                    <p className="text-xs text-gray-400 leading-relaxed">
                        Sovereign system is ready to spawn <span className="text-white">{config.scale}</span> for <span className="text-white">{config.name}</span>. 
                        The swarm will initialize the <span className="text-white">{config.industry}</span> protocol and begin autonomous operations.
                    </p>
                </div>
                <div className="flex gap-4">
                    <button onClick={() => setStep(1)} className="flex-1 border border-white/10 text-white py-4 rounded-xl font-bold text-sm">BACK</button>
                    <button 
                        onClick={handleLaunch}
                        className="flex-[2] bg-primary text-black py-4 rounded-xl font-black flex items-center justify-center gap-2"
                    >
                        {loading ? <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" /> : 'GENERATE REALM'}
                    </button>
                </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div key="s3" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-10 space-y-6">
                <div className="w-20 h-20 bg-primary/20 rounded-full flex items-center justify-center mx-auto text-primary border-2 border-primary animate-pulse">
                    <Check size={40} />
                </div>
                <h3 className="text-3xl font-black text-white tracking-tighter uppercase">Ignition Successful</h3>
                <p className="text-xs text-gray-500 max-w-sm mx-auto">The agent swarm has been deployed. Check the Dashboard for real-time build telemetry and the Cockpit for agent directives.</p>
                <button onClick={onClose} className="bg-white text-black px-10 py-3 rounded-full font-bold text-sm">CLOSE WIZARD</button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
