import { useState, useEffect } from 'react';

export default function CookieBanner() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem('cookiesAccepted')) {
      setVisible(true);
    }
  }, []);

  const accept = () => {
    localStorage.setItem('cookiesAccepted', 'true');
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-primary p-4 flex justify-center items-center gap-4 z-50">
      <span>We use cookies to improve your experience.</span>
      <button onClick={accept} className="bg-primary text-black px-4 py-1 rounded font-bold hover:opacity-90">
        Accept
      </button>
    </div>
  );
}
