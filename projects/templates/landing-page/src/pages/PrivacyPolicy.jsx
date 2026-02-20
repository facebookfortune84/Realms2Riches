import { Shield, Lock, FileText, Scale } from 'lucide-react';

export default function PrivacyPolicy() {
  const sections = [
    {
      title: "1. Data Sovereignty",
      content: "Realms 2 Riches operates on a principle of data sovereignty. Your project specifications, codebases, and agent directives remain your exclusive property. We do not sell or monetize your intellectual property."
    },
    {
      title: "2. Agent Intelligence Training",
      content: "Our autonomous swarms learn from generalized patterns to improve efficiency. However, individual proprietary logic is sharded and encrypted, ensuring that no cross-contamination of business secrets occurs between users."
    },
    {
      title: "3. Cryptographic Security",
      content: "All connections to the Sovereign Matrix are secured via TLS 1.3. Environment variables and API keys are stored using industry-standard AES-256 encryption at rest."
    },
    {
      title: "4. Third-Party Integrations",
      content: "When you link third-party services (Stripe, Twilio, LinkedIn), we only transmit the minimum required telemetry to execute your directives."
    }
  ];

  return (
    <div className="max-w-4xl mx-auto py-16 px-4 font-mono">
      <div className="flex items-center gap-4 mb-12 border-b border-primary/20 pb-8">
        <Lock className="text-primary" size={40} />
        <div>
          <h1 className="text-5xl font-black tracking-tighter uppercase italic">Privacy <span className="text-primary">Protocol</span></h1>
          <p className="text-gray-500 text-xs mt-2 uppercase tracking-widest">Effective Date: February 20, 2026 | v3.4.0</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        {sections.map((s, i) => (
          <div key={i} className="bg-white/5 p-8 rounded-3xl border border-white/5 hover:border-primary/20 transition-all">
            <h3 className="text-white font-bold mb-4 uppercase tracking-tight flex items-center gap-2">
              <Shield size={16} className="text-primary" />
              {s.title}
            </h3>
            <p className="text-gray-400 text-sm leading-relaxed">{s.content}</p>
          </div>
        ))}
      </div>

      <div className="mt-16 p-8 bg-primary/5 rounded-3xl border border-primary/10 text-center">
        <p className="text-gray-500 text-xs uppercase tracking-widest mb-4">Questions regarding the matrix?</p>
        <a href="mailto:intelligence@realms2riches.ai" className="text-primary font-bold hover:underline">intelligence@realms2riches.ai</a>
      </div>
    </div>
  );
}
