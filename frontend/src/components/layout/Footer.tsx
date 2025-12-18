import { Link } from "react-router-dom";
import { Separator } from "@/components/ui/separator";

export const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="border-t border-border/50 bg-muted/30 mt-auto">
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          
          {/* Brand Column */}
          <div className="lg:col-span-1">
            <Link to="/" className="flex items-center space-x-2 mb-4">
              <span className="text-2xl font-bold tracking-tight">
                IMO
              </span>
            </Link>
            <p className="text-sm text-muted-foreground mb-2 font-semibold">
              AI-powered product research that saves you time and money
            </p>
            <p className="text-sm text-muted-foreground">
              Compare thousands of reviews, videos, and expert opinions in seconds—not hours.
            </p>
          </div>
          
          {/* Product Column */}
          <div>
            <h3 className="text-foreground font-semibold text-sm uppercase tracking-wider mb-4">
              Product
            </h3>
            <ul className="space-y-3">
              <li>
                <Link to="/search" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Search
                </Link>
              </li>
              <li>
                <Link to="/how-it-works" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  How It Works
                </Link>
              </li>
              <li>
                <Link to="/#featured" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Featured Products
                </Link>
              </li>
              <li>
                <Link to="/pricing" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Pricing
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Company Column */}
          <div>
            <h3 className="text-foreground font-semibold text-sm uppercase tracking-wider mb-4">
              Company
            </h3>
            <ul className="space-y-3">
              <li>
                <Link to="/about" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/faq" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  FAQ
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Legal Column */}
          <div>
            <h3 className="text-foreground font-semibold text-sm uppercase tracking-wider mb-4">
              Legal
            </h3>
            <ul className="space-y-3">
              <li>
                <Link to="/privacy" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link to="/cookies" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Cookie Policy
                </Link>
              </li>
              <li>
                <Link to="/refund" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Refund Policy
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Support Column */}
          <div>
            <h3 className="text-foreground font-semibold text-sm uppercase tracking-wider mb-4">
              Support
            </h3>
            <ul className="space-y-3">
              <li>
                <Link to="/help" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Help Center
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Contact Support
                </Link>
              </li>
              <li>
                <a href="mailto:support@imo.com" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Report an Issue
                </a>
              </li>
            </ul>
          </div>
          
        </div>
      </div>
      
      {/* Bottom Bar */}
      <Separator className="opacity-30" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground">
            © {currentYear} IMO. All rights reserved.
          </p>
          <p className="text-sm text-muted-foreground">
            Made with ❤️ for smart shoppers
          </p>
        </div>
      </div>
    </footer>
  );
};
