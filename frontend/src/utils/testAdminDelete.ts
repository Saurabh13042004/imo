/**
 * Quick test script to verify auth token and test DELETE request
 * Paste this directly into browser console when on the admin page
 */

async function testAdminDelete() {
  console.log("=== ADMIN DELETE TEST ===");
  
  // 1. Check token in localStorage
  const auth = localStorage.getItem("auth");
  if (!auth) {
    console.error("❌ No auth in localStorage");
    return;
  }
  
  const parsed = JSON.parse(auth);
  const token = parsed.accessToken;
  if (!token) {
    console.error("❌ No accessToken in auth object");
    return;
  }
  
  console.log("✅ Token found, length:", token.length);
  
  // 2. Verify token format (JWT should have 3 parts)
  const parts = token.split(".");
  console.log("✅ Token parts:", parts.length, "(should be 3)");
  
  // 3. Get a user ID from the table (check the DOM)
  const userIdElement = document.querySelector("[data-user-id]");
  if (!userIdElement) {
    console.warn("⚠️  No user element with data-user-id attribute found in DOM");
    return;
  }
  
  const userId = userIdElement.getAttribute("data-user-id");
  console.log("✅ Found user ID:", userId);
  
  // 4. Make a test DELETE request
  try {
    const response = await fetch(`/api/v1/admin/crud/users/${userId}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    
    console.log("Response status:", response.status);
    console.log("Response statusText:", response.statusText);
    
    if (response.status === 401) {
      console.error("❌ Got 401 Unauthorized");
      console.log("Response headers:", {
        "www-authenticate": response.headers.get("www-authenticate"),
      });
      
      // Try to see if response has body
      try {
        const data = await response.json();
        console.log("Response body:", data);
      } catch {
        console.log("No JSON response body");
      }
    } else if (response.status === 204 || response.status === 200) {
      console.log("✅ DELETE successful!");
    } else {
      console.log("Unexpected status");
      const data = await response.json();
      console.log("Response:", data);
    }
    
  } catch (error) {
    console.error("❌ Request failed:", error);
  }
}

// Run the test
testAdminDelete();
