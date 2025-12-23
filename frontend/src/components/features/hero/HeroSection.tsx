'use client';

import { motion } from 'framer-motion';
import { Search, Play, ChevronDown, Sparkles, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useSearchUrl } from '@/hooks/useSearchUrl';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';

interface HeroSectionProps {
  className?: string;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
      delayChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: 'easeOut' },
  },
};

const AnimatedOrb = ({
  delay,
  duration,
  size,
  position,
}: {
  delay: number;
  duration: number;
  size: string;
  position: string;
}) => (
  <motion.div
    className={`absolute ${size} rounded-full blur-3xl opacity-30`}
    style={{
      background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(139, 92, 246, 0.3))',
      ...Object.fromEntries(
        position.split(' ').map((p, i) => {
          const [key, val] = p.split('-');
          return [i === 0 ? key : `${key}`, val];
        })
      ),
    }}
    animate={{
      y: [0, 30, 0],
      x: [0, 20, 0],
    }}
    transition={{
      duration,
      repeat: Infinity,
      ease: 'easeInOut',
      delay,
    }}
  />
);

export const HeroSection = ({ className = '' }: HeroSectionProps) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [videoOpen, setVideoOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
  };

  const scrollToSection = () => {
    const element = document.getElementById('featured-products');
    element?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className={`relative w-full overflow-hidden ${className}`}>
      {/* Animated Background Orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <AnimatedOrb
          delay={0}
          duration={8}
          size="w-96 h-96"
          position="top-20 -left-48"
        />
        <AnimatedOrb
          delay={2}
          duration={10}
          size="w-80 h-80"
          position="top-40 right-0"
        />
        <AnimatedOrb
          delay={1}
          duration={12}
          size="w-72 h-72"
          position="bottom-20 left-1/3"
        />
      </div>

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background pointer-events-none" />

      {/* Mobile Hero Section */}
      <motion.section
        className="md:hidden relative z-10 px-4 py-12 sm:py-16"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants} className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 bg-primary/10 px-3 py-1 rounded-full mb-4"
          >
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm text-primary font-medium">
              AI-Powered Product Research
            </span>
          </motion.div>

          <h1 className="text-4xl font-bold tracking-tight mb-4 text-foreground">
            Find the Perfect{' '}
            <span className="bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
              Product
            </span>
          </h1>

          <p className="text-base text-muted-foreground mb-8 leading-relaxed">
            Get AI-powered insights on products before you buy. Compare features, read smart summaries, and make confident decisions.
          </p>
        </motion.div>

        {/* Mobile Search */}
        <motion.form
          variants={itemVariants}
          onSubmit={handleSearch}
          className="mb-8"
        >
          <div className="flex gap-2">
            <Input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-3 rounded-lg"
            />
            <Button
              type="submit"
              size="sm"
              className="px-4 bg-primary hover:bg-primary/90"
            >
              <Search className="w-4 h-4" />
            </Button>
          </div>
        </motion.form>

        {/* Mobile CTA */}
        <motion.div variants={itemVariants} className="flex gap-3">
          <Button
            asChild
            className="flex-1 bg-primary hover:bg-primary/90 text-white h-12 rounded-lg"
          >
            <Link to="/search">Start Searching</Link>
          </Button>
          <Button
            variant="outline"
            onClick={() => setVideoOpen(true)}
            className="flex-1 h-12 rounded-lg"
          >
            <Play className="w-4 h-4 mr-2" />
            Watch
          </Button>
        </motion.div>

        {/* Mobile Stats */}
        <motion.div
          variants={itemVariants}
          className="grid grid-cols-3 gap-4 mt-8 pt-8 border-t"
        >
          {[
            { number: '10K+', label: 'Products' },
            { number: '500+', label: 'Videos' },
            { number: '98%', label: 'Accuracy' },
          ].map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-xl font-bold text-foreground">{stat.number}</div>
              <div className="text-xs text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </motion.section>

      {/* Desktop Hero Section */}
      <motion.section
        className="hidden md:flex relative z-10 min-h-screen flex-col items-center justify-center px-6 py-20"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Badge */}
        <motion.div
          variants={itemVariants}
          className="inline-flex items-center gap-2 bg-primary/10 px-4 py-2 rounded-full mb-8"
        >
          <span className="text-sm font-medium">📌 Featured on Product Hunt</span>
        </motion.div>

        {/* Main Heading */}
        <motion.h1
          variants={itemVariants}
          className="text-6xl lg:text-7xl font-bold tracking-tight mb-6 text-center max-w-4xl"
        >
          Find the Perfect{' '}
          <motion.span
            className="bg-gradient-to-r from-primary via-blue-500 to-purple-500 bg-clip-text text-transparent"
            animate={{
              backgroundPosition: ['0% center', '100% center', '0% center'],
            }}
            transition={{ duration: 6, repeat: Infinity }}
          >
            Product
          </motion.span>
          {' '}for Any Need
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          variants={itemVariants}
          className="text-xl text-muted-foreground mb-8 text-center max-w-2xl leading-relaxed"
        >
          Get AI-powered insights on products before you buy. Compare features, read video summaries, and make confident decisions in seconds.
        </motion.p>

        {/* Search Bar */}
        <motion.form
          variants={itemVariants}
          onSubmit={handleSearch}
          className="w-full max-w-2xl mb-8"
        >
          <motion.div
            className="relative group"
            whileHover={{ scale: 1.02 }}
            transition={{ type: 'spring', stiffness: 300 }}
          >
            <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/20 to-purple-500/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition duration-500" />
            <div className="relative flex items-center bg-card/50 backdrop-blur-xl border rounded-xl p-2">
              <Search className="w-5 h-5 text-muted-foreground ml-4" />
              <Input
                type="text"
                placeholder="Search for anything... (laptop, camera, headphones)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 border-0 bg-transparent px-4 py-3 text-lg placeholder:text-muted-foreground focus-visible:ring-0"
              />
              <motion.button
                type="submit"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="mr-2 px-6 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg font-medium transition-colors"
              >
                Search
              </motion.button>
            </div>
          </motion.div>

          {!user && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-3 flex items-center justify-center gap-3 text-xs text-muted-foreground"
            >
              <div className="flex items-center gap-1">
                <Zap className="w-3 h-3 text-yellow-500" />
                <span>Get your free AI-powered search</span>
              </div>
              <div className="inline-flex items-center gap-1 bg-green-500/10 px-2 py-0.5 rounded-full">
                <span className="text-xs font-medium text-green-600">✓ No signup required</span>
              </div>
            </motion.div>
          )}
        </motion.form>

        {/* CTA Buttons */}
        <motion.div
          variants={itemVariants}
          className="flex items-center gap-4 mb-8"
        >
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setVideoOpen(true)}
            className="px-8 py-3 border border-foreground/20 rounded-lg font-medium hover:bg-foreground/5 transition-colors flex items-center gap-2 h-12"
          >
            <Play className="w-5 h-5" />
            See How it Works
          </motion.button>
        </motion.div>

        {/* No Signup Required Badge */}


        {/* Stats Grid */}
        <motion.div
          variants={itemVariants}
          className="grid grid-cols-3 gap-8 mb-8 text-center"
        >
          {[
            { number: '10K+', label: 'Products Analyzed' },
            { number: '500+', label: 'Review Videos' },
            { number: '98%', label: 'Accuracy' },
          ].map((stat, index) => (
            <motion.div
              key={index}
              whileHover={{ scale: 1.1 }}
              transition={{ type: 'spring', stiffness: 400, damping: 17 }}
            >
              <div className="text-4xl font-bold text-foreground mb-2">
                {stat.number}
              </div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Product Hunt Badge */}
        {/* <motion.div
          variants={itemVariants}
          className="mb-4"
        >
          <a
            href="https://www.producthunt.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 border rounded-lg text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <span>📌</span>
            Featured on Product Hunt
          </a>
        </motion.div> */}

        {/* Scroll CTA */}
        <motion.button
          onClick={scrollToSection}
          className="mt-2"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <ChevronDown className="w-6 h-6 text-muted-foreground hover:text-foreground transition-colors" />
        </motion.button>
      </motion.section>

      {/* Video Modal */}
      <Dialog open={videoOpen} onOpenChange={setVideoOpen}>
        <DialogContent className="max-w-4xl">
          <div className="aspect-video bg-black rounded-lg flex items-center justify-center">
            <div className="text-center">
              <Play className="w-16 h-16 text-white mx-auto mb-4" />
              <p className="text-white text-lg">
                Video Coming Soon
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};