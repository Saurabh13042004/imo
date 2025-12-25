import { useState, useEffect, useRef } from "react";
import { API_BASE_URL } from "@/config/api";
import toast from "react-hot-toast";

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
  taskId?: string;
}

/**
 * Hook to fetch and manage AI verdict for a product.
 * 
 * CRITICAL: Passes FULL enriched_data from /product/enriched endpoint to backend.
 * Backend uses ONLY this data - no refetching.
 * 
 * Uses Celery async tasks with polling (same pattern as Google reviews).
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
  const [taskId, setTaskId] = useState<string>();

  // Track if we've already initiated verdict generation
  const hasInitiated = useRef(false);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pollCountRef = useRef(0);

  // Poll for task status
  const pollTaskStatus = async (currentTaskId: string) => {
    if (!currentTaskId) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/reviews/status/${currentTaskId}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Status check failed: ${response.status}`);
      }

      const data = await response.json();
      console.log("[useAIVerdict] Task status:", data.status, data.state_meta?.status);

      // Handle PROGRESS state - show progress updates
      if (data.status === "PROGRESS" && data.state_meta) {
        console.log("[useAIVerdict] PROGRESS:", data.state_meta.status);
        setStatus("processing");
        // Could show progress toast here if desired
      } else if (data.status === "SUCCESS" && data.result) {
        console.log("[useAIVerdict] Task completed! Verdict:", data.result.verdict);

        setVerdict(data.result.verdict || null);
        setStatus("ready");
        setIsLoading(false);

        // Stop polling
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }

        // Dismiss loading toast and show success toast
        toast.dismiss("verdict-toast");
        toast.success("✨ IMO AI verdict is ready", {
          position: "bottom-left",
          duration: 3000,
        });
      } else if (data.status === "FAILURE") {
        throw new Error(data.error || "Task failed");
      } else {
        // Task still processing
        pollCountRef.current++;
        if (pollCountRef.current % 5 === 0) {
          console.log(`[useAIVerdict] Still polling... (${pollCountRef.current})`);
        }
      }
    } catch (err) {
      console.error("[useAIVerdict] Error polling status:", err);
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      setStatus("error");
      setIsLoading(false);

      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }

      toast.error(`Could not generate AI verdict: ${errorMessage}`, {
        position: "bottom-left",
        duration: 3000,
      });
    }
  };

  useEffect(() => {
    // Only trigger if we have both productId and enriched data
    if (!productId || !enrichedData) {
      return;
    }

    // Prevent duplicate initiations
    if (hasInitiated.current) {
      return;
    }

    const generateVerdict = async () => {
      try {
        hasInitiated.current = true;
        setStatus("processing");
        setIsLoading(true);
        setError(null);

        // Show toast when processing starts
        toast.loading("🤖 IMO AI is analyzing this product…", {
          position: "bottom-left",
          id: "verdict-toast",
        });

        console.log(`[useAIVerdict] Requesting verdict for product: ${productId}`);
        console.log(`[useAIVerdict] Enriched data keys:`, Object.keys(enrichedData));

        // CRITICAL: Pass FULL enriched_data and scrape_stores flag
        const response = await fetch(
          `${API_BASE_URL}/api/v1/product/${productId}/ai-verdict`,
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
        console.log(`[useAIVerdict] Response:`, result);

        if (result.task_id) {
          // Task queued successfully - now poll for result
          setTaskId(result.task_id);
          console.log(`[useAIVerdict] Task queued: ${result.task_id}. Starting polling...`);
          
          // Start polling immediately
          pollTaskStatus(result.task_id);
          
          // Set up polling interval (every 2 seconds like Google reviews)
          pollIntervalRef.current = setInterval(() => {
            pollTaskStatus(result.task_id);
          }, 2000);
        } else {
          throw new Error("No task_id in response");
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Unknown error";
        console.error("[useAIVerdict] Error:", errorMessage);
        setError(errorMessage);
        setStatus("error");
        setIsLoading(false);

        toast.dismiss("verdict-toast");
        toast.error(`Could not generate AI verdict: ${errorMessage}`, {
          position: "bottom-left",
          duration: 3000,
        });
      }
    };

    // Debounce to avoid multiple calls if enrichedData changes frequently
    const timeoutId = setTimeout(generateVerdict, 500);

    return () => {
      clearTimeout(timeoutId);
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [productId, enrichedData]);

  return {
    verdict,
    status,
    error,
    isLoading,
    taskId,
  };
};
