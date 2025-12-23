import { useAuthContext } from '@/contexts/AuthContext';

/**
 * Hook to access authentication context
 * Provides user state and auth operations
 */
export function useAuth() {
  const context = useAuthContext();

  return {
    user: context.user,
    loading: context.loading,
    isAuthenticated: context.isAuthenticated,
    signOut: context.logout,
    signIn: context.signIn,
    signUp: context.signUp,
    changePassword: context.changePassword,
    refreshToken: context.refreshAccessToken,
    accessToken: context.accessToken,
  };
}