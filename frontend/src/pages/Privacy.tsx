import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function Privacy() {
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
              Privacy Policy & Affiliate Disclosure
            </h1>
            <p className="text-muted-foreground text-lg">
              Last Updated: December 14, 2025
            </p>
          </div>

          <div className="prose prose-slate dark:prose-invert max-w-none space-y-6">
            <p className="text-muted-foreground leading-relaxed">
              At Informed Market Opinions ("we", "us", "our"), accessible from https://informedmarketopinions.com, one of our main priorities is the privacy of our visitors. This Privacy Policy document contains types of information that is collected and recorded by Informed Market Opinions and how we use it.
            </p>

            {/* Section 1 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                1. Affiliate Disclosure (FTC & Merchant Compliance)
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                In compliance with the FTC guidelines, please assume the following about links and posts on this site:
              </p>
              <ul className="space-y-3 text-muted-foreground">
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>
                    <strong>General Affiliate Disclosure:</strong> Informed Market Opinions is a participant in various affiliate marketing programs, which means we may get paid commissions on editorially chosen products purchased through our links to retailer sites. This comes at no extra cost to you.
                  </span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>
                    <strong>Amazon Affiliate Disclosure:</strong> As an Amazon Associate, we earn from qualifying purchases. Informed Market Opinions participates in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com.
                  </span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>
                    <strong>Skimlinks & Third-Party Networks:</strong> We use third-party technologies (such as Skimlinks) to automatically monetize some of the links on our site. These companies may use cookies and other technologies to track clicks and sales for the purpose of calculating commissions.
                  </span>
                </li>
              </ul>
            </div>

            {/* Section 2 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                2. Information We Collect
              </h2>

              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-foreground mb-2">
                    Log Files
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Informed Market Opinions follows a standard procedure of using log files. These files log visitors when they visit websites. The information collected by log files includes internet protocol (IP) addresses, browser type, Internet Service Provider (ISP), date and time stamp, referring/exit pages, and possibly the number of clicks. These are not linked to any information that is personally identifiable. The purpose of the information is for analyzing trends, administering the site, tracking users' movement on the website, and gathering demographic information.
                  </p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-foreground mb-2">
                    Cookies and Web Beacons
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Like any other website, Informed Market Opinions uses "cookies". These cookies are used to store information including visitors' preferences, and the pages on the website that the visitor accessed or visited. The information is used to optimize the users' experience by customizing our web page content based on visitors' browser type and/or other information.
                  </p>
                </div>
              </div>
            </div>

            {/* Section 3 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                3. Third-Party Privacy Policies
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Our Privacy Policy does not apply to other advertisers or websites. Thus, we are advising you to consult the respective Privacy Policies of these third-party ad servers for more detailed information. It may include their practices and instructions about how to opt-out of certain options.
              </p>
              <div className="bg-card rounded-lg border border-border/50 p-6">
                <h3 className="font-semibold text-foreground mb-4">
                  Specific Third-Party Partners we work with:
                </h3>
                <ul className="space-y-3 text-muted-foreground">
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Amazon:</strong>{" "}
                      <a href="#" className="text-primary hover:underline">
                        Amazon Privacy Notice
                      </a>
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Skimlinks (Taboola):</strong> Skimlinks processes personal data for the purpose of affiliate tracking. You can read their full privacy policy and opt-out options here:{" "}
                      <a href="#" className="text-primary hover:underline">
                        Skimlinks Privacy Policy
                      </a>
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Section 4 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                4. CCPA Privacy Rights (Do Not Sell My Personal Information)
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Under the CCPA, among other rights, California consumers have the right to:
              </p>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>Request that a business that collects a consumer's personal data disclose the categories and specific pieces of personal data that a business has collected about consumers.</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>Request that a business delete any personal data about the consumer that a business has collected.</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span>Request that a business that sells a consumer's personal data, not sell the consumer's personal data.</span>
                </li>
              </ul>
              <p className="text-muted-foreground leading-relaxed mt-4">
                If you make a request, we have one month to respond to you. If you would like to exercise any of these rights, please contact us.
              </p>
            </div>

            {/* Section 5 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                5. GDPR Data Protection Rights
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                We would like to make sure you are fully aware of all of your data protection rights. Every user is entitled to the following:
              </p>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span><strong>The right to access</strong> – You have the right to request copies of your personal data.</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span><strong>The right to rectification</strong> – You have the right to request that we correct any information you believe is inaccurate.</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-primary font-bold">•</span>
                  <span><strong>The right to erasure</strong> – You have the right to request that we erase your personal data, under certain conditions.</span>
                </li>
              </ul>
            </div>

            {/* Section 6 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                6. Children's Information
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Another part of our priority is adding protection for children while using the internet. We encourage parents and guardians to observe, participate in, and/or monitor and guide their online activity.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Informed Market Opinions does not knowingly collect any Personal Identifiable Information from children under the age of 13. If you think that your child provided this kind of information on our website, we strongly encourage you to contact us immediately and we will do our best efforts to promptly remove such information from our records.
              </p>
            </div>

            {/* Section 7 */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                7. Contact Us
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                If you have any questions or suggestions about our Privacy Policy, do not hesitate to contact us.
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
