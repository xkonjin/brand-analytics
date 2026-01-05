/**
 * =============================================================================
 * Module Section Component - Apple Liquid Glass UI
 * =============================================================================
 * Reusable template for all analysis module sections with glassmorphism.
 * Provides consistent structure: score header, metrics grid, findings, recommendations.
 * =============================================================================
 */

"use client";

import { ReactNode } from "react";
import { motion } from "framer-motion";
import { ScoreGauge } from "../charts/ScoreGauge";
import { MetricCardGrid } from "../cards/MetricCard";
import { InsightCardList } from "../cards/InsightCard";
import { RecommendationList } from "../cards/RecommendationCard";
import { getGradeInfo } from "@/lib/scoring";
import { getBenchmark, compareToBenchmark } from "@/lib/benchmarks";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface Metric {
  label: string;
  value: string | number;
  unit?: string;
  trend?: "up" | "down" | "stable";
  trendValue?: string;
}

interface Finding {
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low" | "info" | "success";
  data?: Record<string, string | number>;
}

interface Recommendation {
  title: string;
  description: string;
  priority: "critical" | "high" | "medium" | "low";
  category: string;
  impact: "high" | "medium" | "low";
  effort: "high" | "medium" | "low";
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
// Score-based icon background for Glass UI
// -----------------------------------------------------------------------------
function getScoreIconStyle(score: number) {
  if (score >= 80) {
    return {
      bg: "from-emerald-500/20 to-emerald-600/10",
      border: "border-emerald-500/30",
      glow: "shadow-[0_0_30px_rgba(52,211,153,0.3)]",
      text: "text-emerald-400",
    };
  }
  if (score >= 70) {
    return {
      bg: "from-green-500/20 to-green-600/10",
      border: "border-green-500/30",
      glow: "shadow-[0_0_30px_rgba(74,222,128,0.3)]",
      text: "text-green-400",
    };
  }
  if (score >= 60) {
    return {
      bg: "from-yellow-500/20 to-yellow-600/10",
      border: "border-yellow-500/30",
      glow: "shadow-[0_0_30px_rgba(250,204,21,0.3)]",
      text: "text-yellow-400",
    };
  }
  if (score >= 50) {
    return {
      bg: "from-orange-500/20 to-orange-600/10",
      border: "border-orange-500/30",
      glow: "shadow-[0_0_30px_rgba(251,146,60,0.3)]",
      text: "text-orange-400",
    };
  }
  return {
    bg: "from-red-500/20 to-red-600/10",
    border: "border-red-500/30",
    glow: "shadow-[0_0_30px_rgba(248,113,113,0.3)]",
    text: "text-red-400",
  };
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
  className = "",
}: ModuleSectionProps) {
  const gradeInfo = getGradeInfo(score);
  const benchmark = getBenchmark(moduleKey);
  const comparison = compareToBenchmark(score, moduleKey);
  const iconStyle = getScoreIconStyle(score);

  return (
    <section
      id={id}
      className={`py-8 border-t border-white/[0.08] ${className}`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.2 }}
          className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6"
        >
          {/* Left - Title and description */}
          <div className="flex items-start gap-3">
            <div
              className={`
              p-2 rounded-lg bg-gradient-to-br ${iconStyle.bg} 
              border ${iconStyle.border} ${iconStyle.glow} ${iconStyle.text}
            `}
            >
              {icon}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white leading-tight">
                {title}
              </h2>
              <p className="text-white/60 text-sm mt-0.5 max-w-xl">
                {description}
              </p>
              {benchmark && (
                <p className="text-xs text-white/40 mt-1.5">
                  {benchmark.methodology}
                </p>
              )}
            </div>
          </div>

          {/* Right - Score display */}
          <div className="flex items-center gap-3">
            <ScoreGauge
              score={score}
              size="sm"
              showGrade={true}
              animate={false}
            />
            <div className="text-right">
              <div
                className={`text-xs font-medium ${
                  comparison.percentile === "above"
                    ? "text-emerald-400"
                    : comparison.percentile === "below"
                      ? "text-orange-400"
                      : "text-white/50"
                }`}
              >
                {comparison.label}
              </div>
              {benchmark && (
                <div className="text-[10px] text-white/40 mt-0.5">
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
            transition={{ duration: 0.2, delay: 0.05 }}
            className="mb-6"
          >
            <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-3">
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
            transition={{ duration: 0.2, delay: 0.1 }}
            className="mb-6"
          >
            {children}
          </motion.div>
        )}

        {/* Two-column layout for findings and recommendations */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Findings */}
          {findings.length > 0 && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.2, delay: 0.15 }}
            >
              <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-3">
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
              transition={{ duration: 0.2, delay: 0.2 }}
            >
              <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-3">
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
