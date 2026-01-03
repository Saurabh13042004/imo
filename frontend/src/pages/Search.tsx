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
import { getProductDisplayLimit } from "@/utils/accessControl";
import { Button } from "@/components/ui/button";
import X from 'lucide-react/dist/esm/icons/x';
import LogIn from 'lucide-react/dist/esm/icons/log-in';
import { useNavigate } from "react-router-dom";
import { MetaTags } from "@/components/seo";

const Search = () => {
	useParallax();
	const { query, zipcode, country, city, language, isDetectingLocation } = useSearchUrl();
	const { user } = useAuth();
	const navigate = useNavigate();
	
	const [hasSubmitted, setHasSubmitted] = useState(false);
	const [page, setPage] = useState(1);
	const [isLoading, setIsLoading] = useState(false);
	const [productDisplayLimit, setProductDisplayLimit] = useState(5);
	const [clearedProducts, setClearedProducts] = useState<any[]>([]);
	const [lastQuery, setLastQuery] = useState<string>("");
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
		enabled: hasSubmitted && !!query?.trim(),
		page: page,
		isDetectingLocation: isDetectingLocation,
	});

	// Clear products when query changes (new search)
	useEffect(() => {
		if (query && query !== lastQuery) {
			setClearedProducts([]);
			setLastQuery(query);
			setPage(1);
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
			toast.error("Please enter a product name or keyword to search.");
			return;
		}

		setIsLoading(true);
		window.scrollTo({ top: 0, behavior: "smooth" });
		setHasSubmitted(true);
		setPage(1);
	};

	const handlePageChange = (newPage: number) => {
		if (newPage < 1 || (totalPages && newPage > totalPages)) {
			toast.error(`Page ${newPage} doesn't exist.`);
			return;
		}
		setIsLoading(true);
		window.scrollTo({ top: 0, behavior: "smooth" });
		setPage(newPage);
	};

	// Auto-trigger search when URL has query parameter (direct navigation)
	useEffect(() => {
		if (query?.trim() && !hasSubmitted) {
			// Trigger search automatically for direct URL navigation
			setIsLoading(true);
			setHasSubmitted(true);
		}
	}, [query, hasSubmitted]);

	// Clear loading when results arrive
	useEffect(() => {
		if (!searchIsLoading && products.length > 0) {
			const timer = setTimeout(() => {
				setIsLoading(false);
			}, 300);
			return () => clearTimeout(timer);
		}
	}, [products, searchIsLoading]);

	// Handle errors
	useEffect(() => {
		if (error) {
			console.log("🚨 Error detected:", error);
			setIsLoading(false);
			toast.error("❌ " + error);
		}
	}, [error]);

	// Set product display limit based on user tier
	useEffect(() => {
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

						{/* Loading state */}
						<SearchLoading
							isVisible={isLoading}
							isPagination={hasSubmitted && page > 1}
						/>

						{/* Search results */}
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
					</div>
				</div>
			</div>
		</>
	);
};

export default Search;
