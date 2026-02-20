import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Shield, Zap, Users, Globe, Database, Cpu, Terminal } from 'lucide-react';
import CompanyWizard from '../components/CompanyWizard';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [activity, setActivity] = useState([]);
  const [diag, setDiag] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  const fetchStats = async () => {
    try {
      const [mRes, dRes, aRes] = await Promise.all([
        fetch(`${BACKEND_URL}/health`),
        fetch(`${BACKEND_URL}/api/diagnostics`),
        fetch(`${BACKEND_URL}/api/activity`)
      ]);
      setMetrics(await mRes.json());
      setDiag(await dRes.json());
      setActivity(await aRes.json());
    } catch (err) {
      console.error("Failed to load metrics", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center space-y-4 font-mono">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <div className="text-primary animate-pulse tracking-[0.3em] uppercase text-xs">Uplinking to Sovereign Matrix...</div>
    </div>
  );

  const stats = [
    { label: "Active Agents", value: metrics?.agents || 1000, icon: Users, color: "text-primary" },
    { label: "Swarm State", value: metrics?.swarm_active ? "READY" : "RESTRICTED", icon: Shield, color: metrics?.swarm_active ? "text-green-400" : "text-red-400" },
    { label: "Memory Docs", value: metrics?.rag_docs || 0, icon: Database, color: "text-blue-400" },
    { label: "Matrix Link", value: diag?.db === 'connected' ? "SECURE" : "UNSTABLE", icon: Activity, color: diag?.db === 'connected' ? "text-primary" : "text-red-500" }
  ];

  return (
    <div className="py-10 max-w-7xl mx-auto px-4 font-mono">
      <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
        <div>
            <div className="text-primary text-xs mb-2 tracking-[0.5em] uppercase">Sovereign OS v3.3.0</div>
            <h2 className="text-5xl md:text-7xl font-black tracking-tighter">FOUNDER <span className="text-primary">DASHBOARD</span></h2>
        </div>
        <div className="bg-white/5 px-6 py-3 rounded-full border border-white/10 flex items-center gap-3">
            <div className={`w-2 h-2 rounded-full animate-pulse ${metrics?.status === 'ok' ? 'bg-primary' : 'bg-red-500'}`} />
            <span className="text-[10px] text-gray-400 uppercase tracking-widest">System Integrity: {metrics?.status === 'ok' ? 'Verified' : 'Degraded'}</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {stats.map((s, i) => (
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                key={i} 
                className="bg-black/40 backdrop-blur-xl p-8 rounded-3xl border border-white/5 hover:border-primary/30 transition-all group"
            >
                <div className="flex justify-between items-start mb-4">
                    <s.icon size={24} className="text-gray-600 group-hover:text-primary transition-colors" />
                    <span className="text-[10px] text-gray-700">00{i+1}</span>
                </div>
                <div className="text-gray-500 text-[10px] font-bold uppercase tracking-widest mb-1">{s.label}</div>
                <div className={`text-4xl font-black ${s.color}`}>{s.value}</div>
            </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
            <div className="bg-black/40 p-8 rounded-3xl border border-white/5 relative overflow-hidden">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-bold text-gray-300 flex items-center gap-2">
                        <Terminal size={18} className="text-primary" />
                        AUTONOMOUS ACTIVITY LOG
                    </h3>
                    <div className="flex gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary animate-ping" />
                        <span className="text-[10px] text-primary">REALTIME_FEED</span>
                    </div>
                </div>
                <div className="space-y-4 font-mono text-[10px] h-80 overflow-y-auto custom-scrollbar">
                    {activity.length > 0 ? activity.map((a, i) => (
                        <div key={i} className="flex gap-4 p-2 border-b border-white/5 hover:bg-white/5 transition-colors">
                            <span className="text-gray-600">[{new Date(a.timestamp).toLocaleTimeString()}]</span>
                            <span className="text-primary font-bold">[{a.agent}]</span>
                            <span className="text-white">{a.action}:</span>
                            <span className="text-gray-400 italic">{a.result}</span>
                        </div>
                    )) : <div className="text-gray-600">Waiting for agent activity...</div>}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-primary/5 p-8 rounded-3xl border border-primary/10 hover:border-primary/30 transition-all cursor-pointer group" onClick={() => setIsWizardOpen(true)}>
                    <Zap className="text-primary mb-4" />
                    <h4 className="text-white font-bold mb-2 uppercase text-sm">Build a Company</h4>
                    <p className="text-[10px] text-gray-500 mb-6">Deploy a full-stack corporate structure in 60 seconds.</p>
                    <button className="w-full bg-primary text-black py-3 rounded-xl font-bold text-xs uppercase group-hover:bg-primary/90">Initialize Blueprint</button>
                </div>
                <div className="bg-blue-500/5 p-8 rounded-3xl border border-blue-500/10 hover:border-blue-500/30 transition-all cursor-pointer group">
                    <Globe className="text-blue-400 mb-4 group-hover:scale-110 transition-transform" />
                    <h4 className="text-white font-bold mb-2 uppercase text-sm">Global Matrix</h4>
                    <p className="text-[10px] text-gray-500 mb-2">12 Active Clusters across 4 Regions.</p>
                    <div className="grid grid-cols-6 gap-1 mt-4">
                        {[...Array(12)].map((_, i) => (
                            <div key={i} className="h-4 bg-blue-500/20 rounded-sm border border-blue-500/30 animate-pulse" />
                        ))}
                    </div>
                </div>
            </div>

            {/* REVENUE PROJECTIONS */}
            <div className="bg-card-bg p-8 rounded-3xl border border-white/5 mt-8">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-bold text-gray-300">REVENUE FORECAST (SCENARIO A)</h3>
                    <span className="text-[10px] text-green-400 bg-green-400/10 px-3 py-1 rounded-full uppercase tracking-wider">Growth Trajectory</span>
                </div>
                <div className="space-y-4">
                    {[
                        { label: 'Q1', value: 15, goal: '$15k' },
                        { label: 'Q2', value: 45, goal: '$45k' },
                        { label: 'Q3', value: 80, goal: '$80k' },
                        { label: 'Q4', value: 100, goal: '$120k' }
                    ].map((q, i) => (
                        <div key={i} className="flex items-center gap-4 text-xs font-mono text-gray-500">
                            <span className="w-8">{q.label}</span>
                            <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                                <motion.div 
                                    initial={{ width: 0 }}
                                    animate={{ width: `${q.value}%` }}
                                    transition={{ duration: 1, delay: i * 0.2 }}
                                    className="h-full bg-gradient-to-r from-blue-500 to-primary"
                                />
                            </div>
                            <span className="w-12 text-right text-white">{q.goal}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
        
        <CompanyWizard isOpen={isWizardOpen} onClose={() => setIsWizardOpen(false)} />
        
        <div className="bg-black/40 p-8 rounded-3xl border border-white/5 flex flex-col items-center justify-center text-center relative overflow-hidden group">
            <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="w-48 h-48 mb-8 relative">
                <div className="absolute inset-0 border-[1px] border-primary/10 rounded-full animate-[spin_10s_linear_infinite]" />
                <div className="absolute inset-4 border-[1px] border-primary/20 rounded-full animate-[spin_6s_linear_infinite_reverse]" />
                <div className="absolute inset-8 border-[1px] border-primary/30 rounded-full animate-[spin_3s_linear_infinite]" />
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                        <div className="text-5xl font-black text-primary leading-none">100%</div>
                        <div className="text-[10px] text-gray-600 uppercase mt-2">Health</div>
                    </div>
                </div>
            </div>
            <h3 className="text-xl font-bold mb-2 text-white uppercase tracking-tighter">Swarm Integrity</h3>
            <p className="text-xs text-gray-500 px-4">Hyper-parallelized agent execution across 150+ multiplexed domains with zero-trust validation.</p>
            
            <div className="mt-10 w-full space-y-2">
                <div className="flex justify-between text-[10px] text-gray-600 uppercase">
                    <span>CPU Load</span>
                    <span className="text-primary">12%</span>
                </div>
                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-primary w-[12%]" />
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}
