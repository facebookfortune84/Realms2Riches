import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, Rocket, ShieldCheck, Users, ArrowRight, Check, Box, Cpu, Download, Briefcase, Zap } from 'lucide-react';

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
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/95 backdrop-blur-3xl font-mono">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9, rotateX: 10 }}
        animate={{ opacity: 1, scale: 1, rotateX: 0 }}
        className="w-full max-w-4xl bg-[#050505] border-2 border-primary/30 rounded-[3rem] p-12 relative overflow-hidden shadow-[0_0_200px_rgba(0,255,136,0.2)]"
      >
        {/* Animated Background Scanline */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-10">
            <div className="w-full h-full bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,255,136,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,3px_100%]" />
        </div>

        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50" />
        
        <div className="flex justify-between items-start mb-12 relative z-10">
            <div className="flex items-center gap-6">
                <div className="p-4 bg-primary/10 rounded-3xl border border-primary/30 shadow-[0_0_30px_rgba(0,255,136,0.1)]">
                    <img 
                        src={`${BACKEND_URL}/assets/branding/forge_logo.png`} 
                        alt="Forge" 
                        className="h-16 w-auto"
                    />
                </div>
                <div>
                    <h2 className="text-4xl font-black text-white italic tracking-tighter uppercase">
                        Genesis <span className="text-primary">Forge</span>
                    </h2>
                    <p className="text-[10px] text-gray-500 uppercase tracking-[0.4em] mt-1 font-bold">Industrial Swarm Provisioning v2.0</p>
                </div>
            </div>
            <button 
                onClick={onClose} 
                className="group relative bg-white/5 hover:bg-red-500/20 text-gray-500 hover:text-red-500 p-4 rounded-full transition-all border border-white/5 hover:border-red-500/30"
            >
                <span className="text-[10px] font-bold group-hover:hidden">ESC</span>
                <span className="text-[10px] font-bold hidden group-hover:block px-1">CLOSE</span>
            </button>
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="s1" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} className="space-y-10 relative z-10">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                    <div className="space-y-3">
                        <div className="flex items-center gap-2 mb-1">
                            <Zap size={14} className="text-primary" />
                            <label className="text-[10px] text-gray-400 uppercase tracking-widest font-black">Industrial Identity</label>
                        </div>
                        <input 
                            className="w-full bg-white/5 border-2 border-white/10 rounded-[1.5rem] px-8 py-6 text-primary focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all text-xl font-black uppercase tracking-tighter"
                            placeholder="PROJECT_ID_ALPHA"
                            value={config.name}
                            onChange={e => setConfig({...config, name: e.target.value})}
                        />
                    </div>
                    <div className="space-y-3">
                        <div className="flex items-center gap-2 mb-1">
                            <Box size={14} className="text-primary" />
                            <label className="text-[10px] text-gray-400 uppercase tracking-widest font-black">Operational Sector</label>
                        </div>
                        <div className="relative">
                            <select 
                                className="w-full bg-white/5 border-2 border-white/10 rounded-[1.5rem] px-8 py-6 text-white focus:outline-none appearance-none cursor-pointer hover:border-primary/30 transition-all font-bold uppercase text-sm tracking-widest"
                                value={config.industry}
                                onChange={e => setConfig({...config, industry: e.target.value})}
                            >
                                <option>SaaS_DEVELOPMENT</option>
                                <option>E_COMMERCE_NET</option>
                                <option>GROWTH_ENGINEERING</option>
                                <option>QUANT_MARKET_OPS</option>
                                <option>CYBER_SECURITY_CORE</option>
                            </select>
                            <div className="absolute right-6 top-1/2 -translate-y-1/2 pointer-events-none opacity-30"><ArrowRight rotate={90} size={16} /></div>
                        </div>
                    </div>
                </div>
                <button 
                    onClick={() => setStep(2)}
                    disabled={!config.name}
                    className="w-full bg-primary text-black py-7 rounded-[1.5rem] font-black text-sm uppercase tracking-[0.2em] flex items-center justify-center gap-3 hover:bg-white hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-20 disabled:grayscale group shadow-[0_10px_40px_rgba(0,255,136,0.2)]"
                >
                    Provision Agent Workforce <ArrowRight size={18} className="group-hover:translate-x-2 transition-transform" />
                </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="s2" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} className="space-y-10 relative z-10">
                <div className="space-y-6">
                    <label className="text-[10px] text-gray-400 uppercase tracking-[0.3em] font-black flex items-center gap-2">
                        <Users size={14} className="text-primary" /> Configure Logic Nodes
                    </label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {AGENT_ROLES.map(role => (
                            <div 
                                key={role.id}
                                onClick={() => toggleRole(role.id)}
                                className={`group p-6 rounded-[2rem] border-2 transition-all cursor-pointer flex gap-6 items-center relative overflow-hidden ${
                                    config.roles.includes(role.id) ? 'border-primary bg-primary/5 shadow-[0_0_30px_rgba(0,255,136,0.05)]' : 'border-white/5 bg-white/5 hover:border-white/20'
                                }`}
                            >
                                <div className={`p-4 rounded-2xl transition-all duration-500 ${config.roles.includes(role.id) ? 'bg-primary text-black scale-110 shadow-[0_0_20px_rgba(0,255,136,0.3)]' : 'bg-white/5 text-gray-500'}`}>
                                    <role.icon size={24} />
                                </div>
                                <div className="relative z-10">
                                    <h4 className="text-sm font-black text-white uppercase tracking-tight">{role.label}</h4>
                                    <p className="text-[10px] text-gray-500 mt-1 leading-relaxed">{role.desc}</p>
                                </div>
                                {config.roles.includes(role.id) && (
                                    <div className="absolute -right-4 -bottom-4 opacity-10"><role.icon size={80} /></div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
                
                <div className="space-y-6 bg-white/5 p-8 rounded-[2rem] border border-white/5">
                    <div className="flex justify-between items-end mb-2">
                        <label className="text-[10px] text-gray-400 uppercase tracking-widest font-black">Swarm Scale Density</label>
                        <span className="text-3xl font-black text-primary italic tracking-tighter">{config.scale} <span className="text-xs font-bold text-gray-600 not-italic uppercase ml-1">Units</span></span>
                    </div>
                    <input 
                        type="range" min="10" max="1000" step="10"
                        className="w-full h-2 bg-black rounded-lg appearance-none cursor-pointer accent-primary border border-white/10"
                        value={config.scale}
                        onChange={e => setConfig({...config, scale: e.target.value})}
                    />
                    <div className="flex justify-between text-[8px] text-gray-600 font-bold uppercase tracking-widest">
                        <span>MIN_DEPLOYMENT: 10</span>
                        <span>MAX_DEPLOYMENT: 1000</span>
                    </div>
                </div>

                <div className="flex gap-6">
                    <button onClick={() => setStep(1)} className="flex-1 bg-white/5 border border-white/10 text-white py-6 rounded-[1.5rem] font-black text-xs uppercase hover:bg-white/10 transition-all tracking-widest">Adjust Basics</button>
                    <button onClick={() => setStep(3)} className="flex-[2] bg-primary text-black py-6 rounded-[1.5rem] font-black text-xs uppercase tracking-[0.2em] hover:bg-white hover:scale-[1.02] transition-all shadow-[0_10px_40px_rgba(0,255,136,0.2)]">Lock Configuration</button>
                </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div key="s3" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="space-y-10 relative z-10">
                <div className="bg-primary/5 p-10 rounded-[3rem] border-2 border-primary/30 space-y-8 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-8 opacity-5"><Box size={150} /></div>
                    <div className="space-y-6 relative z-10">
                        <div className="flex items-center gap-4 text-primary">
                            <ShieldCheck size={32} className="animate-pulse" />
                            <span className="font-black text-2xl uppercase italic tracking-tighter">Forge_Handshake_Active</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-sm">
                            <div className="space-y-1">
                                <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest">Target Identity</span>
                                <p className="text-white font-black text-lg truncate">{config.name}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest">Swarm Capacity</span>
                                <p className="text-white font-black text-lg">{config.scale} Units</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest">Domain Map</span>
                                <p className="text-white font-black text-lg uppercase">{config.industry.replace('_', ' ')}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-[10px] text-gray-600 uppercase font-black tracking-widest">Logic Specialization</span>
                                <p className="text-white font-black text-lg">{config.roles.length} Domains</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="flex gap-6">
                    <button onClick={() => setStep(2)} className="flex-1 border-2 border-white/10 text-white py-6 rounded-[1.5rem] font-black text-xs uppercase tracking-widest">Recalibrate</button>
                    <button 
                        onClick={handleLaunch}
                        className="flex-[3] bg-primary text-black py-6 rounded-[1.5rem] font-black text-sm uppercase tracking-[0.3em] flex items-center justify-center gap-4 hover:bg-white hover:scale-[1.02] transition-all shadow-[0_15px_50px_rgba(0,255,136,0.3)]"
                    >
                        {loading ? <div className="w-6 h-6 border-4 border-black border-t-transparent rounded-full animate-spin" /> : <>INITIALIZE GENESIS <Zap size={18} /></>}
                    </button>
                </div>
            </motion.div>
          )}

          {step === 4 && (
            <motion.div key="s4" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-12 space-y-10 relative z-10">
                <div className="relative inline-block">
                    <div className="w-32 h-32 bg-primary/20 rounded-[2.5rem] flex items-center justify-center mx-auto text-primary border-4 border-primary animate-pulse shadow-[0_0_60px_rgba(0,255,136,0.4)]">
                        <Check size={64} strokeWidth={3} />
                    </div>
                    <motion.div 
                        animate={{ rotate: 360 }}
                        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                        className="absolute inset-[-20px] border-2 border-dashed border-primary/20 rounded-full"
                    />
                </div>
                
                <div className="space-y-3">
                    <h3 className="text-5xl font-black text-white tracking-tighter uppercase italic">Realm Manifested</h3>
                    <p className="text-xs text-gray-500 max-w-md mx-auto leading-relaxed font-bold uppercase tracking-widest">Industrial Swarm Allocation Complete. Duplicate nodes are migrating to your workspace. Artifact compilation in progress.</p>
                </div>
                
                <div className="bg-white/5 p-8 rounded-[2.5rem] border-2 border-white/10 inline-block text-left w-full max-w-md relative overflow-hidden group">
                    <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="flex items-center justify-between mb-6 relative z-10">
                        <span className="text-[10px] text-gray-500 uppercase font-black tracking-[0.2em]">Deployment Artifact</span>
                        <span className="text-[10px] bg-primary/20 text-primary px-3 py-1 rounded-full font-black animate-bounce shadow-[0_0_15px_rgba(0,255,136,0.2)]">READY</span>
                    </div>
                    <div className="flex items-center gap-4 bg-black/40 p-4 rounded-2xl mb-6 border border-white/5 relative z-10">
                        <div className="p-3 bg-white/5 rounded-xl"><Download size={20} className="text-primary" /></div>
                        <p className="text-[11px] text-white font-black truncate tracking-tighter opacity-80 uppercase">matrix_manifest_{config.name.toLowerCase().replace(/\s/g, '_')}.json</p>
                    </div>
                    <button 
                        onClick={() => window.location.href = '/chamber'}
                        className="w-full bg-white text-black py-5 rounded-2xl font-black text-xs uppercase tracking-[0.2em] flex items-center justify-center gap-3 hover:bg-primary transition-all relative z-10 shadow-[0_10px_30px_rgba(255,255,255,0.1)]"
                    >
                        <Download size={16} /> Download Swarm Data
                    </button>
                </div>

                <p className="text-[9px] text-gray-600 uppercase tracking-[0.5em] pt-6 font-bold animate-pulse">Redirecting to Sovereign Chamber for live uplink...</p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
