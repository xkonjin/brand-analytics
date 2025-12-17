/**
 * =============================================================================
 * Social Media Section Component
 * =============================================================================
 * Displays social media analysis including platform presence,
 * engagement metrics, and content performance.
 * =============================================================================
 */

'use client';

import { Share2, Twitter, Linkedin, Users, Heart, MessageCircle } from 'lucide-react';
import { ModuleSection } from './ModuleSection';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface SocialData {
  score?: number;
  twitter_followers?: number;
  twitter_following?: number;
  twitter_engagement_rate?: number;
  linkedin_followers?: number;
  total_followers?: number;
  engagement_rate?: number;
  posting_frequency?: string;
  platforms_found?: string[];
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

interface SocialSectionProps {
  data: SocialData;
  className?: string;
}

// -----------------------------------------------------------------------------
// Helper - Format large numbers
// -----------------------------------------------------------------------------
function formatNumber(num?: number): string {
  if (num === undefined || num === null) return 'N/A';
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

function formatPercent(num?: number): string {
  if (num === undefined || num === null) return 'N/A';
  return `${num.toFixed(2)}%`;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function SocialSection({ data, className = '' }: SocialSectionProps) {
  // Build metrics
  const metrics = [
    {
      label: 'Total Followers',
      value: formatNumber(data.total_followers || (data.twitter_followers || 0) + (data.linkedin_followers || 0)),
      icon: <Users className="w-4 h-4 text-blue-500" />,
    },
    {
      label: 'Engagement Rate',
      value: formatPercent(data.engagement_rate || data.twitter_engagement_rate),
      icon: <Heart className="w-4 h-4 text-red-500" />,
    },
    {
      label: 'Twitter Followers',
      value: formatNumber(data.twitter_followers),
      icon: <Twitter className="w-4 h-4 text-sky-500" />,
    },
    {
      label: 'LinkedIn Followers',
      value: formatNumber(data.linkedin_followers),
      icon: <Linkedin className="w-4 h-4 text-blue-600" />,
    },
  ].filter(m => m.value !== 'N/A') as Array<{
    label: string;
    value: string | number;
    unit?: string;
    trend?: 'up' | 'down' | 'stable';
  }>;

  // Platform presence
  const platforms = data.platforms_found || [];

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
      id="social"
      moduleKey="social_media"
      title="Social Media"
      description="Platform presence, engagement metrics, and community activity analysis."
      score={data.score ?? 0}
      icon={<Share2 className="w-6 h-6" />}
      metrics={metrics}
      findings={findings}
      recommendations={recommendations}
      className={className}
    >
      {/* Platform presence */}
      {platforms.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
            Platforms Found
          </h3>
          <div className="flex flex-wrap gap-2">
            {platforms.map((platform) => (
              <span
                key={platform}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-700"
              >
                {platform.toLowerCase() === 'twitter' && <Twitter className="w-4 h-4 text-sky-500" />}
                {platform.toLowerCase() === 'linkedin' && <Linkedin className="w-4 h-4 text-blue-600" />}
                {platform}
              </span>
            ))}
          </div>
        </div>
      )}
    </ModuleSection>
  );
}

export default SocialSection;

