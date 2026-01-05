/**
 * =============================================================================
 * Channel Fit Section Component - Apple Liquid Glass UI
 * =============================================================================
 * Displays marketing channel analysis including channel suitability,
 * audience alignment, and go-to-market recommendations with glassmorphism.
 * =============================================================================
 */

"use client";

import { Target, TrendingUp, Users, MessageCircle } from "lucide-react";
import { ModuleSection } from "./ModuleSection";

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
// Helper - Get score color
// -----------------------------------------------------------------------------
function getScoreColor(score: number) {
  if (score >= 70) return { bg: "bg-emerald-500", text: "text-emerald-400" };
  if (score >= 50) return { bg: "bg-yellow-500", text: "text-yellow-400" };
  return { bg: "bg-red-500", text: "text-red-400" };
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ChannelSection({ data, className = "" }: ChannelSectionProps) {
  // Build metrics
  const metrics = [
    {
      label: "Audience Alignment",
      value: data.audience_alignment ?? 0,
      unit: "/100",
    },
    {
      label: "Market Fit",
      value: data.market_fit_score ?? 0,
      unit: "/100",
    },
    {
      label: "Distribution Ready",
      value: data.distribution_readiness ?? 0,
      unit: "/100",
    },
  ].filter((m) => m.value !== undefined && m.value !== 0) as Array<{
    label: string;
    value: string | number;
    unit?: string;
  }>;

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
      <div className="space-y-4">
        {/* Recommended Channels */}
        {data.recommended_channels && data.recommended_channels.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
              Recommended Channels
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.recommended_channels.map((channel) => (
                <span
                  key={channel}
                  className="inline-flex items-center gap-1.5 px-4 py-2 
                           bg-emerald-500/10 text-emerald-400 rounded-md text-sm font-medium 
                           border border-emerald-500/20 hover:bg-emerald-500/15 transition-all duration-150"
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
            <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
              Channel Suitability
            </h3>
            <div className="space-y-2">
              {data.channel_scores.slice(0, 5).map((cs) => {
                const scoreColor = getScoreColor(cs.score);
                return (
                  <div
                    key={cs.channel}
                    className="bg-white/[0.04] backdrop-blur-xl rounded-lg border border-white/[0.06] p-4
                             hover:bg-white/[0.06] transition-all duration-150"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-white">
                        {cs.channel}
                      </span>
                      <span className={`font-semibold ${scoreColor.text}`}>
                        {cs.score}/100
                      </span>
                    </div>
                    {/* Progress bar */}
                    <div className="w-full h-1.5 bg-white/[0.08] rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${scoreColor.bg} transition-all duration-300`}
                        style={{ width: `${cs.score}%` }}
                      />
                    </div>
                    {cs.reasoning && (
                      <p className="text-sm text-white/50 mt-2">
                        {cs.reasoning}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </ModuleSection>
  );
}

export default ChannelSection;
