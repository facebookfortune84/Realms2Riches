import { Link } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Cpu, Shield, ArrowRight, Download, Terminal, Activity, Globe } from 'lucide-react';
import NeuralGlobe from '../components/NeuralGlobe';

const GenesisForge = () => {
  const [status, setStatus] = useState('IDLE');
  const [task, setTask] = useState('');
  const [progress, setProgress] = useState(0);
  const [artifact, setArtifact] = useState(null);

  const startForge = async () => {
    if (!task) return;
    setStatus('FORGING');
    setProgress(0);
    
    // Simulate industrial progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 2;
      });
    }, 100);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: `INITIALIZE COMPANY BLUEPRINT: ${task}` })
      });
      const data = await res.json();
      if (data.status === 'completed') {
        setStatus('COMPLETE');
        // Artifact is usually /swarms/swarm_ID.zip
        setArtifact(`${import.meta.env.VITE_API_URL}/swarms/swarm_${data.result?.task_id?.slice(0,8) || 'latest'}.zip`);
      }
    } catch (e) {
      setStatus('ERROR');
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gray-900/80 backdrop-blur-xl border-2 border-primary/20 p-8 rounded-3xl shadow-2xl shadow-primary/10 max-w-2xl w-full"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-primary/10 rounded-lg">
          <Cpu className="w-6 h-6 text-primary" />
        </div>
        <div>
          <h3 className="text-xl font-black tracking-tight text-white">GENESIS_FORGE_v2</h3>
          <p className="text-[10px] text-gray-500 font-mono uppercase">Industrial Swarm Fabricator</p>
        </div>
      </div>

      {status === 'IDLE' && (
        <div className="space-y-4">
          <input 
            type="text"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Describe the company you want to build..."
            className="w-full bg-black/50 border border-gray-800 rounded-xl px-4 py-4 text-primary focus:outline-none focus:border-primary transition-colors font-mono"
          />
          <button 
            onClick={startForge}
            className="w-full bg-primary text-black font-black py-4 rounded-xl flex items-center justify-center gap-2 hover:bg-white transition-colors"
          >
            MINT AUTONOMOUS SWARM <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      )}

      {status === 'FORGING' && (
        <div className="space-y-6 py-4">
          <div className="flex justify-between text-xs font-mono text-primary mb-2">
            <span>ALIGNING NEURAL NODES...</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              className="h-full bg-primary shadow-[0_0_10px_#00ff88]"
            />
          </div>
          <p className="text-center text-gray-500 text-[10px] animate-pulse">DO NOT DISCONNECT. FABRICATING DISTRIBUTED ARCHITECTURE.</p>
        </div>
      )}

      {status === 'COMPLETE' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center space-y-4">
          <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Download className="w-8 h-8 text-primary" />
          </div>
          <h4 className="text-lg font-bold">SWARM FABRICATED</h4>
          <p className="text-sm text-gray-400">Your industrial-grade autonomous fleet is ready for deployment.</p>
          <a 
            href={artifact}
            className="block w-full bg-white text-black font-black py-4 rounded-xl hover:bg-primary transition-colors"
          >
            DOWNLOAD PACKAGE (.ZIP)
          </a>
          <button onClick={() => setStatus('IDLE')} className="text-xs text-gray-600 underline">Fabricate Another</button>
        </motion.div>
      )}
    </motion.div>
  );
};

const BackgroundPulse = () => (
  <div className="absolute inset-0 z-0 overflow-hidden">
    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-[120px] animate-pulse" />
    <div className="absolute top-0 left-0 w-full h-full bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
    <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20" />
    <div className="absolute inset-0 bg-gradient-to-b from-black via-transparent to-black pointer-events-none" />
    <div className="absolute inset-0 w-full h-full pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-[1] bg-[size:100%_4px,3px_100%]" />
  </div>
);

