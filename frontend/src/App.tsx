import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { Toaster } from 'react-hot-toast'

// Auth Provider
import { AuthProvider } from '@/contexts/AuthContext'

// Pages
import Index from '@/pages/Index'
import Search from '@/pages/Search'
import ProductDetails from '@/pages/ProductDetails'
import Profile from '@/pages/Profile'
import Likes from '@/pages/Likes'
import Auth from '@/pages/Auth'
import Pricing from '@/pages/Pricing'
import About from '@/pages/About'
import Contact from '@/pages/Contact'
import Cookies from '@/pages/Cookies'
import Privacy from '@/pages/Privacy'
import Refund from '@/pages/Refund'
import Terms from '@/pages/Terms'
import Faq from '@/pages/Faq'
import HowItWorks from '@/pages/HowItWorks'
import NotFound from '@/pages/NotFound'
import PaymentSuccess from '@/pages/PaymentSuccess'
import PaymentCanceled from '@/pages/PaymentCanceled'
import Checkout from '@/pages/Checkout'
import { GoogleOAuthCallback } from '@/pages/GoogleOAuthCallback'

// Layout
import { Layout } from '@/components/layout/Layout'
import './App.css'

// Scroll to top on route change
function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Index />} />
      <Route path="/search" element={<Search />} />
      <Route path="/product/:slug" element={<ProductDetails />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/likes" element={<Likes />} />
      <Route path="/auth" element={<Auth />} />
      <Route path="/auth/callback" element={<GoogleOAuthCallback />} />
      <Route path="/pricing" element={<Pricing />} />
      <Route path="/about" element={<About />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/cookies" element={<Cookies />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/refund" element={<Refund />} />
      <Route path="/terms" element={<Terms />} />
      <Route path="/faq" element={<Faq />} />
      <Route path="/how-it-works" element={<HowItWorks />} />
      <Route path="/checkout" element={<Checkout />} />
      <Route path="/payment-success" element={<PaymentSuccess />} />
      <Route path="/payment-canceled" element={<PaymentCanceled />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <Toaster position="bottom-left" />
        <ScrollToTop />
        <Layout>
          <AppRoutes />
        </Layout>
      </AuthProvider>
    </Router>
  )
}
