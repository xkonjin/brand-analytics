const API_URL = ''

/**
 * Generic fetch wrapper with error handling.
 * 
 * @template T - The expected return type
 * @param endpoint - API endpoint (e.g., '/api/v1/analyze')
 * @param options - Fetch options (method, body, headers)
 */
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

  // Fail fast if the response is not OK (2xx)
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `API Error: ${response.status}`)
  }

  return response.json()
}

// -----------------------------------------------------------------------------
// Analysis Endpoints
// -----------------------------------------------------------------------------

export interface AnalysisResponse {
  id: string
  status: string
}

export interface AnalysisOptions {
  description?: string
  industry?: string
  email?: string
}

/**
 * Start a new brand analysis.
 * This is an async operation that returns a job ID immediately.
 */
export async function startAnalysis(url: string, options?: AnalysisOptions) {
  return fetchAPI<AnalysisResponse>('/api/v1/analyze', {
    method: 'POST',
    body: JSON.stringify({ url, ...options }),
  })
}

export interface AnalysisProgress {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  modules: Record<string, string> // e.g., { seo: "completed", social: "running" }
  completion_percentage: number
  error?: string
}

/**
 * Get analysis status/progress.
 * Used for polling the progress bar.
 */
export async function getAnalysisProgress(id: string) {
  return fetchAPI<AnalysisProgress>(`/api/v1/analysis/${id}/progress`)
}

export interface ReportData {
  id: string
  url: string
  overall_score: number
  scores: Record<string, number>
  report: any // This would be the full typed report object
}

/**
 * Get the full analysis report.
 * Called once the status is 'completed'.
 */
export async function getReport(id: string) {
  return fetchAPI<ReportData>(`/api/v1/analysis/${id}/report`)
}

/**
 * Get PDF download URL.
 * Does not fetch; just returns the string for the <a> tag.
 */
export function getPDFUrl(id: string): string {
  return `${API_URL}/api/v1/analysis/${id}/pdf`
}

// Alias for backwards compatibility with older components
export const submitAnalysis = startAnalysis

/**
 * Get analysis status (alternative endpoint).
 */
export async function getAnalysisStatus(id: string) {
  return fetchAPI<{
    id: string
    url: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    result_data?: any
  }>(`/api/v1/analysis/${id}`)
}
