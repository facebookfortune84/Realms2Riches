import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Shield, Zap, Users, Globe, Database, Cpu, Terminal, Layers, Radio, Video, Share2, BarChart3 } from 'lucide-react';
import CompanyWizard from '../components/CompanyWizard';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [activity, setActivity] = useState([]);
  const [integrations, setIntegrations] = useState(null);
  const [telemetry, setTelemetry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  const fetchStats = async () => {
    const headers = { 'X-License-Key': import.meta.env.VITE_SOVEREIGN_LICENSE_KEY || 'mock_dev_key' };
    try {
      const [mRes, aRes, iRes, tRes] = await Promise.all([
        fetch(`${BACKEND_URL}/health`, { headers }),
        fetch(`${BACKEND_URL}/api/activity`, { headers }),
        fetch(`${BACKEND_URL}/api/integrations/status`, { headers }),
        fetch(`${BACKEND_URL}/api/telemetry/stats`, { headers })
      ]);
      setMetrics(await mRes.json());
      setActivity(await aRes.json());
      setIntegrations(await iRes.json());
      setTelemetry(await tRes.json());
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  useEffect(() => {
    fetchStats();
    const timer = setInterval(fetchStats, 5000);
    return () => clearInterval(timer);
  }, []);

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black font-mono">
        <div className="relative w-24 h-24 mb-8">
            <div className="absolute inset-0 border-4 border-primary/20 rounded-full animate-ping" />
            <div className="absolute inset-0 border-4 border-primary rounded-full animate-spin border-t-transparent" />
            <Cpu className="absolute inset-0 m-auto text-primary" size={32} />
        </div>
        <div className="text-primary animate-pulse tracking-[0.5em] uppercase text-[10px]">Neural Synchronizing...</div>
    </div>
  );

  return (
    <div className="py-10 max-w-7xl mx-auto px-4 font-mono text-white">
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 gap-6">
        <div>
            <div className="flex items-center gap-2 text-primary text-[10px] mb-2 tracking-[0.5em] uppercase">
                <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                Sovereign OS v3.8.2-PLATINUM
            </div>
            <h2 className="text-6xl md:text-8xl font-black tracking-tighter italic leading-none">THE <span className="text-primary">CORE</span></h2>
        </div>
        <div className="flex gap-4">
            <div className="bg-white/5 px-6 py-3 rounded-2xl border border-white/10 flex items-center gap-3">
                <Radio size={16} className="text-primary animate-pulse" />
                <span className="text-[10px] text-gray-400 uppercase tracking-widest font-bold">Neural Link: ACTIVE</span>
            </div>
            <button onClick={fetchStats} className="p-3 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-colors">
                <Activity size={18} className="text-primary" />
            </button>
        </div>
      </div>

      {/* INTEGRATION GRID */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-12">
        {integrations && Object.entries(integrations).map(([k, v]) => (
            <div key={k} className="bg-black/40 p-4 rounded-2xl border border-white/5 flex flex-col gap-2 group hover:border-primary/20 transition-all">
                <div className="flex justify-between items-center">
                    <span className="text-[9px] font-bold uppercase text-gray-500">{k}</span>
                    <div className={`w-1.5 h-1.5 rounded-full ${v === 'active' ? 'bg-primary shadow-[0_0_8px_#00ff88]' : 'bg-red-500/30'}`} />
                </div>
                <div className={`text-[10px] font-black ${v === 'active' ? 'text-white' : 'text-gray-700'}`}>
                    {v === 'active' ? 'UPLINK_STABLE' : 'OFFLINE'}
                </div>
            </div>
        ))}
      </div>

      {/* MATRIX WORKSTREAMS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        {metrics?.cells && Object.entries(metrics.cells).map(([name, data]) => (
            <div key={name} className="bg-gradient-to-br from-white/5 to-transparent border-2 border-white/5 p-8 rounded-3xl relative overflow-hidden group hover:border-primary/30 transition-all">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-20 transition-opacity">
                    <Layers size={100} />
                </div>
                <div className="flex justify-between items-start mb-8">
                    <div>
                        <h3 className="text-primary font-black uppercase tracking-tighter text-2xl">CELL_{name}</h3>
                        <p className="text-gray-500 text-[9px] uppercase tracking-[0.2em]">Matrix Shard 0x0{name.length}</p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-[9px] font-black uppercase ${data.active > 0 ? 'bg-primary text-black animate-pulse' : 'bg-white/5 text-gray-600'}`}>
                        {data.active > 0 ? 'Executing' : 'Standby'}
                    </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-black/40 p-4 rounded-2xl border border-white/5">
                        <div className="text-[10px] text-gray-600 uppercase mb-1">Queue</div>
                        <div className="text-2xl font-black text-white">{data.queued}</div>
                    </div>
                    <div className="bg-black/40 p-4 rounded-2xl border border-white/5">
                        <div className="text-[10px] text-gray-600 uppercase mb-1">Units</div>
                        <div className="text-2xl font-black text-primary">{data.units}</div>
                    </div>
                </div>
            </div>
        ))}
      </div>

      {/* ANALYTICS & ACTIVITY */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* LIVE TELEMETRY */}
        <div className="lg:col-span-1 space-y-6">
            <div className="bg-black/40 p-6 rounded-3xl border border-white/5">
                <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                    <BarChart3 size={14} className="text-primary" />
                    Market Telemetry
                </h4>
                <div className="space-y-6">
                    <div>
                        <div className="flex justify-between text-[10px] mb-2">
                            <span className="text-gray-400">Total Outreach</span>
                            <span className="text-primary">{telemetry?.messages_sent || 0}</span>
                        </div>
                        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                            <motion.div animate={{width: '75%'}} className="h-full bg-primary" />
                        </div>
                    </div>
                    <div>
                        <div className="flex justify-between text-[10px] mb-2">
                            <span className="text-gray-400">Impressions</span>
                            <span className="text-blue-400">{telemetry?.impressions || 0}</span>
                        </div>
                        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                            <motion.div animate={{width: '45%'}} className="h-full bg-blue-400" />
                        </div>
                    </div>
                    <div className="pt-4 border-t border-white/5">
                        <div className="text-[10px] text-gray-600 uppercase mb-1 text-center">Net Sovereign Revenue</div>
                        <div className="text-3xl font-black text-center text-white">${telemetry?.revenue?.toFixed(2)}</div>
                    </div>
                </div>
            </div>

            <div className="bg-primary p-8 rounded-3xl text-black cursor-pointer hover:scale-[1.02] active:scale-95 transition-all shadow-[0_0_30px_rgba(0,255,136,0.2)]" onClick={() => setIsWizardOpen(true)}>
                <Zap size={32} className="mb-4" />
                <h4 className="text-2xl font-black uppercase tracking-tighter leading-none mb-2">Genesis<br/>Portal</h4>
                <p className="text-[10px] font-bold opacity-70 uppercase tracking-widest">Architect New Realm</p>
            </div>
        </div>

        {/* LOG FEED */}
        <div className="lg:col-span-3 bg-black/40 p-8 rounded-3xl border border-white/5 relative">
            <div className="flex justify-between items-center mb-8">
                <h3 className="text-lg font-bold flex items-center gap-3">
                    <Terminal className="text-primary" size={20} />
                    NEURAL ACTIVITY LOG
                </h3>
                <div className="flex items-center gap-2 text-[9px] text-gray-500 uppercase">
                    <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" />
                    Live Transmission
                </div>
            </div>
            
            <div className="space-y-2 h-[450px] overflow-y-auto custom-scrollbar pr-4 font-mono text-[11px]">
                {activity.length > 0 ? activity.map((a, i) => (
                    <div key={i} className="flex gap-4 p-3 rounded-xl hover:bg-white/5 transition-colors border border-transparent hover:border-white/5 group">
                        <span className="text-gray-700 shrink-0">[{new Date(a.t).toLocaleTimeString()}]</span>
                        <div className="flex flex-col gap-1 overflow-hidden">
                            <div className="flex items-center gap-2">
                                <span className="text-primary font-black uppercase">[{a.a}]</span>
                                <span className="text-white font-bold opacity-80">{a.op}</span>
                            </div>
                            <span className="text-gray-500 line-clamp-1 group-hover:line-clamp-none transition-all">{a.r}</span>
                        </div>
                    </div>
                )) : (
                    <div className="flex items-center justify-center h-full text-gray-700 uppercase tracking-widest animate-pulse">
                        Uplinking to Swarm Intelligence...
                    </div>
                )}
            </div>
        </div>
      </div>

      <CompanyWizard isOpen={isWizardOpen} onClose={() => setIsWizardOpen(false)} />
    </div>
  );
}
