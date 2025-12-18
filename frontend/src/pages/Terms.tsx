import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function Terms() {
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
              Terms of Service
            </h1>
            <p className="text-muted-foreground text-lg">
              Last Updated: December 14, 2025
            </p>
          </div>

          <div className="prose prose-slate dark:prose-invert max-w-none space-y-6">
            <p className="text-muted-foreground leading-relaxed">
              Please read these Terms of Service ("Terms", "Terms of Service") carefully before using the https://informedmarketopinions.com website (the "Service") operated by Informed Market Opinions ("us", "we", or "our").
            </p>

            <p className="text-muted-foreground leading-relaxed">
              Your access to and use of the Service is conditioned on your acceptance of and compliance with these Terms. These Terms apply to all visitors, users, and others who access or use the Service.
            </p>

            <p className="text-muted-foreground leading-relaxed">
              By accessing or using the Service you agree to be bound by these Terms. If you disagree with any part of the terms, then you may not access the Service.
            </p>

            {/* Section 1 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                1. Nature of Our Service
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Informed Market Opinions is a product research and aggregation platform. We provide data, reviews, and price comparisons to assist users in making purchasing decisions.
              </p>

              <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-lg border border-blue-200 dark:border-blue-900 p-6">
                <h3 className="font-bold text-foreground mb-3">
                  ⚠️ Important Disclaimer: We are not an online store.
                </h3>
                <p className="text-muted-foreground leading-relaxed mb-3">
                  We do not sell, ship, or handle any physical products. All purchases made through links on our site are handled by third-party retailers (such as Amazon, Walmart, Best Buy, etc.). We are not responsible for:
                </p>
                <ul className="space-y-2 text-muted-foreground">
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>Shipping delays or errors.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>Product defects or warranty claims.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>Returns, refunds, or customer service issues related to the purchase.</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>Discrepancies between the price listed on our site and the price on the retailer's site (retailer prices change frequently).</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Section 2 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                2. Affiliate Disclosure
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Our Service includes links to third-party merchant websites. If you click on a link and make a purchase, we may receive a commission at no extra cost to you.
              </p>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>We participate in the Amazon Services LLC Associates Program.</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>We participate in other affiliate programs including, but not limited to, Skimlinks and the eBay Partner Network.</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>Our editorial content and product rankings are generated based on data and analysis, independent of these affiliate partnerships.</span>
                </li>
              </ul>
            </div>

            {/* Section 3 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                3. Intellectual Property
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                The Service and its original content, features, and functionality (including our proprietary review aggregation algorithms, text, and logos) are and will remain the exclusive property of Informed Market Opinions and its licensors. The Service is protected by copyright, trademark, and other laws of both the United States and foreign countries. Our trademarks and trade dress may not be used in connection with any product or service without the prior written consent of Informed Market Opinions.
              </p>
            </div>

            {/* Section 4 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                4. Links to Other Web Sites
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Our Service contains links to third-party web sites or services that are not owned or controlled by Informed Market Opinions.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Informed Market Opinions has no control over, and assumes no responsibility for, the content, privacy policies, or practices of any third-party web sites or services. You further acknowledge and agree that Informed Market Opinions shall not be responsible or liable, directly or indirectly, for any damage or loss caused or alleged to be caused by or in connection with use of or reliance on any such content, goods, or services available on or through any such web sites or services.
              </p>
            </div>

            {/* Section 5 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                5. Accuracy of Information
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                While we strive to provide accurate and up-to-date information, we make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability, or availability with respect to the website or the information, products, services, or related graphics contained on the website for any purpose.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Any reliance you place on such information is therefore strictly at your own risk. Prices and availability of products are subject to change without notice.
              </p>
            </div>

            {/* Section 6 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                6. Limitation of Liability
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                In no event shall Informed Market Opinions, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from:
              </p>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex gap-3">
                  <span className="text-primary font-bold">(i)</span>
                  <span>your access to or use of or inability to access or use the Service;</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">(ii)</span>
                  <span>any conduct or content of any third party on the Service;</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">(iii)</span>
                  <span>any content obtained from the Service; and</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">(iv)</span>
                  <span>unauthorized access, use or alteration of your transmissions or content, whether based on warranty, contract, tort (including negligence) or any other legal theory, whether or not we have been informed of the possibility of such damage.</span>
                </li>
              </ul>
            </div>

            {/* Section 7 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                7. Governing Law
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                These Terms shall be governed and construed in accordance with the laws of the State of California, United States, without regard to its conflict of law provisions.
              </p>
            </div>

            {/* Section 8 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                8. Changes
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                We reserve the right, at our sole discretion, to modify or replace these Terms at any time. By continuing to access or use our Service after those revisions become effective, you agree to be bound by the revised terms.
              </p>
            </div>

            {/* Section 9 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                9. Contact Us
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                If you have any questions about these Terms, please contact us:
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
