/**
 * =============================================================================
 * Website UX Section Component - Apple Liquid Glass UI
 * =============================================================================
 * Displays website user experience analysis including performance,
 * accessibility, and conversion optimization with glassmorphism styling.
 * =============================================================================
 */

'use client';

import { Layout, Smartphone, Monitor, Shield, CheckCircle, XCircle } from 'lucide-react';
import { ModuleSection } from './ModuleSection';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface UXData {
  score?: number;
  mobile_score?: number;
  desktop_score?: number;
  accessibility_score?: number;
  navigation_clarity?: number;
  cta_visibility?: number;
  trust_signals_count?: number;
  trust_signals?: string[];
  has_clear_navigation?: boolean;
  has_visible_cta?: boolean;
  has_contact_info?: boolean;
  has_trust_badges?: boolean;
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

interface UXSectionProps {
  data: UXData;
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function UXSection({ data, className = '' }: UXSectionProps) {
  // Build metrics
  const metrics = [
    {
      label: 'Mobile Score',
      value: data.mobile_score ?? 0,
      unit: '/100',
      icon: <Smartphone className="w-4 h-4" />,
    },
    {
      label: 'Desktop Score',
      value: data.desktop_score ?? 0,
      unit: '/100',
      icon: <Monitor className="w-4 h-4" />,
    },
    {
      label: 'Accessibility',
      value: data.accessibility_score ?? 0,
      unit: '/100',
    },
    {
      label: 'Trust Signals',
      value: data.trust_signals_count ?? 0,
      subtitle: 'identified',
    },
  ].filter(m => m.value !== undefined && m.value !== 0) as Array<{
    label: string;
    value: string | number;
    unit?: string;
    subtitle?: string;
  }>;

  // UX checklist
  const uxChecks = [
    { label: 'Clear Navigation', passed: data.has_clear_navigation },
    { label: 'Visible CTA', passed: data.has_visible_cta },
    { label: 'Contact Information', passed: data.has_contact_info },
    { label: 'Trust Badges', passed: data.has_trust_badges },
  ];

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
      id="ux"
      moduleKey="website_ux"
      title="Website UX"
      description="User experience, accessibility, and conversion optimization analysis."
      score={data.score ?? 0}
      icon={<Layout className="w-6 h-6" />}
      metrics={metrics}
      findings={findings}
      recommendations={recommendations}
      className={className}
    >
      <div className="space-y-6">
        {/* UX Checklist */}
        <div>
          <h3 className="text-sm font-semibold text-white/40 uppercase tracking-wide mb-4">
            UX Essentials Checklist
          </h3>
          <div className="bg-white/[0.05] backdrop-blur-xl rounded-xl border border-white/[0.08] p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {uxChecks.map((check) => (
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

        {/* Trust Signals */}
        {data.trust_signals && data.trust_signals.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-white/40 uppercase tracking-wide mb-4">
              Trust Signals Found
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.trust_signals.map((signal) => (
                <span
                  key={signal}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 
                           bg-emerald-500/10 text-emerald-400 rounded-lg text-sm 
                           border border-emerald-500/20 hover:bg-emerald-500/20 transition-all"
                >
                  <Shield className="w-3.5 h-3.5" />
                  {signal}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </ModuleSection>
  );
}

export default UXSection;
