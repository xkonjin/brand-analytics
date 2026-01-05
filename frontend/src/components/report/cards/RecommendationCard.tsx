/**
 * =============================================================================
 * Recommendation Card Component - Apple Liquid Glass UI
 * =============================================================================
 * Displays actionable recommendations with glassmorphism styling.
 * Highlights quick wins with special glow effects.
 * =============================================================================
 */

"use client";

import { motion } from "framer-motion";
import { Zap, Target, Clock } from "lucide-react";
import { isQuickWin, getPriorityScore } from "@/lib/frameworks";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface Recommendation {
  title: string;
  description: string;
  priority: "critical" | "high" | "medium" | "low";
  category: string;
  impact: "high" | "medium" | "low";
  effort: "high" | "medium" | "low";
}

interface RecommendationCardProps extends Recommendation {
  /** Card index for numbering */
  index?: number;
  /** Whether to show as expanded by default */
  expanded?: boolean;
  /** Whether to animate on mount */
  animate?: boolean;
  /** Animation delay */
  delay?: number;
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Glass UI Priority Classes
// -----------------------------------------------------------------------------
const getPriorityClasses = (priority: string) => {
  switch (priority) {
    case "critical":
      return {
        bg: "bg-red-500/20",
        text: "text-red-300",
        dot: "bg-red-400",
        glow: "shadow-[0_0_10px_rgba(239,68,68,0.3)]",
      };
    case "high":
      return {
        bg: "bg-orange-500/20",
        text: "text-orange-300",
        dot: "bg-orange-400",
        glow: "shadow-[0_0_10px_rgba(249,115,22,0.3)]",
      };
    case "medium":
      return {
        bg: "bg-yellow-500/20",
        text: "text-yellow-300",
        dot: "bg-yellow-400",
        glow: "",
      };
    default:
      return {
        bg: "bg-white/10",
        text: "text-white/70",
        dot: "bg-white/50",
        glow: "",
      };
  }
};

const getImpactClasses = (impact: string) => {
  switch (impact) {
    case "high":
      return "bg-emerald-500/20 text-emerald-300";
    case "medium":
      return "bg-blue-500/20 text-blue-300";
    default:
      return "bg-white/10 text-white/60";
  }
};

const getEffortClasses = (effort: string) => {
  switch (effort) {
    case "low":
      return "bg-emerald-500/20 text-emerald-300";
    case "medium":
      return "bg-yellow-500/20 text-yellow-300";
    default:
      return "bg-orange-500/20 text-orange-300";
  }
};

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function RecommendationCard({
  title,
  description,
  priority,
  category,
  impact,
  effort,
  index,
  expanded = false,
  animate = true,
  delay = 0,
  className = "",
}: RecommendationCardProps) {
  const quickWin = isQuickWin(impact, effort);
  const priorityClasses = getPriorityClasses(priority);

  const content = (
    <div
      className={`
        relative rounded-2xl border p-4 transition-all duration-300
        backdrop-blur-xl
        ${
          quickWin
            ? "bg-gradient-to-br from-emerald-500/15 to-emerald-500/5 border-emerald-500/30 shadow-[0_0_20px_rgba(52,211,153,0.1)]"
            : "bg-white/[0.08] border-white/[0.12] hover:bg-white/[0.12] hover:border-white/[0.18]"
        }
        ${className}
      `}
    >
      {/* Quick Win Badge */}
      {quickWin && (
        <div
          className="absolute -top-2.5 right-3 flex items-center gap-1.5 
                      bg-gradient-to-r from-emerald-500 to-emerald-400 
                      text-white text-xs font-semibold px-2.5 py-0.5 rounded-full 
                      shadow-[0_0_15px_rgba(52,211,153,0.4)]"
        >
          <Zap className="w-3 h-3" />
          Quick Win
        </div>
      )}

      {/* Header */}
      <div className="flex items-start gap-3">
        {/* Index number */}
        {index !== undefined && (
          <span
            className={`
            flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold
            ${
              quickWin
                ? "bg-emerald-500/20 text-emerald-300 shadow-[0_0_10px_rgba(52,211,153,0.2)]"
                : "bg-white/[0.1] text-white/70"
            }
          `}
          >
            {index}
          </span>
        )}

        <div className="flex-1 min-w-0">
          {/* Title */}
          <h4 className="font-semibold text-white text-sm pr-16">{title}</h4>

          {/* Description */}
          <p className="mt-1.5 text-xs text-white/60 leading-relaxed">
            {description}
          </p>

          {/* Tags */}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {/* Category */}
            <span className="inline-flex items-center gap-1 text-[10px] text-white/50 bg-white/[0.08] px-2 py-0.5 rounded-md border border-white/[0.08]">
              {category}
            </span>

            {/* Priority */}
            <span
              className={`inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-md ${priorityClasses.bg} ${priorityClasses.text} ${priorityClasses.glow}`}
            >
              <span className={`w-1 h-1 rounded-full ${priorityClasses.dot}`} />
              {priority}
            </span>

            {/* Impact */}
            <span
              className={`inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-md ${getImpactClasses(impact)}`}
            >
              <Target className="w-2.5 h-2.5" />
              {impact} impact
            </span>

            {/* Effort */}
            <span
              className={`inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-md ${getEffortClasses(effort)}`}
            >
              <Clock className="w-2.5 h-2.5" />
              {effort} effort
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay, duration: 0.4 }}
      >
        {content}
      </motion.div>
    );
  }

  return content;
}

// -----------------------------------------------------------------------------
// Recommendation List - sorted by priority score
// -----------------------------------------------------------------------------
interface RecommendationListProps {
  recommendations: Recommendation[];
  maxItems?: number;
  showQuickWinsFirst?: boolean;
  animate?: boolean;
  className?: string;
}

export function RecommendationList({
  recommendations,
  maxItems,
  showQuickWinsFirst = true,
  animate = true,
  className = "",
}: RecommendationListProps) {
  // Sort recommendations
  let sorted = [...recommendations];

  if (showQuickWinsFirst) {
    sorted = sorted.sort((a, b) => {
      const aQuickWin = isQuickWin(a.impact, a.effort);
      const bQuickWin = isQuickWin(b.impact, b.effort);

      // Quick wins first
      if (aQuickWin && !bQuickWin) return -1;
      if (!aQuickWin && bQuickWin) return 1;

      // Then by priority score
      return (
        getPriorityScore(b.impact, b.effort) -
        getPriorityScore(a.impact, a.effort)
      );
    });
  }

  // Limit items if specified
  const items = maxItems ? sorted.slice(0, maxItems) : sorted;

  return (
    <div className={`space-y-4 ${className}`}>
      {items.map((rec, index) => (
        <RecommendationCard
          key={`${rec.title}-${index}`}
          {...rec}
          index={index + 1}
          animate={animate}
          delay={index * 0.08}
        />
      ))}
    </div>
  );
}

export default RecommendationCard;
