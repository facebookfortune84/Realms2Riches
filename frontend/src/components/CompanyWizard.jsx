import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, Rocket, ShieldCheck, Users, ArrowRight, Check, Box, Cpu, Download, Briefcase, Zap, Settings, Search, LogOut } from 'lucide-react';

import { getApiBase } from '../lib/apiBase';

const BUSINESS_TYPES = [
    { id: 'saas', label: 'SaaS / AI App', icon: Cpu },
    { id: 'ecommerce', label: 'E-Commerce', icon: Box },
    { id: 'agency', label: 'Service Agency', icon: Briefcase },
    { id: 'content', label: 'Media/Content', icon: Rocket },
    { id: 'enterprise', label: 'Enterprise Corp', icon: Building2 },
    { id: 'consulting', label: 'Consulting Firm', icon: Search }
];

// Dynamically load agent roles from oracle/prompts directory names
// In a real app, this might involve a backend API call or build-time process
const AGENT_ROLES_DATA = [
    { id: 'architect_planner', label: 'Architect Planner', desc: 'SOP & Strategic Planning.', icon: Settings },
    { id: 'code_engineer', label: 'Code Engineer', desc: 'Implementation & Infrastructure.', icon: Cpu },
    { id: 'growth_hacker', label: 'Growth Hacker', desc: 'Lead Generation & Funnels.', icon: Rocket },
    { id: 'integrity_shield', label: 'Integrity Shield', desc: 'Security & Validation.', icon: ShieldCheck },
    { id: 'cli_assistant', label: 'CLI Assistant', desc: 'Interactive CLI Support.' },
    { id: 'builder_assistant', label: 'IDE Co-Pilot', desc: 'Pair programming in IDE.' },
    { id: 'enterprise_agent', label: 'Enterprise Agent', desc: 'Live meeting co-pilot.' },
    { id: 'planning_agent', label: 'Strategic Planner', desc: 'Task decomposition & roadmap.' },
    { id: 'gemini_cli', label: 'Gemini CLI Agent', desc: 'Gemini CLI interaction.' },
    { id: 'gpt_5_master', label: 'GPT-5 Master', desc: 'Advanced reasoning & generation.' }
];

// Dynamically load available tools from oracle/tools JSON files
// In a real app, this would involve reading JSON files and parsing tool definitions
const AVAILABLE_TOOLS_DATA = [
    'Vector Memory', 'Stripe Integration', 'Puppeteer Scraper', 'Groq Inference',
    'Builder Tools', 'Plan Mode Tools', 'Oracle Tools', 'Agent CLI Interaction',
    'Genesis Forge'
];

