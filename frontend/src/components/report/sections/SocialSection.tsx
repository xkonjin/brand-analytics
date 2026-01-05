/**
 * =============================================================================
 * Social Media Section Component - Apple Liquid Glass UI
 * =============================================================================
 * Displays social media analysis including platform presence,
 * engagement metrics, and content performance with glassmorphism styling.
 * =============================================================================
 */

"use client";

import {
  Share2,
  Twitter,
  Linkedin,
  Instagram,
  Youtube,
  Users,
  Heart,
  MessageCircle,
} from "lucide-react";
import { ModuleSection } from "./ModuleSection";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface PlatformData {
  platform: string;
  url?: string;
  handle?: string;
  followers?: number;
  following?: number;
  posts_last_30_days?: number;
  engagement_rate?: number;
  avg_likes?: number;
  avg_comments?: number;
  avg_shares?: number;
  is_verified?: boolean;
  last_post_date?: string;
}

interface SocialData {
  score?: number;
  twitter_followers?: number;
  twitter_following?: number;
  twitter_engagement_rate?: number;
  linkedin_followers?: number;
  total_followers?: number;
  engagement_rate?: number;
  overall_engagement_rate?: number;
  posting_frequency?: string;
  posting_consistency?: string;
  platforms?: PlatformData[];
  platforms_found?: string[];
  platforms_active?: string[];
  platforms_dormant?: string[];
  platforms_missing?: string[];
  findings?: Array<{
    title: string;
    detail?: string;
    description?: string;
    severity: string;
    data?: Record<string, any>;
  }>;
  recommendations?: Array<{
    title: string;
    detail?: string;
    description?: string;
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
  if (num === undefined || num === null) return "N/A";
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

function formatPercent(num?: number): string {
  if (num === undefined || num === null) return "N/A";
  return `${num.toFixed(2)}%`;
}

// -----------------------------------------------------------------------------
// Helper - Get platform icon
// -----------------------------------------------------------------------------
function getPlatformIcon(platform: string) {
  const name = platform.toLowerCase();
  switch (name) {
    case "twitter":
    case "x":
      return <Twitter className="w-4 h-4 text-sky-400" />;
    case "linkedin":
      return <Linkedin className="w-4 h-4 text-blue-400" />;
    case "instagram":
      return <Instagram className="w-4 h-4 text-pink-400" />;
    case "youtube":
      return <Youtube className="w-4 h-4 text-red-400" />;
    default:
      return <Share2 className="w-4 h-4 text-white/40" />;
  }
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function SocialSection({ data, className = "" }: SocialSectionProps) {
  const twitterData = data.platforms?.find((p) => p.platform === "twitter");
  const linkedinData = data.platforms?.find((p) => p.platform === "linkedin");

  const metrics = [
    {
      label: "Total Followers",
      value: formatNumber(
        data.total_followers ||
          (twitterData?.followers || 0) + (linkedinData?.followers || 0),
      ),
      icon: <Users className="w-4 h-4 text-blue-400" />,
    },
    {
      label: "Engagement Rate",
      value: formatPercent(
        data.overall_engagement_rate ||
          data.engagement_rate ||
          twitterData?.engagement_rate,
      ),
      icon: <Heart className="w-4 h-4 text-red-400" />,
    },
    {
      label: "Twitter Followers",
      value: formatNumber(twitterData?.followers || data.twitter_followers),
      icon: <Twitter className="w-4 h-4 text-sky-400" />,
    },
    {
      label: "LinkedIn Followers",
      value: formatNumber(linkedinData?.followers || data.linkedin_followers),
      icon: <Linkedin className="w-4 h-4 text-blue-400" />,
    },
  ].filter((m) => m.value !== "N/A") as Array<{
    label: string;
    value: string | number;
    unit?: string;
    trend?: "up" | "down" | "stable";
  }>;

  // Platform presence - handle both object array and string array formats
  const platformObjects = data.platforms || [];
  const platformNames = (data.platforms_found || [])
    .concat(platformObjects.map((p: PlatformData) => p.platform))
    .filter((v, i, a) => v && a.indexOf(v) === i); // unique, non-null

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
      {platformNames.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
            Platforms Found
          </h3>
          <div className="flex flex-wrap gap-2">
            {platformNames.map((platform) => (
              <span
                key={platform}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-white/[0.04] backdrop-blur-xl 
                         border border-white/[0.06] rounded-md text-sm text-white/70
                         hover:bg-white/[0.06] transition-all duration-150"
              >
                {getPlatformIcon(platform)}
                {platform}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Platform Details Grid */}
      {platformObjects.length > 0 && (
        <div className="mt-4">
          <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wide mb-3">
            Platform Performance
          </h3>
          <div className="grid sm:grid-cols-2 gap-3">
            {platformObjects.slice(0, 4).map((platform) => (
              <div
                key={platform.platform}
                className="bg-white/[0.04] backdrop-blur-xl rounded-lg border border-white/[0.06] p-4
                         hover:bg-white/[0.06] transition-all duration-150"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-md bg-white/[0.04]">
                    {getPlatformIcon(platform.platform)}
                  </div>
                  <div>
                    <div className="font-medium text-white capitalize">
                      {platform.platform}
                    </div>
                    {platform.handle && (
                      <div className="text-xs text-white/40">
                        @{platform.handle}
                      </div>
                    )}
                  </div>
                  {platform.is_verified && (
                    <span className="ml-auto text-xs px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-md">
                      Verified
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {platform.followers !== undefined && (
                    <div>
                      <div className="text-white/40 text-xs">Followers</div>
                      <div className="text-white font-medium">
                        {formatNumber(platform.followers)}
                      </div>
                    </div>
                  )}
                  {platform.engagement_rate !== undefined && (
                    <div>
                      <div className="text-white/40 text-xs">Engagement</div>
                      <div className="text-white font-medium">
                        {formatPercent(platform.engagement_rate)}
                      </div>
                    </div>
                  )}
                  {platform.posts_last_30_days !== undefined && (
                    <div>
                      <div className="text-white/40 text-xs">Posts (30d)</div>
                      <div className="text-white font-medium">
                        {platform.posts_last_30_days}
                      </div>
                    </div>
                  )}
                  {platform.avg_likes !== undefined && (
                    <div>
                      <div className="text-white/40 text-xs">Avg Likes</div>
                      <div className="text-white font-medium">
                        {formatNumber(platform.avg_likes)}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </ModuleSection>
  );
}

export default SocialSection;
