import { useState, useEffect, useRef } from 'react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://glowfly-sizeable-lazaro.ngrok-free.dev";

export default function Cockpit() {
  const [messages, setMessages] = useState([{ sender: 'system', text: 'Ready for instructions.' }]);
  const [input, setInput] = useState('');
  const [voiceStatus, setVoiceStatus] = useState('Inactive');
  const socketRef = useRef(null);

  const addMsg = (text, sender) => {
    setMessages(prev => [...prev, { sender, text }]);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    addMsg(input, 'user');
    const currentInput = input;
    setInput('');
    
    // Add a temporary "processing" message
    const processingId = Date.now();
    setMessages(prev => [...prev, { id: processingId, sender: 'system', text: 'Swarm is analyzing your request...' }]);

    try {
        const res = await fetch(`${BACKEND_URL}/api/tasks`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ description: currentInput })
        });
        const data = await res.json();
        
        // Remove processing message
        setMessages(prev => prev.filter(m => m.id !== processingId));

        if (data.status === 'completed') {
            const agentId = data.result?.agent_id || 'Agent';
            const status = data.result?.status || 'completed';
            const reasoning = data.result?.reasoning || 'Thinking...';
            
            let resultText = `[${agentId}] Task ${status}.\n\n`;
            resultText += `REASONING: ${reasoning}\n\n`;
            
            if (data.result?.results && data.result.results.length > 0) {
                resultText += "ACTIONS TAKEN:\n";
                data.result.results.forEach(r => {
                    const output = r.output_data?.result || r.output_data?.error || 'No detail available';
                    resultText += `- ${r.tool_id}: ${output}\n`;
                });
            } else {
                resultText += "SYSTEM NOTE: Internal logic cycle complete. No external tools were required to fulfill this request.";
            }
            
            addMsg(resultText, 'agent');
        } else {
            addMsg(`Error: ${data.error || 'Task failed to complete.'}`, 'system');
        }
    } catch (e) {
        console.error(e);
        setMessages(prev => prev.filter(m => m.id !== processingId));
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
                if (msg.type === 'transcript') addMsg(msg.text, 'user');
                if (msg.type === 'text') addMsg(msg.text, 'agent');
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