export default function CompanyWizard({ isOpen, onClose }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [agentRoles, setAgentRoles] = useState([]);
  const [tools, setTools] = useState([]);

  const [config, setConfig] = useState({
    name: '',
    industry: 'saas',
    scale: '100',
    roles: ['architect_planner', 'code_engineer'], // Default roles
    tools: ['Vector Memory', 'Genesis Forge'] // Default tools
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Populate agent roles from AGENT_ROLES_DATA
        setAgentRoles(AGENT_ROLES_DATA);
        
        // Populate available tools from AVAILABLE_TOOLS_DATA
        setTools(AVAILABLE_TOOLS_DATA);
      } catch (error) {
        console.error("Error fetching roles or tools:", error);
        // Fallback to default values if fetching fails
        setAgentRoles(AGENT_ROLES_DATA); // Use populated data
        setTools(AVAILABLE_TOOLS_DATA);
      }
    };
    if (isOpen) {
      fetchData();
      // Initialize config with at least one default role/tool if none selected
      setConfig(prev => ({
        ...prev,
        roles: prev.roles.length > 0 ? prev.roles : [AGENT_ROLES_DATA[0]?.id].filter(Boolean), // Ensure at least one default role
        tools: prev.tools.length > 0 ? prev.tools : [AVAILABLE_TOOLS_DATA[0]] // Ensure at least one default tool
      }));
    }
  }, [isOpen]);

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${getApiBase()}/api/tasks`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            description: `INITIALIZE COMPANY BLUEPRINT: ${config.name} (${config.industry})`,
            config: { 
              name: config.name,
              industry: config.industry,
              agent_count: parseInt(config.scale),
              roles: config.roles,
              tools: config.tools
            } 
        })
      });
      const data = await response.json();
      if (data.result?.artifact_url) {
        window.open(`${getApiBase()}${data.result.artifact_url}`, '_blank');
      }
      setStep(4);
    } catch (e) {
      console.error("Error launching genesis forge:", e);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelection = (key, value) => {
      setConfig(prev => ({
          ...prev,
          [key]: prev[key].includes(value)
              ? prev[key].filter(item => item !== value)
              : [...prev[key], value]
      }));
  };

  const allRolesSelected = config.roles.length > 0;
  const allToolsSelected = config.tools.length > 0;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/95 backdrop-blur-3xl font-mono text-white">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, rotateX: 10 }}
        animate={{ opacity: 1, scale: 1, rotateX: 0 }}
        transition={{ type: "spring", stiffness: 100, damping: 20 }}
        className="w-full max-w-5xl bg-[#050505] border border-primary/20 rounded-[2rem] p-10 relative overflow-hidden shadow-[0_0_200px_rgba(0,255,136,0.2)]"
      >
        {/* Animated Background Scanline */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-10">
            <div className="w-full h-full bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,255,136,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,3px_100%]" />
        </div>
        
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50" />
        
        <div className="flex justify-between items-start mb-10 relative z-10">
            <div className="flex items-center gap-6">
                <div className="p-4 bg-primary/10 rounded-3xl border border-primary/30 shadow-[0_0_30px_rgba(0,255,136,0.1)]">
                    <img src={`${getApiBase()}/assets/branding/forge_logo.png`} alt="Forge" className="h-16 w-auto" />
                </div>
                <div>
                    <h2 className="text-4xl font-black text-white italic tracking-tighter uppercase">
                        Genesis <span className="text-primary">Forge</span>
                    </h2>
                    <p className="text-[10px] text-gray-500 uppercase tracking-[0.4em] mt-1 font-bold">Industrial Swarm Provisioning v3.0</p>
                </div>
            </div>
            <button onClick={onClose} className="group relative bg-white/5 hover:bg-red-500/20 text-gray-500 hover:text-red-500 p-4 rounded-full transition-all border border-white/5 hover:border-red-500/30">
                <span className="text-[10px] font-bold group-hover:hidden">ESC</span>
                <span className="text-[10px] font-bold hidden group-hover:block px-1">CLOSE</span>
            </button>
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="s1" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} className="space-y-10 relative z-10">
                <h3 className="text-3xl font-black text-white text-center uppercase tracking-tight">Define Your Swarm's Core Identity</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                    <div className="space-y-3">
                        <label className="block text-[10px] text-gray-400 uppercase tracking-widest font-black">Industrial Identity</label>
                        <input 
                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-8 py-6 text-primary focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all text-xl font-black uppercase tracking-tighter"
                            placeholder="PROJECT_ID_ALPHA"
                            value={config.name}
                            onChange={e => setConfig({...config, name: e.target.value})}
                        />
                    </div>
                    <div className="space-y-3">
                        <label className="block text-[10px] text-gray-400 uppercase tracking-widest font-black">Operational Sector</label>
                        <div className="relative">
                            <select 
                                className="w-full bg-white/5 border border-white/10 rounded-2xl px-8 py-6 text-white focus:outline-none appearance-none cursor-pointer hover:border-primary/30 transition-all font-bold uppercase text-sm tracking-widest"
                                value={config.industry}
                                onChange={e => setConfig({...config, industry: e.target.value})}
                            >
                                {BUSINESS_TYPES.map(type => (
                                    <option key={type.id} value={type.id}>{type.label.toUpperCase()}</option>
                                ))}
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
                    Define Swarm Architecture <ArrowRight size={18} className="group-hover:translate-x-2 transition-transform" />
                </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="s2" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} className="space-y-10 relative z-10">
                <div className="space-y-6">
                    <label className="block text-[10px] text-gray-400 uppercase tracking-[0.3em] font-black flex items-center gap-2">
                        <Users size={14} className="text-primary" /> Select Logic Nodes (Agent Personas)
                    </label>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {agentRoles.map(role => (
                            <div 
                                key={role.id}
                                onClick={() => toggleSelection('roles', role.id)}
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
                    <button onClick={() => setStep(1)} className="flex-1 bg-white/5 border border-white/10 text-white py-6 rounded-[1.5rem] font-black text-xs uppercase tracking-widest hover:bg-white/10 transition-all">Adjust Basics</button>
                    <button 
                        onClick={handleLaunch}
                        disabled={loading || !config.name || !config.roles.length || !config.tools.length}
                        className="flex-[2] bg-primary text-black py-4 px-10 rounded-xl font-black text-sm uppercase tracking-[0.2em] flex items-center justify-center gap-4 hover:bg-white hover:scale-[1.02] transition-all disabled:opacity-50 disabled:grayscale shadow-[0_10px_40px_rgba(0,255,136,0.2)]"
                    >
                        {loading ? <div className="w-6 h-6 border-4 border-black border-t-transparent rounded-full animate-spin" /> : <>Finalize Configuration <ArrowRight size={18} /></>}
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
                    <h3 className="text-5xl font-black text-white tracking-tighter uppercase italic">Swarm Manifested</h3>
                    <p className="text-xs text-gray-500 max-w-md mx-auto leading-relaxed font-bold uppercase tracking-widest">Industrial Swarm Allocation Complete. Your custom swarm is being compiled and packaged for download. Artifact generation in progress.</p>
                </div>
                
                <div className="bg-white/5 p-8 rounded-[2.5rem] border-2 border-white/10 inline-block text-left w-full max-w-md relative overflow-hidden group">
                    <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="flex items-center justify-between mb-6 relative z-10">
                        <span className="text-[10px] text-gray-500 uppercase font-black tracking-[0.2em]">Deployment Artifact</span>
                        <span className="text-[10px] bg-primary/20 text-primary px-3 py-1 rounded-full font-black animate-bounce shadow-[0_0_15px_rgba(0,255,136,0.2)]">READY</span>
                    </div>
                    <div className="flex items-center gap-4 bg-black/40 p-4 rounded-2xl mb-6 border border-white/5 relative z-10">
                        <div className="p-3 bg-white/5 rounded-xl"><Download size={20} className="text-primary" /></div>
                        <p className="text-[11px] text-white font-black truncate tracking-tighter opacity-80 uppercase">matrix_manifest_{config.name.toLowerCase().replace(/\s/g, '_')}.zip</p>
                    </div>
                    <button 
                        onClick={() => window.location.href = '/chamber'}
                        className="w-full bg-white text-black py-5 rounded-2xl font-black text-xs uppercase tracking-[0.2em] flex items-center justify-center gap-3 hover:bg-primary transition-all relative z-10 shadow-[0_10px_30px_rgba(255,255,255,0.1)]"
                    >
                        <Download size={16} /> Download Swarm Package
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

