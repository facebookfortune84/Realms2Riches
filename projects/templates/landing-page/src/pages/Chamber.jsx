import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Chamber() {
  const [logs, setLogs] = useState([]);
  const scrollRef = useRef(null);

  useEffect(() => {
    const wsUrl = BACKEND_URL.replace('https', 'wss').replace('http', 'ws');
    const socket = new WebSocket(`${wsUrl}/ws/chamber`);

    socket.onmessage = (event) => {
      setLogs(prev => [...prev.slice(-100), {
        id: Date.now(),
        text: event.data,
        timestamp: new Date().toLocaleTimeString()
      }]);
    };

    return () => socket.close();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="min-h-screen bg-black p-4 md:p-10 font-mono relative overflow-hidden">
      {/* CRT Scanline Effect */}
      <div className="absolute inset-0 pointer-events-none z-50 opacity-10 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%]" />
      
      <div className="max-w-6xl mx-auto border-2 border-primary/30 rounded-lg bg-black/80 backdrop-blur-sm p-6 shadow-[0_0_50px_rgba(0,255,136,0.1)]">
        <div className="flex justify-between items-center mb-6 border-b border-primary/20 pb-4">
          <h1 className="text-primary text-2xl font-black tracking-widest animate-pulse">THE CHAMBER: RECURSIVE ENGINE ROOM</h1>
          <div className="flex gap-4 text-xs text-primary/60">
            <span>UPTIME: 99.99%</span>
            <span>AGENTS: 1,003 ACTIVE</span>
            <span className="text-red-500">LIVE FEED</span>
          </div>
        </div>

        <div 
          ref={scrollRef}
          className="h-[70vh] overflow-y-auto space-y-1 text-sm md:text-base custom-scrollbar"
        >
          {logs.map((log) => (
            <div key={log.id} className="flex gap-4 group">
              <span className="text-gray-700 shrink-0">[{log.timestamp}]</span>
              <span className="text-primary/80 group-hover:text-primary transition-colors">
                {log.text}
              </span>
            </div>
          ))}
          {logs.length === 0 && (
            <div className="text-primary animate-pulse">ESTABLISHING CONNECTION TO THE SWARM...</div>
          )}
        </div>

        <div className="mt-6 pt-4 border-t border-primary/20 text-[10px] text-gray-600 flex justify-between uppercase">
          <span>Sovereign ID: 0xDEADBEEF</span>
          <span>Warning: Authorized Access Only</span>
          <span>Realms2Riches OS v3.1.0</span>
        </div>
      </div>
    </div>
  );
}
