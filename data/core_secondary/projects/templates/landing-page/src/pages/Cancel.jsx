import { Link } from 'react-router-dom';

export default function Cancel() {
  return (
    <div className="text-center py-20">
      <div className="text-6xl mb-4">⚠️</div>
      <h1 className="text-4xl font-bold text-red-500 mb-4">Payment Cancelled</h1>
      <p className="text-xl text-gray-300 mb-8">
        No charges were made. Your agents are still waiting for you.
      </p>
      <Link to="/pricing" className="bg-white text-black px-6 py-3 rounded-lg font-bold hover:bg-gray-200">
        Return to Pricing
      </Link>
    </div>
  );
}
