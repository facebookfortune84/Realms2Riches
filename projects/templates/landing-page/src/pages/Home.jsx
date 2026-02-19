import { Link } from 'react-router-dom';
import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

export default function Home() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const particles = [];
    const particleCount = 50;

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        size: Math.random() * 2 + 1
      });
    }

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#00ff88';
      ctx.strokeStyle = '#00ff8822';

      particles.forEach((p, i) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();

        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
          if (dist < 150) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      });

      animationFrameId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <div className="relative min-h-[80vh] flex flex-col items-center justify-center overflow-hidden">
      <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none opacity-40" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 text-center px-4"
      >
        <h1 className="text-6xl md:text-8xl font-black text-white mb-6 tracking-tighter">
          REALMS TO <span className="text-primary">RICHES</span>
        </h1>
        <p className="text-2xl text-gray-400 max-w-3xl mx-auto mb-10 leading-relaxed font-light">
          Deploy a <span className="text-white font-medium">multi-agent swarm</span> that builds, tests, and grows your business with sub-second reasoning and complete governance.
        </p>
        
        <div className="flex flex-col md:flex-row justify-center gap-6">
          <Link to="/cockpit" className="bg-primary text-black px-10 py-4 rounded-full font-bold text-xl hover:scale-105 transition-transform shadow-[0_0_20px_rgba(0,255,136,0.4)]">
            Open Agent Cockpit
          </Link>
          <Link to="/pricing" className="bg-transparent border-2 border-primary text-primary px-10 py-4 rounded-full font-bold text-xl hover:bg-primary/10 transition-colors">
            View Plans
          </Link>
        </div>

        <div className="mt-8 text-xs font-mono text-gray-600 uppercase tracking-[0.2em]">
          System Integrity: <span className="text-primary">Verified SHA-256 Baseline</span>
        </div>
      </motion.div>

      <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl relative z-10">
        {[
          { title: "100+ Global Agents", desc: "Access a massive fleet of specialized experts across Engineering, Creative, Legal, and Finance." },
          { title: "Barge-in Voice", desc: "Interrupt and steer your agents in real-time using high-fidelity voice control." },
          { title: "Full Lineage", desc: "Every decision and artifact is recorded, hashed, and verifiable." }
        ].map((feat, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.1 }}
            className="bg-card-bg/50 backdrop-blur-md p-8 rounded-2xl border border-gray-800 hover:border-primary/50 transition-colors"
          >
            <h3 className="text-xl font-bold mb-3 text-white">{feat.title}</h3>
            <p className="text-gray-400">{feat.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
