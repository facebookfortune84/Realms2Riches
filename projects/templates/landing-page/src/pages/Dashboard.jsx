import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Shield, Zap, Users, Globe, Database, Cpu, Terminal, Layers, Radio } from 'lucide-react';
import CompanyWizard from '../components/CompanyWizard';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [activity, setActivity] = useState([]);
  const [integrations, setIntegrations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  const fetchStats = async () => {
    const headers = { 'X-License-Key': import.meta.env.VITE_SOVEREIGN_LICENSE_KEY || '' };
    try {
      const [mRes, aRes, iRes] = await Promise.all([
        fetch(`${BACKEND_URL}/health`),
        fetch(`${BACKEND_URL}/api/activity`, { headers }),
        fetch(`${BACKEND_URL}/api/integrations/status`, { headers })
      ]);
      setMetrics(await mRes.json());
      setActivity(await aRes.json());
      setIntegrations(await iRes.json());
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  useEffect(() => {
    fetchStats();
    const timer = setInterval(fetchStats, 5000);
    return () => clearInterval(timer);
  }, []);

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black font-mono">
        <Cpu className="text-primary animate-spin mb-4" size={40} />
        <div className="text-primary animate-pulse tracking-[0.5em] uppercase text-[10px]">Syncing Platinum Matrix</div>
    </div>
  );

  const stats = [
    { label: "Active Agents", value: metrics?.agents || 1000, icon: Users, color: "text-primary" },
    { label: "Swarm State", value: metrics?.swarm || "ACTIVE", icon: Shield, color: "text-green-400" },
    { label: "Memory Docs", value: metrics?.rag || 0, icon: Database, color: "text-blue-400" },
    { label: "Matrix Link", value: "SECURE", icon: Activity, color: "text-primary" }
  ];

  return (
    <div className="py-10 max-w-7xl mx-auto px-4 font-mono text-white">
      {/* HEADER */}
      <div className="flex justify-between items-end mb-12">
        <div>
            <div className="text-primary text-[10px] mb-2 tracking-[0.5em] uppercase">Sovereign OS v3.7.2-PLATINUM</div>
            <h2 className="text-6xl font-black tracking-tighter italic">FOUNDER <span className="text-primary">COCKPIT</span></h2>
        </div>
        <div className="bg-white/5 px-6 py-3 rounded-2xl border border-white/10 flex items-center gap-3">
            <Radio size={16} className="text-primary animate-pulse" />
            <span className="text-[10px] text-gray-400 uppercase tracking-widest">Neural Link: SECURE</span>
        </div>
      </div>

      {/* INTEGRATION LIGHTS */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-12">
        {integrations && Object.entries(integrations).map(([k, v]) => (
            <div key={k} className="bg-white/5 p-4 rounded-2xl border border-white/5 flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${v === 'active' ? 'bg-primary shadow-[0_0_10px_#00ff88]' : 'bg-red-500/50'}`} />
                <span className="text-[10px] font-bold uppercase text-gray-400">{k}</span>
            </div>
        ))}
      </div>

      {/* OVERALL STATS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        {stats.map((s, i) => (
            <div key={i} className="bg-black/40 p-6 rounded-2xl border border-white/5 flex flex-col">
                <div className="flex justify-between items-center mb-2 text-gray-600">
                    <s.icon size={16} />
                    <span className="text-[10px]">00{i+1}</span>
                </div>
                <div className="text-gray-500 text-[10px] uppercase font-bold">{s.label}</div>
                <div className={`text-2xl font-black ${s.color}`}>{s.value}</div>
            </div>
        ))}
      </div>

      {/* MATRIX CELLS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        {metrics?.cells && Object.entries(metrics.cells).map(([name, data]) => (
            <div key={name} className="bg-black border-2 border-white/5 p-8 rounded-3xl relative overflow-hidden group hover:border-primary/30 transition-all">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-20 transition-opacity">
                    <Layers size={80} />
                </div>
                <h3 className="text-primary font-black mb-1 uppercase tracking-tighter text-xl">CELL_{name}</h3>
                <p className="text-gray-500 text-[10px] mb-6 uppercase tracking-widest">Sub-Swarm Cluster</p>
                <div className="flex justify-between items-end">
                    <div>
                        <div className="text-3xl font-black">{data.agents}</div>
                        <div className="text-[10px] text-gray-600 uppercase">Active Units</div>
                    </div>
                    <div className="text-right">
                        <div className={`text-xl font-bold ${data.active_tasks > 0 ? 'text-primary animate-pulse' : 'text-gray-700'}`}>
                            {data.active_tasks > 0 ? 'EXECUTING' : 'IDLE'}
                        </div>
                        <div className="text-[10px] text-gray-600 uppercase">Status</div>
                    </div>
                </div>
            </div>
        ))}
      </div>

      {/* ACTIVITY & ACTIONS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white/5 p-8 rounded-3xl border border-white/10">
            <h3 className="text-lg font-bold mb-6 flex items-center gap-3">
                <Terminal className="text-primary" size={20} />
                SOVEREIGN ACTIVITY STREAM
            </h3>
            <div className="space-y-4 h-96 overflow-y-auto custom-scrollbar pr-4">
                {activity.length > 0 ? activity.map((a, i) => (
                    <div key={i} className="flex gap-4 text-[10px] border-b border-white/5 pb-4">
                        <span className="text-gray-600 shrink-0">[{new Date(a.t).toLocaleTimeString()}]</span>
                        <span className="text-primary font-bold w-32 truncate">[{a.a}]</span>
                        <span className="text-white uppercase">{a.op}:</span>
                        <span className="text-gray-400">{a.r}</span>
                    </div>
                )) : <div className="text-gray-600 text-[10px]">Awaiting telemetry...</div>}
            </div>
        </div>

        <div className="space-y-8">
            <div className="bg-primary p-8 rounded-3xl text-black cursor-pointer hover:scale-[1.02] transition-transform" onClick={() => setIsWizardOpen(true)}>
                <Zap size={32} className="mb-4" />
                <h4 className="text-2xl font-black uppercase tracking-tighter leading-none mb-2">Build a<br/>Company</h4>
                <p className="text-[10px] font-bold opacity-70 uppercase tracking-widest">Initialize Sovereign Realm</p>
            </div>
            
            <div className="bg-white/5 p-8 rounded-3xl border border-white/10">
                <Globe className="text-primary mb-4" />
                <h4 className="font-bold mb-2">GLOBAL TRAFFIC</h4>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <motion.div initial={{width: 0}} animate={{width: '65%'}} className="h-full bg-primary" />
                </div>
                <p className="text-[10px] text-gray-500 mt-2 uppercase">65% Target Penetration</p>
            </div>
        </div>
      </div>

      <CompanyWizard isOpen={isWizardOpen} onClose={() => setIsWizardOpen(false)} />
    </div>
  );
}
