// =============================================================================
// Client Providers
// =============================================================================
// Wraps the app with React Query and other client-side providers.
// =============================================================================

'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  // Create query client with sensible defaults
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        // Don't refetch on window focus in development
        refetchOnWindowFocus: false,
        // Retry once on failure
        retry: 1,
        // Cache for 5 minutes
        staleTime: 5 * 60 * 1000,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

