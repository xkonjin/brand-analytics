/**
 * =============================================================================
 * Metric Bar Component - Apple Liquid Glass UI
 * =============================================================================
 * Horizontal bar chart with glassmorphism and score-based glows.
 * Shows score, benchmark line, and percentage fill with animations.
 * =============================================================================
 */

'use client';

import { motion } from 'framer-motion';
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
// Score-based gradient and glow for Glass UI
// -----------------------------------------------------------------------------
function getScoreGradient(score: number) {
  if (score >= 80) {
    return {
      gradient: 'from-emerald-400 to-emerald-500',
      glow: 'shadow-[0_0_15px_rgba(52,211,153,0.5)]',
      textColor: 'text-emerald-400',
    };
  }
  if (score >= 70) {
    return {
      gradient: 'from-green-400 to-green-500',
      glow: 'shadow-[0_0_15px_rgba(74,222,128,0.5)]',
      textColor: 'text-green-400',
    };
  }
  if (score >= 60) {
    return {
      gradient: 'from-yellow-400 to-yellow-500',
      glow: 'shadow-[0_0_15px_rgba(250,204,21,0.5)]',
      textColor: 'text-yellow-400',
    };
  }
  if (score >= 50) {
    return {
      gradient: 'from-orange-400 to-orange-500',
      glow: 'shadow-[0_0_15px_rgba(251,146,60,0.5)]',
      textColor: 'text-orange-400',
    };
  }
  return {
    gradient: 'from-red-400 to-red-500',
    glow: 'shadow-[0_0_15px_rgba(248,113,113,0.5)]',
    textColor: 'text-red-400',
  };
}

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

  // Get score-based styling
  const scoreStyle = getScoreGradient(score);

  // Calculate comparison to benchmark
  const diff = benchmark ? score - benchmark : 0;
  const comparisonLabel =
    diff > 0
      ? `+${diff.toFixed(0)} above avg`
      : diff < 0
      ? `${diff.toFixed(0)} below avg`
      : 'At average';

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Label row with score */}
      <div className="flex items-center justify-between">
        <span className={`font-medium text-white ${config.labelSize}`}>
          {label}
        </span>
        <div className="flex items-center gap-2">
          {/* Comparison to benchmark */}
          {showBenchmark && benchmark && (
            <span
              className={`text-xs ${
                diff > 0
                  ? 'text-emerald-400'
                  : diff < 0
                  ? 'text-orange-400'
                  : 'text-white/50'
              }`}
            >
              {comparisonLabel}
            </span>
          )}
          {/* Score value */}
          <span
            className={`font-bold tabular-nums ${config.scoreSize} ${scoreStyle.textColor}`}
          >
            {score.toFixed(0)}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="relative">
        {/* Background track - glass style */}
        <div
          className={`w-full bg-white/[0.08] rounded-full overflow-hidden ${config.height}`}
        >
          {/* Filled portion - animated with gradient and glow */}
          <motion.div
            className={`${config.height} rounded-full bg-gradient-to-r ${scoreStyle.gradient} ${scoreStyle.glow}`}
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
            className="absolute top-0 w-0.5 bg-white/50 rounded-full"
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
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="bg-white/10 backdrop-blur-sm text-white text-xs px-1.5 py-0.5 rounded whitespace-nowrap border border-white/10">
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
