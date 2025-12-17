/**
 * =============================================================================
 * Recommendation Card Component
 * =============================================================================
 * Displays actionable recommendations with priority, impact, and effort.
 * Highlights quick wins (high impact + low effort) prominently.
 * =============================================================================
 */

'use client';

import { motion } from 'framer-motion';
import {
  Zap,
  ArrowRight,
  Target,
  Clock,
  Lightbulb,
} from 'lucide-react';
import { isQuickWin, getPriorityScore } from '@/lib/frameworks';
import { getPriorityClasses, getImpactClasses, getEffortClasses } from '@/lib/scoring';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface Recommendation {
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
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
  className = '',
}: RecommendationCardProps) {
  const quickWin = isQuickWin(impact, effort);
  const priorityClasses = getPriorityClasses(priority);

  const content = (
    <div
      className={`
        relative rounded-xl border p-5 transition-all duration-200
        ${quickWin 
          ? 'bg-gradient-to-br from-emerald-50 to-white border-emerald-200 ring-1 ring-emerald-100' 
          : 'bg-white border-slate-200 hover:border-slate-300'
        }
        ${className}
      `}
    >
      {/* Quick Win Badge */}
      {quickWin && (
        <div className="absolute -top-2.5 right-4 flex items-center gap-1 bg-emerald-500 text-white text-xs font-medium px-2.5 py-0.5 rounded-full shadow-sm">
          <Zap className="w-3 h-3" />
          Quick Win
        </div>
      )}

      {/* Header */}
      <div className="flex items-start gap-3">
        {/* Index number */}
        {index !== undefined && (
          <span className={`
            flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-sm font-semibold
            ${quickWin ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}
          `}>
            {index}
          </span>
        )}

        <div className="flex-1 min-w-0">
          {/* Title */}
          <h4 className="font-semibold text-slate-900 pr-16">{title}</h4>

          {/* Description */}
          <p className="mt-2 text-sm text-slate-600 leading-relaxed">
            {description}
          </p>

          {/* Tags */}
          <div className="mt-4 flex flex-wrap items-center gap-2">
            {/* Category */}
            <span className="inline-flex items-center gap-1 text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded">
              {category}
            </span>

            {/* Priority */}
            <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded ${priorityClasses.bg} ${priorityClasses.text}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${priorityClasses.dot}`} />
              {priority}
            </span>

            {/* Impact */}
            <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded ${getImpactClasses(impact)}`}>
              <Target className="w-3 h-3" />
              {impact} impact
            </span>

            {/* Effort */}
            <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded ${getEffortClasses(effort)}`}>
              <Clock className="w-3 h-3" />
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
  className = '',
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
      return getPriorityScore(b.impact, b.effort) - getPriorityScore(a.impact, a.effort);
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

