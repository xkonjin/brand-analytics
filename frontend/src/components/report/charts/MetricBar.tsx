/**
 * =============================================================================
 * Metric Bar Component
 * =============================================================================
 * Horizontal bar chart for comparing scores with benchmarks.
 * Shows score, benchmark line, and percentage fill with animations.
 * =============================================================================
 */

'use client';

import { motion } from 'framer-motion';
import { getScoreColor, getScoreClasses } from '@/lib/scoring';
import { getBenchmarkValue } from '@/lib/benchmarks';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface MetricBarProps {
  /** Label for the metric */
  label: string;
  /** Score value (0-100) */
  score: number;
  /** Module key for benchmark lookup (optional) */
  moduleKey?: string;
  /** Custom benchmark value (optional, overrides moduleKey lookup) */
  benchmark?: number;
  /** Whether to show the benchmark indicator */
  showBenchmark?: boolean;
  /** Whether to animate on mount */
  animate?: boolean;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Size configurations
// -----------------------------------------------------------------------------
const SIZES = {
  sm: {
    height: 'h-2',
    labelSize: 'text-xs',
    scoreSize: 'text-sm',
  },
  md: {
    height: 'h-3',
    labelSize: 'text-sm',
    scoreSize: 'text-base',
  },
  lg: {
    height: 'h-4',
    labelSize: 'text-base',
    scoreSize: 'text-lg',
  },
};

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function MetricBar({
  label,
  score,
  moduleKey,
  benchmark: customBenchmark,
  showBenchmark = true,
  animate = true,
  size = 'md',
  className = '',
}: MetricBarProps) {
  // Get benchmark value from module key or use custom value
  const benchmark =
    customBenchmark ?? (moduleKey ? getBenchmarkValue(moduleKey) : undefined);

  // Get size configuration
  const config = SIZES[size];

  // Get semantic colors
  const fillColor = getScoreColor(score);
  const scoreClasses = getScoreClasses(score);

  // Calculate comparison to benchmark
  const diff = benchmark ? score - benchmark : 0;
  const comparisonLabel =
    diff > 0
      ? `+${diff.toFixed(0)} above avg`
      : diff < 0
      ? `${diff.toFixed(0)} below avg`
      : 'At average';

  return (
    <div className={`space-y-1.5 ${className}`}>
      {/* Label row with score */}
      <div className="flex items-center justify-between">
        <span className={`font-medium text-slate-700 ${config.labelSize}`}>
          {label}
        </span>
        <div className="flex items-center gap-2">
          {/* Comparison to benchmark */}
          {showBenchmark && benchmark && (
            <span
              className={`text-xs ${
                diff > 0
                  ? 'text-emerald-600'
                  : diff < 0
                  ? 'text-orange-600'
                  : 'text-slate-500'
              }`}
            >
              {comparisonLabel}
            </span>
          )}
          {/* Score value */}
          <span
            className={`font-semibold tabular-nums ${config.scoreSize} ${scoreClasses.text}`}
          >
            {score.toFixed(0)}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="relative">
        {/* Background track */}
        <div
          className={`w-full bg-slate-100 rounded-full overflow-hidden ${config.height}`}
        >
          {/* Filled portion - animated */}
          <motion.div
            className={`${config.height} rounded-full`}
            style={{ backgroundColor: fillColor }}
            initial={{ width: animate ? '0%' : `${score}%` }}
            animate={{ width: `${score}%` }}
            transition={{
              duration: animate ? 1 : 0,
              ease: 'easeOut',
            }}
          />
        </div>

        {/* Benchmark indicator line */}
        {showBenchmark && benchmark && (
          <motion.div
            className="absolute top-0 w-0.5 bg-slate-400 rounded-full"
            style={{
              height: '100%',
              left: `${benchmark}%`,
              transform: 'translateX(-50%)',
            }}
            initial={{ opacity: 0, scaleY: 0 }}
            animate={{ opacity: 1, scaleY: 1 }}
            transition={{ delay: 0.5, duration: 0.3 }}
          >
            {/* Benchmark label tooltip */}
            <div className="absolute -top-5 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="bg-slate-700 text-white text-xs px-1.5 py-0.5 rounded whitespace-nowrap">
                Avg: {benchmark}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Metric Bar Group - for displaying multiple bars
// -----------------------------------------------------------------------------
interface MetricBarGroupProps {
  metrics: Array<{
    label: string;
    score: number;
    moduleKey?: string;
    benchmark?: number;
  }>;
  showBenchmarks?: boolean;
  animate?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function MetricBarGroup({
  metrics,
  showBenchmarks = true,
  animate = true,
  size = 'md',
  className = '',
}: MetricBarGroupProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      {metrics.map((metric, index) => (
        <motion.div
          key={metric.label}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{
            delay: animate ? index * 0.1 : 0,
            duration: 0.4,
          }}
        >
          <MetricBar
            label={metric.label}
            score={metric.score}
            moduleKey={metric.moduleKey}
            benchmark={metric.benchmark}
            showBenchmark={showBenchmarks}
            animate={animate}
            size={size}
          />
        </motion.div>
      ))}
    </div>
  );
}

export default MetricBar;

