import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function Refund() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/20 to-background/80">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 max-w-4xl">
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
          className="mb-8 hover:bg-muted"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>

        <div className="space-y-8">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Refund & Return Policy
            </h1>
            <p className="text-muted-foreground text-lg">
              Last Updated: December 14, 2025
            </p>
          </div>

          <div className="prose prose-slate dark:prose-invert max-w-none space-y-6">
            <p className="text-muted-foreground leading-relaxed">
              Thank you for visiting Informed Market Opinions.
            </p>

            {/* Important Section */}
            <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 rounded-lg border border-orange-200 dark:border-orange-900 p-6">
              <h2 className="text-xl font-bold text-foreground mb-3">
                ⚠️ Important: We Do Not Sell Products Directly
              </h2>
              <p className="text-muted-foreground leading-relaxed mb-3">
                Informed Market Opinions is a product research and comparison platform. We provide data, reviews, and links to help you find the best products at the best prices. We do not manufacture, stock, sell, or ship any physical items.
              </p>
              <p className="text-muted-foreground leading-relaxed font-semibold">
                Because we are not the seller, we cannot process refunds, returns, or exchanges.
              </p>
            </div>

            {/* Section 1 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                1. How to Return a Product
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                All purchases made through links on our site are handled by third-party retailers (such as Amazon, Walmart, Best Buy, Home Depot, etc.).
              </p>
              <p className="text-muted-foreground leading-relaxed">
                If you need to return an item, request a refund, or check on a shipping delay, you must contact the retailer where you made the final purchase.
              </p>

              <div className="bg-card rounded-lg border border-border/50 p-6">
                <h3 className="font-semibold text-foreground mb-4">
                  Common Retailer Return Links:
                </h3>
                <p className="text-sm text-muted-foreground mb-4">
                  If you bought a product after clicking a link on our site, please check your email receipt to see which store processed your payment. Here are the return centers for the most common retailers we link to:
                </p>
                <ul className="space-y-2 text-muted-foreground">
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Amazon:</strong>{" "}
                      <a href="#" className="text-primary hover:underline">
                        Start a Return on Amazon
                      </a>
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Walmart:</strong>{" "}
                      <a href="#" className="text-primary hover:underline">
                        Walmart Returns & Refunds
                      </a>
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Best Buy:</strong>{" "}
                      <a href="#" className="text-primary hover:underline">
                        Best Buy Returns & Exchanges
                      </a>
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Home Depot:</strong>{" "}
                      <a href="#" className="text-primary hover:underline">
                        Home Depot Return Policy
                      </a>
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>eBay:</strong>{" "}
                      <a href="#" className="text-primary hover:underline">
                        eBay Returns
                      </a>
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Section 2 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                2. Warranties and Defective Items
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Informed Market Opinions does not offer any warranties or guarantees on products listed on our website.
              </p>
              <ul className="space-y-3 text-muted-foreground">
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>
                    <strong>Defects:</strong> If a product arrives damaged or defective, please contact the merchant immediately.
                  </span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>
                    <strong>Warranties:</strong> Any warranty coverage is provided solely by the manufacturer or the retailer. Please refer to the documentation inside your product packaging.
                  </span>
                </li>
              </ul>
            </div>

            {/* Section 3 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                3. Pricing Discrepancies
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                We do our best to ensure the prices listed on Informed Market Opinions are accurate and up-to-date. However, prices on retailer websites change frequently and dynamically.
              </p>
              <ul className="space-y-3 text-muted-foreground">
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>
                    <strong>The Final Price:</strong> The price displayed on the retailer's checkout page is the final price you will pay.
                  </span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>
                    <strong>Refunds for Price Differences:</strong> We cannot refund the difference if a price on our site does not match the retailer's current price.
                  </span>
                </li>
              </ul>
            </div>

            {/* Section 4 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                4. Contact Us
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                If you are unsure which retailer you purchased from, or if you have questions about how our site works, feel free to contact us. Please note that we cannot authorize refunds, but we can help point you in the right direction.
              </p>
              <div className="bg-card rounded-lg border border-border/50 p-4">
                <p className="text-muted-foreground">
                  Email:{" "}
                  <a href="mailto:imhollc27@gmail.com" className="text-primary hover:underline">
                    imhollc27@gmail.com
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
