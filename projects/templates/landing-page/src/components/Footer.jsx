import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="border-t border-gray-800 py-8 text-center text-gray-500">
      <p>&copy; 2026 Realms to Riches. Powered by Titan Forge.</p>
      <div className="mt-4 space-x-4">
        <Link to="/privacy" className="hover:text-primary">Privacy Policy</Link>
        <Link to="/terms" className="hover:text-primary">Terms of Service</Link>
        <Link to="/affiliate-disclosure" className="hover:text-primary">Affiliate Disclosure</Link>
      </div>
      <p className="mt-4 text-xs">
        **Affiliate Disclosure:** This site may contain affiliate links. We may earn a commission if you click through and make a purchase.
      </p>
    </footer>
  );
}
