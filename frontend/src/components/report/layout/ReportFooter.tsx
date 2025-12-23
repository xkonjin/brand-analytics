/**
 * =============================================================================
 * Report Footer Component - Apple Liquid Glass UI
 * =============================================================================
 * Footer with methodology explanation, disclaimer, and branding.
 * Features collapsible methodology section with glass styling.
 * =============================================================================
 */

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';
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
// Grade color mapping for glass UI
// -----------------------------------------------------------------------------
const GRADE_COLORS = {
  emerald: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
    text: 'text-emerald-400',
    glow: 'shadow-[0_0_15px_rgba(52,211,153,0.2)]',
  },
  green: {
    bg: 'bg-green-500/10',
    border: 'border-green-500/20',
    text: 'text-green-400',
    glow: 'shadow-[0_0_15px_rgba(74,222,128,0.2)]',
  },
  yellow: {
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/20',
    text: 'text-yellow-400',
    glow: 'shadow-[0_0_15px_rgba(250,204,21,0.2)]',
  },
  orange: {
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/20',
    text: 'text-orange-400',
    glow: 'shadow-[0_0_15px_rgba(251,146,60,0.2)]',
  },
  red: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/20',
    text: 'text-red-400',
    glow: 'shadow-[0_0_15px_rgba(248,113,113,0.2)]',
  },
};

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ReportFooter({
  analysisId,
  processingTime,
  className = '',
}: ReportFooterProps) {
  const [showMethodology, setShowMethodology] = useState(false);

  const gradeScale = [
    { grade: 'A+', range: '90-100', color: 'emerald' as const },
    { grade: 'A', range: '80-89', color: 'emerald' as const },
    { grade: 'B', range: '70-79', color: 'green' as const },
    { grade: 'C', range: '60-69', color: 'yellow' as const },
    { grade: 'D', range: '50-59', color: 'orange' as const },
    { grade: 'F', range: '0-49', color: 'red' as const },
  ];

  return (
    <footer className={`border-t border-white/[0.08] ${className}`}>
      {/* Methodology section - collapsible */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Toggle button */}
        <button
          onClick={() => setShowMethodology(!showMethodology)}
          className="w-full py-4 flex items-center justify-between text-sm text-white/50 
                   hover:text-white/80 transition-colors"
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
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="pb-8 space-y-6">
                {/* Overview */}
                <div className="text-sm text-white/60 leading-relaxed max-w-3xl">
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
                    <motion.div
                      key={module.key}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-white/[0.05] backdrop-blur-sm rounded-xl border border-white/[0.08] p-4
                               hover:bg-white/[0.08] transition-all"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-white">
                          {module.label}
                        </h4>
                        <span className="text-xs text-white/40 bg-white/[0.08] px-2 py-0.5 rounded">
                          Benchmark: {module.benchmark}
                        </span>
                      </div>
                      <p className="text-sm text-white/50 mb-3">
                        {module.methodology}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {module.sources.map((source) => (
                          <span
                            key={source}
                            className="text-xs text-white/40 bg-white/[0.05] px-2 py-0.5 rounded"
                          >
                            {source}
                          </span>
                        ))}
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Grade scale */}
                <div className="bg-white/[0.05] backdrop-blur-sm rounded-xl border border-white/[0.08] p-5">
                  <h4 className="font-medium text-white mb-4">
                    Grade Scale
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 text-sm">
                    {gradeScale.map(({ grade, range, color }) => {
                      const colors = GRADE_COLORS[color];
                      return (
                        <div
                          key={grade}
                          className={`text-center p-3 rounded-xl ${colors.bg} border ${colors.border} ${colors.glow}`}
                        >
                          <div className={`font-bold text-lg ${colors.text}`}>
                            {grade}
                          </div>
                          <div className="text-xs text-white/40">{range}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-white/[0.05] bg-white/[0.02]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/40">
            {/* Left - branding */}
            <div className="flex items-center gap-2">
              <span className="font-medium text-white/60">
                Brand Analytics
              </span>
              <span className="text-white/20">·</span>
              <span>Comprehensive Brand Analysis Tool</span>
            </div>

            {/* Right - metadata */}
            <div className="flex items-center gap-4">
              {processingTime && (
                <span>Analysis time: {processingTime.toFixed(1)}s</span>
              )}
              {analysisId && (
                <span className="font-mono text-xs text-white/30">
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
