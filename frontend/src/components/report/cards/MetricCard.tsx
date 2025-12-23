/**
 * =============================================================================
 * Metric Card Component - Apple Liquid Glass UI
 * =============================================================================
 * Displays a single KPI with glassmorphism styling and optional glow effects.
 * Used for showing key metrics in a grid layout.
 * =============================================================================
 */

'use client';

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface MetricCardProps {
  /** Metric label/title */
  label: string;
  /** Primary value to display */
  value: string | number;
  /** Optional unit suffix (e.g., '%', 'ms', 'pts') */
  unit?: string;
  /** Optional subtitle or description */
  subtitle?: string;
  /** Optional trend direction */
  trend?: 'up' | 'down' | 'stable';
  /** Optional trend value (e.g., '+5%') */
  trendValue?: string;
  /** Icon component (optional) */
  icon?: React.ReactNode;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Whether to animate on mount */
  animate?: boolean;
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function MetricCard({
  label,
  value,
  unit,
  subtitle,
  trend,
  trendValue,
  icon,
  size = 'md',
  animate = true,
  className = '',
}: MetricCardProps) {
  // Size-based styling
  const sizeStyles = {
    sm: {
      padding: 'p-3',
      valueSize: 'text-xl',
      labelSize: 'text-xs',
      iconSize: 'w-4 h-4',
    },
    md: {
      padding: 'p-4',
      valueSize: 'text-2xl',
      labelSize: 'text-sm',
      iconSize: 'w-5 h-5',
    },
    lg: {
      padding: 'p-5',
      valueSize: 'text-3xl',
      labelSize: 'text-base',
      iconSize: 'w-6 h-6',
    },
  };

  const styles = sizeStyles[size];

  // Trend icon and color for glass UI
  const TrendIcon =
    trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  const trendColor =
    trend === 'up'
      ? 'text-emerald-400'
      : trend === 'down'
      ? 'text-red-400'
      : 'text-white/40';

  const content = (
    <div
      className={`
        bg-white/[0.08] backdrop-blur-xl rounded-xl border border-white/[0.12]
        ${styles.padding}
        hover:bg-white/[0.12] transition-all duration-300
        group
        ${className}
      `}
    >
      {/* Header with icon and label */}
      <div className="flex items-center justify-between mb-2">
        <span className={`text-white/50 font-medium ${styles.labelSize}`}>
          {label}
        </span>
        {icon && <span className="text-white/40 group-hover:text-white/60 transition-colors">{icon}</span>}
      </div>

      {/* Value */}
      <div className="flex items-baseline gap-1">
        <span className={`font-bold text-white tabular-nums ${styles.valueSize}`}>
          {value}
        </span>
        {unit && (
          <span className="text-white/50 text-sm font-medium">{unit}</span>
        )}
      </div>

      {/* Subtitle or trend */}
      <div className="mt-1 flex items-center gap-2">
        {trend && (
          <div className={`flex items-center gap-1 ${trendColor}`}>
            <TrendIcon className="w-3.5 h-3.5" />
            {trendValue && <span className="text-xs font-medium">{trendValue}</span>}
          </div>
        )}
        {subtitle && (
          <span className="text-xs text-white/40">{subtitle}</span>
        )}
      </div>
    </div>
  );

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {content}
      </motion.div>
    );
  }

  return content;
}

// -----------------------------------------------------------------------------
// Metric Card Grid - for displaying multiple metrics
// -----------------------------------------------------------------------------
interface MetricCardGridProps {
  metrics: Array<{
    label: string;
    value: string | number;
    unit?: string;
    subtitle?: string;
    trend?: 'up' | 'down' | 'stable';
    trendValue?: string;
    icon?: React.ReactNode;
  }>;
  columns?: 2 | 3 | 4;
  size?: 'sm' | 'md' | 'lg';
  animate?: boolean;
  className?: string;
}

export function MetricCardGrid({
  metrics,
  columns = 4,
  size = 'md',
  animate = true,
  className = '',
}: MetricCardGridProps) {
  const gridCols = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div className={`grid ${gridCols[columns]} gap-4 ${className}`}>
      {metrics.map((metric, index) => (
        <motion.div
          key={metric.label}
          initial={animate ? { opacity: 0, y: 20 } : false}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05, duration: 0.4 }}
        >
          <MetricCard {...metric} size={size} animate={false} />
        </motion.div>
      ))}
    </div>
  );
}

export default MetricCard;
