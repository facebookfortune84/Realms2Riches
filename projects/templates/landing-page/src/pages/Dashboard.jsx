import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BACKEND_URL}/metrics`)
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(err => console.error("Failed to load metrics", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-20">Accessing Swarm Metrics...</div>;

  const displayMetrics = [
    { label: "Tasks Processed", value: metrics?.tasks_processed_total || 0, color: "text-primary" },
    { label: "Global Fleet Size", value: metrics?.agents_online || 0, color: "text-blue-400" },
    { label: "Voice Sessions", value: metrics?.voice_sessions_total || 0, color: "text-purple-400" },
    { label: "Build Integrity", value: "Verified", color: "text-green-400" }
  ];

  return (
    <div className="py-10">
      <h2 className="text-4xl font-black mb-10 tracking-tight">FOUNDER DASHBOARD</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        {displayMetrics.map((m, i) => (
            <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                key={i} 
                className="bg-card-bg p-8 rounded-2xl border border-gray-800"
            >
                <div className="text-gray-500 text-sm font-bold uppercase tracking-widest mb-2">{m.label}</div>
                <div className={`text-5xl font-black ${m.color}`}>{m.value}</div>
            </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-card-bg p-8 rounded-2xl border border-gray-800 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent animate-pulse" />
            <h3 className="text-xl font-bold mb-6 text-gray-300 flex justify-between">
                NEURAL PULSE 
                <span className="text-primary text-xs font-mono animate-pulse">LIVE CONSCIOUSNESS STREAM</span>
            </h3>
            <div className="space-y-4 font-mono text-sm h-64 overflow-y-auto custom-scrollbar">
                <div className="text-primary opacity-80">[0.001s] Recursive RAG lookup initiated...</div>
                <div className="text-blue-400 opacity-70">[0.004s] Unit Engineering_12 proposed logic refactor.</div>
                <div className="text-purple-400 opacity-60">[0.012s] ToolSmith forging dynamic_scrapper.py...</div>
                <div className="text-green-400 opacity-50">[0.015s] Build Integrity SHA-256 verified.</div>
                <div className="text-gray-500">[0.022s] Swarm consensus reached on task_id: sovereign-001.</div>
                <div className="text-primary opacity-40">[0.030s] Data_Research_42 mining market sentiment.</div>
            </div>
        </div>
        
        <div className="bg-card-bg p-8 rounded-2xl border border-gray-800 flex flex-col justify-center items-center text-center">
            <div className="w-32 h-32 mb-6 relative">
                <div className="absolute inset-0 border-4 border-primary/20 rounded-full animate-ping" />
                <div className="absolute inset-2 border-2 border-primary/40 rounded-full animate-pulse" />
                <div className="absolute inset-4 bg-primary/10 rounded-full flex items-center justify-center font-black text-primary text-3xl">
                    1k+
                </div>
            </div>
            <h3 className="text-xl font-bold mb-2 text-white">Sovereign Swarm</h3>
            <p className="text-gray-500 text-sm">Hyper-parallelized agent execution across 150+ multiplexed domains.</p>
        </div>
      </div>
    </div>
  );
}
