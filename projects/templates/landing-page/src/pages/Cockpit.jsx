import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, XCircle, Terminal, Cpu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Cockpit() {
  const [messages, setMessages] = useState([{ sender: 'system', text: 'Sovereign Neural Link Established. Awaiting directive.' }]);
  const [input, setInput] = useState('');
  const [voiceStatus, setVoiceStatus] = useState('Inactive');
  const [isThinking, setIsThinking] = useState(false);
  const socketRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  const addMsg = (text, sender) => {
    setMessages(prev => [...prev, { id: Date.now() + Math.random(), sender, text }]);
  };

  const sendMessage = async () => {
    if (!input.trim() || isThinking) return;
    const currentInput = input;
    addMsg(currentInput, 'user');
    setInput('');
    setIsThinking(true);

    try {
        const res = await fetch(`${BACKEND_URL}/api/tasks`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ description: currentInput })
        });
        const data = await res.json();
        
        if (data.status === 'completed') {
            const agentId = data.result?.agent_id || 'Swarm';
            const reasoning = data.result?.reasoning || 'Task executed successfully.';
            addMsg(`[${agentId}] ${reasoning}`, 'agent');
        } else {
            addMsg(`Error: ${data.error || 'Direct uplink failed.'}`, 'system');
        }
    } catch (e) {
        console.error(e);
        addMsg("Critical: Connection to matrix dropped. Re-establishing...", 'system');
    } finally {
        setIsThinking(false);
    }
  };

  const interruptSwarm = () => {
    if (socketRef.current) {
        socketRef.current.send(JSON.stringify({ type: 'interrupt', action: 'stop' }));
        addMsg("INTERRUPT SIGNAL SENT.", 'system');
    }
  };

  const toggleVoice = () => {
    if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
        setVoiceStatus('Inactive');
    } else {
        const wsUrl = BACKEND_URL.replace('https', 'wss').replace('http', 'ws');
        try {
            const socket = new WebSocket(`${wsUrl}/ws/voice`);
            socket.onopen = () => {
                setVoiceStatus('Connected');
                addMsg("VOICE UPLINK ACTIVE.", 'system');
            };
            socket.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if (msg.type === 'transcript') addMsg(msg.text, 'user');
                if (msg.type === 'text') addMsg(msg.text, 'agent');
                if (msg.type === 'control' && msg.action === 'stop_audio') addMsg("AUDIO STREAM CUT.", 'system');
            };
            socket.onclose = () => {
                setVoiceStatus('Disconnected');
                socketRef.current = null;
            };
            socket.onerror = (err) => {
                console.error("WS Error:", err);
                setVoiceStatus('Error');
            };
            socketRef.current = socket;
        } catch (e) {
            console.error(e);
            setVoiceStatus('Error');
        }
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-10 px-4 font-mono">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
            <h2 className="text-4xl font-black tracking-tighter uppercase italic flex items-center gap-3">
                <Cpu className="text-primary" />
                Agent <span className="text-primary">Cockpit</span>
            </h2>
            <p className="text-gray-600 text-[10px] uppercase tracking-widest mt-1">Sovereign Directive Input Console</p>
        </div>
        <div className="flex items-center gap-3 bg-white/5 p-2 rounded-2xl border border-white/5">
            <div className="flex items-center gap-2 px-3">
                <div className={`w-2 h-2 rounded-full ${voiceStatus === 'Connected' ? 'bg-primary animate-pulse' : 'bg-red-500'}`} />
                <span className="text-[10px] text-white uppercase font-bold">Voice: {voiceStatus}</span>
            </div>
            <button 
                onClick={toggleVoice}
                className={`p-3 rounded-xl transition-all ${socketRef.current ? 'bg-red-500/20 text-red-500 hover:bg-red-500/30' : 'bg-primary text-black hover:scale-105'}`}
            >
                {socketRef.current ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
            {/* Visual Waveform */}
            {socketRef.current && (
                <div className="flex items-center gap-1 h-8 px-2">
                    {[...Array(5)].map((_, i) => (
                        <div 
                            key={i} 
                            className="w-1 bg-primary rounded-full animate-waveform" 
                            style={{ 
                                height: '100%', 
                                animationDelay: `${i * 0.1}s`,
                                animationDuration: '0.8s' 
                            }} 
                        />
                    ))}
                </div>
            )}
            {socketRef.current && (
                <button 
                    onClick={interruptSwarm}
                    className="p-3 rounded-xl bg-yellow-500/20 text-yellow-500 hover:bg-yellow-500/30"
                    title="Interrupt Current Stream"
                >
                    <XCircle size={18} />
                </button>
            )}
        </div>
      </div>

      <div className="bg-black border-2 border-primary/20 rounded-3xl h-[600px] flex flex-col relative overflow-hidden shadow-[0_0_100px_rgba(0,255,136,0.05)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,255,136,0.02),transparent)] pointer-events-none" />
        
        <div 
            ref={scrollRef}
            className="flex-grow p-6 overflow-y-auto space-y-6 custom-scrollbar relative z-10"
        >
            <AnimatePresence initial={false}>
                {messages.map((m) => (
                    <motion.div 
                        key={m.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`max-w-[85%] p-4 rounded-2xl text-xs leading-relaxed ${
                            m.sender === 'user' ? 'bg-primary/10 text-primary border border-primary/20 rounded-tr-none' : 
                            m.sender === 'system' ? 'bg-white/5 text-gray-500 italic text-[10px] border border-white/5' :
                            'bg-white/5 text-gray-200 border border-white/10 rounded-tl-none'
                        }`}>
                            {m.sender === 'agent' && <div className="text-[10px] text-primary font-black mb-2 uppercase tracking-widest">Incoming Transmission</div>}
                            <div className="whitespace-pre-wrap">{m.text}</div>
                        </div>
                    </motion.div>
                ))}
            </AnimatePresence>
            {isThinking && (
                <div className="flex justify-start">
                    <div className="bg-white/5 p-4 rounded-2xl border border-white/10 flex items-center gap-3">
                        <div className="flex gap-1">
                            <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                            <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                            <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                        </div>
                        <span className="text-[10px] text-gray-500 uppercase tracking-widest">Swarm is processing...</span>
                    </div>
                </div>
            )}
        </div>

        <div className="p-6 border-t border-white/5 bg-black/50 backdrop-blur-xl relative z-10">
            <div className="flex gap-4 items-center">
                <div className="bg-white/5 p-3 rounded-xl text-gray-500">
                    <Terminal size={18} />
                </div>
                <input 
                    type="text" 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Enter directive for the Sovereign Swarm..."
                    className="flex-grow bg-transparent border-none text-white text-sm focus:outline-none focus:ring-0 placeholder:text-gray-700"
                />
                <button 
                    onClick={sendMessage} 
                    disabled={isThinking || !input.trim()}
                    className="bg-primary text-black p-3 rounded-xl font-bold hover:scale-105 transition-transform disabled:opacity-50 disabled:grayscale"
                >
                    <Send size={18} />
                </button>
            </div>
        </div>
      </div>
    </div>
  );
}
