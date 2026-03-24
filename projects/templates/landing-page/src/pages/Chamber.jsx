import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Cpu, HardDrive, Download, AlertCircle } from 'lucide-react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://api.realms2riches.com";

export default function Chamber() {
  const [logs, setLogs] = useState([]);
  const [artifacts, setArtifacts] = useState([]);
  const scrollRef = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    const token = import.meta.env.VITE_SOVEREIGN_LICENSE_KEY || '';
    const wsUrl = BACKEND_URL.replace('https', 'wss').replace('http', 'ws');
    const socket = new WebSocket(`${wsUrl}/ws/chamber?token=${token}`);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'log') {
          const newLog = {
            id: Date.now() + Math.random(),
            timestamp: new Date(data.timestamp).toLocaleTimeString(),
            agent: data.agent,
            op: data.operation,
            result: data.result
          };
          
          setLogs(prev => [...prev.slice(-150), newLog]);

          // Detect downloadable artifacts
          if (data.result && data.result.includes('/swarms/swarm_')) {
            const urlMatch = data.result.match(/\/swarms\/swarm_[a-z0-9]+\.json/);
            if (urlMatch) {
              setArtifacts(prev => [...prev, {
                id: Date.now(),
                url: `${BACKEND_URL}${urlMatch[0]}`,
                name: urlMatch[0].split('/').pop()
              }]);
            }
          }
        }
      } catch (e) {
        // Fallback for non-json
        setLogs(prev => [...prev.slice(-150), {
          id: Date.now(),
          timestamp: new Date().toLocaleTimeString(),
          agent: 'SYSTEM',
          op: 'RAW_DATA',
          result: event.data
        }]);
      }
    };

    return () => socket.close();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="min-h-screen bg-black p-4 md:p-8 font-mono relative overflow-hidden text-primary">
      {/* Matrix Background Effect */}
      <div className="absolute inset-0 pointer-events-none opacity-5 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]" />
      
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6 h-[85vh]">
        
        {/* SIDEBAR: SYSTEM STATUS */}
        <div className="lg:col-span-1 space-y-6">
            <div className="bg-black border-2 border-primary/20 p-6 rounded-2xl shadow-[0_0_30px_rgba(0,255,136,0.05)]">
                <div className="flex items-center gap-3 mb-6">
                    <Cpu className="text-primary animate-pulse" />
                    <h2 className="font-black text-white uppercase tracking-tighter">System Core</h2>
                </div>
                <div className="space-y-4 text-[10px]">
                    <div className="flex justify-between border-b border-white/5 pb-2">
                        <span className="text-gray-500">KERNEL</span>
                        <span className="text-white">SOVEREIGN_v5.8.2</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 pb-2">
                        <span className="text-gray-500">LOAD</span>
                        <span className="text-white">OPTIMAL</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 pb-2">
                        <span className="text-gray-500">UPTIME</span>
                        <span className="text-white">99.999%</span>
                    </div>
                </div>
            </div>

            <div className="bg-black border-2 border-primary/20 p-6 rounded-2xl shadow-[0_0_30px_rgba(0,255,136,0.05)]">
                <div className="flex items-center gap-3 mb-6">
                    <HardDrive className="text-blue-400" />
                    <h2 className="font-black text-white uppercase tracking-tighter">Genesis Artifacts</h2>
                </div>
                <div className="space-y-3">
                    {artifacts.length === 0 ? (
                        <p className="text-[10px] text-gray-600 italic">No swarms generated in this session.</p>
                    ) : artifacts.map(art => (
                        <a 
                            key={art.id}
                            href={art.url}
                            download
                            className="flex items-center justify-between p-3 bg-white/5 border border-white/10 rounded-xl hover:border-primary/50 transition-all group"
                        >
                            <span className="text-[10px] text-gray-400 truncate max-w-[120px]">{art.name}</span>
                            <Download size={14} className="text-primary group-hover:scale-110 transition-transform" />
                        </a>
                    ))}
                </div>
            </div>
        </div>

        {/* MAIN FEED: RECURSIVE LOGS */}
        <div className="lg:col-span-3 bg-black border-2 border-primary/30 rounded-2xl flex flex-col relative overflow-hidden shadow-[0_0_50px_rgba(0,255,136,0.1)]">
            <div className="p-4 bg-primary/10 border-b border-primary/20 flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <Terminal size={18} className="text-primary" />
                    <h1 className="text-white text-sm font-black tracking-widest uppercase italic">The Chamber // Recursive Live Feed</h1>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                    <span className="text-[10px] font-bold text-white uppercase">Neural Link Established</span>
                </div>
            </div>

            <div 
                ref={scrollRef}
                className="flex-grow overflow-y-auto p-6 space-y-2 custom-scrollbar bg-[radial-gradient(circle_at_50%_0%,rgba(0,255,136,0.03),transparent)]"
            >
                {logs.map((log) => (
                    <motion.div 
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        key={log.id} 
                        className="flex gap-4 text-xs md:text-sm group py-1 border-b border-white/5 last:border-0"
                    >
                        <span className="text-gray-700 shrink-0 tabular-nums">[{log.timestamp}]</span>
                        <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2">
                                <span className="text-primary font-black uppercase tracking-tighter">[{log.agent}]</span>
                                <span className="text-white font-bold opacity-60 uppercase italic">{log.op}</span>
                            </div>
                            <span className="text-gray-400 group-hover:text-white transition-colors leading-relaxed">
                                {log.result}
                            </span>
                        </div>
                    </motion.div>
                ))}
                {logs.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full gap-4">
                        <AlertCircle className="text-gray-800 animate-spin" size={40} />
                        <div className="text-gray-700 text-xs uppercase tracking-[0.5em] animate-pulse">Uplinking to Swarm Intelligence...</div>
                    </div>
                )}
            </div>

            <div className="p-4 border-t border-white/5 bg-black/50 text-[9px] text-gray-600 flex justify-between uppercase font-bold tracking-widest">
                <span>Memory: 0xDEADBEEF</span>
                <span>Recursive Stack: {logs.length} Operations</span>
                <span>Swarm: 750 Industrial Units</span>
            </div>
        </div>
      </div>
    </div>
  );
}

