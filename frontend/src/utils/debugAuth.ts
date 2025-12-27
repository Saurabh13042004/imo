/**
 * Debug utility to check auth token and localStorage state
 */

export const debugAuthState = () => {
  console.log("=== AUTH STATE DEBUG ===");
  
  // Check localStorage
  const auth = localStorage.getItem("auth");
  console.log("localStorage.auth exists:", !!auth);
  
  if (auth) {
    try {
      const parsed = JSON.parse(auth);
      console.log("Parsed auth object:", {
        hasAccessToken: !!parsed.accessToken,
        accessTokenLength: parsed.accessToken?.length || 0,
        accessTokenPreview: parsed.accessToken?.substring(0, 50) + "...",
        hasRefreshToken: !!parsed.refreshToken,
        keys: Object.keys(parsed),
      });
      
      // Check if token is valid JWT
      if (parsed.accessToken) {
        const parts = parsed.accessToken.split(".");
        console.log("Token parts:", parts.length, "(should be 3 for JWT)");
        
        if (parts.length === 3) {
          try {
            const payload = JSON.parse(atob(parts[1]));
            console.log("Token payload:", {
              sub: payload.sub,
              user_id: payload.user_id,
              type: payload.type,
              exp: payload.exp,
              iat: payload.iat,
            });
            
            // Check if expired
            const now = Math.floor(Date.now() / 1000);
            console.log("Token expired:", payload.exp < now);
          } catch (e) {
            console.log("Could not decode token payload:", e);
          }
        }
      }
    } catch (e) {
      console.log("Could not parse auth JSON:", e);
    }
  } else {
    console.log("⚠️  No auth token in localStorage!");
  }
  
  console.log("=========================");
};

/**
 * Test auth header on API request
 */
export const testAuthHeader = async () => {
  console.log("=== TESTING AUTH HEADER ===");
  
  const auth = localStorage.getItem("auth");
  if (!auth) {
    console.log("❌ No auth token found");
    return;
  }
  
  try {
    const parsed = JSON.parse(auth);
    const token = parsed.accessToken;
    
    if (!token) {
      console.log("❌ No accessToken in auth object");
      return;
    }
    
    // Make a test request to a protected endpoint
    const response = await fetch("/api/v1/auth/me", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    
    console.log("GET /api/v1/auth/me status:", response.status);
    const data = await response.json();
    console.log("Response:", data);
    
  } catch (e) {
    console.log("Error testing auth:", e);
  }
  
  console.log("===========================");
};
