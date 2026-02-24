import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="border-t border-gray-800 py-8 text-center text-primary drop-shadow-[0_0_8px_rgba(0,255,136,0.5)]">
      <p>&copy; 2026 Realms to Riches. Powered by Titan Forge.</p>
      <div className="mt-4 space-x-4">
        <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
        <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
        <Link to="/affiliate-disclosure" className="hover:text-white transition-colors">Affiliate Disclosure</Link>
        <a href="mailto:robertdemottojr50@gmail.com?subject=Support%20Request%20-%20Realms%20to%20Riches" className="hover:text-white transition-colors">Support</a>
      </div>
      <p className="mt-4 text-xs font-bold">
        **Affiliate Disclosure:** This site may contain affiliate links. We may earn a commission if you click through and make a purchase.
      </p>
    </footer>
  );
}
