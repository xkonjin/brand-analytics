// =============================================================================
// Report Section Component
// =============================================================================
// Collapsible section for displaying detailed analysis results.
// =============================================================================

'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { ScoreCard } from './ScoreCard'

interface ReportSectionProps {
  title: string
  score?: number
  data: any
}

export function ReportSection({ title, score, data }: ReportSectionProps) {
  const [isOpen, setIsOpen] = useState(false)

  const findings = data?.findings || []
  const recommendations = data?.recommendations || []

  return (
    <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      {/* Header - clickable to toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-4">
          {score !== undefined && <ScoreCard score={score} size="small" />}
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
        {isOpen ? (
          <ChevronUp className="w-5 h-5 text-slate-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-slate-400" />
        )}
      </button>

      {/* Content */}
      {isOpen && (
        <div className="px-6 pb-6 border-t border-slate-100">
          {/* Findings */}
          {findings.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-3">
                Key Findings
              </h4>
              <div className="space-y-3">
                {findings.map((finding: any, i: number) => (
                  <div
                    key={i}
                    className={`p-3 rounded-lg border-l-4 ${
                      finding.severity === 'critical' ? 'bg-red-50 border-red-500' :
                      finding.severity === 'high' ? 'bg-amber-50 border-amber-500' :
                      finding.severity === 'medium' ? 'bg-blue-50 border-blue-500' :
                      'bg-slate-50 border-slate-300'
                    }`}
                  >
                    <p className="font-medium">{finding.title}</p>
                    <p className="text-sm text-slate-600 mt-1">{finding.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-3">
                Recommendations
              </h4>
              <div className="space-y-3">
                {recommendations.map((rec: any, i: number) => (
                  <div key={i} className="p-3 bg-emerald-50 rounded-lg">
                    <p className="font-medium text-emerald-800">{rec.title}</p>
                    <p className="text-sm text-emerald-700 mt-1">{rec.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