export default function Home() {
  return (
    <div className="relative min-h-screen flex flex-col items-center pt-20 pb-32 px-4 overflow-x-hidden bg-black text-white">
      <BackgroundPulse />
      
      {/* Moving Particles/Data Stream Simulation */}
      <div className="absolute inset-0 pointer-events-none opacity-30">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ y: -100, x: Math.random() * 2000, opacity: 0 }}
            animate={{ y: 1200, opacity: [0, 1, 0] }}
            transition={{ duration: Math.random() * 5 + 5, repeat: Infinity, ease: "linear", delay: Math.random() * 5 }}
            className="absolute w-[1px] h-20 bg-gradient-to-b from-primary to-transparent"
          />
        ))}
      </div>

      <div className="relative z-10 w-full max-w-7xl flex flex-col lg:flex-row items-center gap-16 lg:gap-24">
        
        <div className="lg:w-1/2 text-left space-y-8">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-[10px] font-bold tracking-widest uppercase mb-6">
              <Activity className="w-3 h-3" /> System Status: Autonomous
            </div>
            <h1 className="text-7xl md:text-9xl font-black tracking-tighter leading-[0.85] mb-6">
              MINT <br />
              <span className="text-primary italic underline decoration-white/10">MONEY.</span>
            </h1>
            <p className="text-xl text-gray-400 font-light leading-relaxed max-w-xl">
              Realms2Riches is the world's first <span className="text-white font-medium">Autonomous Revenue Fabricator</span>. We don't just provide agents; we provide turn-key monetization swarms that work while you sleep.
            </p>
          </motion.div>

          <div className="flex flex-wrap gap-4">
            <Link to="/console" className="px-8 py-4 bg-white text-black font-black rounded-full hover:bg-primary transition-all flex items-center gap-2">
              LAUNCH CONSOLE <Terminal className="w-4 h-4" />
            </Link>
            <Link to="/pricing" className="px-8 py-4 bg-transparent border border-white/20 text-white font-bold rounded-full hover:bg-white/10 transition-all">
              VIEW INDUSTRIAL PLANS
            </Link>
          </div>

          <div className="grid grid-cols-3 gap-8 pt-8 border-t border-white/10">
            <div>
              <div className="text-2xl font-black text-white">1,000</div>
              <div className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Agents Active</div>
            </div>
            <div>
              <div className="text-2xl font-black text-primary">$0.00</div>
              <div className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Revenue Cap</div>
            </div>
            <div>
              <div className="text-2xl font-black text-white">99.9%</div>
              <div className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Uptime</div>
            </div>
          </div>
        </div>

        <div className="lg:w-1/2 w-full flex justify-center relative">
          <div className="absolute inset-0 flex items-center justify-center -z-10 opacity-40 scale-150">
            <NeuralGlobe />
          </div>
          <GenesisForge />
        </div>

      </div>

      {/* Feature Grid */}
      <div className="mt-40 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-7xl relative z-10">
        {[
          { 
            title: "Autonomous Outreach", 
            icon: Zap,
            desc: "Our agents scrape, qualify, and engage leads on LinkedIn and Email with 18% average reply rates." 
          },
          { 
            title: "Programmatic SEO", 
            icon: Shield,
            desc: "Generate 1,000+ targeted landing pages in minutes to capture long-tail high-intent traffic." 
          },
          { 
            title: "Industrial Governance", 
            icon: Activity,
            desc: "Every agent action is hashed and recorded on the Sovereign Lineage for complete accountability." 
          }
        ].map((feat, i) => (
          <motion.div 
            key={i}
            whileHover={{ y: -5 }}
            className="p-8 rounded-3xl bg-gray-900/40 border border-white/5 hover:border-primary/30 transition-all group"
          >
            <feat.icon className="w-10 h-10 text-primary mb-6 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-bold mb-4 text-white uppercase tracking-tight">{feat.title}</h3>
            <p className="text-gray-500 leading-relaxed text-sm font-light italic">"{feat.desc}"</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
