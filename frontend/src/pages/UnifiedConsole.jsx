import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Activity, Zap, Shield, TrendingUp, Users, Cpu, Server } from 'lucide-react';
import { getApiBase } from '../lib/apiBase';

export default function UnifiedConsole() {
  const [activeTab, setActiveTab] = useState('telemetry');
  const [stats, setTelemetry] = useState({ clicks: 0, conversions: 0, revenue: 0, impressions: 0 });
  const [logs, setLogs] = useState([]);
  const [command, setCommand] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${getApiBase()}/api/telemetry/stats`);
        const data = await res.json();
        setTelemetry(data);
      } catch (e) { console.error(e); }
    };

    const fetchLogs = async () => {
      try {
        const res = await fetch(`${getApiBase()}/api/activity`);
        const data = await res.json();
        setLogs(data);
      } catch (e) { console.error(e); }
    };

    fetchStats();
    fetchLogs();
    const interval = setInterval(() => { fetchStats(); fetchLogs(); }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCommand = async (e) => {
    e.preventDefault();
    if (!command.trim()) return;
    setIsProcessing(true);
    try {
      const res = await fetch(`${getApiBase()}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: command })
      });
      const data = await res.json();
      if (data.status === 'completed') {
        // Result is already in logs via activity refresh
        setCommand('');
      }
    } catch (e) { console.error(e); }
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-black text-white p-4 md:p-8 font-mono">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header / Global Status */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-primary/30 pb-6 gap-4">
          <div>
            <h1 className="text-3xl font-black tracking-tighter flex items-center gap-3">
              <div className="w-3 h-3 bg-primary rounded-full animate-pulse" />
              SOVEREIGN_COMMAND_CENTER_v5.8.2
            </h1>
            <p className="text-gray-500 text-xs mt-1">UPLINK STATUS: OPTIMAL | ENCRYPTION: SHA-256</p>
          </div>
          <div className="flex gap-4">
            <div className="bg-gray-900 px-4 py-2 rounded border border-gray-800">
              <div className="text-[10px] text-gray-500 uppercase">Revenue</div>
              <div className="text-xl font-bold text-primary">${stats.revenue.toFixed(2)}</div>
            </div>
            <div className="bg-gray-900 px-4 py-2 rounded border border-gray-800">
              <div className="text-[10px] text-gray-500 uppercase">Agents</div>
              <div className="text-xl font-bold text-white">1,000</div>
            </div>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left: Telemetry & Controls */}
          <div className="lg:col-span-4 space-y-6">
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: 'Impressions', val: stats.impressions, icon: TrendingUp },
                { label: 'Conversions', val: stats.conversions, icon: Zap },
                { label: 'Network Load', val: '12%', icon: Cpu },
                { label: 'Sovereignty', val: '100%', icon: Shield },
              ].map((s, i) => (
                <div key={i} className="bg-card-bg p-4 rounded-xl border border-gray-800">
                  <s.icon className="w-4 h-4 text-primary mb-2" />
                  <div className="text-[10px] text-gray-500 uppercase">{s.label}</div>
                  <div className="text-xl font-bold">{s.val}</div>
                </div>
              ))}
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-900/50 p-6 rounded-2xl border border-gray-800">
              <h3 className="text-sm font-bold mb-4 uppercase tracking-widest text-primary">Strategic Actions</h3>
              <div className="space-y-3">
                {[
                  { label: 'Launch Ad Swarm', path: '#' },
                  { label: 'Optimize SEO Forge', path: '#' },
                  { label: 'High-Ticket Affiliate Hub', path: '/affiliate-hub' },
                  { label: 'Deploy Cold Outreach', path: '#' }
                ].map((action, i) => (
                  <Link key={i} to={action.path} className="w-full text-left px-4 py-3 bg-black rounded border border-gray-800 hover:border-primary/50 transition-colors flex justify-between items-center group">
                    <span className="text-sm">{action.label}</span>
                    <Zap className="w-3 h-3 text-gray-600 group-hover:text-primary" />
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Unified Terminal */}
          <div className="lg:col-span-8 flex flex-col h-[600px] bg-card-bg rounded-2xl border border-gray-800 overflow-hidden shadow-2xl shadow-primary/5">
            <div className="bg-gray-900 px-6 py-3 border-b border-gray-800 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-primary" />
                <span className="text-xs font-bold uppercase tracking-widest">Neural Uplink Terminal</span>
              </div>
              <div className="flex gap-1">
                <div className="w-2 h-2 rounded-full bg-red-500/50" />
                <div className="w-2 h-2 rounded-full bg-yellow-500/50" />
                <div className="w-2 h-2 rounded-full bg-green-500/50" />
              </div>
            </div>

            {/* Activity Stream */}
            <div className="flex-grow overflow-y-auto p-6 space-y-4 scrollbar-hide bg-black/40">
              {logs.map((log, i) => (
                <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  key={i} 
                  className="flex gap-4 text-sm"
                >
                  <span className="text-gray-600 shrink-0">[{log.t?.split('T')[1].split('.')[0]}]</span>
                  <span className="text-primary font-bold shrink-0">{log.a}:</span>
                  <span className="text-gray-300 leading-relaxed italic">{log.r}</span>
                </motion.div>
              ))}
              {isProcessing && (
                <div className="flex gap-4 text-sm animate-pulse">
                  <span className="text-primary font-bold">SWARM:</span>
                  <span className="text-gray-500 italic">Processing high-level directive...</span>
                </div>
              )}
            </div>

            {/* Command Input */}
            <form onSubmit={handleCommand} className="p-4 bg-gray-900/50 border-t border-gray-800">
              <div className="relative">
                <input 
                  type="text"
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  placeholder="Enter high-level directive for the swarm..."
                  className="w-full bg-black border border-gray-800 rounded-lg px-4 py-4 pr-16 focus:outline-none focus:border-primary transition-colors text-primary font-mono text-sm"
                />
                <button 
                  type="submit"
                  disabled={isProcessing}
                  className="absolute right-2 top-2 bottom-2 bg-primary text-black px-4 rounded font-bold hover:scale-105 transition-transform disabled:opacity-50"
                >
                  SEND
                </button>
              </div>
            </form>
          </div>

        </div>
      </div>
    </div>
  );
}
