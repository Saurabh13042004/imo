import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { HighConversionPricing } from "@/components/home/pricing";
import { MetaTags } from "@/components/seo";

const Pricing = () => {
  return (
    <>
      <MetaTags 
        title="Pricing - Flexible Plans for Every Shopper | IMO"
        description="Choose from Free Forever, Pay-as-you-Go ($4.99), or Premium Unlimited ($10.99/mo). No hidden fees, cancel anytime."
        keywords="IMO pricing, product research pricing, AI shopping plans, subscription pricing"
        canonicalUrl="https://informedmarketopinions.com/pricing"
      />
      <div className="min-h-screen bg-background">
      {/* Hero Section */}
      {/* <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Badge variant="secondary" className="mb-4">Pricing</Badge>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
              Simple, Transparent Pricing
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Choose the plan that fits your needs. Start free and upgrade whenever you're ready.
            </p>
          </motion.div>
        </div>
      </section> */}

      {/* Pricing Section */}
      <section className="py-16 px-1 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <HighConversionPricing />
        </div>
      </section>

      </div>
    </>
  );
};

export default Pricing;