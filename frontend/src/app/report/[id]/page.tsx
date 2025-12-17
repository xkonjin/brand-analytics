// =============================================================================
// Report Page
// =============================================================================
// Displays the complete brand analysis report with scores and recommendations.
// =============================================================================

'use client'

import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { Download, Share2, ArrowLeft, ExternalLink } from 'lucide-react'
import { ScoreCard } from '@/components/ScoreCard'
import { ReportSection } from '@/components/ReportSection'

interface Report {
  id: string
  url: string
  overall_score: number
  scores: Record<string, number>
  report: any
}

export default function ReportPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const { id } = params

  // Fetch the full report
  const { data, isLoading, error } = useQuery<Report>({
    queryKey: ['report', id],
    queryFn: async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analysis/${id}/report`
      )
      if (!res.ok) throw new Error('Failed to fetch report')
      return res.json()
    },
  })

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-slate-500">Loading report...</div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Failed to load report</p>
          <button onClick={() => router.push('/')} className="btn-primary">
            Start New Analysis
          </button>
        </div>
      </div>
    )
  }

  const { url, overall_score, scores, report } = data
  const scorecard = report?.scorecard || {}

  return (
    <main className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-slate-600 hover:text-slate-900"
          >
            <ArrowLeft className="w-4 h-4" />
            New Analysis
          </button>

          <div className="flex items-center gap-3">
            <a
              href={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/analysis/${id}/pdf`}
              className="flex items-center gap-2 px-4 py-2 border border-slate-300 
                       rounded-lg hover:bg-slate-50 transition-colors"
            >
              <Download className="w-4 h-4" />
              Download PDF
            </a>
            <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 
                             text-white rounded-lg hover:bg-blue-700 transition-colors">
              <Share2 className="w-4 h-4" />
              Share
            </button>
          </div>
        </div>
      </header>

      {/* Report Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <section className="bg-white rounded-2xl border border-slate-200 p-8 mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center gap-8">
            {/* Brand info */}
            <div className="flex-1">
              <p className="text-sm text-slate-500 mb-2">Brand Analysis Report</p>
              <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
                {url}
                <a href={url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 text-slate-400" />
                </a>
              </h1>
              <p className="text-slate-600">{scorecard.summary}</p>
            </div>

            {/* Overall score */}
            <div className="text-center">
              <ScoreCard score={overall_score} size="large" />
              <p className="text-sm text-slate-500 mt-2">Overall Score</p>
              <p className="text-2xl font-bold text-blue-600">
                Grade: {scorecard.grade || 'B'}
              </p>
            </div>
          </div>
        </section>

        {/* Scores Grid */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {Object.entries(scores || {}).map(([key, score]) => (
            <div key={key} className="bg-white rounded-xl border border-slate-200 p-4 text-center">
              <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">
                {key.replace('_', ' ')}
              </p>
              <ScoreCard score={score as number} size="small" />
            </div>
          ))}
        </section>

        {/* Strengths & Weaknesses */}
        <section className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-emerald-50 rounded-2xl border border-emerald-200 p-6">
            <h3 className="font-semibold text-emerald-800 mb-4">Key Strengths</h3>
            <ul className="space-y-2">
              {(scorecard.strengths || []).slice(0, 5).map((s: string, i: number) => (
                <li key={i} className="flex items-start gap-2 text-emerald-700">
                  <span className="text-emerald-500">✓</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-amber-50 rounded-2xl border border-amber-200 p-6">
            <h3 className="font-semibold text-amber-800 mb-4">Areas to Improve</h3>
            <ul className="space-y-2">
              {(scorecard.weaknesses || []).slice(0, 5).map((w: string, i: number) => (
                <li key={i} className="flex items-start gap-2 text-amber-700">
                  <span className="text-amber-500">!</span>
                  {w}
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* Top Recommendations */}
        <section className="bg-white rounded-2xl border border-slate-200 p-6 mb-8">
          <h2 className="text-xl font-bold mb-6">Top Recommendations</h2>
          <div className="space-y-4">
            {(scorecard.top_recommendations || []).slice(0, 5).map((rec: any, i: number) => (
              <div key={i} className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-1">
                      {i + 1}. {rec.title}
                    </h4>
                    <p className="text-slate-600 text-sm">{rec.description}</p>
                  </div>
                  <div className="flex gap-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      rec.impact === 'high' ? 'bg-emerald-100 text-emerald-700' :
                      'bg-slate-100 text-slate-600'
                    }`}>
                      {rec.impact} impact
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Detailed Sections */}
        <section className="space-y-6">
          <h2 className="text-xl font-bold">Detailed Analysis</h2>
          
          {report?.seo && (
            <ReportSection title="SEO Performance" score={scores?.seo} data={report.seo} />
          )}
          {report?.social_media && (
            <ReportSection title="Social Media" score={scores?.social_media} data={report.social_media} />
          )}
          {report?.brand_messaging && (
            <ReportSection title="Brand Messaging" score={scores?.brand_messaging} data={report.brand_messaging} />
          )}
          {report?.website_ux && (
            <ReportSection title="Website UX" score={scores?.website_ux} data={report.website_ux} />
          )}
        </section>
      </div>

      {/* Footer */}
      <footer className="py-8 border-t border-slate-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 text-center text-slate-500 text-sm">
          <p>Generated by Brand Analytics Tool</p>
        </div>
      </footer>
    </main>
  )
}

