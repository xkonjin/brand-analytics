/**
 * =============================================================================
 * EXPLAINER: Score Overview Section
 * =============================================================================
 *
 * WHAT IS THIS?
 * The "Hero" section of the report results. It shows the high-level scores.
 *
 * VISUALIZATION LOGIC:
 * 1. **Radar Chart**: Used to show balance/skew. A perfect brand is a full circle.
 *    - Spikes indicate strengths.
 *    - Dips indicate weaknesses.
 * 2. **Benchmark Line**: Dotted line on the radar chart.
 *    - Shows "Industry Average". If you're inside the line, you're losing.
 * 3. **Bar Charts**: Break down the individual module scores for clarity.
 *
 * DATA FLOW:
 * - Takes `scores` (Record<string, number>) as input.
 * - Maps them to `MODULE_BENCHMARKS` to get labels and ordering.
 * - Computes aggregate stats (Average, Highest, Lowest).
 * =============================================================================
 */

'use client';

import { motion } from 'framer-motion';
import { Info, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { BrandRadarChart } from '../charts/BrandRadarChart';
import { MetricBar } from '../charts/MetricBar';
import { getScoreClasses, getGradeInfo } from '@/lib/scoring';
import { MODULE_BENCHMARKS, compareToBenchmark } from '@/lib/benchmarks';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface ModuleScore {
  key: string;
  label: string;
  score: number;
}

interface ScoreOverviewProps {
  /** Scores for each module (0-100) */
  scores: Record<string, number>;
  /** Whether to show benchmark comparisons */
  showBenchmarks?: boolean;
  /** Optional className for styling */
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ScoreOverview({
  scores,
  showBenchmarks = true,
  className = '',
}: ScoreOverviewProps) {
  // Transform raw score object into sorted array for rendering
  const moduleScores: ModuleScore[] = MODULE_BENCHMARKS
    .map((benchmark) => ({
      key: benchmark.key,
      label: benchmark.label,
      score: scores[benchmark.key] ?? 0,
    }))
    .sort((a, b) => b.score - a.score); // Sort highest to lowest

  // Calculate summary statistics
  const avgScore = Object.values(scores).reduce((sum, s) => sum + s, 0) / (Object.keys(scores).length || 1);
  
  // Count how many modules beat the benchmark
  const aboveBenchmark = moduleScores.filter(
    (m) => m.score > (MODULE_BENCHMARKS.find((b) => b.key === m.key)?.benchmark ?? 0)
  ).length;

  return (
    <section className={`py-12 border-t border-slate-100 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-8"
        >
          <h2 className="text-2xl font-bold text-slate-900 mb-2">
            Performance Overview
          </h2>
          <p className="text-slate-600">
            How your brand performs across 8 key dimensions compared to industry benchmarks.
          </p>
        </motion.div>

        {/* Two-column layout: Radar chart (Visual) + Score bars (Detail) */}
        <div className="grid lg:grid-cols-2 gap-8">
          
          {/* Left Column: Radar Chart */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="bg-white rounded-xl border border-slate-200 p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-900">Score Radar</h3>
              {showBenchmarks && (
                <div className="flex items-center gap-4 text-xs text-slate-500">
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-0.5 bg-slate-400 rounded" style={{ borderStyle: 'dashed' }} />
                    Industry Benchmark
                  </span>
                </div>
              )}
            </div>
            {/* The Radar Chart component handles the SVG rendering */}
            <BrandRadarChart
              scores={scores}
              showBenchmark={showBenchmarks}
              height={320}
            />
          </motion.div>

          {/* Right Column: Detailed Breakdown */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="space-y-6"
          >
            {/* KPI Cards */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white rounded-lg border border-slate-200 p-4">
                <div className="text-2xl font-bold text-slate-900">
                  {avgScore.toFixed(0)}
                </div>
                <div className="text-sm text-slate-500">Average Score</div>
              </div>
              <div className="bg-white rounded-lg border border-slate-200 p-4">
                <div className="text-2xl font-bold text-emerald-600">
                  {aboveBenchmark}/{moduleScores.length}
                </div>
                <div className="text-sm text-slate-500">Above Benchmark</div>
              </div>
            </div>

            {/* Score Bars List */}
            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-900 mb-5">
                Module Scores
              </h3>
              <div className="space-y-4">
                {moduleScores.map((module, index) => {
                  const comparison = compareToBenchmark(module.score, module.key);
                  
                  return (
                    <motion.div
                      key={module.key}
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <MetricBar
                        label={module.label}
                        score={module.score}
                        moduleKey={module.key}
                        showBenchmark={showBenchmarks}
                        size="sm"
                        animate={false}
                      />
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        </div>

        {/* Bottom Section: Strengths & Weaknesses Analysis */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-8 grid md:grid-cols-2 gap-6"
        >
          {/* Top strengths (Top 3 scores) */}
          <div className="bg-emerald-50 rounded-xl border border-emerald-100 p-5">
            <h4 className="font-semibold text-emerald-800 mb-3 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Top Strengths
            </h4>
            <ul className="space-y-2">
              {moduleScores.slice(0, 3).map((module) => (
                <li
                  key={module.key}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-emerald-700">{module.label}</span>
                  <span className="font-semibold text-emerald-800">
                    {module.score.toFixed(0)}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {/* Areas for improvement (Bottom 3 scores) */}
          <div className="bg-orange-50 rounded-xl border border-orange-100 p-5">
            <h4 className="font-semibold text-orange-800 mb-3 flex items-center gap-2">
              <TrendingDown className="w-4 h-4" />
              Areas for Improvement
            </h4>
            <ul className="space-y-2">
              {[...moduleScores].reverse().slice(0, 3).map((module) => (
                <li
                  key={module.key}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-orange-700">{module.label}</span>
                  <span className="font-semibold text-orange-800">
                    {module.score.toFixed(0)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

export default ScoreOverview;
