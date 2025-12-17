/**
 * =============================================================================
 * Module Section Component
 * =============================================================================
 * Reusable template for all analysis module sections.
 * Provides consistent structure: score header, metrics grid, findings, recommendations.
 * =============================================================================
 */

'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { Info, ChevronRight } from 'lucide-react';
import { ScoreGauge } from '../charts/ScoreGauge';
import { MetricCardGrid } from '../cards/MetricCard';
import { InsightCardList } from '../cards/InsightCard';
import { RecommendationList } from '../cards/RecommendationCard';
import { getGradeInfo, getScoreClasses } from '@/lib/scoring';
import { getBenchmark, compareToBenchmark } from '@/lib/benchmarks';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface Metric {
  label: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;
}

interface Finding {
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info' | 'success';
  data?: Record<string, string | number>;
}

interface Recommendation {
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
}

interface ModuleSectionProps {
  /** Section HTML ID for navigation */
  id: string;
  /** Module key for benchmark lookup */
  moduleKey: string;
  /** Section title */
  title: string;
  /** Section description */
  description: string;
  /** Module score (0-100) */
  score: number;
  /** Icon component */
  icon: ReactNode;
  /** Key metrics to display */
  metrics?: Metric[];
  /** Analysis findings */
  findings?: Finding[];
  /** Recommendations */
  recommendations?: Recommendation[];
  /** Custom content to render */
  children?: ReactNode;
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ModuleSection({
  id,
  moduleKey,
  title,
  description,
  score,
  icon,
  metrics = [],
  findings = [],
  recommendations = [],
  children,
  className = '',
}: ModuleSectionProps) {
  const gradeInfo = getGradeInfo(score);
  const benchmark = getBenchmark(moduleKey);
  const comparison = compareToBenchmark(score, moduleKey);
  const scoreClasses = getScoreClasses(score);

  return (
    <section id={id} className={`py-12 border-t border-slate-100 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="flex flex-col md:flex-row md:items-start md:justify-between gap-6 mb-8"
        >
          {/* Left - Title and description */}
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-xl ${scoreClasses.bg} ${scoreClasses.text}`}>
              {icon}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900">{title}</h2>
              <p className="text-slate-600 mt-1 max-w-xl">{description}</p>
              {benchmark && (
                <p className="text-sm text-slate-500 mt-2">
                  Methodology: {benchmark.methodology}
                </p>
              )}
            </div>
          </div>

          {/* Right - Score display */}
          <div className="flex items-center gap-4">
            <ScoreGauge score={score} size="md" showGrade={true} animate={false} />
            <div className="text-right">
              <div
                className={`text-sm font-medium ${
                  comparison.percentile === 'above'
                    ? 'text-emerald-600'
                    : comparison.percentile === 'below'
                    ? 'text-orange-600'
                    : 'text-slate-500'
                }`}
              >
                {comparison.label}
              </div>
              {benchmark && (
                <div className="text-xs text-slate-400 mt-1">
                  Benchmark: {benchmark.benchmark}
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Metrics grid */}
        {metrics.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-8"
          >
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
              Key Metrics
            </h3>
            <MetricCardGrid
              metrics={metrics}
              columns={metrics.length > 4 ? 4 : (metrics.length as 2 | 3 | 4)}
              size="sm"
              animate={false}
            />
          </motion.div>
        )}

        {/* Custom content */}
        {children && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-8"
          >
            {children}
          </motion.div>
        )}

        {/* Two-column layout for findings and recommendations */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Findings */}
          {findings.length > 0 && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
                Findings ({findings.length})
              </h3>
              <InsightCardList insights={findings} animate={false} />
            </motion.div>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
                Recommendations ({recommendations.length})
              </h3>
              <RecommendationList
                recommendations={recommendations}
                maxItems={3}
                animate={false}
              />
            </motion.div>
          )}
        </div>
      </div>
    </section>
  );
}

export default ModuleSection;

