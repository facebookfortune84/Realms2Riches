import { useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';

export default function Success() {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');

  return (
    <div className="text-center py-20">
      <div className="text-6xl mb-4">🎉</div>
      <h1 className="text-4xl font-bold text-primary mb-4">Payment Successful!</h1>
      <p className="text-xl text-gray-300 mb-8">
        Your agent swarm is ready to deploy.
        {sessionId && <span className="block text-sm text-gray-600 mt-2">Ref: {sessionId}</span>}
      </p>
      <div className="flex justify-center gap-4">
        <Link to="/cockpit" className="bg-primary text-black px-6 py-3 rounded-lg font-bold hover:opacity-90">
          Go to Cockpit
        </Link>
        <Link to="/dashboard" className="border border-gray-600 text-white px-6 py-3 rounded-lg hover:border-white">
          View Dashboard
        </Link>
      </div>
    </div>
  );
}
