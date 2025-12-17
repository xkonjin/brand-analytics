/**
 * =============================================================================
 * Scoring Utilities
 * =============================================================================
 * Score interpretation logic based on marketing industry standards.
 * Provides consistent grading, color coding, and score categorization.
 * =============================================================================
 */

/**
 * Grade scale based on a16z and industry standards
 * Maps numeric scores to letter grades with interpretations
 */
export type Grade = 'A+' | 'A' | 'B' | 'C' | 'D' | 'F';

export interface GradeInfo {
  grade: Grade;
  label: string;
  description: string;
  color: string;
  bgColor: string;
  borderColor: string;
}

/**
 * Get letter grade and interpretation from a numeric score
 * 
 * Grade Scale:
 * - A+ (90-100): Exceptional - Industry leader
 * - A  (80-89):  Excellent - Strong foundation
 * - B  (70-79):  Good - Above average
 * - C  (60-69):  Average - Room for improvement
 * - D  (50-59):  Below average - Needs attention
 * - F  (0-49):   Critical - Immediate action needed
 */
export function getGradeInfo(score: number): GradeInfo {
  if (score >= 90) {
    return {
      grade: 'A+',
      label: 'Exceptional',
      description: 'Industry leader with outstanding brand presence',
      color: 'text-emerald-700',
      bgColor: 'bg-emerald-50',
      borderColor: 'border-emerald-200',
    };
  }
  if (score >= 80) {
    return {
      grade: 'A',
      label: 'Excellent',
      description: 'Strong foundation with minor optimization opportunities',
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
      borderColor: 'border-emerald-200',
    };
  }
  if (score >= 70) {
    return {
      grade: 'B',
      label: 'Good',
      description: 'Above average performance with growth potential',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
    };
  }
  if (score >= 60) {
    return {
      grade: 'C',
      label: 'Average',
      description: 'Meets basic standards but has room for improvement',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
    };
  }
  if (score >= 50) {
    return {
      grade: 'D',
      label: 'Below Average',
      description: 'Needs attention in multiple areas',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
    };
  }
  return {
    grade: 'F',
    label: 'Critical',
    description: 'Requires immediate action to address fundamental issues',
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
  };
}

/**
 * Get semantic color for a score value
 * Used for charts, badges, and visual indicators
 */
export function getScoreColor(score: number): string {
  if (score >= 80) return '#10b981'; // emerald-500
  if (score >= 70) return '#22c55e'; // green-500
  if (score >= 60) return '#eab308'; // yellow-500
  if (score >= 50) return '#f97316'; // orange-500
  return '#ef4444'; // red-500
}

/**
 * Get Tailwind color classes for a score
 */
export function getScoreClasses(score: number): {
  text: string;
  bg: string;
  border: string;
  ring: string;
} {
  if (score >= 80) {
    return {
      text: 'text-emerald-700',
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      ring: 'ring-emerald-500',
    };
  }
  if (score >= 70) {
    return {
      text: 'text-green-700',
      bg: 'bg-green-50',
      border: 'border-green-200',
      ring: 'ring-green-500',
    };
  }
  if (score >= 60) {
    return {
      text: 'text-yellow-700',
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      ring: 'ring-yellow-500',
    };
  }
  if (score >= 50) {
    return {
      text: 'text-orange-700',
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      ring: 'ring-orange-500',
    };
  }
  return {
    text: 'text-red-700',
    bg: 'bg-red-50',
    border: 'border-red-200',
    ring: 'ring-red-500',
  };
}

/**
 * Get priority color classes
 */
export function getPriorityClasses(priority: string): {
  text: string;
  bg: string;
  border: string;
  dot: string;
} {
  switch (priority.toLowerCase()) {
    case 'critical':
      return {
        text: 'text-red-800',
        bg: 'bg-red-100',
        border: 'border-red-200',
        dot: 'bg-red-500',
      };
    case 'high':
      return {
        text: 'text-orange-800',
        bg: 'bg-orange-100',
        border: 'border-orange-200',
        dot: 'bg-orange-500',
      };
    case 'medium':
      return {
        text: 'text-yellow-800',
        bg: 'bg-yellow-100',
        border: 'border-yellow-200',
        dot: 'bg-yellow-500',
      };
    case 'low':
    default:
      return {
        text: 'text-slate-700',
        bg: 'bg-slate-100',
        border: 'border-slate-200',
        dot: 'bg-slate-500',
      };
  }
}

/**
 * Get impact/effort color classes
 */
export function getImpactClasses(impact: string): string {
  switch (impact.toLowerCase()) {
    case 'high':
      return 'bg-emerald-100 text-emerald-800';
    case 'medium':
      return 'bg-blue-100 text-blue-800';
    case 'low':
    default:
      return 'bg-slate-100 text-slate-700';
  }
}

export function getEffortClasses(effort: string): string {
  switch (effort.toLowerCase()) {
    case 'low':
      return 'bg-emerald-100 text-emerald-800';
    case 'medium':
      return 'bg-blue-100 text-blue-800';
    case 'high':
    default:
      return 'bg-orange-100 text-orange-700';
  }
}

/**
 * Format score for display (round to nearest integer)
 */
export function formatScore(score: number): number {
  return Math.round(score);
}

/**
 * Calculate percentage change between two scores
 */
export function calculateChange(current: number, previous: number): {
  value: number;
  direction: 'up' | 'down' | 'stable';
  label: string;
} {
  const change = current - previous;
  const direction = change > 0 ? 'up' : change < 0 ? 'down' : 'stable';
  const label = change > 0 ? `+${change.toFixed(1)}` : change.toFixed(1);
  
  return { value: change, direction, label };
}

/**
 * Determine if a score is considered "good" (above average)
 */
export function isGoodScore(score: number): boolean {
  return score >= 70;
}

/**
 * Determine if a score needs attention (below average)
 */
export function needsAttention(score: number): boolean {
  return score < 60;
}

/**
 * Determine if a score is critical
 */
export function isCritical(score: number): boolean {
  return score < 50;
}

