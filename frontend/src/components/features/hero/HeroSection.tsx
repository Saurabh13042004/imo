'use client';

import { motion } from 'framer-motion';
import Search from 'lucide-react/dist/esm/icons/search';
import Play from 'lucide-react/dist/esm/icons/play';
import ChevronDown from 'lucide-react/dist/esm/icons/chevron-down';
import Sparkles from 'lucide-react/dist/esm/icons/sparkles';
import Zap from 'lucide-react/dist/esm/icons/zap';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useSearchUrl } from '@/hooks/useSearchUrl';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef, useMemo } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import React from 'react';

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
  animationsEnabled = false,
}: {
  delay: number;
  duration: number;
  size: string;
  position: string;
  animationsEnabled?: boolean;
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
    animate={animationsEnabled ? {
      y: [0, 30, 0],
      x: [0, 20, 0],
    } : { y: 0, x: 0 }}
    transition={{
      duration,
      repeat: animationsEnabled ? Infinity : 0,
      ease: 'easeInOut',
      delay,
    }}
  />
);

const MemoizedAnimatedOrb = React.memo(AnimatedOrb);

const Counter = ({ 
  from = 0, 
  to, 
  suffix = '', 
  duration = 2,
  animationsEnabled = false,
}: { 
  from?: number; 
  to: number; 
  suffix?: string; 
  duration?: number;
  animationsEnabled?: boolean;
}) => {
  const [count, setCount] = useState(from);

  useEffect(() => {
    if (!animationsEnabled) {
      // Show final value immediately if animations not enabled
      setCount(to);
      return;
    }

    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = (currentTime - startTime) / (duration * 1000);

      if (progress < 1) {
        setCount(Math.floor(from + (to - from) * progress));
        animationFrame = requestAnimationFrame(animate);
      } else {
        setCount(to);
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrame);
  }, [from, to, duration, animationsEnabled]);

  return <>{count}{suffix}</>;
};

const MemoizedCounter = React.memo(Counter);

