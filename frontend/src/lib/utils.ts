import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// =============================================================================
// Score Utilities
// =============================================================================

export type ScoreLevel = "excellent" | "good" | "average" | "poor" | "critical";

/**
 * Get the score level based on numeric score
 */
export function getScoreLevel(score: number): ScoreLevel {
  if (score >= 80) return "excellent";
  if (score >= 70) return "good";
  if (score >= 60) return "average";
  if (score >= 50) return "poor";
  return "critical";
}

/**
 * Get Tailwind classes for score-based styling
 * Returns border, text, and glow classes
 */
export function getScoreClasses(score: number): {
  border: string;
  text: string;
  bg: string;
  glow: string;
} {
  const level = getScoreLevel(score);

  const classes = {
    excellent: {
      border: "border-emerald-500/30",
      text: "text-emerald-400",
      bg: "bg-emerald-500/10",
      glow: "shadow-[0_0_20px_rgba(16,185,129,0.15)]",
    },
    good: {
      border: "border-green-500/30",
      text: "text-green-400",
      bg: "bg-green-500/10",
      glow: "shadow-[0_0_20px_rgba(34,197,94,0.15)]",
    },
    average: {
      border: "border-yellow-500/30",
      text: "text-yellow-400",
      bg: "bg-yellow-500/10",
      glow: "shadow-[0_0_20px_rgba(234,179,8,0.15)]",
    },
    poor: {
      border: "border-orange-500/30",
      text: "text-orange-400",
      bg: "bg-orange-500/10",
      glow: "shadow-[0_0_20px_rgba(249,115,22,0.15)]",
    },
    critical: {
      border: "border-red-500/30",
      text: "text-red-400",
      bg: "bg-red-500/10",
      glow: "shadow-[0_0_20px_rgba(239,68,68,0.15)]",
    },
  };

  return classes[level];
}

/**
 * Get the score label text
 */
export function getScoreLabel(score: number): string {
  const level = getScoreLevel(score);

  const labels = {
    excellent: "Excellent",
    good: "Good",
    average: "Average",
    poor: "Poor",
    critical: "Critical",
  };

  return labels[level];
}

/**
 * Get score color for charts/visualizations
 */
export function getScoreColor(score: number): {
  primary: string;
  secondary: string;
  glow: string;
} {
  const level = getScoreLevel(score);

  const colors = {
    excellent: {
      primary: "#10b981",
      secondary: "#34d399",
      glow: "rgba(16, 185, 129, 0.4)",
    },
    good: {
      primary: "#22c55e",
      secondary: "#4ade80",
      glow: "rgba(34, 197, 94, 0.4)",
    },
    average: {
      primary: "#eab308",
      secondary: "#facc15",
      glow: "rgba(234, 179, 8, 0.4)",
    },
    poor: {
      primary: "#f97316",
      secondary: "#fb923c",
      glow: "rgba(249, 115, 22, 0.4)",
    },
    critical: {
      primary: "#ef4444",
      secondary: "#f87171",
      glow: "rgba(239, 68, 68, 0.4)",
    },
  };

  return colors[level];
}

// =============================================================================
// Format Utilities
// =============================================================================

/**
 * Format a number with thousands separators
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat("en-US").format(num);
}

/**
 * Format a number as compact (1.2K, 3.4M, etc.)
 */
export function formatCompact(num: number): string {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(num);
}

/**
 * Format milliseconds as seconds
 */
export function formatMs(ms: number | undefined | null): string {
  if (ms === undefined || ms === null) return "N/A";
  return `${(ms / 1000).toFixed(1)}s`;
}

/**
 * Format a percentage
 */
export function formatPercent(value: number, decimals = 0): string {
  return `${value.toFixed(decimals)}%`;
}
