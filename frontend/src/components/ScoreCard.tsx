// =============================================================================
// Score Card Component
// =============================================================================
// Displays a score with color-coded styling based on value.
// =============================================================================

interface ScoreCardProps {
  score: number
  size?: 'small' | 'medium' | 'large'
}

export function ScoreCard({ score, size = 'medium' }: ScoreCardProps) {
  // Determine color based on score
  const getColorClass = (score: number) => {
    if (score >= 80) return 'bg-emerald-100 text-emerald-700 border-emerald-200'
    if (score >= 60) return 'bg-amber-100 text-amber-700 border-amber-200'
    return 'bg-red-100 text-red-700 border-red-200'
  }

  // Size classes
  const sizeClasses = {
    small: 'w-12 h-12 text-lg',
    medium: 'w-16 h-16 text-2xl',
    large: 'w-24 h-24 text-4xl',
  }

  return (
    <div className={`
      inline-flex items-center justify-center rounded-full font-bold border-2
      ${sizeClasses[size]}
      ${getColorClass(score)}
    `}>
      {Math.round(score)}
    </div>
  )
}

