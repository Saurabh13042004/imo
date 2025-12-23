/**
 * Session management utilities for guest users
 */

const SESSION_ID_KEY = 'guest-session-id';

/**
 * Generate a unique session ID for guest users
 */
function generateSessionId(): string {
  return `guest-${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
}

/**
 * Get or create a session ID for the current user
 */
export function getSessionId(): string {
  // Check if we already have a session ID
  let sessionId = localStorage.getItem(SESSION_ID_KEY);
  
  if (!sessionId) {
    // Generate new session ID
    sessionId = generateSessionId();
    localStorage.setItem(SESSION_ID_KEY, sessionId);
  }
  
  return sessionId;
}

/**
 * Clear the session ID (for testing or logout)
 */
export function clearSessionId(): void {
  localStorage.removeItem(SESSION_ID_KEY);
}
