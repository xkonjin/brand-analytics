/**
 * =============================================================================
 * Score Gauge Component - Apple Liquid Glass UI
 * =============================================================================
 * Animated circular gauge with glassmorphism and score-based glow effects.
 * Uses SVG for precise rendering and Framer Motion for animations.
 * =============================================================================
 */

'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getGradeInfo, formatScore } from '@/lib/scoring';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface ScoreGaugeProps {
  /** Score value (0-100) */
  score: number;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Whether to show the grade label */
  showGrade?: boolean;
  /** Whether to show the score label */
  showLabel?: boolean;
  /** Custom label text */
  label?: string;
  /** Whether to animate on mount */
  animate?: boolean;
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Size configurations
// -----------------------------------------------------------------------------
const SIZES = {
  sm: {
    size: 80,
    strokeWidth: 6,
    fontSize: 'text-xl',
    gradeSize: 'text-xs',
    labelSize: 'text-xs',
  },
  md: {
    size: 120,
    strokeWidth: 8,
    fontSize: 'text-3xl',
    gradeSize: 'text-sm',
    labelSize: 'text-sm',
  },
  lg: {
    size: 160,
    strokeWidth: 10,
    fontSize: 'text-4xl',
    gradeSize: 'text-base',
    labelSize: 'text-sm',
  },
  xl: {
    size: 200,
    strokeWidth: 12,
    fontSize: 'text-5xl',
    gradeSize: 'text-lg',
    labelSize: 'text-base',
  },
};

// -----------------------------------------------------------------------------
// Score-based colors with glow for Glass UI
// -----------------------------------------------------------------------------
function getScoreColorConfig(score: number) {
  if (score >= 80) {
    return {
      color: '#34d399', // emerald-400
      glow: 'drop-shadow(0 0 20px rgba(52, 211, 153, 0.6))',
      textColor: 'text-emerald-400',
    };
  }
  if (score >= 70) {
    return {
      color: '#4ade80', // green-400
      glow: 'drop-shadow(0 0 20px rgba(74, 222, 128, 0.6))',
      textColor: 'text-green-400',
    };
  }
  if (score >= 60) {
    return {
      color: '#facc15', // yellow-400
      glow: 'drop-shadow(0 0 20px rgba(250, 204, 21, 0.6))',
      textColor: 'text-yellow-400',
    };
  }
  if (score >= 50) {
    return {
      color: '#fb923c', // orange-400
      glow: 'drop-shadow(0 0 20px rgba(251, 146, 60, 0.6))',
      textColor: 'text-orange-400',
    };
  }
  return {
    color: '#f87171', // red-400
    glow: 'drop-shadow(0 0 20px rgba(248, 113, 113, 0.6))',
    textColor: 'text-red-400',
  };
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ScoreGauge({
  score,
  size = 'md',
  showGrade = true,
  showLabel = false,
  label,
  animate = true,
  className = '',
}: ScoreGaugeProps) {
  // Animated score value for number counter effect
  const [displayScore, setDisplayScore] = useState(animate ? 0 : score);

  // Get size configuration
  const config = SIZES[size];
  const radius = (config.size - config.strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const center = config.size / 2;

  // Calculate stroke offset based on score (0-100 maps to full circle)
  const strokeOffset = circumference - (score / 100) * circumference;

  // Get semantic color and grade info
  const colorConfig = getScoreColorConfig(score);
  const gradeInfo = getGradeInfo(score);

  // Animate score counter on mount
  useEffect(() => {
    if (!animate) {
      setDisplayScore(score);
      return;
    }

    const duration = 1500; // 1.5 seconds
    const steps = 60;
    const increment = score / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(current);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [score, animate]);

  return (
    <div
      className={`relative inline-flex flex-col items-center ${className}`}
      style={{ width: config.size, height: config.size }}
    >
      {/* SVG Gauge with glow */}
      <svg
        width={config.size}
        height={config.size}
        className="transform -rotate-90"
        style={{ filter: colorConfig.glow }}
      >
        {/* Background circle - glass style */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={config.strokeWidth}
        />

        {/* Progress arc - animated with glow */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={colorConfig.color}
          strokeWidth={config.strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: strokeOffset }}
          transition={{
            duration: animate ? 1.5 : 0,
            ease: 'easeOut',
          }}
        />
      </svg>

      {/* Center content - score and grade */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {/* Score number */}
        <motion.span
          className={`font-bold text-white tabular-nums ${config.fontSize}`}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          {formatScore(displayScore)}
        </motion.span>

        {/* Grade badge */}
        {showGrade && (
          <motion.span
            className={`font-semibold ${config.gradeSize} ${colorConfig.textColor}`}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.3 }}
          >
            {gradeInfo.grade}
          </motion.span>
        )}

        {/* Custom label */}
        {showLabel && label && (
          <motion.span
            className={`text-white/50 mt-1 ${config.labelSize}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.3 }}
          >
            {label}
          </motion.span>
        )}
      </div>
    </div>
  );
}

export default ScoreGauge;
