// =============================================================================
// Home Page - Apple Liquid Glass UI with x402 Payment Integration
// =============================================================================
// Beautiful landing page with glass morphism, ambient effects, and animations.
// Includes x402 payment gateway for gating brand analysis.
// =============================================================================

'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowRight, 
  Sparkles, 
  BarChart3, 
  Target, 
  Zap,
  Search,
  TrendingUp,
  Users,
  Globe,
  Shield,
  Brain
} from 'lucide-react'
import { GlassNavbar } from '@/components/glass/GlassNavbar'
import { PaymentModal } from '@/components/PaymentModal'
import { usePayment } from '@/lib/usePayment'
import { Button } from '@/components/ui/button'
import { GlassCard } from '@/components/ui/card'
import { cn } from '@/lib/utils'

// =============================================================================
// Home Page Component
// =============================================================================

export default function HomePage() {
  const router = useRouter()
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  
  // Payment state
  const [showPayment, setShowPayment] = useState(false)
  const [invoiceData, setInvoiceData] = useState<{
    invoice_id: string
    amount: string
    token: string
    network: string
    merchant_address: string
  } | null>(null)
  usePayment()

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (!url.trim()) {
      setError('Please enter a website URL')
      return
    }

    let normalizedUrl = url.trim()
    if (!normalizedUrl.startsWith('http://') && !normalizedUrl.startsWith('https://')) {
      normalizedUrl = `https://${normalizedUrl}`
    }

    setIsLoading(true)

    try {
      await startAnalysis(normalizedUrl)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setIsLoading(false)
    }
  }

  const startAnalysis = async (targetUrl: string, invoiceId?: string) => {
    const headers: HeadersInit = { 'Content-Type': 'application/json' }
    if (invoiceId) {
      headers['X-Invoice-ID'] = invoiceId
    }

    const response = await fetch('/api/v1/analyze', {
      method: 'POST',
      headers,
      body: JSON.stringify({ url: targetUrl }),
    })

    if (response.status === 402) {
      // Payment required - show payment modal
      setIsLoading(false)
      setShowPayment(true)
      return
    }

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Failed to start analysis')
    }

    const data = await response.json()
    router.push(`/analyze/${data.id}`)
  }

  const handlePaymentModalOpen = async (open: boolean) => {
    setShowPayment(open)
  }

  const handlePaymentSuccess = (invoiceId: string) => {
    setShowPayment(false)
    setIsLoading(true)
    let normalizedUrl = url.trim()
    if (!normalizedUrl.startsWith('http://') && !normalizedUrl.startsWith('https://')) {
      normalizedUrl = `https://${normalizedUrl}`
    }
    startAnalysis(normalizedUrl, invoiceId).catch((err) => {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setIsLoading(false)
    })
  }

  return (
    <main className="min-h-screen">
      <GlassNavbar />
      
      <PaymentModal 
        open={showPayment} 
        onOpenChange={handlePaymentModalOpen}
        invoiceData={invoiceData}
        onSuccess={handlePaymentSuccess}
      />
      
      {/* Hero Section */}
      <section className="relative pt-12 pb-24 md:pt-20 md:pb-32 overflow-hidden">
        <div className="container-glass relative z-10">
          {/* Badge */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="flex justify-center mb-8"
          >
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full 
                           bg-white/[0.08] backdrop-blur-md border border-white/[0.15]
                           text-white/90 text-sm font-medium
                           shadow-[0_0_20px_rgba(59,130,246,0.2)]">
              <Sparkles className="w-4 h-4 text-blue-400" />
              AI-Powered Brand Intelligence
            </span>
          </motion.div>

          {/* Headline */}
          <motion.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="text-4xl sm:text-5xl lg:text-7xl font-bold text-center 
                       leading-[1.1] tracking-tight mb-6"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            <span className="text-white drop-shadow-[0_4px_8px_rgba(0,0,0,0.3)]">
              Get a 360° Audit of Your
            </span>
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 
                           bg-clip-text text-transparent">
              Brand&apos;s Digital Presence
            </span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-lg sm:text-xl text-white/70 text-center max-w-2xl mx-auto mb-12"
          >
            Analyze your SEO, social media, brand messaging, and more in minutes.
            Get actionable insights to grow your brand.
          </motion.p>

          {/* URL Input Form */}
          <motion.form 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            onSubmit={handleSubmit} 
            className="max-w-2xl mx-auto"
          >
            <div 
              className={cn(
                'relative p-2 rounded-2xl transition-all duration-300',
                'bg-white/[0.06] backdrop-blur-xl border',
                isFocused 
                  ? 'border-blue-500/50 shadow-[0_0_40px_rgba(59,130,246,0.25)]' 
                  : 'border-white/[0.15] shadow-glass'
              )}
            >
              <div className="flex flex-col sm:flex-row gap-2">
                <div className="flex-1 relative">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">
                    <Globe className="w-5 h-5" />
                  </div>
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    placeholder="Enter your website URL (e.g., example.com)"
                    className="w-full pl-12 pr-4 py-4 text-lg rounded-xl
                             bg-transparent text-white
                             placeholder:text-white/40
                             focus:outline-none
                             disabled:opacity-50"
                    disabled={isLoading}
                  />
                </div>
                <Button
                  type="submit"
                  disabled={isLoading}
                  variant="default"
                  size="lg"
                  className="text-base px-8"
                >
                  {isLoading ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Analyze Now
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Error message */}
            <AnimatePresence>
              {error && (
                <motion.p 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mt-4 text-center text-red-400"
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>
          </motion.form>

          {/* Trust indicators */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="flex flex-wrap justify-center items-center gap-6 mt-8 text-white/50 text-sm"
          >
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" />
              <span>$0.10 per analysis</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-400" />
              <span>No signup required</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-400" />
              <span>Results in 2 minutes</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 md:py-32">
        <div className="container-glass">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4"
                style={{ fontFamily: 'var(--font-display)' }}>
              Comprehensive Brand Analysis
            </h2>
            <p className="text-white/60 max-w-2xl mx-auto">
              Get a complete audit covering every aspect of your brand&apos;s online presence
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <FeatureCard {...feature} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20">
        <div className="container-glass">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <GlassCard className="p-6 text-center">
                  <div className="text-3xl md:text-4xl font-bold text-white mb-2"
                       style={{ fontFamily: 'var(--font-display)' }}>
                    {stat.value}
                  </div>
                  <div className="text-white/60 text-sm">{stat.label}</div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 md:py-32">
        <div className="container-glass">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="relative"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-pink-500/20 
                          rounded-3xl blur-3xl" />
            <GlassCard intensity="heavy" className="relative p-8 md:p-12 text-center">
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-4"
                  style={{ fontFamily: 'var(--font-display)' }}>
                Ready to discover your brand&apos;s potential?
              </h2>
              <p className="text-white/70 mb-8 max-w-xl mx-auto">
                Get a comprehensive analysis of your brand&apos;s digital presence in minutes.
                Just $0.10 per analysis, no signup required.
              </p>
              <Button 
                variant="glow" 
                size="xl" 
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                className="gap-2"
              >
                <Sparkles className="w-5 h-5" />
                Start Analysis
              </Button>
            </GlassCard>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/[0.1]">
        <div className="container-glass">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
                <BarChart3 className="h-5 w-5 text-white" />
              </div>
              <span className="text-white font-semibold">Brand Analytics</span>
            </div>
            <p className="text-white/50 text-sm text-center md:text-right">
              Built with ❤️ for startups and marketers
            </p>
          </div>
        </div>
      </footer>
    </main>
  )
}

// =============================================================================
// Feature Card Component
// =============================================================================

interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  description: string
  gradient: string
}

function FeatureCard({ icon, title, description, gradient }: FeatureCardProps) {
  return (
    <GlassCard interactive className="h-full p-6">
      <div className={cn(
        'inline-flex items-center justify-center w-12 h-12 rounded-xl mb-4',
        gradient
      )}>
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-white/60 text-sm leading-relaxed">{description}</p>
    </GlassCard>
  )
}

// =============================================================================
// Features Data
// =============================================================================

const features: FeatureCardProps[] = [
  {
    icon: <Search className="w-6 h-6 text-white" />,
    title: "SEO Performance",
    description: "Page speed, meta tags, indexing status, and technical SEO health analysis",
    gradient: "bg-gradient-to-br from-blue-500 to-blue-600",
  },
  {
    icon: <Users className="w-6 h-6 text-white" />,
    title: "Social Media",
    description: "Follower counts, engagement rates, and content strategy insights",
    gradient: "bg-gradient-to-br from-pink-500 to-rose-600",
  },
  {
    icon: <Target className="w-6 h-6 text-white" />,
    title: "Brand Messaging",
    description: "Brand archetype analysis, voice consistency, and value proposition clarity",
    gradient: "bg-gradient-to-br from-purple-500 to-purple-600",
  },
  {
    icon: <Brain className="w-6 h-6 text-white" />,
    title: "AI Discoverability",
    description: "How well AI assistants and search engines understand your brand",
    gradient: "bg-gradient-to-br from-emerald-500 to-emerald-600",
  },
  {
    icon: <BarChart3 className="w-6 h-6 text-white" />,
    title: "Content Analysis",
    description: "Content mix, sentiment analysis, and topic coverage evaluation",
    gradient: "bg-gradient-to-br from-orange-500 to-orange-600",
  },
  {
    icon: <TrendingUp className="w-6 h-6 text-white" />,
    title: "Growth Opportunities",
    description: "Channel recommendations and actionable growth strategies",
    gradient: "bg-gradient-to-br from-cyan-500 to-cyan-600",
  },
]

// =============================================================================
// Stats Data
// =============================================================================

const stats = [
  { value: "8", label: "Analysis Modules" },
  { value: "100+", label: "Data Points" },
  { value: "2 min", label: "Average Time" },
  { value: "$0.10", label: "Per Analysis" },
]
