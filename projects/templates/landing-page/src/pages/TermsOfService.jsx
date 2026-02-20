import { FileText, Gavel, Zap, ShieldAlert } from 'lucide-react';

export default function TermsOfService() {
  const terms = [
    {
      title: "1. Autonomous Agency",
      content: "Realms 2 Riches provides an autonomous agentic platform. Users acknowledge that agents execute logic based on human-provided directives. The platform is not responsible for unforeseen outcomes of autonomous execution."
    },
    {
      title: "2. Payment & Tokenization",
      content: "Access to the 1000-agent swarm is provided on a subscription or credit basis. All transactions are handled via Stripe. No refunds are issued for used agent cycles."
    },
    {
      title: "3. Acceptable Use",
      content: "The platform shall not be used for generating malicious code, disinformation, or conducting unauthorized cyber operations. Violation results in immediate termination of the Neural Link."
    },
    {
      title: "4. Intellectual Property",
      content: "Code and business structures built by the swarm belong to the user. The underlying Sovereign Orchestration logic remains the exclusive property of Realms 2 Riches."
    }
  ];

  return (
    <div className="max-w-4xl mx-auto py-16 px-4 font-mono">
      <div className="flex items-center gap-4 mb-12 border-b border-primary/20 pb-8">
        <Scale className="text-primary" size={40} />
        <div>
          <h1 className="text-5xl font-black tracking-tighter uppercase italic">Terms of <span className="text-primary">Engagement</span></h1>
          <p className="text-gray-500 text-xs mt-2 uppercase tracking-widest">Revision: 0xDEADBEEF | v3.4.0</p>
        </div>
      </div>

      <div className="space-y-8">
        {terms.map((t, i) => (
          <div key={i} className="bg-black border border-white/10 p-8 rounded-3xl group hover:border-primary/30 transition-all">
            <h3 className="text-primary font-black mb-4 uppercase flex items-center gap-3">
              <span className="text-gray-700">0{i+1}</span>
              {t.title}
            </h3>
            <p className="text-gray-400 text-sm leading-relaxed">{t.content}</p>
          </div>
        ))}
      </div>

      <div className="mt-16 text-[10px] text-gray-600 uppercase tracking-[0.3em] text-center">
        By proceeding with the Sovereign Ignition, you agree to the matrix protocols.
      </div>
    </div>
  );
}

function Scale({ className, size }) {
    return <Gavel className={className} size={size} />;
}
