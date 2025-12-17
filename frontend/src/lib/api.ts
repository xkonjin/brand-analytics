// =============================================================================
// API Client
// =============================================================================
// Helper functions for making API calls to the backend.
// =============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Generic fetch wrapper with error handling
async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_URL}${endpoint}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `API Error: ${response.status}`)
  }

  return response.json()
}

// Start a new analysis
export async function startAnalysis(url: string, options?: {
  description?: string
  industry?: string
  email?: string
}) {
  return fetchAPI<{ id: string; status: string }>('/api/v1/analyze', {
    method: 'POST',
    body: JSON.stringify({ url, ...options }),
  })
}

// Get analysis status/progress
export async function getAnalysisProgress(id: string) {
  return fetchAPI<{
    id: string
    status: string
    modules: Record<string, string>
    completion_percentage: number
  }>(`/api/v1/analysis/${id}/progress`)
}

// Get the full report
export async function getReport(id: string) {
  return fetchAPI<{
    id: string
    url: string
    overall_score: number
    scores: Record<string, number>
    report: any
  }>(`/api/v1/analysis/${id}/report`)
}

// Get PDF download URL
export function getPDFUrl(id: string): string {
  return `${API_URL}/api/v1/analysis/${id}/pdf`
}

// Alias for backwards compatibility
export const submitAnalysis = startAnalysis

// Get analysis status (for polling)
export async function getAnalysisStatus(id: string) {
  return fetchAPI<{
    id: string
    url: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    result_data?: any
  }>(`/api/v1/analysis/${id}`)
}