export const HeroSection = ({ className = '' }: HeroSectionProps) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [videoOpen, setVideoOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [animationsEnabled, setAnimationsEnabled] = useState(false);

  // Lazy load video after component mounts
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load();
    }
  }, []);

  // Enable animations after first paint to avoid blocking LCP
  useEffect(() => {
    if ('requestIdleCallback' in window) {
      // Use requestIdleCallback for better prioritization
      requestIdleCallback(() => setAnimationsEnabled(true));
    } else {
      // Fallback for browsers without requestIdleCallback
      const timeoutId = setTimeout(() => setAnimationsEnabled(true), 100);
      return () => clearTimeout(timeoutId);
    }
  }, []);

  // Microsoft Clarity is initialized globally in main.tsx using the NPM package
  // No additional loading needed here

  const handleVideoClick = () => {
    if (videoRef.current && !isVideoPlaying) {
      videoRef.current.play();
      setIsVideoPlaying(true);
    }
  };

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
      {/* Animated Background Orbs - Deferred */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <MemoizedAnimatedOrb
          delay={0}
          duration={8}
          size="w-96 h-96"
          position="top-20 -left-48"
          animationsEnabled={animationsEnabled}
        />
        <MemoizedAnimatedOrb
          delay={2}
          duration={10}
          size="w-80 h-80"
          position="top-40 right-0"
          animationsEnabled={animationsEnabled}
        />
        <MemoizedAnimatedOrb
          delay={1}
          duration={12}
          size="w-72 h-72"
          position="bottom-20 left-1/3"
          animationsEnabled={animationsEnabled}
        />
      </div>

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background pointer-events-none" />

      {/* Mobile Hero Section */}
      <motion.section
        className="md:hidden relative z-10 px-4 py-8 sm:py-12"
        variants={containerVariants}
        initial="hidden"
        animate={animationsEnabled ? "visible" : "hidden"}
      >
        <motion.div variants={itemVariants} className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4 text-foreground leading-tight">
            AI That Reads Every Review
            <br />
            <span className="text-foreground text-2xl sm:text-3xl font-semibold">—So You Don't Have To</span>
          </h1>

          <p className="text-sm text-muted-foreground mb-6 leading-relaxed font-light">
            IMO compares 10,000+ reviews, videos, Reddit threads, and blogs so you can shop smarter in seconds.
          </p>
        </motion.div>

        {/* Mobile Search - Constrained */}
        <motion.form
          variants={itemVariants}
          onSubmit={handleSearch}
          className="mb-8 w-full"
        >
          <motion.div
            className="relative group"
            whileHover={{ scale: 1.01 }}
            transition={{ type: 'spring', stiffness: 300 }}
          >
            <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/20 to-blue-500/20 rounded-xl blur opacity-50 group-hover:opacity-75 transition duration-500" />
            <div className="relative flex items-center bg-card/95 backdrop-blur-xl border border-primary/20 rounded-xl p-3">
              <Search className="w-5 h-5 text-primary ml-3 flex-shrink-0" />
              <Input
                type="text"
                placeholder="Search any product..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 border-0 bg-transparent px-3 py-3 text-sm placeholder:text-muted-foreground/50 focus-visible:ring-0"
              />
              <Button
                type="submit"
                size="sm"
                className="mr-2 px-3 bg-primary hover:bg-primary/90"
              >
                <Search className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>

          {!user && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={animationsEnabled ? { opacity: 1, y: 0 } : { opacity: 1, y: 0 }}
              transition={{ delay: animationsEnabled ? 0.2 : 0 }}
              className="mt-2 flex items-center justify-center gap-1 text-xs text-muted-foreground"
            >
              <Zap className="w-4 h-4 text-yellow-500" />
              <span>No signup • 3 free • 7 days trial</span>
            </motion.div>
          )}
        </motion.form>

        {/* Trust Grid - Mobile (2x2) with Counting Animation */}
        <motion.div
          variants={itemVariants}
          className="grid grid-cols-2 gap-4 mb-8"
        >
          <div className="bg-card/50 rounded-lg p-4 border border-foreground/10 text-center">
            <div className="text-2xl font-bold text-primary mb-1">
              <MemoizedCounter to={10} suffix="K+" duration={2} animationsEnabled={animationsEnabled} />
            </div>
            <div className="text-xs text-muted-foreground">Reviews</div>
          </div>
          <div className="bg-card/50 rounded-lg p-4 border border-foreground/10 text-center">
            <div className="text-2xl font-bold text-primary mb-1">
              <MemoizedCounter to={98} suffix="%" duration={2} animationsEnabled={animationsEnabled} />
            </div>
            <div className="text-xs text-muted-foreground">Accuracy</div>
          </div>
          <div className="bg-card/50 rounded-lg p-4 border border-foreground/10 text-center">
            <div className="text-2xl font-bold text-primary mb-1">
              <MemoizedCounter to={500} suffix="+" duration={2} animationsEnabled={animationsEnabled} />
            </div>
            <div className="text-xs text-muted-foreground">Videos</div>
          </div>
          <div className="bg-card/50 rounded-lg p-4 border border-foreground/10 text-center">
            <div className="text-2xl font-bold text-primary mb-1">
              <MemoizedCounter to={100} suffix="+" duration={2} animationsEnabled={animationsEnabled} />
            </div>
            <div className="text-xs text-muted-foreground">Retailers</div>
          </div>
        </motion.div>

        {/* Key Features - Mobile */}
        <motion.div
          variants={itemVariants}
          className="space-y-3 mb-8"
        >
          <div className="flex gap-3 p-3 bg-card/50 rounded-lg border border-foreground/5">
            <div className="text-2xl flex-shrink-0">📊</div>
            <div className="text-sm">
              <div className="font-semibold text-xs mb-1">Comprehensive Analysis</div>
              <div className="text-xs text-muted-foreground">Amazon, Reddit, YouTube, blogs & more</div>
            </div>
          </div>
          <div className="flex gap-3 p-3 bg-card/50 rounded-lg border border-foreground/5">
            <div className="text-2xl flex-shrink-0">⚡</div>
            <div className="text-sm">
              <div className="font-semibold text-xs mb-1">AI-Powered</div>
              <div className="text-xs text-muted-foreground">Filters fake reviews & real insights</div>
            </div>
          </div>
          <div className="flex gap-3 p-3 bg-card/50 rounded-lg border border-foreground/5">
            <div className="text-2xl flex-shrink-0">🎯</div>
            <div className="text-sm">
              <div className="font-semibold text-xs mb-1">Top 3 Ranked</div>
              <div className="text-xs text-muted-foreground">Best options based on your needs</div>
            </div>
          </div>
        </motion.div>
      </motion.section>

      {/* Desktop Hero Section */}
      <motion.section
        className="hidden md:flex relative z-10 min-h-screen flex-col items-center justify-center px-6 pt-20 pb-12"
        variants={containerVariants}
        initial="hidden"
        animate={animationsEnabled ? "visible" : "hidden"}
      >
        {/* Main Heading - Professional and Bold */}
        <motion.h1
          variants={itemVariants}
          className="text-5xl lg:text-6xl font-bold tracking-tight mb-6 text-center max-w-5xl leading-tight"
        >
          AI That Reads Every Review
          <br />
          <span className="text-foreground">—So You Don't Have To</span>
        </motion.h1>

        {/* Subtitle - Informative and Clear */}
        <motion.p
          variants={itemVariants}
          className="text-xl text-muted-foreground mb-12 text-center max-w-3xl leading-relaxed font-light"
        >
          IMO compares and summarizes 10,000+ reviews, videos, Reddit threads, and blogs—so you can shop smarter in seconds, not hours.
        </motion.p>

        {/* Search Bar - Constrained Width */}
        <motion.form
          onSubmit={handleSearch}
          className="mb-8 w-full max-w-2xl"
          variants={itemVariants}
          whileHover={{ scale: 1.01 }}
          transition={{ type: 'spring', stiffness: 300 }}
        >
          <div className="relative group">
            {/* Subtle glow */}
            <div className="absolute -inset-1 bg-gradient-to-r from-primary/30 to-blue-500/20 rounded-2xl blur-2xl opacity-30 group-hover:opacity-50 transition duration-500" />
            
            {/* Search input */}
            <div className="relative flex items-center bg-card/95 backdrop-blur-xl border border-primary/20 rounded-2xl p-5 shadow-xl">
              <Search className="w-6 h-6 text-primary ml-4 flex-shrink-0" />
              <Input
                type="text"
                placeholder="Search any product..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 border-0 bg-transparent px-4 py-3 text-base placeholder:text-muted-foreground/50 focus-visible:ring-0 focus-visible:outline-none"
              />
              <motion.button
                type="submit"
                whileHover={{ scale: 1.08 }}
                whileTap={{ scale: 0.92 }}
                className="mr-2 px-6 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-lg font-semibold transition-colors text-sm"
              >
                Search
              </motion.button>
            </div>
          </div>
          
          {!user && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={animationsEnabled ? { opacity: 1, y: 0 } : { opacity: 1, y: 0 }}
              transition={{ delay: animationsEnabled ? 0.2 : 0 }}
              className="mt-3 flex items-center justify-center gap-2 text-xs text-muted-foreground"
            >
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="font-medium">No signup • 3 free searches • 7 days free trial</span>
            </motion.div>
          )}
        </motion.form>

        {/* Trust Indicators - Clean Grid with Counting Animation */}
        <motion.div
          variants={itemVariants}
          className="w-full max-w-4xl mb-20 mt-8"
        >
          <div className="grid grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-primary mb-2">
                <MemoizedCounter to={10} suffix="K+" duration={2} animationsEnabled={animationsEnabled} />
              </div>
              <div className="text-sm text-muted-foreground">Reviews Analyzed</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary mb-2">
                <MemoizedCounter to={500} suffix="+" duration={2} animationsEnabled={animationsEnabled} />
              </div>
              <div className="text-sm text-muted-foreground">Video Sources</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary mb-2">
                <MemoizedCounter to={98} suffix="%" duration={2} animationsEnabled={animationsEnabled} />
              </div>
              <div className="text-sm text-muted-foreground">Accuracy</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary mb-2">
                <MemoizedCounter to={100} suffix="+" duration={2} animationsEnabled={animationsEnabled} />
              </div>
              <div className="text-sm text-muted-foreground">Retailers</div>
            </div>
          </div>
        </motion.div>

        {/* Video Demo */}
        <motion.div
          variants={itemVariants}
          className="w-full max-w-4xl mb-12"
        >
          <div 
            className="relative rounded-xl overflow-hidden shadow-2xl border border-foreground/10 cursor-pointer group"
            onClick={handleVideoClick}
          >
            <div className="aspect-video bg-gradient-to-br from-primary/20 to-purple-500/20 relative">
              <video
                ref={videoRef}
                controls={isVideoPlaying}
                muted
                playsInline
                preload="none"
                poster="https://d3tmtixqwd7vky.cloudfront.net/imo-assets/hero-poster.webp"
                className="w-full h-full object-cover"
              >
                <source
                  src="https://d3tmtixqwd7vky.cloudfront.net/imo-assets/IMOVideo-optimized.mp4"
                  type="video/mp4"
                />
                Your browser does not support the video tag.
              </video>
              
              {!isVideoPlaying && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/30 transition-colors">
                  <div className="flex items-center justify-center w-16 h-16 bg-white/20 backdrop-blur-sm rounded-full group-hover:bg-white/30 transition-colors">
                    <Play className="w-8 h-8 text-white ml-1" fill="white" />
                  </div>
                </div>
              )}
            </div>
          </div>
          <p className="text-center text-sm text-muted-foreground mt-3">
            See how IMO works in action
          </p>
        </motion.div>

        {/* Scroll CTA */}
        <motion.button
          onClick={scrollToSection}
          className="mt-4"
          animate={animationsEnabled ? { y: [0, 10, 0] } : { y: 0 }}
          transition={{ duration: 2, repeat: animationsEnabled ? Infinity : 0 }}
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