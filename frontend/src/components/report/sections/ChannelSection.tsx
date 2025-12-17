/**
 * =============================================================================
 * Channel Fit Section Component
 * =============================================================================
 * Displays marketing channel analysis including channel suitability,
 * audience alignment, and go-to-market recommendations.
 * =============================================================================
 */

'use client';

import { Target, TrendingUp, Users, MessageCircle } from 'lucide-react';
import { ModuleSection } from './ModuleSection';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface ChannelScore {
  channel: string;
  score: number;
  reasoning?: string;
}

interface ChannelData {
  score?: number;
  recommended_channels?: string[];
  channel_scores?: ChannelScore[];
  audience_alignment?: number;
  market_fit_score?: number;
  distribution_readiness?: number;
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

interface ChannelSectionProps {
  data: ChannelData;
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ChannelSection({ data, className = '' }: ChannelSectionProps) {
  // Build metrics
  const metrics = [
    {
      label: 'Audience Alignment',
      value: data.audience_alignment ?? 0,
      unit: '/100',
    },
    {
      label: 'Market Fit',
      value: data.market_fit_score ?? 0,
      unit: '/100',
    },
    {
      label: 'Distribution Ready',
      value: data.distribution_readiness ?? 0,
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
      id="channels"
      moduleKey="channel_fit"
      title="Channel Fit"
      description="Marketing channel optimization and audience alignment analysis."
      score={data.score ?? 0}
      icon={<Target className="w-6 h-6" />}
      metrics={metrics}
      findings={findings}
      recommendations={recommendations}
      className={className}
    >
      <div className="space-y-6">
        {/* Recommended Channels */}
        {data.recommended_channels && data.recommended_channels.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
              Recommended Channels
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.recommended_channels.map((channel) => (
                <span
                  key={channel}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-50 text-emerald-700 rounded-lg text-sm font-medium border border-emerald-100"
                >
                  <TrendingUp className="w-4 h-4" />
                  {channel}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Channel Scores */}
        {data.channel_scores && data.channel_scores.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
              Channel Suitability
            </h3>
            <div className="space-y-3">
              {data.channel_scores.slice(0, 5).map((cs) => (
                <div
                  key={cs.channel}
                  className="bg-white rounded-lg border border-slate-200 p-4"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-slate-900">
                      {cs.channel}
                    </span>
                    <span
                      className={`font-semibold ${
                        cs.score >= 70
                          ? 'text-emerald-600'
                          : cs.score >= 50
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}
                    >
                      {cs.score}/100
                    </span>
                  </div>
                  {/* Progress bar */}
                  <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        cs.score >= 70
                          ? 'bg-emerald-500'
                          : cs.score >= 50
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${cs.score}%` }}
                    />
                  </div>
                  {cs.reasoning && (
                    <p className="text-sm text-slate-500 mt-2">{cs.reasoning}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </ModuleSection>
  );
}

export default ChannelSection;

