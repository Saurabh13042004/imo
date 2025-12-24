import { useCallback, useEffect, useState } from "react";
import { SearchForm } from "@/components/search/SearchForm";
import { SearchResults } from "@/components/search/SearchResults";
import { SearchLoading } from "@/components/search/SearchLoading";
import { LocationPermissionBanner } from "@/components/search/LocationPermissionBanner";
import { useToast } from "@/hooks/use-toast";
import { useParallax } from "@/hooks/useParallax";
import { useProductSearch } from "@/hooks/useProductSearch";
import { useSearchUrl } from "@/hooks/useSearchUrl";
import { useAuth } from "@/hooks/useAuth";
import toast from "react-hot-toast";
import {
	getRemainingGuestSearches,
	incrementGuestSearchCount,
	hasGuestSearchesRemaining,
	getProductDisplayLimit,
	getGuestFreeSearchCount,
} from "@/utils/accessControl";
import { Button } from "@/components/ui/button";
import { X, LogIn } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { MetaTags } from "@/components/seo";
import { number } from "framer-motion";
import { set } from "date-fns";

const Search = () => {
	useParallax();
	const { query, zipcode, country, city, language, isDetectingLocation } = useSearchUrl();
	const { user } = useAuth();
	const navigate = useNavigate();
	
	const [hasSubmitted, setHasSubmitted] = useState(false);
	const [page, setPage] = useState(1);
	const [isLoading, setIsLoading] = useState(false);
	const [remainingSearches, setRemainingSearches] = useState(getGuestFreeSearchCount());
	const [dailyLimitReached, setDailyLimitReached] = useState(false);
	const [showGuestBanner, setShowGuestBanner] = useState(!user);
	const [searchesExhausted, setSearchesExhausted] = useState(false);
	const [productDisplayLimit, setProductDisplayLimit] = useState(5);
	const [clearedProducts, setClearedProducts] = useState<any[]>([]);
	const [lastQuery, setLastQuery] = useState<string>("");
	const [searchCounted, setSearchCounted] = useState(false);
	const [dismissLocationBanner, setDismissLocationBanner] = useState(() => {
		// Check localStorage on mount
		return localStorage.getItem('location-banner-dismissed') === 'true' || 
		       localStorage.getItem('location-permission-granted') === 'true';
	});


	const {
		products,
		totalCount,
		totalPages,
		hasNextPage,
		hasPrevPage,
		error,
		isLoading: searchIsLoading,
	} = useProductSearch({
		query: query,
		zipcode: zipcode,
		country: country,
		city: city,
		language: language,
		enabled: hasSubmitted && !!query?.trim() && !searchesExhausted,
		page: page,
	});

	// Clear products when query changes (new search)
	useEffect(() => {
		if (query && query !== lastQuery) {
			setClearedProducts([]);
			setLastQuery(query);
			setPage(1);
			setSearchCounted(false); // Reset count flag for new query
		}
	}, [query, lastQuery]);

	// Use cleared products for new searches, but use actual products once they arrive
	const displayedProducts = products.length > 0 ? products : clearedProducts;

	// Apply display limit based on user tier
	const displayProducts = user
		? displayedProducts
		: displayedProducts.slice(0, productDisplayLimit);

	const handleSearch = (searchQuery?: string) => {
		const effectiveQuery = searchQuery || query;
		if (!effectiveQuery?.trim()) {
			toast({
				title: "Search query required",
				description: "Please enter a product name or keyword to search.",
				variant: "destructive",
			});
			return;
		}

		// Check guest search limit for unauthenticated users - PREVENT SEARCH CALL
		if (!user && !hasGuestSearchesRemaining()) {
			setSearchesExhausted(true);
			setHasSubmitted(true);
			toast({
				title: "Free searches exhausted",
				description: `You've used all ${getGuestFreeSearchCount()} free search${getGuestFreeSearchCount() !== 1 ? 'es' : ''}. Sign in to continue!`,
				variant: "destructive",
				action: (
					<Button
						variant="outline"
						size="sm"
						onClick={() => navigate('/auth')}
					>
						<LogIn className="h-4 w-4 mr-2" />
						Sign In
					</Button>
				),
			});
			return;
		}

		// Reset exhausted state if user has searches
		setSearchesExhausted(false);

		setIsLoading(true);
		window.scrollTo({ top: 0, behavior: "smooth" });
		setHasSubmitted(true);
		setPage(1);
	};

	const handlePageChange = (newPage: number) => {
		if (newPage < 1 || (totalPages && newPage > totalPages)) {
			toast({
				title: "Invalid page",
				description: `Page ${newPage} doesn't exist.`,
				variant: "destructive",
			});
			return;
		}
		setIsLoading(true);
		window.scrollTo({ top: 0, behavior: "smooth" });
		setPage(newPage);
	};

	// Auto-trigger search when URL has query parameter (direct navigation)
	useEffect(() => {
		if (query?.trim() && !hasSubmitted) {
			// Check if guest user has searches remaining
			if (!user && !hasGuestSearchesRemaining()) {
				setSearchesExhausted(true);
				setHasSubmitted(true);
				return;
			}
			
			// Trigger search automatically for direct URL navigation
			setIsLoading(true);
			setHasSubmitted(true);
		}
	}, [query, hasSubmitted, user]);

	// Clear loading and increment guest count when results arrive
	useEffect(() => {
		if (!searchIsLoading && products.length > 0) {
			// Increment guest search count only once per search after successful results
			if (!user && hasSubmitted && !searchCounted) {
				incrementGuestSearchCount();
				setRemainingSearches(getRemainingGuestSearches());
				setSearchCounted(true); // Mark this search as counted
			}
			
			const timer = setTimeout(() => {
				setIsLoading(false);
			}, 300);
			return () => clearTimeout(timer);
		}
	}, [products, searchIsLoading, user, hasSubmitted, searchCounted]);

	// Handle errors separately - SIMPLIFIED
	useEffect(() => {
		if (error) {
			console.log("🚨 Error detected:", error);
			setIsLoading(false);
			
			// Check if it's a daily limit error
			const isLimitError = error.includes("Daily search limit reached") || 
			                    error.includes("limit reached") ||
			                    error.includes("403");
			
			if (isLimitError) {
				console.log("🚫 Daily limit reached - setting exhausted state");
				setSearchesExhausted(true);
				setHasSubmitted(true); // Ensure banner shows
				toast.error("🚫 Daily search limit reached. Sign in for unlimited searches.");
				setDailyLimitReached(true);


			} else {
				console.log("❌ Generic error");
				toast("❌ " + error, {
					duration: 5000,
					position: 'top-center',
					style: {
						background: '#dc2626',
						color: 'white',
						padding: '12px 20px',
					},
				});
			}
		}
	}, [error]); // Only depend on error

	// Load guest search count on mount and set product display limit
	useEffect(() => {
		if (!user) {
			setRemainingSearches(getRemainingGuestSearches());
		}
		setProductDisplayLimit(getProductDisplayLimit(!!user, user?.subscription_tier || 'free'));
	}, [user]);

	return (
		<>
			<MetaTags
				title={query ? `${query} - Product Research | IMO` : "Search Products | IMO"}
				description={`Find the best ${query || 'products'} with AI-powered analysis of thousands of reviews, expert opinions, and video content.`}
				keywords={`${query}, product reviews, best ${query}, ${query} comparison, AI product research`}
				canonicalUrl={`https://informedmarketopinions.com/search${query ? `?q=${encodeURIComponent(query)}` : ''}`}
			/>
			<div className="min-h-screen bg-background">
				<div className="relative overflow-hidden">
					{/* Very subtle animated background */}
					<div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5 opacity-30"></div>

					{/* Subtle floating orbs */}
					<div className="absolute -top-32 -left-32 w-96 h-96 bg-gradient-to-br from-primary to-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-[0.15] dark:opacity-[0.08]"></div>
					<div className="absolute top-1/3 -right-32 w-80 h-80 bg-gradient-to-br from-secondary to-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-[0.15] dark:opacity-[0.08]"></div>
					<div className="absolute bottom-1/4 left-1/3 w-72 h-72 bg-gradient-to-br from-primary to-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-[0.1] dark:opacity-[0.05]"></div>

					<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
						{/* Search form */}
						<div className="mb-12">
							<SearchForm
								query={query || ""}
								loading={isLoading}
								onQueryChange={() => {}}
								onSearch={handleSearch}
							/>
						</div>

						{/* Location Permission Banner */}
						{!dismissLocationBanner && !isDetectingLocation && (
							<div className="max-w-2xl mx-auto mb-6">
								<LocationPermissionBanner
									detectedCountry={country !== 'India' ? country : undefined}
									onDismiss={() => setDismissLocationBanner(true)}
								/>
							</div>
						)}

					{/* Guest Search Banner */}
					{!user && remainingSearches > 0 && showGuestBanner && (
						<div className="mb-6 mx-auto max-w-2xl bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/20 rounded-2xl p-4 flex items-center justify-between gap-4">
							<div className="flex items-center gap-3 flex-1">
								<div className="bg-primary/20 rounded-full px-4 py-1.5 inline-flex items-center justify-center whitespace-nowrap">
									<span className="text-sm font-semibold text-primary">
										{remainingSearches}/{getGuestFreeSearchCount()} free search{getGuestFreeSearchCount() !== 1 ? 'es' : ''}
									</span>
								</div>
								<p className="text-sm text-foreground">
									You have <strong>{remainingSearches}</strong> free search{remainingSearches !== 1 ? 'es' : ''} remaining (limited to {productDisplayLimit} products per search). Sign in for unlimited searches and more results!
								</p>
							</div>
							<div className="flex items-center gap-2 flex-shrink-0">
								<Button
									variant="default"
									size="sm"
									onClick={() => navigate('/auth')}
									className="whitespace-nowrap"
								>
									<LogIn className="h-4 w-4 mr-2" />
									Sign In
								</Button>
								<Button
									variant="ghost"
									size="sm"
									onClick={() => setShowGuestBanner(false)}
									className="h-8 w-8 p-0"
								>
									<X className="h-4 w-4" />
								</Button>
							</div>
						</div>
					)}	
					
					
					{/*Daily Limit Reached Banner */}

					{dailyLimitReached && (
						<div className="mb-6 mx-auto max-w-2xl bg-gradient-to-r from-red-100 to-red-200 border border-red-300 rounded-2xl p-4 flex items-center justify-between gap-4">
							<div className="flex items-center gap-3 flex-1">
								<div className="bg-red-200 rounded-full px-4 py-1.5 inline-flex items-center justify-center whitespace-nowrap">
									<span className="text-sm font-semibold text-red-800">
										Daily Limit Reached
									</span>
								</div>
								<p className="text-sm text-foreground">
									You've reached yoour free daily search limit. Upgrade to premium for unlimited searches and more results per search!
								</p>
							</div>
							<div className="flex items-center gap-2 flex-shrink-0">
								<Button
									variant="default"
									size="sm"
									onClick={() => navigate('/pricing')}
									className="whitespace-nowrap"
								>
									View Pricing
								</Button>

								<Button
									variant="ghost"
									size="sm"
									onClick={() => setDailyLimitReached(false)}
									className="h-8 w-8 p-0"
								>
									<X className="h-4 w-4" />
								</Button>
							</div>
						</div>
					)}
					

					
					
										{/* Searches exhausted message */}
						{searchesExhausted && !user && (
							<div className="mb-12 bg-gradient-to-br from-primary/10 to-secondary/10 border-2 border-primary/30 rounded-2xl p-12 text-center space-y-6">
								<div className="flex justify-center">
									<div className="bg-primary/20 rounded-full p-6">
										<LogIn className="h-12 w-12 text-primary" />
									</div>
								</div>
								<div className="space-y-3">
									<h2 className="text-3xl font-bold tracking-tight">Free Searches Exhausted</h2>
									<p className="text-lg text-muted-foreground max-w-md mx-auto">
										You've used all {getGuestFreeSearchCount()} free search{getGuestFreeSearchCount() !== 1 ? 'es' : ''} (each showing {productDisplayLimit} products). 
										Sign in to continue searching with unlimited access and more results per page!
									</p>
								</div>
								<div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
									<Button
										size="lg"
										onClick={() => navigate('/auth')}
										className="text-lg px-8"
									>
										<LogIn className="h-5 w-5 mr-2" />
										Sign In to Continue
									</Button>
									<Button
										size="lg"
										variant="outline"
										onClick={() => navigate('/pricing')}
										className="text-lg px-8"
									>
										View Pricing
									</Button>
								</div>
							</div>
						)}

						{/* Loading state */}
						<SearchLoading
							isVisible={isLoading}
							isPagination={hasSubmitted && page > 1}
						/>

						{/* Search results */}
						{!searchesExhausted && (
							<div data-search-results>
								<SearchResults
									loading={isLoading}
									products={displayProducts}
									totalCount={totalCount}
									searchPerformed={hasSubmitted}
									searchQuery={query || ""}
									showUpgradeBanner={false}
									currentPage={page}
									totalPages={totalPages}
									hasNextPage={hasNextPage}
									hasPrevPage={hasPrevPage}
									onPageChange={handlePageChange}
									isGuest={!user}
									productDisplayLimit={productDisplayLimit}
								/>
							</div>
						)}
					</div>
				</div>
			</div>
		</>
	);
};

export default Search;
