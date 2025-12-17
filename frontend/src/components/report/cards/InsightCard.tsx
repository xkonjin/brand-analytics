/**
 * =============================================================================
 * Insight Card Component
 * =============================================================================
 * Displays analysis findings with severity-coded styling.
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
import { getPriorityClasses } from '@/lib/scoring';

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
// Severity configurations
// -----------------------------------------------------------------------------
const SEVERITY_CONFIG = {
  critical: {
    icon: XCircle,
    bg: 'bg-red-50',
    border: 'border-l-red-500',
    iconColor: 'text-red-500',
    titleColor: 'text-red-900',
    textColor: 'text-red-700',
  },
  high: {
    icon: AlertCircle,
    bg: 'bg-orange-50',
    border: 'border-l-orange-500',
    iconColor: 'text-orange-500',
    titleColor: 'text-orange-900',
    textColor: 'text-orange-700',
  },
  medium: {
    icon: AlertTriangle,
    bg: 'bg-yellow-50',
    border: 'border-l-yellow-500',
    iconColor: 'text-yellow-500',
    titleColor: 'text-yellow-900',
    textColor: 'text-yellow-700',
  },
  low: {
    icon: Info,
    bg: 'bg-slate-50',
    border: 'border-l-slate-400',
    iconColor: 'text-slate-500',
    titleColor: 'text-slate-900',
    textColor: 'text-slate-600',
  },
  info: {
    icon: Info,
    bg: 'bg-blue-50',
    border: 'border-l-blue-500',
    iconColor: 'text-blue-500',
    titleColor: 'text-blue-900',
    textColor: 'text-blue-700',
  },
  success: {
    icon: CheckCircle,
    bg: 'bg-emerald-50',
    border: 'border-l-emerald-500',
    iconColor: 'text-emerald-500',
    titleColor: 'text-emerald-900',
    textColor: 'text-emerald-700',
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
        rounded-lg border-l-4 p-4
        ${config.bg} ${config.border}
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
                  className="text-xs bg-white/50 rounded px-2 py-1"
                >
                  <span className="text-slate-500">{key}:</span>{' '}
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

