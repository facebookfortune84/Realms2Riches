import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";
const MASTER_KEY = "sk-realm-god-mode-888"; // In production, this would be handled via secure login

export default function LaunchControl() {
  const [status, setStatus] = useState('idle'); // idle, signing, launching, active
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);

  const addLog = (msg) => setLogs(prev => [...prev.slice(-5), `> ${msg}`]);

  const handleLaunch = async () => {
    setStatus('signing');
    addLog("Initiating Cryptographic Handshake...");
    
    // Simulate signing delay
    await new Promise(r => setTimeout(r, 1500));
    
    // In a real scenario, we'd fetch the client IP first or the backend handles it
    // For this UI, we generate the signature using the Master Key
    const signature = btoa(MASTER_KEY + "-signature"); // Simple placeholder for the visual flow
    
    setStatus('launching');
    addLog("Signature Applied. Authenticating IP...");

    try {
        const res = await fetch(`${BACKEND_URL}/api/sovereign/launch`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ signature: "verified_mock_signature" })
        });
        
        if (!res.ok) throw new Error("Access Denied");

        // Start progress simulation
        let p = 0;
        const interval = setInterval(() => {
            p += 2;
            setProgress(p);
            if (p === 20) addLog("Loading Grand Fleet Registry (1,003 Units)...");
            if (p === 50) addLog("Engaging Action Multiplexer (150+ Capabilities)...");
            if (p === 80) addLog("Establishing RAG Neural Link...");
            if (p >= 100) {
                clearInterval(interval);
                setStatus('active');
                addLog("SOVEREIGN STATE ACTIVE");
            }
        }, 50);

    } catch (err) {
        addLog("FATAL ERROR: IP NOT AUTHORIZED");
        setStatus('idle');
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4 font-mono overflow-hidden relative">
      {/* Background Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,136,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,136,0.05)_1px,transparent_1px)] bg-[size:40px_40px]" />
      
      <div className="w-full max-w-2xl relative z-10">
        <div className="bg-black border-2 border-primary/20 p-10 rounded-3xl shadow-[0_0_100px_rgba(0,255,136,0.05)] text-center">
          
          <h1 className="text-primary text-xs tracking-[0.5em] font-black mb-10 uppercase opacity-50">Sovereign Command Console</h1>

          <AnimatePresence mode="wait">
            {status === 'idle' && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.1 }}
                className="space-y-8"
              >
                <div className="text-gray-500 text-sm mb-10">SYSTEM STATUS: <span className="text-yellow-500 animate-pulse font-bold">READY FOR ACTIVATION</span></div>
                
                <button 
                  onClick={handleLaunch}
                  className="group relative inline-block p-1 rounded-full bg-gradient-to-b from-primary to-primary/20 shadow-[0_0_30px_rgba(0,255,136,0.2)] hover:shadow-[0_0_50px_rgba(0,255,136,0.4)] transition-all duration-500"
                >
                  <div className="bg-black rounded-full p-8 transition-transform group-hover:scale-95 duration-500">
                    <div className="w-32 h-32 rounded-full border-4 border-primary flex items-center justify-center relative overflow-hidden">
                        <div className="absolute inset-0 bg-primary/10 group-hover:bg-primary/20 transition-colors" />
                        <span className="text-primary font-black text-xl tracking-tighter">LAUNCH</span>
                    </div>
                  </div>
                </button>
                <p className="text-gray-700 text-[10px] mt-10">REQUIRES MASTER SIGNATURE + IP VERIFICATION</p>
              </motion.div>
            )}

            {(status === 'launching' || status === 'signing') && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6 py-10"
              >
                <div className="w-full bg-gray-900 h-1 rounded-full overflow-hidden">
                    <motion.div 
                        className="h-full bg-primary"
                        animate={{ width: `${progress}%` }}
                    />
                </div>
                <div className="text-left space-y-2">
                    {logs.map((log, i) => (
                        <div key={i} className="text-primary/60 text-xs font-mono">{log}</div>
                    ))}
                </div>
              </motion.div>
            )}

            {status === 'active' && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
              >
                <div className="w-24 h-24 bg-primary rounded-full mx-auto flex items-center justify-center shadow-[0_0_50px_rgba(0,255,136,0.6)]">
                    <svg className="w-12 h-12 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>
                </div>
                <h2 className="text-primary text-3xl font-black tracking-tighter">THE BEAST IS AWAKE</h2>
                <div className="flex justify-center gap-4">
                    <a href="/cockpit" className="text-xs border border-primary/30 text-primary/60 px-4 py-2 rounded-full hover:bg-primary hover:text-black transition-all">Go to Cockpit</a>
                    <a href="/chamber" className="text-xs border border-primary/30 text-primary/60 px-4 py-2 rounded-full hover:bg-primary hover:text-black transition-all">Enter The Chamber</a>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </div>
    </div>
  );
}
