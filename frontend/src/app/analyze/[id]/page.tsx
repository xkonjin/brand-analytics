// =============================================================================
// Analysis Progress Page
// =============================================================================
// Shows real-time progress of the brand analysis with module status.
// =============================================================================

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, Circle, Loader2, XCircle } from 'lucide-react'

// Module display names
const MODULE_NAMES: Record<string, string> = {
  seo: 'SEO Performance',
  social_media: 'Social Media',
  brand_messaging: 'Brand Messaging',
  website_ux: 'Website UX',
  ai_discoverability: 'AI Discoverability',
  content: 'Content Analysis',
  team_presence: 'Team Presence',
  channel_fit: 'Channel Fit',
  scorecard: 'Generating Report',
}

interface AnalysisProgress {
  id: string
  status: string
  modules: Record<string, string>
  completion_percentage: number
}

export default function AnalyzePage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const { id } = params

  // Poll for progress updates
  const { data, isLoading, error } = useQuery<AnalysisProgress>({
    queryKey: ['analysis-progress', id],
    queryFn: async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analysis/${id}/progress`
      )
      if (!res.ok) throw new Error('Failed to fetch progress')
      return res.json()
    },
    refetchInterval: (data) => {
      // Stop polling when completed or failed
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false
      }
      return 2000 // Poll every 2 seconds
    },
  })

  // Redirect to report when completed
  useEffect(() => {
    if (data?.status === 'completed') {
      // Brief delay to show completion state
      setTimeout(() => {
        router.push(`/report/${id}`)
      }, 1000)
    }
  }, [data?.status, id, router])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Analysis Not Found</h1>
          <p className="text-slate-600 mb-6">
            The analysis you're looking for doesn't exist or has expired.
          </p>
          <button onClick={() => router.push('/')} className="btn-primary">
            Start New Analysis
          </button>
        </div>
      </div>
    )
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 
                          rounded-full bg-blue-100 mb-6">
            <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
          </div>
          <h1 className="text-2xl font-bold mb-2">Analyzing Your Brand</h1>
          <p className="text-slate-600">
            This usually takes 1-2 minutes. Please don't close this page.
          </p>
        </div>

        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-slate-600">Progress</span>
            <span className="font-medium text-blue-600">
              {data?.completion_percentage ?? 0}%
            </span>
          </div>
          <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-blue-600 
                         rounded-full transition-all duration-500"
              style={{ width: `${data?.completion_percentage ?? 0}%` }}
            />
          </div>
        </div>

        {/* Module status list */}
        <div className="card p-6">
          <h2 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-4">
            Analysis Modules
          </h2>
          <div className="space-y-4">
            {Object.entries(MODULE_NAMES).map(([key, name]) => {
              const status = data?.modules?.[key] ?? 'pending'
              return (
                <ModuleStatus key={key} name={name} status={status} />
              )
            })}
          </div>
        </div>

        {/* Status message */}
        {data?.status === 'failed' && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-center">
            <p className="text-red-700">
              Analysis failed. Please try again or contact support.
            </p>
            <button onClick={() => router.push('/')} className="btn-primary mt-4">
              Try Again
            </button>
          </div>
        )}
      </div>
    </main>
  )
}

// Module status row component
function ModuleStatus({ name, status }: { name: string; status: string }) {
  return (
    <div className="flex items-center gap-3">
      {/* Status icon */}
      {status === 'completed' && (
        <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />
      )}
      {status === 'running' && (
        <Loader2 className="w-5 h-5 text-blue-500 animate-spin flex-shrink-0" />
      )}
      {status === 'failed' && (
        <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
      )}
      {status === 'pending' && (
        <Circle className="w-5 h-5 text-slate-300 flex-shrink-0" />
      )}

      {/* Module name */}
      <span className={`flex-1 ${
        status === 'pending' ? 'text-slate-400' : 'text-slate-700'
      }`}>
        {name}
      </span>

      {/* Status badge */}
      <span className={`text-xs px-2 py-1 rounded-full ${
        status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
        status === 'running' ? 'bg-blue-100 text-blue-700' :
        status === 'failed' ? 'bg-red-100 text-red-700' :
        'bg-slate-100 text-slate-500'
      }`}>
        {status === 'running' ? 'Analyzing...' : 
         status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    </div>
  )
}

