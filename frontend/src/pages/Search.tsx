import { useCallback, useEffect, useState } from "react";
import { SearchForm } from "@/components/search/SearchForm";
import { SearchResults } from "@/components/search/SearchResults";
import { SearchLoading } from "@/components/search/SearchLoading";
import { Navbar } from "@/components/layout/Navbar";
import { useToast } from "@/hooks/use-toast";
import { useParallax } from "@/hooks/useParallax";
import { useProductSearch } from "@/hooks/useProductSearch";
import { useSearchUrl } from "@/hooks/useSearchUrl";

const Search = () => {
	useParallax();
	const { query, zipcode, country, city, language } = useSearchUrl();
	const [hasSubmitted, setHasSubmitted] = useState(false);
	const [page, setPage] = useState(1);
	const [isLoading, setIsLoading] = useState(false);
	const { toast } = useToast();

	const {
		products,
		totalCount,
		totalPages,
		hasNextPage,
		hasPrevPage,
	} = useProductSearch({
		query: query,
		zipcode: zipcode,
		country: country,
		city: city,
		language: language,
		enabled: hasSubmitted && !!query?.trim(),
		page: page,
	});

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

		setIsLoading(true);
		window.scrollTo({ top: 0, behavior: "smooth" });
		setHasSubmitted(true);
		setPage(1);
		// Loading state will continue until results arrive via useProductSearch
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
		// Loading state will continue until results arrive via useProductSearch
	};

	useEffect(() => {
		if (query?.trim()) {
			setHasSubmitted(true);
		} else {
			setHasSubmitted(false);
		}
	}, [query]);

	// Clear loading when results arrive
	useEffect(() => {
		if (isLoading && (products.length > 0 || (!isLoading && hasSubmitted))) {
			// Give a small delay to show results smoothly
			const timer = setTimeout(() => {
				setIsLoading(false);
			}, 300);
			return () => clearTimeout(timer);
		}
	}, [products, isLoading, hasSubmitted]);

	return (
		<>
			{/* <Navbar /> */}
			<div className="min-h-screen bg-background">
				<div className="relative">
					<div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
						{/* Search form */}
						<div className="mb-12">
							<SearchForm
								query={query || ""}
								loading={isLoading}
								onQueryChange={() => {}}
								onSearch={handleSearch}
							/>
						</div>

						{/* Loading state */}
						<SearchLoading
							isVisible={isLoading}
							isPagination={hasSubmitted && page > 1}
						/>

						{/* Search results */}
						<div data-search-results>
							<SearchResults
								loading={isLoading}
								products={products}
								totalCount={totalCount}
								searchPerformed={hasSubmitted}
								searchQuery={query || ""}
								showUpgradeBanner={false}
								currentPage={page}
								totalPages={totalPages}
								hasNextPage={hasNextPage}
								hasPrevPage={hasPrevPage}
								onPageChange={handlePageChange}
							/>
						</div>
					</div>
				</div>
			</div>
		</>
	);
};

export default Search;
