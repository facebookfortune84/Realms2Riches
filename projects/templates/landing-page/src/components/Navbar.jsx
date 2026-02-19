import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function Navbar() {
  const location = useLocation();
  
  const links = [
    { name: 'Pricing', path: '/pricing' },
    { name: 'Cockpit', path: '/cockpit' },
    { name: 'Blog', path: '/blog' },
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Chamber', path: '/chamber' },
    { name: 'Command', path: '/sovereign' }
  ];

  return (
    <nav className="border-b border-gray-800 py-6 sticky top-0 bg-bg/80 backdrop-blur-xl z-50">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link to="/" className="text-2xl font-black tracking-tighter text-white hover:text-primary transition-colors">
          REALMS2<span className="text-primary">RICHES</span>
        </Link>
        <div className="hidden md:flex space-x-8">
          {links.map(link => (
            <Link 
              key={link.path} 
              to={link.path} 
              className={`text-sm font-bold uppercase tracking-widest hover:text-primary transition-colors ${location.pathname === link.path ? 'text-primary' : 'text-gray-400'}`}
            >
              {link.name}
            </Link>
          ))}
        </div>
        <Link to="/cockpit" className="bg-primary text-black px-6 py-2 rounded-full font-bold text-sm hover:scale-105 transition-transform">
          LAUNCH
        </Link>
      </div>
    </nav>
  );
}
