import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useEffect, lazy, Suspense, useMemo } from 'react'
import { Toaster } from 'react-hot-toast'

// Auth Provider
import { AuthProvider } from '@/contexts/AuthContext'

// QueryClient Provider - lazy loaded for routes that need it
import { QueryClientWrapper } from '@/components/providers/QueryClientWrapper'

// Layout
import { Layout } from '@/components/layout/Layout'
import './App.css'

// Lightweight loading fallback for code-split routes
const LoadingFallback = () => (
  <div className="flex items-center justify-center min-h-screen bg-background">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
  </div>
)

// Lazy-loaded Pages - Only Index is loaded initially
const Index = lazy(() => import('@/pages/Index'))
const Search = lazy(() => import('@/pages/Search'))
const ProductDetails = lazy(() => import('@/pages/ProductDetails'))
const Profile = lazy(() => import('@/pages/Profile'))
const Likes = lazy(() => import('@/pages/Likes'))
const Auth = lazy(() => import('@/pages/Auth'))
const Pricing = lazy(() => import('@/pages/Pricing'))
const About = lazy(() => import('@/pages/About'))
const Contact = lazy(() => import('@/pages/Contact'))
const Cookies = lazy(() => import('@/pages/Cookies'))
const Privacy = lazy(() => import('@/pages/Privacy'))
const Refund = lazy(() => import('@/pages/Refund'))
const Terms = lazy(() => import('@/pages/Terms'))
const Faq = lazy(() => import('@/pages/Faq'))
const HowItWorks = lazy(() => import('@/pages/HowItWorks'))
const NotFound = lazy(() => import('@/pages/NotFound'))
const PaymentSuccess = lazy(() => import('@/pages/PaymentSuccess'))
const PaymentCanceled = lazy(() => import('@/pages/PaymentCanceled'))
const Checkout = lazy(() => import('@/pages/Checkout'))
const GoogleOAuthCallback = lazy(() => import('@/pages/GoogleOAuthCallback'))
const SubscriptionManager = lazy(() => import('@/pages/SubscriptionManager'))
const ReviewGuidelines = lazy(() => import('@/pages/ReviewGuidelines'))
const Admin = lazy(() => import('@/pages/Admin'))
const ResetPassword = lazy(() => import('@/pages/ResetPassword'))

// Routes that require react-query (async data fetching)
const QUERY_CLIENT_ROUTES = new Set([
  '/search',
  '/product/:slug',
  '/admin',
  '/checkout',
  '/payment-success',
  '/payment-canceled',
  '/subscription-manager',
  '/review-guidelines',
  '/profile',
  '/likes',
])

// Scroll to top on route change
function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

function AppRoutes() {
  const { pathname } = useLocation()
  
  // Check if current route needs react-query
  const needsQueryClient = useMemo(() => {
    return Array.from(QUERY_CLIENT_ROUTES).some(route => {
      if (route === '/product/:slug') {
        return pathname.startsWith('/product/')
      }
      return pathname === route
    })
  }, [pathname])

  const routes = (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/search" element={<Search />} />
        <Route path="/product/:slug" element={<ProductDetails />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/likes" element={<Likes />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/auth/callback" element={<GoogleOAuthCallback />} />
        <Route path="/reset-password" element={<ResetPassword />} />
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
        <Route path="/subscription-manager" element={<SubscriptionManager />} />
        <Route path="/review-guidelines" element={<ReviewGuidelines />} />
        <Route path="/admin" element={<Admin />} />
        {/* Dashboard redirect for backward compatibility */}
        <Route path="/dashboard" element={<Navigate to="/payment-success" replace />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  )

  // Only wrap with QueryClientProvider if needed
  if (needsQueryClient) {
    return <QueryClientWrapper>{routes}</QueryClientWrapper>
  }

  return routes
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
