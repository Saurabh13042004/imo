import { useState, useEffect } from "react";
import { searchProducts } from "@/integrations/fastapi";
import type { Product } from "@/types/search";

interface SearchProductsParams {
	query: string;
	enabled?: boolean;
	page?: number;
	pageSize?: number;
	sortBy?: "price_low" | "price_high" | "imo_score" | "rating" | "newest" | "most_reviewed";
	priceRange?: [number, number];
	minImoScore?: number;
	minRating?: number;
	zipcode?: string;
	country?: string;
	city?: string;
	language?: string;
}

interface SearchResponse {
	products: Product[];
	isFromCache: boolean;
	isStaleData?: boolean;
	message: string;
	totalCount: number;
	count: number;
	currentPage: number;
	totalPages: number;
	hasNextPage: boolean;
	hasPrevPage: boolean;
}

export function useProductSearch({
	query,
	enabled = true,
	page = 1,
	pageSize = 12,
	sortBy = "newest",
	priceRange,
	minImoScore,
	minRating,
	zipcode = "60607",
	country = "United States",
	city = "",
	language = "en",
}: SearchProductsParams) {
	const [products, setProducts] = useState<Product[]>([]);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [totalCount, setTotalCount] = useState(0);
	const [totalPages, setTotalPages] = useState(0);
	const [lastQuery, setLastQuery] = useState<string>("");

	useEffect(() => {
		if (!enabled || !query?.trim()) {
			setProducts([]);
			setTotalCount(0);
			setTotalPages(0);
			return;
		}

		// Clear products when query changes (new search)
		if (query !== lastQuery && page === 1) {
			setProducts([]);
		}

		setLastQuery(query);

		const fetchProducts = async () => {
			setIsLoading(true);
			setError(null);

			try {
				const data = await searchProducts({
					keyword: query.trim(),
					zipcode: zipcode,
					country: country,
					city: city,
					language: language,
				});

				if (!data.success || !data.results) {
					throw new Error("Invalid API response");
				}

				// Transform API results to Product type
				const transformedProducts: Product[] = data.results.map((item: any) => ({
					// Core fields
					id: item.id || item.source_id,
					title: item.title,
					description: item.description || item.title,
					price: parseFloat(item.price as any) || 0,
					image_url: item.image_url || "https://via.placeholder.com/300",
					product_url: item.url || "#",
					source: item.source || "amazon",
					source_id: item.source_id,
					
					// Metadata
					imo_score: item.imo_score || 0,
					pros: item.pros || [],
					cons: item.cons || [],
					brand: item.brand || "",
					category: item.category || "",
					availability: item.availability || "In Stock",
					asin: item.asin || "",
					
					// Ratings
					site_rating: parseFloat(item.rating) || 0,
					reviews_count: parseInt(item.review_count) || 0,
					review_count: parseInt(item.review_count) || 0,
					rating: parseFloat(item.rating) || 0,
					
					// URLs
					url: item.url || "#",
					
					// Timestamps
					created_at: item.created_at || new Date().toISOString(),
					updated_at: item.updated_at,
					
					// IMPORTANT: Immersive product fields from API
					immersive_product_api_link: item.immersive_product_api_link || "",
					immersive_product_page_token: item.immersive_product_page_token || "",
					
					// Additional fields
					is_detailed_fetched: item.is_detailed_fetched || false,
					reviews_summary: item.reviews_summary,
					
					// Preserve any other fields from the API response
					...item
				}));

				// Apply client-side filters if needed
				let filteredProducts = transformedProducts;

				if (priceRange) {
					filteredProducts = filteredProducts.filter(
						(p) => p.price >= priceRange[0] && p.price <= priceRange[1]
					);
				}

				if (minRating) {
					filteredProducts = filteredProducts.filter((p) => (p.site_rating || 0) >= minRating);
				}

				// Apply sorting
				if (sortBy === "price_low") {
					filteredProducts.sort((a, b) => a.price - b.price);
				} else if (sortBy === "price_high") {
					filteredProducts.sort((a, b) => b.price - a.price);
				} else if (sortBy === "rating") {
					filteredProducts.sort((a, b) => (b.site_rating || 0) - (a.site_rating || 0));
				}

				// Paginate
				const calculatedTotalPages = Math.ceil(filteredProducts.length / pageSize);
				const startIndex = (page - 1) * pageSize;
				const paginatedProducts = filteredProducts.slice(startIndex, startIndex + pageSize);

				setProducts(paginatedProducts);
				setTotalCount(filteredProducts.length);
				setTotalPages(calculatedTotalPages);
			} catch (err) {
				console.error("Search error:", err);
				const errorMessage = err instanceof Error ? err.message : "Failed to fetch products";
				console.log("Setting error state to:", errorMessage);
				setError(errorMessage);
				setProducts([]);
				setTotalCount(0);
				setTotalPages(0);
			} finally {
				console.log("Setting isLoading to false");
				setIsLoading(false);
			}
		};

		fetchProducts();
	}, [query, enabled, page, pageSize, sortBy, priceRange, minRating, zipcode, country, city, language]);

	return {
		products,
		totalCount,
		count: products.length,
		isFromCache: false,
		isStaleData: false,
		message: totalCount > 0 ? `Found ${totalCount} products` : "No products found",
		currentPage: page,
		totalPages,
		hasNextPage: page < totalPages,
		hasPrevPage: page > 1,
		isPending: isLoading,
		isAnalyzing: false,
		isLoading,
		isFetching: isLoading,
		isError: !!error,
		error,
		fetchFresh: () => {},
		isFetchingFresh: false,
		refetch: () => {},
		showUpgradeBanner: false,
	};
}

export function useProductDetails(productId?: string) {
	return {
		data: null,
		isLoading: false,
		isError: false,
		error: null,
	};
}
