/**
 * =============================================================================
 * Score Overview Section - Apple Liquid Glass UI
 * =============================================================================
 * The "Hero" section showing high-level scores with glassmorphism.
 * Features radar chart and module score bars with glow effects.
 * =============================================================================
 */

"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown } from "lucide-react";
import { BrandRadarChart } from "../charts/BrandRadarChart";
import { MetricBar } from "../charts/MetricBar";
import { MODULE_BENCHMARKS, compareToBenchmark } from "@/lib/benchmarks";

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
  className = "",
}: ScoreOverviewProps) {
  // Transform raw score object into sorted array for rendering
  const moduleScores: ModuleScore[] = MODULE_BENCHMARKS.map((benchmark) => ({
    key: benchmark.key,
    label: benchmark.label,
    score: scores[benchmark.key] ?? 0,
  })).sort((a, b) => b.score - a.score); // Sort highest to lowest

  // Calculate summary statistics
  const avgScore =
    Object.values(scores).reduce((sum, s) => sum + s, 0) /
    (Object.keys(scores).length || 1);

  // Count how many modules beat the benchmark
  const aboveBenchmark = moduleScores.filter(
    (m) =>
      m.score >
      (MODULE_BENCHMARKS.find((b) => b.key === m.key)?.benchmark ?? 0),
  ).length;

  return (
    <section className={`py-8 border-t border-white/[0.08] ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-6"
        >
          <h2 className="text-2xl font-bold text-white mb-2">
            Performance Overview
          </h2>
          <p className="text-white/60">
            How your brand performs across 8 key dimensions compared to industry
            benchmarks.
          </p>
        </motion.div>

        {/* Two-column layout: Radar chart (Visual) + Score bars (Detail) */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Left Column: Radar Chart */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="bg-white/[0.05] backdrop-blur-xl rounded-2xl border border-white/[0.1] p-4"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-white">Score Radar</h3>
              {showBenchmarks && (
                <div className="flex items-center gap-4 text-xs text-white/40">
                  <span className="flex items-center gap-1">
                    <span
                      className="w-4 h-0.5 bg-white/30 rounded"
                      style={{ borderStyle: "dashed" }}
                    />
                    Industry Benchmark
                  </span>
                </div>
              )}
            </div>
            {/* The Radar Chart component handles the SVG rendering */}
            <BrandRadarChart
              scores={scores}
              showBenchmark={showBenchmarks}
              height={260}
            />
          </motion.div>

          {/* Right Column: Detailed Breakdown */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="space-y-4"
          >
            {/* KPI Cards */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/[0.05] backdrop-blur-xl rounded-xl border border-white/[0.1] p-4 flex flex-col justify-center">
                <div className="text-2xl font-bold text-white">
                  {avgScore.toFixed(0)}
                </div>
                <div className="text-sm text-white/50">Average Score</div>
              </div>
              <div className="bg-white/[0.05] backdrop-blur-xl rounded-xl border border-white/[0.1] p-4 flex flex-col justify-center">
                <div className="text-2xl font-bold text-emerald-400">
                  {aboveBenchmark}/{moduleScores.length}
                </div>
                <div className="text-sm text-white/50">Above Benchmark</div>
              </div>
            </div>

            {/* Score Bars List */}
            <div className="bg-white/[0.05] backdrop-blur-xl rounded-2xl border border-white/[0.1] p-4">
              <h3 className="font-semibold text-white mb-3">Module Scores</h3>
              <div className="space-y-3">
                {moduleScores.map((module, index) => {
                  return (
                    <motion.div
                      key={module.key}
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.02 }}
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
          className="mt-6 grid md:grid-cols-2 gap-6"
        >
          {/* Top strengths (Top 3 scores) */}
          <div
            className="bg-emerald-500/10 backdrop-blur-xl rounded-2xl border border-emerald-500/20 p-4
                        shadow-[0_0_30px_rgba(52,211,153,0.1)]"
          >
            <h4 className="font-semibold text-emerald-400 mb-3 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Top Strengths
            </h4>
            <ul className="space-y-2">
              {moduleScores.slice(0, 3).map((module) => (
                <li
                  key={module.key}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-emerald-300/80">{module.label}</span>
                  <span className="font-semibold text-emerald-400">
                    {module.score.toFixed(0)}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {/* Areas for improvement (Bottom 3 scores) */}
          <div
            className="bg-orange-500/10 backdrop-blur-xl rounded-2xl border border-orange-500/20 p-4
                        shadow-[0_0_30px_rgba(251,146,60,0.1)]"
          >
            <h4 className="font-semibold text-orange-400 mb-3 flex items-center gap-2">
              <TrendingDown className="w-4 h-4" />
              Areas for Improvement
            </h4>
            <ul className="space-y-2">
              {[...moduleScores]
                .reverse()
                .slice(0, 3)
                .map((module) => (
                  <li
                    key={module.key}
                    className="flex items-center justify-between text-sm"
                  >
                    <span className="text-orange-300/80">{module.label}</span>
                    <span className="font-semibold text-orange-400">
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
