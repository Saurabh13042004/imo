import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";

interface AIVerdict {
  imo_score: number;
  summary: string;
  pros: string[];
  cons: string[];
  who_should_buy?: string;
  who_should_avoid?: string;
  price_fairness?: string;
  deal_breakers?: string[];
}

interface UseAIVerdictReturn {
  verdict: AIVerdict | null;
  status: "idle" | "processing" | "ready" | "error";
  error: string | null;
  isLoading: boolean;
}

/**
 * Hook to fetch and manage AI verdict for a product.
 * 
 * CRITICAL: Passes FULL enriched_data from /product/enriched endpoint to backend.
 * Backend uses ONLY this data - no refetching.
 * 
 * Non-blocking: page renders immediately while verdict processes in background.
 */
export const useAIVerdict = (
  productId: string | undefined,
  enrichedData: any
): UseAIVerdictReturn => {
  const [verdict, setVerdict] = useState<AIVerdict | null>(null);
  const [status, setStatus] = useState<"idle" | "processing" | "ready" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    // Only trigger if we have both productId and enriched data
    if (!productId || !enrichedData) {
      return;
    }

    const generateVerdict = async () => {
      try {
        setStatus("processing");
        setIsLoading(true);
        setError(null);

        // Show toast when processing starts
        toast({
          title: "🤖 IMO AI is crafting the best verdict for you…",
          duration: 2000,
        });

        console.log(`[useAIVerdict] Requesting verdict for product: ${productId}`);
        console.log(`[useAIVerdict] Enriched data keys:`, Object.keys(enrichedData));

        // CRITICAL: Pass FULL enriched_data and scrape_stores flag
        const response = await fetch(
          `/api/v1/product/${productId}/ai-verdict`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              enriched_data: enrichedData,  // Full response from /product/enriched
              scrape_stores: true,          // Enable store scraping for better insights
            }),
          }
        );

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }

        const result = await response.json();
        console.log(`[useAIVerdict] Response status: ${result.status}`, result);

        if (result.status === "ready" && result.verdict) {
          // Verdict ready
          setVerdict(result.verdict);
          setStatus("ready");
          setIsLoading(false);

          // Show success toast
          toast({
            title: "✨ IMO AI verdict is ready",
            duration: 2000,
          });
        } else if (result.status === "processing") {
          // Verdict is being generated
          setStatus("processing");
          setIsLoading(false);
          console.log("[useAIVerdict] Verdict generation started in background");
        } else if (result.status === "error") {
          throw new Error(result.message || "Failed to generate verdict");
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Unknown error";
        console.error("[useAIVerdict] Error:", errorMessage);
        setError(errorMessage);
        setStatus("error");
        setIsLoading(false);

        toast({
          title: "Could not generate AI verdict",
          description: errorMessage,
          variant: "destructive",
          duration: 3000,
        });
      }
    };

    // Debounce to avoid multiple calls if enrichedData changes frequently
    const timeoutId = setTimeout(generateVerdict, 500);

    return () => clearTimeout(timeoutId);
  }, [productId, enrichedData, toast]);

  return {
    verdict,
    status,
    error,
    isLoading,
  };
};
