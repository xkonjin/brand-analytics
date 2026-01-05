/**
 * =============================================================================
 * Executive Summary Section - Apple Liquid Glass UI
 * =============================================================================
 * Hero section with overall score gauge, grade interpretation, and key stats.
 * Uses glassmorphism and score-based glow effects.
 * =============================================================================
 */

"use client";

import { motion } from "framer-motion";
import { TrendingUp, AlertTriangle, Zap, ArrowRight } from "lucide-react";
import { ScoreGauge } from "../charts/ScoreGauge";
import { MetricCard } from "../cards/MetricCard";
import { getGradeInfo } from "@/lib/scoring";

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
// Score-based styling for Glass UI
// -----------------------------------------------------------------------------
function getGradeGlassStyle(score: number) {
  if (score >= 80) {
    return {
      bg: "bg-emerald-500/15",
      border: "border-emerald-500/30",
      text: "text-emerald-400",
      glow: "shadow-[0_0_30px_rgba(52,211,153,0.3)]",
    };
  }
  if (score >= 70) {
    return {
      bg: "bg-green-500/15",
      border: "border-green-500/30",
      text: "text-green-400",
      glow: "shadow-[0_0_30px_rgba(74,222,128,0.3)]",
    };
  }
  if (score >= 60) {
    return {
      bg: "bg-yellow-500/15",
      border: "border-yellow-500/30",
      text: "text-yellow-400",
      glow: "shadow-[0_0_30px_rgba(250,204,21,0.3)]",
    };
  }
  if (score >= 50) {
    return {
      bg: "bg-orange-500/15",
      border: "border-orange-500/30",
      text: "text-orange-400",
      glow: "shadow-[0_0_30px_rgba(251,146,60,0.3)]",
    };
  }
  return {
    bg: "bg-red-500/15",
    border: "border-red-500/30",
    text: "text-red-400",
    glow: "shadow-[0_0_30px_rgba(248,113,113,0.3)]",
  };
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
  className = "",
}: ExecutiveSummaryProps) {
  const gradeInfo = getGradeInfo(score);
  const gradeStyle = getGradeGlassStyle(score);

  // Extract domain from URL for display
  const domain = url.replace(/^https?:\/\//, "").replace(/\/$/, "");

  return (
    <section id="summary" className={`py-8 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-6 lg:gap-8 items-center">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
            className="flex flex-col items-center lg:items-start"
          >
            <div className="flex items-center gap-6">
              <ScoreGauge score={score} size="lg" showGrade={true} />

              <div className="flex flex-col items-start space-y-3">
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2, duration: 0.3 }}
                  className={`
                    inline-flex items-center gap-2 px-3 py-1.5 rounded-full
                    ${gradeStyle.bg} ${gradeStyle.text} border ${gradeStyle.border} ${gradeStyle.glow}
                    backdrop-blur-xl
                  `}
                >
                  <span className="text-base font-bold">{gradeInfo.grade}</span>
                  <span className="text-xs font-medium opacity-80 uppercase tracking-wider">
                    {gradeInfo.label}
                  </span>
                </motion.div>

                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3, duration: 0.3 }}
                  className="text-sm text-white/50 text-left max-w-[200px] leading-snug"
                >
                  {gradeInfo.description}
                </motion.p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">
              Brand Analysis
            </h1>
            <p className="text-lg text-white/60 mb-4">
              Comprehensive audit of{" "}
              <span className="font-semibold text-white">{domain}</span>
            </p>

            {summary && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.3 }}
                className="bg-white/[0.06] backdrop-blur-xl rounded-xl p-4 border border-white/[0.1]"
              >
                <p className="text-white/70 leading-relaxed text-sm">
                  {summary}
                </p>
              </motion.div>
            )}
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
          className="mt-6 grid grid-cols-3 gap-4"
        >
          <MetricCard
            label="Strengths"
            value={strengthsCount}
            icon={<TrendingUp className="w-4 h-4 text-emerald-400" />}
            subtitle="Areas performing well"
            animate={false}
          />

          <MetricCard
            label="Issues Found"
            value={issuesCount}
            icon={<AlertTriangle className="w-4 h-4 text-orange-400" />}
            subtitle="Opportunities to improve"
            animate={false}
          />

          <MetricCard
            label="Quick Wins"
            value={quickWinsCount}
            icon={<Zap className="w-4 h-4 text-yellow-400" />}
            subtitle="High impact, low effort"
            animate={false}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.3 }}
          className="mt-6 text-center"
        >
          <button
            onClick={() => {
              const el = document.getElementById("action-plan");
              if (el) {
                const offset = 80;
                const top =
                  el.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({ top, behavior: "smooth" });
              }
            }}
            className="inline-flex items-center gap-2 text-sm font-medium text-white/50 
                     hover:text-white transition-colors group"
          >
            Jump to Action Plan
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>
      </div>
    </section>
  );
}

export default ExecutiveSummary;
