/**
 * =============================================================================
 * Report Footer Component
 * =============================================================================
 * Footer with methodology explanation, disclaimer, and branding.
 * Provides transparency about how scores are calculated.
 * =============================================================================
 */

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Info, ExternalLink } from 'lucide-react';
import { MODULE_BENCHMARKS } from '@/lib/benchmarks';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface ReportFooterProps {
  /** Analysis ID */
  analysisId?: string;
  /** Processing time in seconds */
  processingTime?: number;
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ReportFooter({
  analysisId,
  processingTime,
  className = '',
}: ReportFooterProps) {
  const [showMethodology, setShowMethodology] = useState(false);

  return (
    <footer className={`border-t border-slate-200 bg-slate-50 ${className}`}>
      {/* Methodology section - collapsible */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Toggle button */}
        <button
          onClick={() => setShowMethodology(!showMethodology)}
          className="w-full py-4 flex items-center justify-between text-sm text-slate-600 hover:text-slate-900 transition-colors"
        >
          <span className="flex items-center gap-2 font-medium">
            <Info className="w-4 h-4" />
            Scoring Methodology & Sources
          </span>
          {showMethodology ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
        </button>

        {/* Methodology content */}
        <AnimatePresence>
          {showMethodology && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="pb-8 space-y-6">
                {/* Overview */}
                <div className="prose prose-sm prose-slate max-w-none">
                  <p>
                    This analysis uses industry-standard benchmarks and established
                    marketing frameworks to evaluate brand performance. Each module
                    is scored from 0-100 based on specific criteria, with scores
                    weighted according to their impact on overall brand health.
                  </p>
                </div>

                {/* Module breakdowns */}
                <div className="grid md:grid-cols-2 gap-4">
                  {MODULE_BENCHMARKS.map((module) => (
                    <div
                      key={module.key}
                      className="bg-white rounded-lg border border-slate-200 p-4"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-slate-900">
                          {module.label}
                        </h4>
                        <span className="text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                          Benchmark: {module.benchmark}
                        </span>
                      </div>
                      <p className="text-sm text-slate-600 mb-3">
                        {module.methodology}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {module.sources.map((source) => (
                          <span
                            key={source}
                            className="text-xs text-slate-500 bg-slate-50 px-2 py-0.5 rounded"
                          >
                            {source}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Grade scale */}
                <div className="bg-white rounded-lg border border-slate-200 p-4">
                  <h4 className="font-medium text-slate-900 mb-3">
                    Grade Scale
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 text-sm">
                    {[
                      { grade: 'A+', range: '90-100', color: 'emerald' },
                      { grade: 'A', range: '80-89', color: 'emerald' },
                      { grade: 'B', range: '70-79', color: 'green' },
                      { grade: 'C', range: '60-69', color: 'yellow' },
                      { grade: 'D', range: '50-59', color: 'orange' },
                      { grade: 'F', range: '0-49', color: 'red' },
                    ].map(({ grade, range, color }) => (
                      <div
                        key={grade}
                        className={`text-center p-2 rounded-lg bg-${color}-50 border border-${color}-200`}
                      >
                        <div className={`font-bold text-${color}-700`}>
                          {grade}
                        </div>
                        <div className="text-xs text-slate-500">{range}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate-500">
            {/* Left - branding */}
            <div className="flex items-center gap-2">
              <span className="font-medium text-slate-700">
                Brand Analytics
              </span>
              <span className="text-slate-300">·</span>
              <span>Comprehensive Brand Analysis Tool</span>
            </div>

            {/* Right - metadata */}
            <div className="flex items-center gap-4">
              {processingTime && (
                <span>Analysis time: {processingTime.toFixed(1)}s</span>
              )}
              {analysisId && (
                <span className="font-mono text-xs text-slate-400">
                  ID: {analysisId.slice(0, 8)}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default ReportFooter;

