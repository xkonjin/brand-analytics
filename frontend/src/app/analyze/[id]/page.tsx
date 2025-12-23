// =============================================================================
// Analysis Progress Page - Apple Liquid Glass UI
// =============================================================================
// Beautiful real-time progress tracking with glass effects and animations.
// =============================================================================

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CheckCircle2, 
  Circle, 
  Loader2, 
  XCircle,
  BarChart3,
  Search,
  Users,
  Target,
  Brain,
  FileText,
  UserCircle,
  TrendingUp,
  Sparkles
} from 'lucide-react'
import { SimpleNavbar } from '@/components/glass/GlassNavbar'
import { Button } from '@/components/ui/button'
import { GlassCard } from '@/components/ui/card'
import { cn } from '@/lib/utils'

// =============================================================================
// Module Configuration
// =============================================================================

interface ModuleConfig {
  name: string
  icon: React.ElementType
  gradient: string
  glowColor: string
}

const MODULE_CONFIG: Record<string, ModuleConfig> = {
  seo: { 
    name: 'SEO Performance', 
    icon: Search,
    gradient: 'from-blue-500 to-blue-600',
    glowColor: 'rgba(59, 130, 246, 0.5)',
  },
  social_media: { 
    name: 'Social Media', 
    icon: Users,
    gradient: 'from-pink-500 to-rose-600',
    glowColor: 'rgba(236, 72, 153, 0.5)',
  },
  brand_messaging: { 
    name: 'Brand Messaging', 
    icon: Target,
    gradient: 'from-purple-500 to-purple-600',
    glowColor: 'rgba(139, 92, 246, 0.5)',
  },
  website_ux: { 
    name: 'Website UX', 
    icon: BarChart3,
    gradient: 'from-orange-500 to-orange-600',
    glowColor: 'rgba(249, 115, 22, 0.5)',
  },
  ai_discoverability: { 
    name: 'AI Discoverability', 
    icon: Brain,
    gradient: 'from-emerald-500 to-emerald-600',
    glowColor: 'rgba(16, 185, 129, 0.5)',
  },
  content: { 
    name: 'Content Analysis', 
    icon: FileText,
    gradient: 'from-cyan-500 to-cyan-600',
    glowColor: 'rgba(6, 182, 212, 0.5)',
  },
  team_presence: { 
    name: 'Team Presence', 
    icon: UserCircle,
    gradient: 'from-indigo-500 to-indigo-600',
    glowColor: 'rgba(99, 102, 241, 0.5)',
  },
  channel_fit: { 
    name: 'Channel Fit', 
    icon: TrendingUp,
    gradient: 'from-amber-500 to-amber-600',
    glowColor: 'rgba(245, 158, 11, 0.5)',
  },
  scorecard: { 
    name: 'Generating Report', 
    icon: Sparkles,
    gradient: 'from-violet-500 to-fuchsia-600',
    glowColor: 'rgba(167, 139, 250, 0.5)',
  },
}

// =============================================================================
// Types
// =============================================================================

interface AnalysisProgress {
  id: string
  status: string
  modules: Record<string, string>
  completion_percentage: number
}

// =============================================================================
// Analysis Progress Page Component
// =============================================================================

