/**
 * Frontend Changes Guide - SerpAPI Geo-Targeting
 * 
 * This document outlines the changes needed in the React frontend to support
 * geo-targeted product searches with SerpAPI.
 */

// =============================================================================
// 1. Update SearchForm Component
// =============================================================================
// File: src/components/search/SharedSearchInput.tsx

import React, { useState } from 'react';

interface SearchFormProps {
  onSearch: (query: string, country: string, city: string, language: string) => void;
}

export function SharedSearchInput({ onSearch }: SearchFormProps) {
  const [query, setQuery] = useState('');
  const [country, setCountry] = useState('United States');
  const [city, setCity] = useState('');
  const [language, setLanguage] = useState('en');

  const countries = [
    { value: 'India', label: 'India' },
    { value: 'United States', label: 'United States' },
    { value: 'Canada', label: 'Canada' },
    { value: 'United Kingdom', label: 'United Kingdom' },
    { value: 'Brazil', label: 'Brazil' },
    { value: 'Germany', label: 'Germany' },
    { value: 'France', label: 'France' },
    { value: 'Japan', label: 'Japan' },
    { value: 'Australia', label: 'Australia' },
  ];

  const languages = [
    { value: 'en', label: 'English' },
    { value: 'hi', label: 'Hindi' },
    { value: 'es', label: 'Spanish' },
    { value: 'fr', label: 'French' },
    { value: 'de', label: 'German' },
    { value: 'pt', label: 'Portuguese' },
    { value: 'ja', label: 'Japanese' },
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, country, city, language);
    }
  };

  return (
    <form onSubmit={handleSearch} className="search-form">
      <div className="search-grid">
        {/* Search Query */}
        <input
          type="text"
          placeholder="Search products..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="search-input"
        />

        {/* Country Selector */}
        <select
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          className="select-input"
        >
          {countries.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* City Input (Optional) */}
        <input
          type="text"
          placeholder="City (optional)"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          className="search-input"
        />

        {/* Language Selector */}
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="select-input"
        >
          {languages.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <button type="submit" className="search-button">
        Search
      </button>
    </form>
  );
}

// =============================================================================
// 2. Update useProductSearch Hook
// =============================================================================
// File: src/hooks/useProductSearch.tsx

import { useState, useCallback } from 'react';
import type { Product, SearchResponse } from '@/types';

interface SearchParams {
  query: string;
  country?: string;
  city?: string;
  language?: string;
  zipcode?: string;
}

export function useProductSearch() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useState<SearchParams | null>(null);

  const search = useCallback(async (params: SearchParams) => {
    setLoading(true);
    setError(null);

    try {
      const payload = {
        keyword: params.query,
        country: params.country || 'United States',
        city: params.city || undefined,
        language: params.language || 'en',
        zipcode: params.zipcode || undefined,
      };

      console.log('[Search] Payload:', payload);

      const response = await fetch('/api/v1/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data: SearchResponse = await response.json();

      console.log('[Search] Response:', data);

      setProducts(data.results || []);
      setSearchParams(params);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, []);

  return { products, loading, error, search, searchParams };
}

// =============================================================================
// 3. Update useSearchUrl Hook
// =============================================================================
// File: src/hooks/useSearchUrl.tsx

import { useSearchParams, useNavigate } from 'react-router-dom';
import { useCallback, useEffect, useState } from 'react';

interface SearchUrlParams {
  query: string;
  country: string;
  city: string;
  language: string;
  zipcode?: string;
}

export function useSearchUrl(): SearchUrlParams & { updateUrl: (params: SearchUrlParams) => void } {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [params, setParams] = useState<SearchUrlParams>({
    query: searchParams.get('q') || '',
    country: searchParams.get('country') || 'United States',
    city: searchParams.get('city') || '',
    language: searchParams.get('language') || 'en',
    zipcode: searchParams.get('zipcode') || undefined,
  });

  const updateUrl = useCallback(
    (newParams: SearchUrlParams) => {
      const queryParams = new URLSearchParams();
      queryParams.set('q', newParams.query);
      queryParams.set('country', newParams.country);
      if (newParams.city) queryParams.set('city', newParams.city);
      queryParams.set('language', newParams.language);
      if (newParams.zipcode) queryParams.set('zipcode', newParams.zipcode);

      navigate(`/search?${queryParams.toString()}`);
      setParams(newParams);
    },
    [navigate]
  );

  return { ...params, updateUrl };
}

// =============================================================================
// 4. Update Search Page Component
// =============================================================================
// File: src/pages/Search.tsx

import { useSearchUrl } from '@/hooks/useSearchUrl';
import { useProductSearch } from '@/hooks/useProductSearch';
import { SharedSearchInput } from '@/components/search/SharedSearchInput';
import ProductGrid from '@/components/product/ProductGrid';

export default function SearchPage() {
  const searchUrl = useSearchUrl();
  const { products, loading, error, search } = useProductSearch();

  const handleSearch = (query: string, country: string, city: string, language: string) => {
    searchUrl.updateUrl({ query, country, city, language, zipcode: searchUrl.zipcode });
    search({ query, country, city, language });
  };

  return (
    <div className="search-page">
      <SharedSearchInput onSearch={handleSearch} />

      {error && <div className="error-message">{error}</div>}

      {loading && <div className="loading">Searching...</div>}

      {products.length > 0 && (
        <div className="search-results">
          <p className="results-count">
            Found {products.length} products in {searchUrl.country}
            {searchUrl.city && ` - ${searchUrl.city}`}
          </p>
          <ProductGrid products={products} />
        </div>
      )}

      {!loading && products.length === 0 && !error && (
        <div className="no-results">No products found</div>
      )}
    </div>
  );
}

// =============================================================================
// 5. Update Type Definitions (if needed)
// =============================================================================
// File: src/types/index.ts

export interface SearchResponse {
  success: boolean;
  keyword: string;
  country?: string;
  city?: string;
  language?: string;
  zipcode?: string;
  total_results: number;
  results: Product[];
}

export interface Product {
  id: string;
  title: string;
  source: string;
  price: number;
  currency: string;
  image_url: string;
  rating?: number;
  review_count?: number;
  url: string;
  availability: string;
  [key: string]: any;
}

// =============================================================================
// CSS Example
// =============================================================================
/* src/styles/search.css */

.search-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.search-input,
.select-input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.search-input:focus,
.select-input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.search-button {
  padding: 0.75rem 1.5rem;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.search-button:hover {
  background: #4338ca;
}

.results-count {
  text-align: center;
  color: #666;
  margin: 1rem 0;
}

// =============================================================================
// Testing Example
// =============================================================================

/**
 * Test Cases:
 * 
 * 1. Search from India
 *    - Query: "samsung tv"
 *    - Country: "India"
 *    - City: "Bengaluru"
 *    - Language: "hi"
 *    - Expected: Indian retailers (Flipkart, Amazon.in, etc.)
 * 
 * 2. Search from United States
 *    - Query: "iphone 15"
 *    - Country: "United States"
 *    - City: "Austin"
 *    - Language: "en"
 *    - Expected: US retailers (Best Buy, Amazon.com, Walmart, etc.)
 * 
 * 3. Verify URL parameters preserved
 *    - Perform search
 *    - Check URL contains: ?q=samsung+tv&country=India&city=Bengaluru&language=hi
 * 
 * 4. Test language variations
 *    - Same product, different languages
 *    - Verify interface text changes
 */
