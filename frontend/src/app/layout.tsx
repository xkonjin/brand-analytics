// =============================================================================
// Root Layout Component - Apple Liquid Glass UI
// =============================================================================
// Main layout wrapper with ambient background, glass effects, and typography.
// =============================================================================

import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";
import { Providers } from "./providers";

// Load Inter font with variable weight
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

// SEO metadata for the application
export const metadata: Metadata = {
  title: "Brand Analytics - Comprehensive Brand Analysis Tool",
  description:
    "Get a 360° marketing audit of your brand. Analyze SEO, social media, brand messaging, and more with AI-powered insights.",
  keywords: [
    "brand analysis",
    "SEO audit",
    "marketing analysis",
    "brand archetype",
    "social media analytics",
  ],
  authors: [{ name: "Brand Analytics" }],
  openGraph: {
    title: "Brand Analytics - Comprehensive Brand Analysis Tool",
    description:
      "Get a 360° marketing audit of your brand with AI-powered insights.",
    type: "website",
  },
};

// Viewport configuration for mobile optimization
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#0f0f23",
};

// Ambient Background Component - Creates floating gradient orbs
function AmbientBackground() {
  return (
    <div className="ambient-background" aria-hidden="true">
      <div className="ambient-orb ambient-orb-1 opacity-20" />
      <div className="ambient-orb ambient-orb-2 opacity-20" />
      <div className="ambient-orb ambient-orb-3 opacity-20" />
    </div>
  );
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable}`}>
      <body className="min-h-screen bg-[rgb(15,15,35)] text-white antialiased overflow-x-hidden">
        {/* Ambient gradient background with floating orbs */}
        <AmbientBackground />

        {/* Main content */}
        <Providers>
          <div className="relative z-10">{children}</div>
        </Providers>
      </body>
    </html>
  );
}
