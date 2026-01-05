// =============================================================================
// Score Gauge Component - Apple Liquid Glass UI
// =============================================================================
// Animated circular gauge with glowing effects based on score.
// =============================================================================

"use client";

import * as React from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { cn } from "@/lib/utils";

interface ScoreGaugeProps {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  label?: string;
  animated?: boolean;
  className?: string;
}

// Score color configuration
const getScoreColor = (score: number) => {
  if (score >= 80)
    return {
      primary: "#10b981", // emerald-500
      secondary: "#34d399", // emerald-400
      glow: "rgba(16, 185, 129, 0.15)",
      label: "Excellent",
      textClass: "text-emerald-400",
    };
  if (score >= 70)
    return {
      primary: "#22c55e", // green-500
      secondary: "#4ade80", // green-400
      glow: "rgba(34, 197, 94, 0.15)",
      label: "Good",
      textClass: "text-green-400",
    };
  if (score >= 60)
    return {
      primary: "#eab308", // yellow-500
      secondary: "#facc15", // yellow-400
      glow: "rgba(234, 179, 8, 0.15)",
      label: "Average",
      textClass: "text-yellow-400",
    };
  if (score >= 50)
    return {
      primary: "#f97316", // orange-500
      secondary: "#fb923c", // orange-400
      glow: "rgba(249, 115, 22, 0.15)",
      label: "Poor",
      textClass: "text-orange-400",
    };
  return {
    primary: "#ef4444", // red-500
    secondary: "#f87171", // red-400
    glow: "rgba(239, 68, 68, 0.15)",
    label: "Critical",
    textClass: "text-red-400",
  };
};

// Size configuration
const sizeConfig = {
  sm: { size: 80, stroke: 6, fontSize: "text-lg", labelSize: "text-xs" },
  md: { size: 120, stroke: 8, fontSize: "text-2xl", labelSize: "text-sm" },
  lg: { size: 160, stroke: 10, fontSize: "text-4xl", labelSize: "text-base" },
};

