/**
 * =============================================================================
 * Insight Card Component - Apple Liquid Glass UI
 * =============================================================================
 * Displays analysis findings with severity-coded glass styling and glows.
 * Used for showing issues, observations, and key insights.
 * =============================================================================
 */

'use client';

import { motion } from 'framer-motion';
import {
  AlertCircle,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
} from 'lucide-react';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info' | 'success';

interface InsightCardProps {
  /** Finding title */
  title: string;
  /** Detailed description */
  description: string;
  /** Severity level */
  severity: Severity;
  /** Optional additional data to display */
  data?: Record<string, string | number>;
  /** Whether card is expandable with more details */
  expandable?: boolean;
  /** Whether to animate on mount */
  animate?: boolean;
  /** Animation delay in seconds */
  delay?: number;
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Severity configurations for Glass UI
// -----------------------------------------------------------------------------
const SEVERITY_CONFIG = {
  critical: {
    icon: XCircle,
    bg: 'bg-red-500/10',
    border: 'border-l-red-500',
    borderGlow: 'shadow-[inset_4px_0_20px_-10px_rgba(239,68,68,0.5)]',
    iconColor: 'text-red-400',
    titleColor: 'text-red-300',
    textColor: 'text-red-200/80',
    dataBg: 'bg-red-500/10',
  },
  high: {
    icon: AlertCircle,
    bg: 'bg-orange-500/10',
    border: 'border-l-orange-500',
    borderGlow: 'shadow-[inset_4px_0_20px_-10px_rgba(249,115,22,0.5)]',
    iconColor: 'text-orange-400',
    titleColor: 'text-orange-300',
    textColor: 'text-orange-200/80',
    dataBg: 'bg-orange-500/10',
  },
  medium: {
    icon: AlertTriangle,
    bg: 'bg-yellow-500/10',
    border: 'border-l-yellow-500',
    borderGlow: 'shadow-[inset_4px_0_20px_-10px_rgba(234,179,8,0.5)]',
    iconColor: 'text-yellow-400',
    titleColor: 'text-yellow-300',
    textColor: 'text-yellow-200/80',
    dataBg: 'bg-yellow-500/10',
  },
  low: {
    icon: Info,
    bg: 'bg-white/[0.05]',
    border: 'border-l-white/30',
    borderGlow: '',
    iconColor: 'text-white/50',
    titleColor: 'text-white',
    textColor: 'text-white/60',
    dataBg: 'bg-white/[0.05]',
  },
  info: {
    icon: Info,
    bg: 'bg-blue-500/10',
    border: 'border-l-blue-500',
    borderGlow: 'shadow-[inset_4px_0_20px_-10px_rgba(59,130,246,0.5)]',
    iconColor: 'text-blue-400',
    titleColor: 'text-blue-300',
    textColor: 'text-blue-200/80',
    dataBg: 'bg-blue-500/10',
  },
  success: {
    icon: CheckCircle,
    bg: 'bg-emerald-500/10',
    border: 'border-l-emerald-500',
    borderGlow: 'shadow-[inset_4px_0_20px_-10px_rgba(52,211,153,0.5)]',
    iconColor: 'text-emerald-400',
    titleColor: 'text-emerald-300',
    textColor: 'text-emerald-200/80',
    dataBg: 'bg-emerald-500/10',
  },
};

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function InsightCard({
  title,
  description,
  severity,
  data,
  expandable = false,
  animate = true,
  delay = 0,
  className = '',
}: InsightCardProps) {
  const config = SEVERITY_CONFIG[severity];
  const Icon = config.icon;

  const content = (
    <div
      className={`
        rounded-xl border-l-4 p-4 backdrop-blur-xl
        border border-white/[0.08]
        ${config.bg} ${config.border} ${config.borderGlow}
        ${className}
      `}
    >
      {/* Header with icon and title */}
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${config.iconColor}`} />
        <div className="flex-1 min-w-0">
          <h4 className={`font-semibold ${config.titleColor}`}>{title}</h4>
          <p className={`mt-1 text-sm ${config.textColor}`}>{description}</p>

          {/* Optional data display */}
          {data && Object.keys(data).length > 0 && (
            <div className="mt-3 flex flex-wrap gap-3">
              {Object.entries(data).map(([key, value]) => (
                <div
                  key={key}
                  className={`text-xs ${config.dataBg} rounded px-2 py-1 border border-white/[0.08]`}
                >
                  <span className="text-white/50">{key}:</span>{' '}
                  <span className={`font-medium ${config.titleColor}`}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay, duration: 0.3 }}
      >
        {content}
      </motion.div>
    );
  }

  return content;
}

// -----------------------------------------------------------------------------
// Insight Card List - for displaying multiple findings
// -----------------------------------------------------------------------------
interface InsightCardListProps {
  insights: Array<{
    title: string;
    description: string;
    severity: Severity;
    data?: Record<string, string | number>;
  }>;
  animate?: boolean;
  className?: string;
}

export function InsightCardList({
  insights,
  animate = true,
  className = '',
}: InsightCardListProps) {
  // Sort by severity (critical first)
  const severityOrder: Record<Severity, number> = {
    critical: 0,
    high: 1,
    medium: 2,
    low: 3,
    info: 4,
    success: 5,
  };

  const sortedInsights = [...insights].sort(
    (a, b) => severityOrder[a.severity] - severityOrder[b.severity]
  );

  return (
    <div className={`space-y-3 ${className}`}>
      {sortedInsights.map((insight, index) => (
        <InsightCard
          key={`${insight.title}-${index}`}
          {...insight}
          animate={animate}
          delay={index * 0.1}
        />
      ))}
    </div>
  );
}

export default InsightCard;
