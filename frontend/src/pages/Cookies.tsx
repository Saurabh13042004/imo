import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function Cookies() {
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
              Cookie Policy
            </h1>
            <p className="text-muted-foreground text-lg">
              Last Updated: December 14, 2025
            </p>
          </div>

          <div className="prose prose-slate dark:prose-invert max-w-none space-y-6">
            <p className="text-muted-foreground leading-relaxed">
              This Cookie Policy explains how Informed Market Opinions ("we", "us", and "our") uses cookies and similar technologies to recognize you when you visit our website at https://informedmarketopinions.com. It explains what these technologies are and why we use them, as well as your rights to control our use of them.
            </p>

            {/* Section 1 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                1. What are cookies?
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Cookies are small data files that are placed on your computer or mobile device when you visit a website. Cookies are widely used by website owners in order to make their websites work, or to work more efficiently, as well as to provide reporting information.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Cookies set by the website owner (Informed Market Opinions) are called "first-party cookies". Cookies set by parties other than the website owner are called "third-party cookies". Third-party cookies enable third-party features or functionality to be provided on or through the website (e.g., advertising, interactive content, and analytics).
              </p>
            </div>

            {/* Section 2 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                2. Why do we use cookies?
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                We use first-party and third-party cookies for several reasons. Some cookies are required for technical reasons in order for our Website to operate, and we refer to these as "essential" or "strictly necessary" cookies. Other cookies also enable us to track and target the interests of our users to enhance the experience on our Online Properties. Third parties serve cookies through our Website for advertising, analytics, and other purposes.
              </p>
            </div>

            {/* Section 3 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                3. Specific Types of Cookies We Use
              </h2>

              <div className="space-y-4 bg-card rounded-lg border border-border/50 p-6">
                <h3 className="text-xl font-semibold text-foreground">
                  Essential Website Cookies
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  These cookies are strictly necessary to provide you with services available through our Website and to use some of its features, such as access to secure areas.
                </p>
              </div>

              <div className="space-y-4 bg-card rounded-lg border border-border/50 p-6">
                <h3 className="text-xl font-semibold text-foreground">
                  Performance and Analytics Cookies
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  These cookies collect information that is used either in aggregate form to help us understand how our Website is being used or how effective our marketing campaigns are, or to help us customize our Website for you.
                </p>
              </div>

              <div className="space-y-4 bg-gradient-to-br from-purple-500/10 to-blue-500/10 rounded-lg border border-purple-200 dark:border-purple-900 p-6">
                <h3 className="text-xl font-semibold text-foreground">
                  Affiliate & Advertising Cookies (Crucial)
                </h3>
                <p className="text-muted-foreground leading-relaxed font-semibold mb-3">
                  This is the most important section for our users. Informed Market Opinions is an affiliate marketing site. We use third-party cookies to track referrals to retailer websites.
                </p>

                <div className="space-y-3">
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">
                      How it works:
                    </h4>
                    <p className="text-muted-foreground leading-relaxed">
                      When you click a link on our site to a retailer (like Walmart, Best Buy, or Amazon), a cookie is placed on your device. This cookie identifies that you came from our site so the retailer can pay us a small commission if you make a purchase.
                    </p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-foreground mb-2">
                      Third Parties:
                    </h4>
                    <p className="text-muted-foreground leading-relaxed">
                      We work with Amazon Associates, Skimlinks, and the eBay Partner Network. These partners may place cookies on your browser to track the performance of their advertising program.
                    </p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-foreground mb-2">
                      Skimlinks:
                    </h4>
                    <p className="text-muted-foreground leading-relaxed">
                      Skimlinks collects data about the websites you visit and the links you click to provide relevant advertising and analyze trends.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Section 4 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                4. How can you control cookies?
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                You have the right to decide whether to accept or reject cookies. You can exercise your cookie rights by setting your browser controls to accept or refuse cookies. If you choose to reject cookies, you may still use our website though your access to some functionality and areas of our website may be restricted.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Most advertising networks offer you a way to opt out of targeted advertising. If you would like to find out more information, please visit{" "}
                <a href="http://www.aboutads.info/choices/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                  http://www.aboutads.info/choices/
                </a>{" "}
                or{" "}
                <a href="http://www.youronlinechoices.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                  http://www.youronlinechoices.com
                </a>
                .
              </p>
            </div>

            {/* Section 5 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                5. Updates to this Policy
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                We may update this Cookie Policy from time to time in order to reflect, for example, changes to the cookies we use or for other operational, legal, or regulatory reasons. Please therefore re-visit this Cookie Policy regularly to stay informed about our use of cookies and related technologies.
              </p>
            </div>

            {/* Section 6 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                6. Contact Us
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                If you have any questions about our use of cookies or other technologies, please email us at:
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
