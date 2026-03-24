import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "https://api.realms2riches.com";

export default function Navbar() {
  const location = useLocation();
  
  const links = [
    { name: 'Pricing', path: '/pricing' },
    { name: 'Console', path: '/console' },
    { name: 'Blog', path: '/blog' },
    { name: 'Affiliate Hub', path: '/affiliate-hub' },
    { name: 'Chamber', path: '/chamber' }
  ];

  return (
    <nav className="border-b border-white/5 py-4 sticky top-0 bg-black/80 backdrop-blur-2xl z-50">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link to="/" className="flex items-center gap-3 group">
          <img 
            src={`${BACKEND_URL}/assets/branding/forge_logo.png`} 
            alt="Realms2Riches" 
            className="h-10 w-auto group-hover:scale-110 transition-transform duration-500"
            onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
            }}
          />
          <span className="text-xl font-black tracking-tighter text-white hidden sm:block">
            REALMS2<span className="text-primary">RICHES</span>
          </span>
        </Link>
        <div className="hidden md:flex space-x-8 items-center">
          {links.map(link => (
            <Link 
              key={link.path} 
              to={link.path} 
              className={`text-[10px] font-black uppercase tracking-[0.2em] hover:text-primary transition-all ${location.pathname === link.path ? 'text-primary border-b-2 border-primary pb-1' : 'text-gray-500'}`}
            >
              {link.name}
            </Link>
          ))}
        </div>
        <Link to="/console" className="bg-primary text-black px-8 py-2.5 rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-white transition-all shadow-[0_0_20px_rgba(0,255,136,0.2)]">
          LAUNCH_OS
        </Link>
      </div>
    </nav>
  );
}

