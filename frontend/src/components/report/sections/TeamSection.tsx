/**
 * =============================================================================
 * Team Presence Section Component
 * =============================================================================
 * Displays team visibility analysis including founder presence,
 * team member profiles, and professional credibility.
 * =============================================================================
 */

'use client';

import { Users, Linkedin, Award, Building } from 'lucide-react';
import { ModuleSection } from './ModuleSection';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface TeamMember {
  name?: string;
  role?: string;
  linkedin_url?: string;
  credibility_score?: number;
}

interface TeamData {
  score?: number;
  founder_visibility_score?: number;
  team_size?: number;
  linkedin_presence?: boolean;
  team_members?: TeamMember[];
  leadership_visibility?: number;
  company_credibility_score?: number;
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

interface TeamSectionProps {
  data: TeamData;
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function TeamSection({ data, className = '' }: TeamSectionProps) {
  // Build metrics
  const metrics = [
    {
      label: 'Founder Visibility',
      value: data.founder_visibility_score ?? 0,
      unit: '/100',
    },
    {
      label: 'Team Size',
      value: data.team_size ?? 0,
      subtitle: 'identified members',
    },
    {
      label: 'Leadership Visibility',
      value: data.leadership_visibility ?? 0,
      unit: '/100',
    },
    {
      label: 'Credibility Score',
      value: data.company_credibility_score ?? 0,
      unit: '/100',
    },
  ].filter(m => m.value !== undefined && m.value !== 0) as Array<{
    label: string;
    value: string | number;
    unit?: string;
    subtitle?: string;
  }>;

  // Transform findings
  const findings = (data.findings || []).map(f => ({
    title: f.title,
    description: f.description || f.detail || '',
    severity: f.severity as 'critical' | 'high' | 'medium' | 'low' | 'info' | 'success',
    data: f.data as Record<string, string | number> | undefined,
  }));

  // Transform recommendations
  const recommendations = (data.recommendations || []).map(r => ({
    title: r.title,
    description: r.description || r.detail || '',
    priority: r.priority as 'critical' | 'high' | 'medium' | 'low',
    category: r.category,
    impact: r.impact as 'high' | 'medium' | 'low',
    effort: r.effort as 'high' | 'medium' | 'low',
  }));

  return (
    <ModuleSection
      id="team"
      moduleKey="team_presence"
      title="Team Presence"
      description="Founder visibility, team profiles, and professional credibility assessment."
      score={data.score ?? 0}
      icon={<Users className="w-6 h-6" />}
      metrics={metrics}
      findings={findings}
      recommendations={recommendations}
      className={className}
    >
      {/* Team Members */}
      {data.team_members && data.team_members.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
            Key Team Members
          </h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.team_members.slice(0, 6).map((member, idx) => (
              <div
                key={member.name || idx}
                className="bg-white rounded-lg border border-slate-200 p-4 flex items-center gap-3"
              >
                <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-500">
                  <Users className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-slate-900 truncate">
                    {member.name || 'Unknown'}
                  </div>
                  <div className="text-sm text-slate-500 truncate">
                    {member.role || 'Team Member'}
                  </div>
                </div>
                {member.linkedin_url && (
                  <a
                    href={member.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700"
                  >
                    <Linkedin className="w-4 h-4" />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* LinkedIn Presence Indicator */}
      {data.linkedin_presence !== undefined && (
        <div className="mt-4">
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg ${
            data.linkedin_presence
              ? 'bg-blue-50 text-blue-700 border border-blue-100'
              : 'bg-slate-50 text-slate-600 border border-slate-200'
          }`}>
            <Linkedin className="w-4 h-4" />
            <span className="text-sm font-medium">
              {data.linkedin_presence ? 'LinkedIn presence confirmed' : 'No LinkedIn presence detected'}
            </span>
          </div>
        </div>
      )}
    </ModuleSection>
  );
}

export default TeamSection;

