/**
 * =============================================================================
 * AI Discoverability Section Component - Apple Liquid Glass UI
 * =============================================================================
 * Displays AI readiness analysis including structured data,
 * Wikipedia presence, and visibility in AI assistants with glassmorphism.
 * =============================================================================
 */

"use client";

import {
  Bot,
  Database,
  BookOpen,
  Globe,
  CheckCircle,
  XCircle,
} from "lucide-react";
import { ModuleSection } from "./ModuleSection";

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
export function AISection({ data, className = "" }: AISectionProps) {
  // Build metrics
  const metrics = [
    {
      label: "AI Readiness",
      value: data.ai_readiness_level?.toUpperCase() ?? "N/A",
    },
    {
      label: "Structured Data",
      value: data.structured_data_score ?? 0,
      unit: "/100",
    },
    {
      label: "Entity Recognition",
      value: data.entity_recognition_score ?? 0,
      unit: "/100",
    },
  ].filter(
    (m) => m.value !== undefined && m.value !== "N/A" && m.value !== 0,
  ) as Array<{
    label: string;
    value: string | number;
    unit?: string;
  }>;

  // AI readiness checks
  const readinessChecks = [
    {
      label: "Wikipedia Presence",
      passed: data.wikipedia_present,
      icon: BookOpen,
    },
    {
      label: "Knowledge Graph",
      passed: data.knowledge_graph_presence,
      icon: Globe,
    },
    {
      label: "Structured Data",
      passed: (data.structured_data_score ?? 0) > 50,
      icon: Database,
    },
  ];

  // Transform findings - support both 'description' and legacy 'detail' field names
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

  // Transform recommendations - support both 'description' and legacy 'detail' field names
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
      <div className="space-y-4">
        {/* AI Readiness Indicators */}
        <div>
          <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
            AI Readiness Indicators
          </h3>
          <div className="grid grid-cols-3 gap-4">
            {readinessChecks.map((check) => {
              const Icon = check.icon;
              return (
                <div
                  key={check.label}
                  className={`p-4 rounded-lg backdrop-blur-xl border transition-all duration-150 ${
                    check.passed
                      ? "bg-emerald-500/8 border-emerald-500/20 hover:bg-emerald-500/12"
                      : "bg-white/[0.04] border-white/[0.06] hover:bg-white/[0.06]"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Icon
                      className={`w-5 h-5 ${check.passed ? "text-emerald-400" : "text-white/40"}`}
                    />
                    {check.passed ? (
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <XCircle className="w-4 h-4 text-white/30" />
                    )}
                  </div>
                  <span
                    className={`text-sm font-medium ${check.passed ? "text-emerald-400" : "text-white/60"}`}
                  >
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
            <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
              Schema.org Types Found
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.schema_types_found.map((type) => (
                <span
                  key={type}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 
                           bg-blue-500/10 text-blue-400 rounded-lg text-sm font-mono 
                           border border-blue-500/20 hover:bg-blue-500/15 transition-all duration-150"
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
            <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
              Wikipedia Summary
            </h3>
            <div
              className="bg-white/[0.04] backdrop-blur-xl rounded-lg border border-white/[0.06] p-4
                          hover:bg-white/[0.06] transition-all duration-150"
            >
              <div className="flex items-start gap-3">
                <BookOpen className="w-5 h-5 text-white/40 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-white/60 leading-relaxed">
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
