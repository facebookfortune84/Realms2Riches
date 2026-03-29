import { Share2, Info, Scale } from 'lucide-react';

export default function AffiliateDisclosure() {
  const points = [
    {
      title: "Transparency Protocol",
      content: "At Realms 2 Riches, transparency is a core pillar of our autonomous ecosystem. In compliance with Federal Trade Commission (FTC) guidelines, we disclose that certain links on this platform are affiliate links."
    },
    {
      title: "How it Works",
      content: "When you click on these links and subsequently make a purchase from the associated third-party provider, we may receive a commission. This occurs at zero additional cost to you and often includes exclusive discounts negotiated by our agent swarm."
    },
    {
      title: "Selection Criteria",
      content: "Our agents only recommend tools and services (e.g., Groq, ElevenLabs, Stripe) that have been vetted for performance, security, and compatibility with the Sovereign Matrix."
    },
    {
      title: "Independence",
      content: "Our editorial integrity and autonomous agent reasoning are never influenced by affiliate partnerships. We prioritize the optimization of your Realm above all else."
    }
  ];

  return (
    <div className="max-w-5xl mx-auto py-20 px-4 font-mono text-white">
      <div className="text-center mb-20 border-b border-primary/20 pb-12">
        <Share2 className="text-primary mx-auto mb-6" size={48} />
        <h1 className="text-6xl font-black tracking-tighter uppercase italic">Affiliate <span className="text-primary">Disclosure</span></h1>
        <p className="text-gray-500 text-xs mt-4 uppercase tracking-[0.4em]">Strategic Partnership Transparency v3.9.1</p>
      </div>

      <div className="space-y-12">
        {points.map((p, i) => (
          <div key={i} className="bg-black/40 border border-white/5 p-10 rounded-[2rem] hover:border-primary/20 transition-all group">
            <h3 className="text-white font-black mb-4 uppercase tracking-tight flex items-center gap-3">
              <Info size={18} className="text-primary" />
              {p.title}
            </h3>
            <p className="text-gray-400 text-sm leading-relaxed font-light">{p.content}</p>
          </div>
        ))}
      </div>

      <div className="mt-20 text-[10px] text-gray-600 uppercase tracking-[0.2em] text-center max-w-xl mx-auto">
        Your support through these links enables the continuous evolution of our 1000-agent specialized fleet.
      </div>
    </div>
  );
}
