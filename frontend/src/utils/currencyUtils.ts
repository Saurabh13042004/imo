/**
 * Currency Utilities
 * Maps countries to their currency symbols and codes for proper formatting
 */

export interface CurrencyConfig {
  symbol: string;
  code: string;
  locale: string;
  position: 'prefix' | 'suffix';
}

export const COUNTRY_CURRENCY_MAP: Record<string, CurrencyConfig> = {
  'India': {
    symbol: '₹',
    code: 'INR',
    locale: 'en-IN',
    position: 'prefix'
  },
  'United States': {
    symbol: '$',
    code: 'USD',
    locale: 'en-US',
    position: 'prefix'
  },
  'Canada': {
    symbol: 'C$',
    code: 'CAD',
    locale: 'en-CA',
    position: 'prefix'
  },
  'United Kingdom': {
    symbol: '£',
    code: 'GBP',
    locale: 'en-GB',
    position: 'prefix'
  },
  'Brazil': {
    symbol: 'R$',
    code: 'BRL',
    locale: 'pt-BR',
    position: 'prefix'
  },
  'Germany': {
    symbol: '€',
    code: 'EUR',
    locale: 'de-DE',
    position: 'suffix'
  },
  'France': {
    symbol: '€',
    code: 'EUR',
    locale: 'fr-FR',
    position: 'suffix'
  },
  'Japan': {
    symbol: '¥',
    code: 'JPY',
    locale: 'ja-JP',
    position: 'prefix'
  },
  'Australia': {
    symbol: 'A$',
    code: 'AUD',
    locale: 'en-AU',
    position: 'prefix'
  }
};

/**
 * Get currency configuration for a country
 * Falls back to USD if country not found
 */
export function getCurrencyConfig(country: string = 'United States'): CurrencyConfig {
  return COUNTRY_CURRENCY_MAP[country] || COUNTRY_CURRENCY_MAP['United States'];
}

/**
 * Format price with appropriate currency symbol and locale
 * @param price - The price value
 * @param country - The country name
 * @returns Formatted price string with currency symbol
 */
export function formatPriceWithCurrency(price: number, country: string = 'United States'): string {
  const config = getCurrencyConfig(country);
  const numValue = typeof price === 'string' ? parseFloat(price) : price;
  
  if (isNaN(numValue)) {
    return `${config.symbol}0.00`;
  }

  // Determine decimal places (JPY doesn't use decimals)
  const decimals = config.code === 'JPY' ? 0 : 2;
  const formatted = numValue.toFixed(decimals);

  if (config.position === 'prefix') {
    return `${config.symbol}${formatted}`;
  } else {
    return `${formatted} ${config.symbol}`;
  }
}

/**
 * Format price using Intl API with proper locale
 * More comprehensive formatting with thousands separators
 */
export function formatPriceIntl(price: number, country: string = 'United States'): string {
  const config = getCurrencyConfig(country);
  const numValue = typeof price === 'string' ? parseFloat(price) : price;

  if (isNaN(numValue)) {
    return new Intl.NumberFormat(config.locale, {
      style: 'currency',
      currency: config.code
    }).format(0);
  }

  return new Intl.NumberFormat(config.locale, {
    style: 'currency',
    currency: config.code
  }).format(numValue);
}

/**
 * Get currency symbol for a country
 */
export function getCurrencySymbol(country: string = 'United States'): string {
  return getCurrencyConfig(country).symbol;
}

/**
 * Get currency code for a country (ISO 4217)
 */
export function getCurrencyCode(country: string = 'United States'): string {
  return getCurrencyConfig(country).code;
}

/**
 * Check if currency symbol should be displayed before or after amount
 */
export function getCurrencyPosition(country: string = 'United States'): 'prefix' | 'suffix' {
  return getCurrencyConfig(country).position;
}
