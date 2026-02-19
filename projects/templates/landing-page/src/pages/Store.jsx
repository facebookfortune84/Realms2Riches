const storeData = [
  {
    "id": "tmpl_saas_starter",
    "name": "SaaS Starter Kit",
    "price": 49,
    "description": "Next.js + Tailwind + Stripe boilerplate.",
    "category": "Template"
  },
  {
    "id": "prompt_pack_marketing",
    "name": "Marketing Agent Prompts",
    "price": 19,
    "description": "50+ optimized prompts for growth agents.",
    "category": "Prompts"
  }
];

export default function Store() {
  return (
    <div>
      <h2 className="text-3xl font-bold mb-8">Templates & Assets</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {storeData.map((item, i) => (
            <div key={i} className="bg-card-bg p-6 rounded-lg border border-gray-800 hover:border-primary transition-colors">
                <div className="text-sm text-gray-500 mb-2">{item.category}</div>
                <h3 className="text-xl font-bold mb-2">{item.name}</h3>
                <p className="text-gray-400 mb-4">{item.description}</p>
                <div className="flex justify-between items-center mt-auto">
                    <span className="text-2xl font-bold">${item.price}</span>
                    <button className="bg-primary text-black px-4 py-2 rounded font-bold hover:opacity-90">
                        Buy
                    </button>
                </div>
            </div>
        ))}
      </div>
    </div>
  );
}
