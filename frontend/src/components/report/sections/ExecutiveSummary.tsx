/**
 * =============================================================================
 * Executive Summary Section
 * =============================================================================
 * Hero section with overall score gauge, grade interpretation, and key stats.
 * Uses the "5-second test" principle - users should understand overall health immediately.
 * =============================================================================
 */

'use client';

import { motion } from 'framer-motion';
import { TrendingUp, AlertTriangle, Zap, ArrowRight } from 'lucide-react';
import { ScoreGauge } from '../charts/ScoreGauge';
import { MetricCard } from '../cards/MetricCard';
import { getGradeInfo } from '@/lib/scoring';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface ExecutiveSummaryProps {
  /** Overall score (0-100) */
  score: number;
  /** AI-generated summary text */
  summary?: string;
  /** Number of strengths identified */
  strengthsCount: number;
  /** Number of issues identified */
  issuesCount: number;
  /** Number of quick win recommendations */
  quickWinsCount: number;
  /** Website URL being analyzed */
  url: string;
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ExecutiveSummary({
  score,
  summary,
  strengthsCount,
  issuesCount,
  quickWinsCount,
  url,
  className = '',
}: ExecutiveSummaryProps) {
  const gradeInfo = getGradeInfo(score);

  // Extract domain from URL for display
  const domain = url.replace(/^https?:\/\//, '').replace(/\/$/, '');

  return (
    <section id="summary" className={`py-12 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero grid - Score gauge + Summary */}
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Left - Score visualization */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col items-center lg:items-start"
          >
            {/* Score gauge */}
            <div className="relative">
              <ScoreGauge score={score} size="xl" showGrade={true} />
              
              {/* Grade interpretation badge */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.4 }}
                className={`
                  mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full
                  ${gradeInfo.bgColor} ${gradeInfo.color} border ${gradeInfo.borderColor}
                `}
              >
                <span className="text-lg font-bold">{gradeInfo.grade}</span>
                <span className="text-sm font-medium">{gradeInfo.label}</span>
              </motion.div>
            </div>

            {/* Grade description */}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 0.4 }}
              className="mt-4 text-sm text-slate-600 text-center lg:text-left max-w-sm"
            >
              {gradeInfo.description}
            </motion.p>
          </motion.div>

          {/* Right - Summary and headline */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {/* Domain heading */}
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Brand Analysis
            </h1>
            <p className="text-xl text-slate-600 mb-6">
              Comprehensive audit of{' '}
              <span className="font-semibold text-slate-900">{domain}</span>
            </p>

            {/* AI Summary */}
            {summary && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5, duration: 0.4 }}
                className="bg-slate-50 rounded-xl p-5 border border-slate-100"
              >
                <p className="text-slate-700 leading-relaxed">{summary}</p>
              </motion.div>
            )}
          </motion.div>
        </div>

        {/* Quick stats row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="mt-10 grid grid-cols-3 gap-4"
        >
          {/* Strengths */}
          <MetricCard
            label="Strengths"
            value={strengthsCount}
            icon={<TrendingUp className="w-5 h-5 text-emerald-500" />}
            subtitle="Areas performing well"
            animate={false}
          />

          {/* Issues */}
          <MetricCard
            label="Issues Found"
            value={issuesCount}
            icon={<AlertTriangle className="w-5 h-5 text-orange-500" />}
            subtitle="Opportunities to improve"
            animate={false}
          />

          {/* Quick Wins */}
          <MetricCard
            label="Quick Wins"
            value={quickWinsCount}
            icon={<Zap className="w-5 h-5 text-yellow-500" />}
            subtitle="High impact, low effort"
            animate={false}
          />
        </motion.div>

        {/* CTA to jump to action plan */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.4 }}
          className="mt-8 text-center"
        >
          <button
            onClick={() => {
              const el = document.getElementById('action-plan');
              if (el) {
                const offset = 80;
                const top = el.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({ top, behavior: 'smooth' });
              }
            }}
            className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
          >
            Jump to Action Plan
            <ArrowRight className="w-4 h-4" />
          </button>
        </motion.div>
      </div>
    </section>
  );
}

export default ExecutiveSummary;

