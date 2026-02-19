import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="border-b border-gray-800 py-4">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-primary">Realms to Riches</Link>
        <div className="space-x-6">
          <Link to="/pricing" className="hover:text-primary">Pricing</Link>
          <Link to="/cockpit" className="hover:text-primary">Cockpit</Link>
          <Link to="/blog" className="hover:text-primary">Blog</Link>
          <Link to="/store" className="hover:text-primary">Store</Link>
          <Link to="/affiliates" className="hover:text-primary">Affiliates</Link>
          <Link to="/dashboard" className="hover:text-primary">Dashboard</Link>
        </div>
      </div>
    </nav>
  );
}
