/**
 * =============================================================================
 * SEO Section Component - Apple Liquid Glass UI
 * =============================================================================
 * Displays SEO performance analysis with glassmorphism styling.
 * Includes Core Web Vitals and technical SEO checklist.
 * =============================================================================
 */

"use client";

import { Search, CheckCircle, XCircle } from "lucide-react";
import { ModuleSection } from "./ModuleSection";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface SEOData {
  score?: number;
  performance_score?: number;
  accessibility_score?: number;
  best_practices_score?: number;
  seo_score?: number;
  first_contentful_paint?: number;
  largest_contentful_paint?: number;
  total_blocking_time?: number;
  cumulative_layout_shift?: number;
  speed_index?: number;
  has_meta_title?: boolean;
  has_meta_description?: boolean;
  has_canonical?: boolean;
  has_robots_txt?: boolean;
  has_sitemap?: boolean;
  has_ssl?: boolean;
  mobile_friendly?: boolean;
  findings?: Array<{
    title: string;
    description: string;
    severity: string;
    data?: Record<string, any>;
  }>;
  recommendations?: Array<{
    title: string;
    description: string;
    priority: string;
    category: string;
    impact: string;
    effort: string;
  }>;
}

interface SEOSectionProps {
  data: SEOData;
  className?: string;
}

// -----------------------------------------------------------------------------
// Helper - Format milliseconds to seconds
// -----------------------------------------------------------------------------
function formatMs(ms?: number): string {
  if (ms === undefined || ms === null) return "N/A";
  return `${(ms / 1000).toFixed(1)}s`;
}

function formatCLS(cls?: number): string {
  if (cls === undefined || cls === null) return "N/A";
  return cls.toFixed(3);
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function SEOSection({ data, className = "" }: SEOSectionProps) {
  // Build metrics from available data
  const metrics = [
    {
      label: "Performance",
      value: data.performance_score ?? 0,
      unit: "/100",
      trend:
        (data.performance_score ?? 0) >= 90
          ? "up"
          : (data.performance_score ?? 0) >= 50
            ? "stable"
            : "down",
    },
    {
      label: "Accessibility",
      value: data.accessibility_score ?? 0,
      unit: "/100",
    },
    {
      label: "Best Practices",
      value: data.best_practices_score ?? 0,
      unit: "/100",
    },
    {
      label: "SEO Score",
      value: data.seo_score ?? 0,
      unit: "/100",
    },
  ].filter((m) => m.value !== undefined) as Array<{
    label: string;
    value: string | number;
    unit?: string;
    trend?: "up" | "down" | "stable";
  }>;

  // Add Core Web Vitals if available
  const webVitals = [
    {
      label: "FCP",
      value: formatMs(data.first_contentful_paint),
      subtitle: "First Contentful Paint",
    },
    {
      label: "LCP",
      value: formatMs(data.largest_contentful_paint),
      subtitle: "Largest Contentful Paint",
    },
    {
      label: "TBT",
      value: `${data.total_blocking_time ?? 0}ms`,
      subtitle: "Total Blocking Time",
    },
    {
      label: "CLS",
      value: formatCLS(data.cumulative_layout_shift),
      subtitle: "Cumulative Layout Shift",
    },
  ];

  // Technical SEO checklist
  const technicalChecks = [
    { label: "Meta Title", passed: data.has_meta_title },
    { label: "Meta Description", passed: data.has_meta_description },
    { label: "Canonical URL", passed: data.has_canonical },
    { label: "robots.txt", passed: data.has_robots_txt },
    { label: "Sitemap", passed: data.has_sitemap },
    { label: "SSL/HTTPS", passed: data.has_ssl },
    { label: "Mobile Friendly", passed: data.mobile_friendly },
  ];

  // Transform findings
  const findings = (data.findings || []).map((f) => ({
    title: f.title,
    description: f.description || (f as any).detail || "",
    severity: f.severity as
      | "critical"
      | "high"
      | "medium"
      | "low"
      | "info"
      | "success",
    data: f.data as Record<string, string | number> | undefined,
  }));

  // Transform recommendations
  const recommendations = (data.recommendations || []).map((r) => ({
    title: r.title,
    description: r.description || (r as any).detail || "",
    priority: r.priority as "critical" | "high" | "medium" | "low",
    category: r.category,
    impact: r.impact as "high" | "medium" | "low",
    effort: r.effort as "high" | "medium" | "low",
  }));

  return (
    <ModuleSection
      id="seo"
      moduleKey="seo"
      title="SEO Performance"
      description="Technical SEO health, Core Web Vitals, and search engine optimization."
      score={data.score ?? 0}
      icon={<Search className="w-6 h-6" />}
      metrics={metrics}
      findings={findings}
      recommendations={recommendations}
      className={className}
    >
      {/* Core Web Vitals grid */}
      <div className="space-y-4">
        <div>
          <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
            Core Web Vitals
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {webVitals.map((vital) => (
              <div
                key={vital.label}
                className="bg-white/[0.04] backdrop-blur-xl rounded-lg border border-white/[0.06] p-4
                         hover:bg-white/[0.06] transition-all duration-150"
              >
                <div className="text-xs text-white/40 mb-1">{vital.label}</div>
                <div className="text-xl font-bold text-white">
                  {vital.value}
                </div>
                <div className="text-xs text-white/30 mt-1">
                  {vital.subtitle}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Technical SEO Checklist */}
        <div>
          <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
            Technical SEO Checklist
          </h3>
          <div className="bg-white/[0.04] backdrop-blur-xl rounded-lg border border-white/[0.06] p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {technicalChecks.map((check) => (
                <div key={check.label} className="flex items-center gap-2">
                  {check.passed ? (
                    <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  )}
                  <span className="text-sm text-white/70">{check.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </ModuleSection>
  );
}

export default SEOSection;