export function ScoreGauge({
  score,
  size = "md",
  showLabel = true,
  label,
  animated = true,
  className,
}: ScoreGaugeProps) {
  const config = sizeConfig[size];
  const colors = getScoreColor(score);

  const radius = (config.size - config.stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const center = config.size / 2;

  // Animated score value
  const springScore = useSpring(0, { stiffness: 50, damping: 20 });
  const displayScore = useTransform(springScore, (v) => Math.round(v));

  React.useEffect(() => {
    if (animated) {
      springScore.set(score);
    }
  }, [score, animated, springScore]);

  // Calculate stroke dashoffset for the progress
  const progress = score / 100;
  const strokeDashoffset = circumference * (1 - progress);

  return (
    <div
      className={cn("relative inline-flex flex-col items-center", className)}
    >
      {/* Glow effect behind the gauge */}
      <div
        className="absolute inset-0 rounded-full blur-2xl opacity-20"
        style={{
          background: `radial-gradient(circle, ${colors.glow} 0%, transparent 70%)`,
        }}
      />

      {/* SVG Gauge */}
      <svg
        width={config.size}
        height={config.size}
        className="relative transform -rotate-90"
      >
        {/* Gradient Definition */}
        <defs>
          <linearGradient
            id={`gauge-gradient-${score}`}
            x1="0%"
            y1="0%"
            x2="100%"
            y2="0%"
          >
            <stop offset="0%" stopColor={colors.primary} />
            <stop offset="100%" stopColor={colors.secondary} />
          </linearGradient>

          {/* Glow filter */}
          <filter
            id={`gauge-glow-${score}`}
            x="-50%"
            y="-50%"
            width="200%"
            height="200%"
          >
            <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Background track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.05)"
          strokeWidth={config.stroke}
          strokeLinecap="round"
        />

        {/* Progress arc with glow */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={`url(#gauge-gradient-${score})`}
          strokeWidth={config.stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{
            strokeDashoffset: animated ? strokeDashoffset : circumference,
          }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          filter={`url(#gauge-glow-${score})`}
          style={{
            filter: `drop-shadow(0 0 4px ${colors.glow})`,
          }}
        />

        {/* Progress arc with glow */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={`url(#gauge-gradient-${score})`}
          strokeWidth={config.stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{
            strokeDashoffset: animated ? strokeDashoffset : circumference,
          }}
          transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
          filter={`url(#gauge-glow-${score})`}
          style={{
            filter: `drop-shadow(0 0 8px ${colors.glow})`,
          }}
        />
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className={cn(
            "font-bold tabular-nums text-white",
            config.fontSize,
            "drop-shadow-[0_2px_4px_rgba(0,0,0,0.3)]",
          )}
          style={{ fontFamily: "var(--font-display)" }}
        >
          {animated ? <motion.span>{displayScore}</motion.span> : score}
        </motion.span>

        {showLabel && (
          <span
            className={cn("font-medium", config.labelSize, colors.textClass)}
          >
            {label || colors.label}
          </span>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Mini Score Badge
// =============================================================================

interface ScoreBadgeProps {
  score: number;
  className?: string;
}

export function ScoreBadge({ score, className }: ScoreBadgeProps) {
  const colors = getScoreColor(score);

  return (
    <span
      className={cn(
        "inline-flex items-center justify-center",
        "px-3 py-1 rounded-full text-sm font-semibold",
        "backdrop-blur-sm border",
        className,
      )}
      style={{
        backgroundColor: `${colors.primary}20`,
        borderColor: `${colors.primary}40`,
        color: colors.secondary,
        boxShadow: `0 0 15px ${colors.glow}`,
      }}
    >
      {score}
    </span>
  );
}

// =============================================================================
// Score Bar (Horizontal)
// =============================================================================

interface ScoreBarProps {
  score: number;
  label?: string;
  showValue?: boolean;
  animated?: boolean;
  className?: string;
}

export function ScoreBar({
  score,
  label,
  showValue = true,
  animated = true,
  className,
}: ScoreBarProps) {
  const colors = getScoreColor(score);

  return (
    <div className={cn("w-full", className)}>
      {(label || showValue) && (
        <div className="flex justify-between items-center mb-2">
          {label && (
            <span className="text-sm font-medium text-white/80">{label}</span>
          )}
          {showValue && (
            <span className={cn("text-sm font-semibold", colors.textClass)}>
              {score}/100
            </span>
          )}
        </div>
      )}

      <div className="h-2 bg-white/[0.1] rounded-full overflow-hidden backdrop-blur-sm">
        <motion.div
          className="h-full rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: animated ? 0.8 : 0, ease: [0.16, 1, 0.3, 1] }}
          style={{
            background: `linear-gradient(90deg, ${colors.primary}, ${colors.secondary})`,
            boxShadow: `0 0 10px ${colors.glow}`,
          }}
        />
      </div>
    </div>
  );
}

// =============================================================================
// Module Score Card
// =============================================================================

interface ModuleScoreProps {
  name: string;
  score: number;
  icon?: React.ReactNode;
  description?: string;
  className?: string;
}

export function ModuleScore({
  name,
  score,
  icon,
  description,
  className,
}: ModuleScoreProps) {
  const colors = getScoreColor(score);

  return (
    <div
      className={cn(
        "p-4 rounded-xl",
        "bg-white/[0.06] backdrop-blur-xl",
        "border border-white/[0.1]",
        "transition-all duration-300",
        "hover:bg-white/[0.1] hover:border-white/[0.2]",
        "hover:-translate-y-0.5",
        className,
      )}
      style={{
        boxShadow: `0 4px 20px rgba(0,0,0,0.2), 0 0 20px ${colors.glow.replace("0.15", "0.05")}`,
      }}
    >
      <div className="flex items-center gap-3">
        {icon && (
          <div
            className="p-2 rounded-lg"
            style={{ backgroundColor: `${colors.primary}20` }}
          >
            <div style={{ color: colors.secondary }}>{icon}</div>
          </div>
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h4 className="text-sm font-medium text-white truncate">{name}</h4>
            <ScoreBadge score={score} />
          </div>

          {description && (
            <p className="text-xs text-white/50 mt-1 truncate">{description}</p>
          )}
        </div>
      </div>

      <div className="mt-3">
        <ScoreBar score={score} showValue={false} />
      </div>
    </div>
  );
}

export default ScoreGauge;
