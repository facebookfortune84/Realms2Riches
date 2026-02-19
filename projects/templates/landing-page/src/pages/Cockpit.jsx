import { useState, useEffect, useRef } from 'react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Cockpit() {
  const [messages, setMessages] = useState([{ sender: 'system', text: 'Ready for instructions.' }]);
  const [input, setInput] = useState('');
  const [voiceStatus, setVoiceStatus] = useState('Inactive');
  const socketRef = useRef(null);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setMessages(prev => [...prev, { sender: 'user', text: input }]);
    const currentInput = input;
    setInput('');
    
    try {
        const res = await fetch(`${BACKEND_URL}/api/tasks`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ description: currentInput })
        });
        const data = await res.json();
        if (data.status === 'queued') {
            addMsg(`Task queued for ${data.agent_count} agents. Swarm is engaging.`, 'system');
        }
    } catch (e) {
        console.error(e);
        addMsg("Connectivity warning: Swarm currently operating in autonomous mode.", 'system');
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
            socket.onopen = () => setVoiceStatus('Connected');
            socket.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if (msg.type === 'transcript') setMessages(prev => [...prev, { sender: 'user', text: msg.text }]);
                if (msg.type === 'text') setMessages(prev => [...prev, { sender: 'agent', text: msg.text }]);
            };
            socket.onclose = () => setVoiceStatus('Disconnected');
            socketRef.current = socket;
        } catch (e) {
            console.error(e);
            setVoiceStatus('Error');
        }
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold">Agent Cockpit</h2>
        <div className="flex items-center gap-4">
            <span className={`text-sm ${voiceStatus === 'Connected' ? 'text-primary' : 'text-gray-500'}`}>Voice: {voiceStatus}</span>
            <button 
                onClick={toggleVoice}
                className={`px-4 py-2 rounded font-bold ${socketRef.current ? 'bg-red-500 text-white' : 'bg-primary text-black'}`}
            >
                {socketRef.current ? 'Stop Voice' : 'Start Voice'}
            </button>
        </div>
      </div>

      <div className="bg-black border border-gray-800 rounded-lg h-[500px] flex flex-col">
        <div className="flex-grow p-4 overflow-y-auto space-y-4">
            {messages.map((m, i) => (
                <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] p-3 rounded-lg ${
                        m.sender === 'user' ? 'bg-gray-800 text-white' : 
                        m.sender === 'system' ? 'bg-gray-900 text-gray-400 text-xs' :
                        'bg-primary/10 text-primary border border-primary/20'
                    }`}>
                        {m.text}
                    </div>
                </div>
            ))}
        </div>
        <div className="p-4 border-t border-gray-800 flex gap-4">
            <input 
                type="text" 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Describe your task..."
                className="flex-grow bg-gray-900 border border-gray-700 rounded px-4 py-2 focus:outline-none focus:border-primary"
            />
            <button onClick={sendMessage} className="bg-primary text-black px-6 py-2 rounded font-bold hover:opacity-90">
                Send
            </button>
        </div>
      </div>
    </div>
  );
}
