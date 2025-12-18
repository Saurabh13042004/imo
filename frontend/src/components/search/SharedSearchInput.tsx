import { useState, useEffect, useRef } from "react";
import { Search as SearchIcon, Loader2, ArrowRight, MapPin, Globe } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useSearchUrl } from "@/hooks/useSearchUrl";
import { validateSearchQuery, normalizeSearchQuery, getSearchPlaceholder } from "@/utils/searchUtils";
import { SearchAutosuggest } from "./SearchAutosuggest";

interface SharedSearchInputProps {
  variant?: 'default' | 'compact' | 'hero';
  loading?: boolean;
  onSearch?: (query: string, zipcode?: string, country?: string, city?: string, language?: string) => void;
  className?: string;
  showButton?: boolean;
  autoFocus?: boolean;
  showZipcode?: boolean;
}

const COUNTRIES = [
  { value: 'India', label: '🇮🇳 India' },
  { value: 'United States', label: '🇺🇸 United States' },
  { value: 'Canada', label: '🇨🇦 Canada' },
  { value: 'United Kingdom', label: '🇬🇧 United Kingdom' },
  { value: 'Brazil', label: '🇧🇷 Brazil' },
  { value: 'Germany', label: '🇩🇪 Germany' },
  { value: 'France', label: '🇫🇷 France' },
  { value: 'Japan', label: '🇯🇵 Japan' },
  { value: 'Australia', label: '🇦🇺 Australia' },
];

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'hi', label: 'हिन्दी (Hindi)' },
  { value: 'es', label: 'Español' },
  { value: 'fr', label: 'Français' },
  { value: 'de', label: 'Deutsch' },
  { value: 'pt', label: 'Português' },
  { value: 'ja', label: '日本語' },
];

export const SharedSearchInput = ({ 
  variant = 'default', 
  loading = false, 
  onSearch,
  className = "",
  showButton = true,
  autoFocus = false,
  showZipcode = true
}: SharedSearchInputProps) => {
  const { query, zipcode: urlZipcode, country: urlCountry, city: urlCity, language: urlLanguage, updateSearchUrl } = useSearchUrl();
  const [localQuery, setLocalQuery] = useState(query || '');
  const [localZipcode, setLocalZipcode] = useState(urlZipcode || '60607');
  const [localCountry, setLocalCountry] = useState(urlCountry || 'India');  // DEFAULT: India
  const [localCity, setLocalCity] = useState(urlCity || '');
  const [localLanguage, setLocalLanguage] = useState(urlLanguage || 'en');
  const [isAutosuggestOpen, setIsAutosuggestOpen] = useState(false);
  const [showLocationPanel, setShowLocationPanel] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync with URL query and geo params
  useEffect(() => {
    setLocalQuery(query || '');
  }, [query]);

  useEffect(() => {
    setLocalZipcode(urlZipcode || '60607');
    setLocalCountry(urlCountry || 'India');
    setLocalCity(urlCity || '');
    setLocalLanguage(urlLanguage || 'en');
  }, [urlZipcode, urlCountry, urlCity, urlLanguage]);

  // Handle auto focus
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [autoFocus]);

  const handleSearch = () => {
    const normalizedQuery = normalizeSearchQuery(localQuery);
    if (validateSearchQuery(normalizedQuery)) {
      updateSearchUrl(normalizedQuery, localZipcode, localCountry, localCity, localLanguage);
      onSearch?.(normalizedQuery, localZipcode, localCountry, localCity, localLanguage);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleContainerClick = () => {
    inputRef.current?.focus();
  };

  const handleSelectSuggestion = (suggestion: string) => {
    setLocalQuery(suggestion);
    updateSearchUrl(suggestion, localZipcode, localCountry, localCity, localLanguage);
    onSearch?.(suggestion, localZipcode, localCountry, localCity, localLanguage);
    setIsAutosuggestOpen(false);
  };

  const handleInputFocus = () => {
    setIsAutosuggestOpen(true);
  };

  const handleInputBlur = () => {
    // Don't close on blur - let user interact freely
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setLocalQuery(value);
    setIsAutosuggestOpen(true);
  };

  const handleCountryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setLocalCountry(e.target.value);
  };

  const handleCityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalCity(e.target.value);
  };

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setLocalLanguage(e.target.value);
  };

  return (
    <div className={`flex flex-col gap-3 ${className}`}>
      {/* Main search row */}
      <div className={`flex gap-3`}>
        <SearchAutosuggest
          searchQuery={localQuery}
          isOpen={isAutosuggestOpen}
          onOpenChange={setIsAutosuggestOpen}
          onSelectSuggestion={handleSelectSuggestion}
          variant={variant}
          loading={loading}
        >
          <div className="relative flex-1 h-full cursor-text" onClick={handleContainerClick}>
            <SearchIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground pointer-events-none" />
            <Input
              ref={inputRef}
              placeholder={getSearchPlaceholder()}
              value={localQuery}
              onChange={handleInputChange}
              onKeyDown={handleKeyPress}
              onFocus={handleInputFocus}
              onBlur={handleInputBlur}
              className={`h-12 pl-11 ${className.includes('border-0') ? 'border-0 focus:ring-0 shadow-none' : ''}`}
              disabled={loading}
            />
          </div>
        </SearchAutosuggest>

        {/* Location Panel Toggle Button */}
        <Button
          variant="outline"
          onClick={() => setShowLocationPanel(!showLocationPanel)}
          className={`h-12 px-4 rounded-lg border-border/60 hover:bg-secondary ${
            showLocationPanel ? 'bg-secondary' : ''
          }`}
          title="Toggle location settings"
        >
          <Globe className="h-5 w-5" />
        </Button>

        {showButton && (
          <Button
            onClick={handleSearch}
            disabled={loading || !validateSearchQuery(localQuery)}
            className="h-12 px-6"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                {variant === 'compact' ? '...' : 'Searching...'}
              </>
            ) : (
              <>
                {variant === 'compact' ? <SearchIcon className="h-4 w-4" /> : 'Search'}
                {variant !== 'compact' && <ArrowRight className="h-5 w-5 ml-2" />}
              </>
            )}
          </Button>
        )}
      </div>

      {/* Location Settings Panel */}
      {showLocationPanel && (
        <div className="bg-secondary/50 p-4 rounded-lg space-y-3 border border-border/50">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Country Selector */}
            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground/70">Country</label>
              <select
                value={localCountry}
                onChange={handleCountryChange}
                className="w-full px-3 py-2 rounded-md border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {COUNTRIES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* City Input */}
            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground/70">City (Optional)</label>
              <Input
                placeholder="e.g., Bengaluru"
                value={localCity}
                onChange={handleCityChange}
                className="h-10 px-3 text-sm"
              />
            </div>

            {/* Language Selector */}
            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground/70">Language</label>
              <select
                value={localLanguage}
                onChange={handleLanguageChange}
                className="w-full px-3 py-2 rounded-md border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {LANGUAGES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Summary */}
          <div className="text-xs text-foreground/60 pt-2">
            Searching in <span className="font-semibold text-foreground">{localCountry}</span>
            {localCity && <span> • <span className="font-semibold">{localCity}</span></span>}
            {localLanguage !== 'en' && <span> • <span className="font-semibold">{LANGUAGES.find(l => l.value === localLanguage)?.label}</span></span>}
          </div>
        </div>
      )}
    </div>
  );
};