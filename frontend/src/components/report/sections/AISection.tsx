/**
 * =============================================================================
 * AI Discoverability Section Component
 * =============================================================================
 * Displays AI readiness analysis including structured data,
 * Wikipedia presence, and visibility in AI assistants.
 * =============================================================================
 */

'use client';

import { Bot, Database, BookOpen, Globe, CheckCircle, XCircle } from 'lucide-react';
import { ModuleSection } from './ModuleSection';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface AIData {
  score?: number;
  ai_readiness_level?: string;
  structured_data_score?: number;
  wikipedia_present?: boolean;
  wikipedia_summary?: string;
  schema_types_found?: string[];
  entity_recognition_score?: number;
  knowledge_graph_presence?: boolean;
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

interface AISectionProps {
  data: AIData;
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function AISection({ data, className = '' }: AISectionProps) {
  // Build metrics
  const metrics = [
    {
      label: 'AI Readiness',
      value: data.ai_readiness_level?.toUpperCase() ?? 'N/A',
    },
    {
      label: 'Structured Data',
      value: data.structured_data_score ?? 0,
      unit: '/100',
    },
    {
      label: 'Entity Recognition',
      value: data.entity_recognition_score ?? 0,
      unit: '/100',
    },
  ].filter(m => m.value !== undefined && m.value !== 'N/A' && m.value !== 0) as Array<{
    label: string;
    value: string | number;
    unit?: string;
  }>;

  // AI readiness checks
  const readinessChecks = [
    { label: 'Wikipedia Presence', passed: data.wikipedia_present, icon: BookOpen },
    { label: 'Knowledge Graph', passed: data.knowledge_graph_presence, icon: Globe },
    { label: 'Structured Data', passed: (data.structured_data_score ?? 0) > 50, icon: Database },
  ];

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
      id="ai"
      moduleKey="ai_discoverability"
      title="AI Discoverability"
      description="Visibility in AI assistants, structured data, and knowledge graph presence."
      score={data.score ?? 0}
      icon={<Bot className="w-6 h-6" />}
      metrics={metrics}
      findings={findings}
      recommendations={recommendations}
      className={className}
    >
      <div className="space-y-6">
        {/* AI Readiness Indicators */}
        <div>
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
            AI Readiness Indicators
          </h3>
          <div className="grid grid-cols-3 gap-4">
            {readinessChecks.map((check) => {
              const Icon = check.icon;
              return (
                <div
                  key={check.label}
                  className={`p-4 rounded-lg border ${
                    check.passed
                      ? 'bg-emerald-50 border-emerald-200'
                      : 'bg-slate-50 border-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={`w-5 h-5 ${check.passed ? 'text-emerald-600' : 'text-slate-400'}`} />
                    {check.passed ? (
                      <CheckCircle className="w-4 h-4 text-emerald-600" />
                    ) : (
                      <XCircle className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                  <span className={`text-sm font-medium ${check.passed ? 'text-emerald-700' : 'text-slate-600'}`}>
                    {check.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Schema Types Found */}
        {data.schema_types_found && data.schema_types_found.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
              Schema.org Types Found
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.schema_types_found.map((type) => (
                <span
                  key={type}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-sm font-mono border border-blue-100"
                >
                  <Database className="w-3.5 h-3.5" />
                  {type}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Wikipedia Summary */}
        {data.wikipedia_present && data.wikipedia_summary && (
          <div>
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
              Wikipedia Summary
            </h3>
            <div className="bg-white rounded-lg border border-slate-200 p-4">
              <div className="flex items-start gap-3">
                <BookOpen className="w-5 h-5 text-slate-400 mt-0.5" />
                <p className="text-sm text-slate-600 leading-relaxed">
                  {data.wikipedia_summary}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </ModuleSection>
  );
}

export default AISection;

