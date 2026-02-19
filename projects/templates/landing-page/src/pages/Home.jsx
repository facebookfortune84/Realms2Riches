import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="text-center py-20">
      <h1 className="text-5xl font-bold text-primary mb-6">Agentic Software Agency in a Box</h1>
      <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-10">
        Orchestrate a swarm of specialized AI agents to build, test, and deploy software autonomously.
      </p>
      <div className="flex justify-center gap-4">
        <Link to="/cockpit" className="bg-primary text-black px-6 py-3 rounded-lg font-bold text-lg hover:opacity-90">
          Try Agent Cockpit
        </Link>
        <Link to="/pricing" className="border border-primary text-primary px-6 py-3 rounded-lg font-bold text-lg hover:bg-primary/10">
          View Pricing
        </Link>
      </div>
      
      <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-card-bg p-6 rounded-xl">
          <h3 className="text-xl font-bold mb-2">Multi-Agent Swarm</h3>
          <p className="text-gray-400">Architect, Dev, QA, and Growth agents working in harmony.</p>
        </div>
        <div className="bg-card-bg p-6 rounded-xl">
          <h3 className="text-xl font-bold mb-2">Voice Interface</h3>
          <p className="text-gray-400">Talk to your agents with sub-second latency and barge-in capability.</p>
        </div>
        <div className="bg-card-bg p-6 rounded-xl">
          <h3 className="text-xl font-bold mb-2">Governance First</h3>
          <p className="text-gray-400">Every line of code is traced, hashed, and validated.</p>
        </div>
      </div>
    </div>
  );
}
