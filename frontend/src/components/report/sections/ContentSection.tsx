/**
 * =============================================================================
 * Content Section Component
 * =============================================================================
 * Displays content quality analysis including themes, consistency,
 * and content strategy assessment.
 * =============================================================================
 */

'use client';

import { FileText, Tag, BarChart3, Calendar } from 'lucide-react';
import { ModuleSection } from './ModuleSection';

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
export function ContentSection({ data, className = '' }: ContentSectionProps) {
  // Build metrics
  const metrics = [
    {
      label: 'Content Quality',
      value: data.content_quality_score ?? 0,
      unit: '/100',
    },
    {
      label: 'Freshness',
      value: data.content_freshness ?? 0,
      unit: '/100',
    },
    {
      label: 'Consistency',
      value: data.posting_consistency ?? 0,
      unit: '/100',
    },
    {
      label: 'Variety',
      value: data.content_variety_score ?? 0,
      unit: '/100',
    },
  ].filter(m => m.value !== undefined && m.value !== 0) as Array<{
    label: string;
    value: string | number;
    unit?: string;
  }>;

  // Combined topics/themes - use Array.from for broader TypeScript compatibility
  const allTopics = [...(data.topics || []), ...(data.themes || [])];
  const uniqueTopics = Array.from(new Set(allTopics));

  // Transform findings
  const findings = (data.findings || []).map(f => ({
    title: f.title,
    description: f.description || (f as any).detail || '',
    severity: f.severity as 'critical' | 'high' | 'medium' | 'low' | 'info' | 'success',
    data: f.data as Record<string, string | number> | undefined,
  }));

  // Transform recommendations
  const recommendations = (data.recommendations || []).map(r => ({
    title: r.title,
    description: r.description || (r as any).detail || '',
    priority: r.priority as 'critical' | 'high' | 'medium' | 'low',
    category: r.category,
    impact: r.impact as 'high' | 'medium' | 'low',
    effort: r.effort as 'high' | 'medium' | 'low',
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
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
            Content Topics
          </h3>
          <div className="flex flex-wrap gap-2">
            {uniqueTopics.map((topic) => (
              <span
                key={topic}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-700 rounded-full text-sm"
              >
                <Tag className="w-3.5 h-3.5 text-slate-400" />
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}
    </ModuleSection>
  );
}

export default ContentSection;

