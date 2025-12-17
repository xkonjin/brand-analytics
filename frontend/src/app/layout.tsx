// =============================================================================
// Root Layout Component
// =============================================================================
// Main layout wrapper for all pages with fonts, metadata, and providers.
// =============================================================================

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

// Load Inter font with variable weight
const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

// SEO metadata for the application
export const metadata: Metadata = {
  title: 'Brand Analytics - Comprehensive Brand Analysis Tool',
  description: 'Get a 360° marketing audit of your brand. Analyze SEO, social media, brand messaging, and more with AI-powered insights.',
  keywords: ['brand analysis', 'SEO audit', 'marketing analysis', 'brand archetype', 'social media analytics'],
  authors: [{ name: 'Brand Analytics' }],
  openGraph: {
    title: 'Brand Analytics - Comprehensive Brand Analysis Tool',
    description: 'Get a 360° marketing audit of your brand with AI-powered insights.',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}

