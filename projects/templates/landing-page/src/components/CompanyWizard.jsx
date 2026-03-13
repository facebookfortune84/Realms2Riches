import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, Rocket, ShieldCheck, Users, ArrowRight, Check, Box, Cpu, Download, Briefcase } from 'lucide-react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

const AGENT_ROLES = [
    { id: 'manager', label: 'Strategic Manager', icon: Briefcase, desc: 'Orchestrates swarm priorities and roadmap.' },
    { id: 'developer', label: 'Cybernetic Engineer', icon: Cpu, desc: 'Generates code and infrastructure.' },
    { id: 'marketer', label: 'Growth Hacker', icon: Rocket, desc: 'Automates outreach and sales funnels.' },
    { id: 'auditor', label: 'Integrity Shield', icon: ShieldCheck, desc: 'Validates system state and security.' }
];

export default function CompanyWizard({ isOpen, onClose }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState({
    name: '',
    industry: 'Software',
    scale: '100',
    roles: ['manager', 'developer']
  });

  const toggleRole = (roleId) => {
    setConfig(prev => ({
        ...prev,
        roles: prev.roles.includes(roleId) 
            ? prev.roles.filter(r => r !== roleId)
            : [...prev.roles, roleId]
    }));
  };

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const description = `INITIALIZE COMPANY BLUEPRINT: 
        Name: ${config.name}
        Industry: ${config.industry}
        Agent Count: ${config.scale}
        Selected Specializations: ${config.roles.join(', ')}
        Action: Duplicate high-performance nodes for selected roles. 
        Deliverable: Complete JSON swarm manifest and initialization script.`;

      await fetch(`${BACKEND_URL}/api/tasks`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({ description })
      });
      setStep(4);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/95 backdrop-blur-xl font-mono">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-3xl bg-[#050505] border-2 border-primary/20 rounded-[2rem] p-10 relative overflow-hidden shadow-[0_0_150px_rgba(0,255,136,0.15)]"
      >
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50" />
        
        <div className="flex justify-between items-center mb-10">
            <div>
                <h2 className="text-3xl font-black text-white italic tracking-tighter flex items-center gap-3">
                    <Box className="text-primary" />
                    GENESIS <span className="text-primary">FORGE</span>
                </h2>
                <p className="text-[10px] text-gray-600 uppercase tracking-[0.3em] mt-1">Autonomous Swarm Vending System v2.0</p>
            </div>
            <button onClick={onClose} className="bg-white/5 hover:bg-white/10 text-gray-500 hover:text-white p-3 rounded-full transition-all">ESC</button>
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="s1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-2">
                        <label className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Realm Identity</label>
                        <input 
                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-primary focus:outline-none focus:border-primary transition-all text-lg font-bold"
                            placeholder="Company Name..."
                            value={config.name}
                            onChange={e => setConfig({...config, name: e.target.value})}
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Industry Domain</label>
                        <select 
                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white focus:outline-none appearance-none cursor-pointer hover:border-primary/30 transition-all"
                            value={config.industry}
                            onChange={e => setConfig({...config, industry: e.target.value})}
                        >
                            <option>SaaS / Software</option>
                            <option>E-Commerce</option>
                            <option>Digital Marketing</option>
                            <option>Quant Finance</option>
                            <option>Cyber Security</option>
                        </select>
                    </div>
                </div>
                <button 
                    onClick={() => setStep(2)}
                    disabled={!config.name}
                    className="w-full bg-primary text-black py-5 rounded-2xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-white transition-all disabled:opacity-30 disabled:grayscale"
                >
                    Configure Agent Workforce <ArrowRight size={16} />
                </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="s2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-8">
                <div className="space-y-4">
                    <label className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Select Specializations</label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {AGENT_ROLES.map(role => (
                            <div 
                                key={role.id}
                                onClick={() => toggleRole(role.id)}
                                className={`p-4 rounded-2xl border-2 transition-all cursor-pointer flex gap-4 items-center ${
                                    config.roles.includes(role.id) ? 'border-primary bg-primary/5' : 'border-white/5 bg-white/5 hover:border-white/20'
                                }`}
                            >
                                <div className={`p-3 rounded-xl ${config.roles.includes(role.id) ? 'bg-primary text-black' : 'bg-white/5 text-gray-500'}`}>
                                    <role.icon size={20} />
                                </div>
                                <div>
                                    <h4 className="text-xs font-black text-white uppercase">{role.label}</h4>
                                    <p className="text-[9px] text-gray-500 mt-1">{role.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
                
                <div className="space-y-4">
                    <label className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Swarm Magnitude: <span className="text-primary">{config.scale} Units</span></label>
                    <input 
                        type="range" min="10" max="1000" step="10"
                        className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-primary"
                        value={config.scale}
                        onChange={e => setConfig({...config, scale: e.target.value})}
                    />
                </div>

                <div className="flex gap-4">
                    <button onClick={() => setStep(1)} className="flex-1 bg-white/5 text-white py-5 rounded-2xl font-bold text-xs uppercase hover:bg-white/10 transition-all">Back</button>
                    <button onClick={() => setStep(3)} className="flex-[2] bg-primary text-black py-5 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-white transition-all">Review Order</button>
                </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div key="s3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-8">
                <div className="bg-primary/5 p-8 rounded-3xl border-2 border-primary/20 space-y-6 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10"><Box size={80} /></div>
                    <div className="space-y-4 relative z-10">
                        <div className="flex items-center gap-3 text-primary">
                            <ShieldCheck size={24} />
                            <span className="font-black text-lg uppercase italic tracking-tighter">Forge Ready</span>
                        </div>
                        <div className="space-y-2 text-sm">
                            <p className="text-gray-400">Deploying industrial swarm for <span className="text-white font-bold">{config.name}</span></p>
                            <p className="text-gray-400">Magnitude: <span className="text-white font-bold">{config.scale} Autonomous Units</span></p>
                            <p className="text-gray-400">Protocols: <span className="text-white font-bold">{config.roles.length} Active Domains</span></p>
                        </div>
                    </div>
                </div>
                <div className="flex gap-4">
                    <button onClick={() => setStep(2)} className="flex-1 border border-white/10 text-white py-5 rounded-2xl font-bold text-xs uppercase">Adjust</button>
                    <button 
                        onClick={handleLaunch}
                        className="flex-[2] bg-primary text-black py-5 rounded-2xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-3"
                    >
                        {loading ? <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" /> : 'Confirm & Initialize'}
                    </button>
                </div>
            </motion.div>
          )}

          {step === 4 && (
            <motion.div key="s4" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-10 space-y-8">
                <div className="w-24 h-24 bg-primary/20 rounded-full flex items-center justify-center mx-auto text-primary border-4 border-primary animate-pulse">
                    <Check size={48} />
                </div>
                <div className="space-y-2">
                    <h3 className="text-4xl font-black text-white tracking-tighter uppercase italic italic">Realm Manifested</h3>
                    <p className="text-xs text-gray-500 max-w-sm mx-auto">The Sovereign Swarm has been allocated and duplicate nodes are coming online. Your deployment manifest is being compiled.</p>
                </div>
                
                <div className="bg-white/5 p-6 rounded-2xl border border-white/10 inline-block text-left w-full max-w-sm">
                    <div className="flex items-center justify-between mb-4">
                        <span className="text-[10px] text-gray-500 uppercase font-bold">Deployment Artifact</span>
                        <span className="text-[9px] bg-primary/20 text-primary px-2 py-0.5 rounded-full font-black">READY</span>
                    </div>
                    <p className="text-[10px] text-white font-mono truncate mb-4 opacity-60">matrix_manifest_${config.name.toLowerCase().replace(/\s/g, '_')}.json</p>
                    <button 
                        onClick={() => window.location.href = '/chamber'}
                        className="w-full bg-white text-black py-3 rounded-xl font-bold text-xs uppercase flex items-center justify-center gap-2 hover:bg-primary transition-all"
                    >
                        <Download size={14} /> Download Swarm Data
                    </button>
                </div>

                <p className="text-[10px] text-gray-600 uppercase tracking-widest pt-4">Redirecting to the Chamber for live uplink...</p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
