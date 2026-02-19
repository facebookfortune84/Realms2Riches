import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function LaunchControl() {
  const [status, setStatus] = useState('idle'); 
  const [diag, setDiag] = useState({ backend: 'checking', tunnel: 'checking' });
  const [launchData, setLaunchData] = useState(null);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const probe = async () => {
        try {
            const res = await fetch(`${BACKEND_URL}/health`, { mode: 'cors' });
            if (res.ok) setDiag({ backend: 'ONLINE', tunnel: 'ACTIVE' });
            else setDiag({ backend: 'ERROR', tunnel: 'ACTIVE' });
        } catch (e) {
            setDiag({ backend: 'OFFLINE', tunnel: 'UNREACHABLE' });
        }
    };
    probe();
    const interval = setInterval(probe, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleLaunch = async () => {
    setStatus('launching');
    setLogs(["> Initiating Signature Handshake...", "> Verifying Master Key..."]);

    try {
        const res = await fetch(`${BACKEND_URL}/api/sovereign/launch`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ signature: "verified_mock_signature" })
        });
        
        if (!res.ok) throw new Error("Verification Failed");
        const data = await res.json();
        
        setLaunchData(data);
        setStatus('active');
    } catch (err) {
        setLogs(prev => [...prev, "❌ ERROR: CONNECTION REFUSED BY TUNNEL", "💡 Fix: Ensure ngrok is running and URL matches .env.prod"]);
        setStatus('idle');
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4 font-mono relative overflow-hidden">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,136,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,136,0.05)_1px,transparent_1px)] bg-[size:40px_40px]" />
      
      <div className="w-full max-w-2xl relative z-10">
        <div className="bg-black border-2 border-primary/20 p-8 rounded-3xl shadow-2xl">
          
          <div className="flex justify-between items-center mb-8 border-b border-primary/10 pb-4">
            <span className="text-[10px] text-gray-500 uppercase tracking-widest">Sovereign Command</span>
            <div className="flex gap-4">
                <span className={`text-[10px] ${diag.tunnel === 'ACTIVE' ? 'text-primary' : 'text-red-500'}`}>TUNNEL: {diag.tunnel}</span>
                <span className={`text-[10px] ${diag.backend === 'ONLINE' ? 'text-primary' : 'text-red-500'}`}>API: {diag.backend}</span>
            </div>
          </div>

          <AnimatePresence mode="wait">
            {status === 'idle' && (
              <div className="text-center space-y-10 py-10">
                <button 
                  onClick={handleLaunch}
                  disabled={diag.backend !== 'ONLINE'}
                  className={`group relative p-1 rounded-full transition-all duration-500 ${diag.backend === 'ONLINE' ? 'bg-primary/20 hover:bg-primary/40' : 'bg-red-500/10 grayscale'}`}
                >
                  <div className="bg-black rounded-full p-8 border-2 border-primary shadow-[0_0_30px_rgba(0,255,136,0.2)]">
                    <span className="text-primary font-black text-2xl">LAUNCH</span>
                  </div>
                </button>
                
                <div className="space-y-2 text-left bg-black/50 p-4 rounded-lg border border-white/5">
                    {logs.map((log, i) => <div key={i} className="text-[10px] text-gray-500">{log}</div>)}
                    {diag.backend !== 'ONLINE' && (
                        <div className="text-[10px] text-yellow-500 animate-pulse">⚠️ STANDBY: Waiting for local backend connection...</div>
                    )}
                </div>
              </div>
            )}

            {status === 'active' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6 text-center py-10">
                <div className="inline-block px-4 py-1 bg-primary text-black text-[10px] font-bold rounded-full mb-4">SUCCESSFULLY ACTIVATED</div>
                <h2 className="text-primary text-4xl font-black tracking-tighter uppercase">The Beast is Awake</h2>
                
                <div className="grid grid-cols-2 gap-4 text-left mt-8">
                    <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                        <div className="text-[10px] text-gray-500 uppercase">Session IP</div>
                        <div className="text-sm text-primary">AUTHORIZED</div>
                    </div>
                    <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                        <div className="text-[10px] text-gray-500 uppercase">Swarm Status</div>
                        <div className="text-sm text-primary">ENGAGED</div>
                    </div>
                </div>

                <div className="flex gap-4 pt-10">
                    <a href="/cockpit" className="flex-1 bg-primary text-black py-3 rounded-xl font-bold text-sm">Open Cockpit</a>
                    <a href="/chamber" className="flex-1 border border-primary/20 text-primary py-3 rounded-xl font-bold text-sm">Chamber Feed</a>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
