// =============================================================================
// Glass Navbar Component - Apple Liquid Glass UI
// =============================================================================
// A floating glass navbar with scroll-based effects and responsive design.
// =============================================================================

'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, useScroll, useTransform } from 'framer-motion'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

// Icons
import { 
  BarChart3, 
  Home, 
  FileText, 
  Settings,
  Menu,
  X,
  Sparkles
} from 'lucide-react'

interface NavItem {
  href: string
  label: string
  icon: React.ElementType
}

const navItems: NavItem[] = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/reports', label: 'Reports', icon: FileText },
]

interface GlassNavbarProps {
  className?: string
}

export function GlassNavbar({ className }: GlassNavbarProps) {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false)
  const { scrollY } = useScroll()
  
  // Scroll-based animations
  const navBackground = useTransform(
    scrollY,
    [0, 50],
    ['rgba(255, 255, 255, 0)', 'rgba(255, 255, 255, 0.08)']
  )
  
  const navBorder = useTransform(
    scrollY,
    [0, 50],
    ['rgba(255, 255, 255, 0)', 'rgba(255, 255, 255, 0.1)']
  )
  
  const navBlur = useTransform(scrollY, [0, 50], [0, 24])
  const navShadow = useTransform(
    scrollY,
    [0, 50],
    ['0 0 0 rgba(0, 0, 0, 0)', '0 8px 32px rgba(0, 0, 0, 0.2)']
  )

  return (
    <>
      <motion.header
        style={{
          backgroundColor: navBackground,
          borderColor: navBorder,
          boxShadow: navShadow,
        }}
        className={cn(
          'fixed top-0 left-0 right-0 z-50',
          'border-b transition-all duration-300',
          className
        )}
      >
        <motion.div
          style={{ backdropFilter: useTransform(navBlur, (v) => `blur(${v}px)`) }}
          className="absolute inset-0"
        />
        
        <nav className="relative container-glass">
          <div className="flex items-center justify-between h-16 md:h-20">
            {/* Logo */}
            <Link 
              href="/" 
              className="flex items-center gap-3 group"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
                <div className="relative bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-xl">
                  <BarChart3 className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="hidden sm:block">
                <span className="text-xl font-bold text-white">
                  Brand Analytics
                </span>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-2">
              {navItems.map((item) => {
                const isActive = pathname === item.href
                const Icon = item.icon
                
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2 rounded-xl',
                      'text-sm font-medium transition-all duration-200',
                      isActive
                        ? 'bg-white/[0.12] text-white'
                        : 'text-white/70 hover:text-white hover:bg-white/[0.08]'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                )
              })}
            </div>

            {/* CTA Button */}
            <div className="hidden md:flex items-center gap-4">
              <Link href="/">
                <Button variant="default" size="default" className="gap-2">
                  <Sparkles className="h-4 w-4" />
                  Analyze Brand
                </Button>
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-xl text-white/80 hover:text-white hover:bg-white/[0.1] transition-all"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </nav>
      </motion.header>

      {/* Mobile Menu */}
      <motion.div
        initial={false}
        animate={mobileMenuOpen ? 'open' : 'closed'}
        variants={{
          open: { opacity: 1, y: 0, pointerEvents: 'auto' as const },
          closed: { opacity: 0, y: -20, pointerEvents: 'none' as const },
        }}
        transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
        className="fixed inset-x-0 top-16 z-40 md:hidden"
      >
        <div className="mx-4 mt-2 p-4 rounded-2xl bg-white/[0.08] backdrop-blur-2xl border border-white/[0.1] shadow-glass">
          <div className="flex flex-col gap-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              const Icon = item.icon
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 rounded-xl',
                    'text-base font-medium transition-all duration-200',
                    isActive
                      ? 'bg-white/[0.12] text-white'
                      : 'text-white/70 hover:text-white hover:bg-white/[0.08]'
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {item.label}
                </Link>
              )
            })}
            
            <div className="pt-2 mt-2 border-t border-white/[0.1]">
              <Link href="/" onClick={() => setMobileMenuOpen(false)}>
                <Button variant="default" size="lg" className="w-full gap-2">
                  <Sparkles className="h-4 w-4" />
                  Analyze Brand
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Mobile Menu Backdrop */}
      {mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setMobileMenuOpen(false)}
          className="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm md:hidden"
        />
      )}

      {/* Spacer for fixed navbar */}
      <div className="h-16 md:h-20" />
    </>
  )
}

// =============================================================================
// Simple Navbar Variant (for report pages)
// =============================================================================

interface SimpleNavbarProps {
  title?: string
  backHref?: string
  className?: string
}

export function SimpleNavbar({ title, backHref = '/', className }: SimpleNavbarProps) {
  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50',
        'bg-white/[0.06] backdrop-blur-2xl',
        'border-b border-white/[0.1]',
        className
      )}
    >
      <nav className="container-glass">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            <Link 
              href={backHref}
              className="flex items-center gap-2 text-white/70 hover:text-white transition-colors"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="text-sm font-medium">Back</span>
            </Link>
            
            {title && (
              <>
                <div className="h-6 w-px bg-white/[0.2]" />
                <h1 className="text-lg font-semibold text-white truncate max-w-[200px] sm:max-w-none">
                  {title}
                </h1>
              </>
            )}
          </div>
          
          <Link href="/">
            <div className="flex items-center gap-2">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-1.5 rounded-lg">
                <BarChart3 className="h-4 w-4 text-white" />
              </div>
              <span className="hidden sm:block text-sm font-semibold text-white">
                Brand Analytics
              </span>
            </div>
          </Link>
        </div>
      </nav>
    </header>
  )
}

export default GlassNavbar
