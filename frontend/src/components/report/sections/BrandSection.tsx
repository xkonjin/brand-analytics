/**
 * =============================================================================
 * Brand Messaging Section Component
 * =============================================================================
 * Displays brand archetype analysis, value proposition, tone,
 * and messaging clarity assessment.
 * =============================================================================
 */

'use client';

import { MessageSquare, Sparkles } from 'lucide-react';
import { ModuleSection } from './ModuleSection';
import { ArchetypeCard } from '../cards/ArchetypeCard';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface BrandData {
  score?: number;
  archetype?: string;
  archetype_secondary?: string;
  archetype_confidence?: number;
  archetype_description?: string;
  value_proposition?: string;
  value_proposition_clarity?: number;
  tone?: string[];
  tone_consistency?: number;
  readability_score?: number;
  clarity_score?: number;
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

interface BrandSectionProps {
  data: BrandData;
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function BrandSection({ data, className = '' }: BrandSectionProps) {
  // Build metrics
  const metrics = [
    {
      label: 'Value Prop Clarity',
      value: data.value_proposition_clarity ?? 0,
      unit: '/100',
    },
    {
      label: 'Tone Consistency',
      value: data.tone_consistency ?? 0,
      unit: '/100',
    },
    {
      label: 'Readability',
      value: data.readability_score ?? 0,
      unit: '/100',
    },
    {
      label: 'Overall Clarity',
      value: data.clarity_score ?? 0,
      unit: '/100',
    },
  ].filter(m => m.value !== undefined && m.value !== 0) as Array<{
    label: string;
    value: string | number;
    unit?: string;
  }>;

  // Transform findings
  const findings = (data.findings || []).map(f => ({
    title: f.title,
    description: f.description,
    severity: f.severity as 'critical' | 'high' | 'medium' | 'low' | 'info' | 'success',
    data: f.data as Record<string, string | number> | undefined,
  }));

  // Transform recommendations
  const recommendations = (data.recommendations || []).map(r => ({
    title: r.title,
    description: r.description,
    priority: r.priority as 'critical' | 'high' | 'medium' | 'low',
    category: r.category,
    impact: r.impact as 'high' | 'medium' | 'low',
    effort: r.effort as 'high' | 'medium' | 'low',
  }));

  return (
    <ModuleSection
      id="brand"
      moduleKey="brand_messaging"
      title="Brand Messaging"
      description="Brand archetype, value proposition, tone analysis, and messaging clarity."
      score={data.score ?? 0}
      icon={<MessageSquare className="w-6 h-6" />}
      metrics={metrics}
      findings={findings}
      recommendations={recommendations}
      className={className}
    >
      <div className="space-y-6">
        {/* Brand Archetype Card */}
        {data.archetype && (
          <div>
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
              Brand Archetype
            </h3>
            <ArchetypeCard
              primary={data.archetype}
              secondary={data.archetype_secondary}
              confidence={data.archetype_confidence ?? 0.7}
              description={data.archetype_description}
              animate={false}
            />
          </div>
        )}

        {/* Value Proposition */}
        {data.value_proposition && (
          <div>
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
              Value Proposition
            </h3>
            <div className="bg-white rounded-lg border border-slate-200 p-5">
              <p className="text-slate-700 italic">"{data.value_proposition}"</p>
            </div>
          </div>
        )}

        {/* Tone Keywords */}
        {data.tone && data.tone.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
              Brand Tone
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.tone.map((keyword) => (
                <span
                  key={keyword}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-700 rounded-full text-sm"
                >
                  <Sparkles className="w-3.5 h-3.5 text-slate-400" />
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </ModuleSection>
  );
}

export default BrandSection;

