import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Pricing from './pages/Pricing';
import Cockpit from './pages/Cockpit';
import Dashboard from './pages/Dashboard';
import Blog from './pages/Blog';
import BlogPost from './pages/BlogPost';
import Affiliates from './pages/Affiliates';
import Store from './pages/Store';
import Chamber from './pages/Chamber';
import LaunchControl from './pages/LaunchControl';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';
import AffiliateDisclosure from './pages/AffiliateDisclosure';
import Success from './pages/Success';
import Cancel from './pages/Cancel';
import Footer from './components/Footer';
import Navbar from './components/Navbar';
import CookieBanner from './components/CookieBanner';
import LeadGenPopup from './components/LeadGenPopup';

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/cockpit" element={<Cockpit />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/blog" element={<Blog />} />
            <Route path="/blog/:slug" element={<BlogPost />} />
            <Route path="/affiliates" element={<Affiliates />} />
            <Route path="/store" element={<Store />} />
            <Route path="/chamber" element={<Chamber />} />
            <Route path="/sovereign" element={<LaunchControl />} />
            <Route path="/privacy" element={<PrivacyPolicy />} />
            <Route path="/terms" element={<TermsOfService />} />
            <Route path="/affiliate-disclosure" element={<AffiliateDisclosure />} />
            <Route path="/success" element={<Success />} />
            <Route path="/cancel" element={<Cancel />} />
          </Routes>
        </main>
        <Footer />
        <CookieBanner />
        <LeadGenPopup />
      </div>
    </Router>
  );
}

export default App;
