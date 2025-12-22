// =============================================================================
// Home Page - Analysis Form
// =============================================================================
// Landing page with hero section and URL input form to start analysis.
// =============================================================================

'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowRight, Sparkles, BarChart3, Target, Zap } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  // Handle form submission - start analysis
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    // Basic validation
    if (!url.trim()) {
      setError('Please enter a website URL')
      return
    }

    // Normalize URL
    let normalizedUrl = url.trim()
    if (!normalizedUrl.startsWith('http://') && !normalizedUrl.startsWith('https://')) {
      normalizedUrl = `https://${normalizedUrl}`
    }

    setIsLoading(true)

    try {
      const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: normalizedUrl }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to start analysis')
      }

      const data = await response.json()
      
      // Redirect to analysis progress page
      router.push(`/analyze/${data.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 gradient-bg opacity-10" />
        
        <div className="relative max-w-6xl mx-auto px-4 py-24 sm:px-6 lg:px-8">
          {/* Badge */}
          <div className="flex justify-center mb-8">
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full 
                           bg-blue-50 text-blue-700 text-sm font-medium">
              <Sparkles className="w-4 h-4" />
              AI-Powered Brand Analysis
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-center 
                         leading-tight tracking-tight mb-6">
            Get a 360° Audit of Your{' '}
            <span className="gradient-text">Brand's Digital Presence</span>
          </h1>

          {/* Subheadline */}
          <p className="text-lg sm:text-xl text-slate-600 text-center max-w-2xl mx-auto mb-12">
            Analyze your SEO, social media, brand messaging, and more in minutes.
            Get actionable insights to grow your brand.
          </p>

          {/* URL Input Form */}
          <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter your website URL (e.g., example.com)"
                  className="w-full px-6 py-4 text-lg rounded-2xl border-2 border-slate-200
                           focus:border-blue-500 focus:ring-4 focus:ring-blue-100
                           outline-none transition-all duration-200
                           placeholder:text-slate-400"
                  disabled={isLoading}
                />
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary text-lg px-8 py-4"
              >
                {isLoading ? (
                  <>
                    <span className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    Analyze Now
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </div>

            {/* Error message */}
            {error && (
              <p className="mt-4 text-center text-red-600">{error}</p>
            )}
          </form>

          {/* Trust indicators */}
          <p className="text-center text-slate-500 text-sm mt-6">
            Free analysis • No signup required • Results in 2 minutes
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-4">
            What We Analyze
          </h2>
          <p className="text-slate-600 text-center max-w-2xl mx-auto mb-12">
            A comprehensive audit covering every aspect of your brand's online presence
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature cards */}
            <FeatureCard
              icon={<BarChart3 className="w-8 h-8 text-blue-600" />}
              title="SEO & Performance"
              description="Page speed, meta tags, indexing status, and technical SEO health"
            />
            <FeatureCard
              icon={<Target className="w-8 h-8 text-emerald-600" />}
              title="Brand & Messaging"
              description="Brand archetype, voice analysis, value proposition clarity"
            />
            <FeatureCard
              icon={<Zap className="w-8 h-8 text-amber-600" />}
              title="Social & Engagement"
              description="Follower counts, engagement rates, content strategy analysis"
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-slate-200">
        <div className="max-w-6xl mx-auto px-4 text-center text-slate-500 text-sm">
          <p>Brand Analytics Tool • Built with ❤️ for startups and marketers</p>
        </div>
      </footer>
    </main>
  )
}

// Feature card component
function FeatureCard({ 
  icon, 
  title, 
  description 
}: { 
  icon: React.ReactNode
  title: string
  description: string 
}) {
  return (
    <div className="card p-6 text-center hover:shadow-md transition-shadow">
      <div className="inline-flex items-center justify-center w-16 h-16 
                      rounded-2xl bg-slate-50 mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  )
}

