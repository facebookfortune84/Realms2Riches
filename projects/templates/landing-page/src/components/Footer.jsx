export default function Footer() {
  return (
    <footer className="border-t border-gray-800 py-8 text-center text-gray-500">
      <p>&copy; 2026 Realms to Riches. Powered by Titan Forge.</p>
      <div className="mt-4 space-x-4">
        <a href="#" className="hover:text-primary">Privacy Policy</a>
        <a href="#" className="hover:text-primary">Terms of Service</a>
        <a href="#" className="hover:text-primary">Affiliate Disclosure</a>
      </div>
      <p className="mt-4 text-xs">
        **Affiliate Disclosure:** This site may contain affiliate links. We may earn a commission if you click through and make a purchase.
      </p>
    </footer>
  );
}
