/**
 * =============================================================================
 * Content Section Component - Apple Liquid Glass UI
 * =============================================================================
 * Displays content quality analysis including themes, consistency,
 * and content strategy assessment with glassmorphism styling.
 * =============================================================================
 */

"use client";

import { FileText, Tag, BarChart3, Calendar } from "lucide-react";
import { ModuleSection } from "./ModuleSection";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface ContentData {
  score?: number;
  content_quality_score?: number;
  content_freshness?: number;
  topics?: string[];
  themes?: string[];
  posting_consistency?: number;
  content_variety_score?: number;
  word_count_avg?: number;
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

interface ContentSectionProps {
  data: ContentData;
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ContentSection({ data, className = "" }: ContentSectionProps) {
  // Build metrics
  const metrics = [
    {
      label: "Content Quality",
      value: data.content_quality_score ?? 0,
      unit: "/100",
    },
    {
      label: "Freshness",
      value: data.content_freshness ?? 0,
      unit: "/100",
    },
    {
      label: "Consistency",
      value: data.posting_consistency ?? 0,
      unit: "/100",
    },
    {
      label: "Variety",
      value: data.content_variety_score ?? 0,
      unit: "/100",
    },
  ].filter((m) => m.value !== undefined && m.value !== 0) as Array<{
    label: string;
    value: string | number;
    unit?: string;
  }>;

  // Combined topics/themes - use Array.from for broader TypeScript compatibility
  const allTopics = [...(data.topics || []), ...(data.themes || [])];
  const uniqueTopics = Array.from(new Set(allTopics));

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
      id="content"
      moduleKey="content"
      title="Content Quality"
      description="Content strategy assessment, topic coverage, and posting consistency."
      score={data.score ?? 0}
      icon={<FileText className="w-6 h-6" />}
      metrics={metrics}
      findings={findings}
      recommendations={recommendations}
      className={className}
    >
      {/* Content Topics/Themes */}
      {uniqueTopics.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
            Content Topics
          </h3>
          <div className="flex flex-wrap gap-2">
            {uniqueTopics.map((topic) => (
              <span
                key={topic}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 
                         bg-white/[0.04] text-white/70 rounded-lg text-sm
                         border border-white/[0.06] hover:bg-white/[0.06] transition-all duration-150"
              >
                <Tag className="w-3.5 h-3.5 text-white/40" />
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Word Count Average */}
      {data.word_count_avg && data.word_count_avg > 0 && (
        <div className="mt-4">
          <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
            Content Depth
          </h3>
          <div
            className="bg-white/[0.04] backdrop-blur-xl rounded-lg border border-white/[0.06] p-4
                        inline-flex items-center gap-3"
          >
            <BarChart3 className="w-5 h-5 text-white/40" />
            <div>
              <div className="text-white font-medium">
                {Math.round(data.word_count_avg).toLocaleString()} words
              </div>
              <div className="text-xs text-white/40">
                Average content length
              </div>
            </div>
          </div>
        </div>
      )}
    </ModuleSection>
  );
}

export default ContentSection;