export default function AnalyzePage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const { id } = params

  const { data, isLoading, error } = useQuery<AnalysisProgress>({
    queryKey: ['analysis-progress', id],
    queryFn: async () => {
      const res = await fetch(`/api/v1/analysis/${id}/progress`)
      if (!res.ok) throw new Error('Failed to fetch progress')
      return res.json()
    },
    refetchInterval: (query) => {
      const data = query.state.data
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false
      }
      return 2000
    },
  })

  // Redirect to report when completed
  useEffect(() => {
    if (data?.status === 'completed') {
      setTimeout(() => {
        router.push(`/report/${id}`)
      }, 1500)
    }
  }, [data?.status, id, router])

  // Error state
  if (error) {
    return (
      <main className="min-h-screen">
        <SimpleNavbar backHref="/" />
        <div className="min-h-[80vh] flex items-center justify-center p-4">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center"
          >
            <div className="relative inline-block mb-6">
              <div className="absolute inset-0 bg-red-500/30 rounded-full blur-2xl" />
              <div className="relative bg-white/[0.1] backdrop-blur-xl p-6 rounded-full border border-red-500/30">
                <XCircle className="w-12 h-12 text-red-400" />
              </div>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Analysis Not Found</h1>
            <p className="text-white/60 mb-8 max-w-md">
              The analysis you&apos;re looking for doesn&apos;t exist or has expired.
            </p>
            <Button onClick={() => router.push('/')} variant="default">
              Start New Analysis
            </Button>
          </motion.div>
        </div>
      </main>
    )
  }

  const completionPercentage = data?.completion_percentage ?? 0
  const isCompleted = data?.status === 'completed'
  const isFailed = data?.status === 'failed'

  return (
    <main className="min-h-screen">
      <SimpleNavbar backHref="/" title="Analyzing..." />
      
      <div className="min-h-[80vh] flex items-center justify-center p-4 pt-24">
        <div className="w-full max-w-lg">
          {/* Header */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-10"
          >
            {/* Animated Logo */}
            <div className="relative inline-flex items-center justify-center w-24 h-24 mb-6">
              {/* Glow effect */}
              <motion.div 
                className="absolute inset-0 rounded-full blur-2xl"
                style={{ 
                  background: isCompleted 
                    ? 'rgba(16, 185, 129, 0.3)' 
                    : 'rgba(59, 130, 246, 0.3)' 
                }}
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.5, 0.3],
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "easeInOut" 
                }}
              />
              
              {/* Icon container */}
              <motion.div 
                className={cn(
                  'relative z-10 flex items-center justify-center w-20 h-20',
                  'rounded-2xl backdrop-blur-xl border',
                  isCompleted 
                    ? 'bg-emerald-500/20 border-emerald-500/30' 
                    : 'bg-white/[0.1] border-white/[0.2]'
                )}
              >
                {isCompleted ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 200 }}
                  >
                    <CheckCircle2 className="w-10 h-10 text-emerald-400" />
                  </motion.div>
                ) : (
                  <Loader2 className="w-10 h-10 text-blue-400 animate-spin" />
                )}
              </motion.div>
            </div>
            
            <motion.h1 
              className="text-2xl md:text-3xl font-bold text-white mb-3"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              {isCompleted ? 'Analysis Complete!' : 'Analyzing Your Brand'}
            </motion.h1>
            <p className="text-white/60">
              {isCompleted 
                ? 'Redirecting to your report...' 
                : 'This usually takes 1-2 minutes. Please don\'t close this page.'}
            </p>
          </motion.div>

          {/* Progress bar */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-8"
          >
            <div className="flex justify-between text-sm mb-3">
              <span className="text-white/60">Progress</span>
              <span className="font-semibold text-blue-400 tabular-nums">
                {completionPercentage}%
              </span>
            </div>
            <div className="h-3 bg-white/[0.1] rounded-full overflow-hidden backdrop-blur-sm">
              <motion.div
                className="h-full rounded-full relative overflow-hidden"
                initial={{ width: 0 }}
                animate={{ width: `${completionPercentage}%` }}
                transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                style={{
                  background: isCompleted 
                    ? 'linear-gradient(90deg, #10b981, #34d399)' 
                    : 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
                  boxShadow: isCompleted 
                    ? '0 0 20px rgba(16, 185, 129, 0.5)' 
                    : '0 0 20px rgba(59, 130, 246, 0.5)',
                }}
              >
                {/* Shimmer effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                />
              </motion.div>
            </div>
          </motion.div>

          {/* Module status list */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <GlassCard className="p-6">
              <h2 className="text-sm font-medium text-white/50 uppercase tracking-wide mb-5">
                Analysis Modules
              </h2>
              <div className="space-y-3">
                {Object.entries(MODULE_CONFIG).map(([key, config], index) => {
                  const status = data?.modules?.[key] ?? 'pending'
                  return (
                    <motion.div
                      key={key}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3 + index * 0.05 }}
                    >
                      <ModuleStatus
                        config={config}
                        status={status}
                      />
                    </motion.div>
                  )
                })}
              </div>
            </GlassCard>
          </motion.div>

          {/* Failed state */}
          <AnimatePresence>
            {isFailed && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="mt-6"
              >
                <GlassCard className="p-6 border-red-500/30">
                  <div className="text-center">
                    <p className="text-red-400 mb-4">
                      Analysis failed. Please try again or contact support.
                    </p>
                    <Button onClick={() => router.push('/')} variant="destructive">
                      Try Again
                    </Button>
                  </div>
                </GlassCard>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </main>
  )
}

// =============================================================================
// Module Status Component
// =============================================================================

interface ModuleStatusProps {
  config: ModuleConfig
  status: string
}

function ModuleStatus({ config, status }: ModuleStatusProps) {
  const Icon = config.icon
  const isActive = status === 'running'
  const isComplete = status === 'completed'
  const isFailed = status === 'failed'
  const isPending = status === 'pending'

  return (
    <div className={cn(
      'flex items-center gap-4 p-3 rounded-xl transition-all duration-300',
      isActive && 'bg-white/[0.05]',
      isComplete && 'bg-white/[0.03]',
    )}>
      {/* Icon */}
      <div className={cn(
        'relative flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center',
        'transition-all duration-300',
        isPending && 'bg-white/[0.05]',
        isActive && `bg-gradient-to-br ${config.gradient}`,
        isComplete && 'bg-emerald-500/20',
        isFailed && 'bg-red-500/20',
      )}>
        {/* Glow for active state */}
        {isActive && (
          <motion.div
            className="absolute inset-0 rounded-lg blur-md"
            style={{ background: config.glowColor }}
            animate={{ opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
        
        <div className="relative z-10">
          {isComplete && (
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          )}
          {isActive && (
            <Icon className="w-5 h-5 text-white animate-pulse" />
          )}
          {isFailed && (
            <XCircle className="w-5 h-5 text-red-400" />
          )}
          {isPending && (
            <Icon className="w-5 h-5 text-white/30" />
          )}
        </div>
      </div>

      {/* Name */}
      <span className={cn(
        'flex-1 text-sm font-medium transition-colors duration-300',
        isPending && 'text-white/40',
        isActive && 'text-white',
        isComplete && 'text-white/70',
        isFailed && 'text-red-400',
      )}>
        {config.name}
      </span>

      {/* Status indicator */}
      <span className={cn(
        'text-xs px-2.5 py-1 rounded-full font-medium',
        'backdrop-blur-sm border transition-all duration-300',
        isPending && 'bg-white/[0.05] border-white/[0.1] text-white/40',
        isActive && 'bg-blue-500/20 border-blue-500/30 text-blue-400',
        isComplete && 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400',
        isFailed && 'bg-red-500/20 border-red-500/30 text-red-400',
      )}>
        {isActive ? (
          <span className="flex items-center gap-1.5">
            <motion.span
              className="w-1.5 h-1.5 rounded-full bg-blue-400"
              animate={{ scale: [1, 1.5, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
            Analyzing
          </span>
        ) : (
          status.charAt(0).toUpperCase() + status.slice(1)
        )}
      </span>
    </div>
  )
}
