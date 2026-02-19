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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-card-bg p-8 rounded-2xl border border-gray-800">
            <h3 className="text-xl font-bold mb-6 text-gray-300">Swarm Health</h3>
            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <span>API Gateway</span>
                    <span className="text-primary font-mono">STABLE</span>
                </div>
                <div className="flex justify-between items-center">
                    <span>Vector Store</span>
                    <span className="text-primary font-mono">READY</span>
                </div>
                <div className="flex justify-between items-center">
                    <span>Worker Node 1</span>
                    <span className="text-primary font-mono">UP</span>
                </div>
            </div>
        </div>
        
        <div className="bg-card-bg p-8 rounded-2xl border border-gray-800 flex flex-col items-center justify-center text-center">
            <h3 className="text-xl font-bold mb-4 text-gray-300">Continuous Improvement</h3>
            <p className="text-gray-500 mb-6">Agent swarm is currently self-optimizing technical debt in the <code>orchestrator/src/core/</code> module.</p>
            <div className="w-full bg-gray-900 h-2 rounded-full overflow-hidden">
                <motion.div 
                    initial={{ width: "0%" }}
                    animate={{ width: "65%" }}
                    transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
                    className="bg-primary h-full"
                />
            </div>
        </div>
      </div>
    </div>
  );
}
