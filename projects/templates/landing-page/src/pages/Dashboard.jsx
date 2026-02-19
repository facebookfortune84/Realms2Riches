import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Shield, Zap, Users, Globe, Database, Cpu, Terminal } from 'lucide-react';
import CompanyWizard from '../components/CompanyWizard';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [diag, setDiag] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  const fetchStats = async () => {
    try {
      const [mRes, dRes] = await Promise.all([
        fetch(`${BACKEND_URL}/health`),
        fetch(`${BACKEND_URL}/api/diagnostics`)
      ]);
      const mData = await mRes.json();
      const dData = await dRes.json();
      setMetrics(mData);
      setDiag(dData);
    } catch (err) {
      console.error("Failed to load metrics", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center space-y-4 font-mono">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <div className="text-primary animate-pulse tracking-[0.3em] uppercase text-xs">Accessing Sovereign Core...</div>
    </div>
  );

  const stats = [
    { label: "Active Agents", value: metrics?.agents || 1000, icon: Users, color: "text-primary" },
    { label: "Swarm State", value: metrics?.swarm_active ? "READY" : "RESTRICTED", icon: Shield, color: metrics?.swarm_active ? "text-green-400" : "text-red-400" },
    { label: "Memory Docs", value: metrics?.rag_docs || 0, icon: Database, color: "text-blue-400" },
    { label: "DB Link", value: diag?.db === 'connected' ? "ACTIVE" : "ERROR", icon: Activity, color: diag?.db === 'connected' ? "text-primary" : "text-red-500" }
  ];

  return (
    <div className="py-10 max-w-7xl mx-auto px-4 font-mono">
      <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
        <div>
            <div className="text-primary text-xs mb-2 tracking-[0.5em] uppercase">Sovereign OS v3.1.0</div>
            <h2 className="text-5xl md:text-7xl font-black tracking-tighter">FOUNDER <span className="text-primary">COCKPIT</span></h2>
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
                        LIVE NEURAL TELEMETRY
                    </h3>
                    <div className="flex gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary animate-ping" />
                        <span className="text-[10px] text-primary">RECURSIVE_UPSTREAM</span>
                    </div>
                </div>
                <div className="space-y-3 font-mono text-[11px] h-80 overflow-y-auto custom-scrollbar">
                    <div className="text-primary/60">[0.001s] Sovereign Core Ignition: Authorized.</div>
                    <div className="text-gray-600">[0.004s] Multi-agent multiplexing protocol engaged...</div>
                    <div className="text-primary/40">[0.012s] Mapping 150+ logic domains to active swarm.</div>
                    <div className="text-gray-600">[0.015s] PostgreSQL Vector Extension: Latency 2ms.</div>
                    <div className="text-primary/20">[0.022s] Consensus reached on task_id: {Math.random().toString(36).substring(7)}.</div>
                    <div className="text-green-400/50">[0.045s] Integrity Check: 0x{Math.random().toString(16).substring(2, 10).toUpperCase()} Verified.</div>
                    <div className="text-gray-700 animate-pulse">_ Awaiting user directive...</div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-primary/5 p-8 rounded-3xl border border-primary/10">
                    <Zap className="text-primary mb-4" />
                    <h4 className="text-white font-bold mb-2">Build a Company</h4>
                    <p className="text-xs text-gray-500 mb-6">Deploy a full-stack corporate structure in 60 seconds.</p>
                    <button 
                        onClick={() => setIsWizardOpen(true)}
                        className="w-full bg-primary text-black py-3 rounded-xl font-bold text-xs uppercase hover:scale-105 transition-transform"
                    >
                        Initialize Blueprint
                    </button>
                </div>
                <div className="bg-blue-500/5 p-8 rounded-3xl border border-blue-500/10">
                    <Globe className="text-blue-400 mb-4" />
                    <h4 className="text-white font-bold mb-2">Global Scale</h4>
                    <p className="text-xs text-gray-500 mb-6">Distribute agents across 12 edge clusters.</p>
                    <button className="w-full border border-blue-500/20 text-blue-400 py-3 rounded-xl font-bold text-xs uppercase">Manage Nodes</button>
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

