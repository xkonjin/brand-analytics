/**
 * =============================================================================
 * Report Page
 * =============================================================================
 * Main report page that displays the comprehensive brand analysis.
 * Uses new modular components for a publication-quality layout.
 * =============================================================================
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

// Layout components
import { ReportHeader } from '@/components/report/layout/ReportHeader';
import { ReportNav } from '@/components/report/layout/ReportNav';
import { ReportFooter } from '@/components/report/layout/ReportFooter';

// Section components
import { ExecutiveSummary } from '@/components/report/sections/ExecutiveSummary';
import { ScoreOverview } from '@/components/report/sections/ScoreOverview';
import { SEOSection } from '@/components/report/sections/SEOSection';
import { SocialSection } from '@/components/report/sections/SocialSection';
import { BrandSection } from '@/components/report/sections/BrandSection';
import { UXSection } from '@/components/report/sections/UXSection';
import { AISection } from '@/components/report/sections/AISection';
import { ContentSection } from '@/components/report/sections/ContentSection';
import { TeamSection } from '@/components/report/sections/TeamSection';
import { ChannelSection } from '@/components/report/sections/ChannelSection';
import { ActionPlan } from '@/components/report/sections/ActionPlan';

import { isQuickWin } from '@/lib/frameworks';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface Report {
  id: string;
  url: string;
  overall_score: number;
  scores: Record<string, number>;
  report: {
    seo?: any;
    social_media?: any;
    brand_messaging?: any;
    website_ux?: any;
    ai_discoverability?: any;
    content?: any;
    team_presence?: any;
    channel_fit?: any;
    scorecard?: {
      grade?: string;
      summary?: string;
      strengths?: string[];
      weaknesses?: string[];
      top_recommendations?: Array<{
        title: string;
        description: string;
        priority: string;
        category: string;
        impact: string;
        effort: string;
      }>;
    };
  };
  created_at?: string;
  processing_time?: number;
}

interface Recommendation {
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
}

// -----------------------------------------------------------------------------
// Loading Skeleton
// -----------------------------------------------------------------------------
function LoadingSkeleton() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center"
          >
            <div className="w-16 h-16 rounded-full bg-slate-200 flex items-center justify-center mx-auto mb-6">
              <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
            </div>
            <h2 className="text-xl font-semibold text-slate-900 mb-2">
              Loading Report
            </h2>
            <p className="text-slate-500">
              Preparing your brand analysis...
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Error State
// -----------------------------------------------------------------------------
function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center max-w-md mx-auto px-4"
      >
        <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-6">
          <span className="text-2xl">⚠️</span>
        </div>
        <h2 className="text-xl font-semibold text-slate-900 mb-2">
          Failed to Load Report
        </h2>
        <p className="text-slate-600 mb-6">
          We couldn't retrieve your brand analysis. This might be a temporary issue.
        </p>
        <button onClick={onRetry} className="btn-primary">
          Try Again
        </button>
      </motion.div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Main Component
// -----------------------------------------------------------------------------
export default function ReportPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { id } = params;

  // Fetch the full report data from the API
  const { data, isLoading, error, refetch } = useQuery<Report>({
    queryKey: ['report', id],
    queryFn: async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analysis/${id}/report`
      );
      if (!res.ok) throw new Error('Failed to fetch report');
      return res.json();
    },
  });

  // Loading state
  if (isLoading) {
    return <LoadingSkeleton />;
  }

  // Error state
  if (error || !data) {
    return <ErrorState onRetry={() => refetch()} />;
  }

  // Extract report data
  const { url, overall_score, scores, report, created_at, processing_time } = data;
  const scorecard = report?.scorecard || {};

  // Collect all recommendations from all modules
  const allRecommendations: Recommendation[] = [];
  
  // Add top recommendations from scorecard
  if (scorecard.top_recommendations) {
    allRecommendations.push(
      ...scorecard.top_recommendations.map((rec: any) => ({
        title: rec.title || '',
        description: rec.description || '',
        priority: (rec.priority || 'medium') as 'critical' | 'high' | 'medium' | 'low',
        category: rec.category || 'General',
        impact: (rec.impact || 'medium') as 'high' | 'medium' | 'low',
        effort: (rec.effort || 'medium') as 'high' | 'medium' | 'low',
      }))
    );
  }

  // Add module-specific recommendations
  const modules = [
    report?.seo,
    report?.social_media,
    report?.brand_messaging,
    report?.website_ux,
    report?.ai_discoverability,
    report?.content,
    report?.team_presence,
    report?.channel_fit,
  ];

  modules.forEach((module) => {
    if (module?.recommendations) {
      allRecommendations.push(
        ...module.recommendations.map((rec: any) => ({
          title: rec.title || '',
          description: rec.description || '',
          priority: (rec.priority || 'medium') as 'critical' | 'high' | 'medium' | 'low',
          category: rec.category || 'General',
          impact: (rec.impact || 'medium') as 'high' | 'medium' | 'low',
          effort: (rec.effort || 'medium') as 'high' | 'medium' | 'low',
        }))
      );
    }
  });

  // Deduplicate recommendations by title
  const uniqueRecs = allRecommendations.reduce((acc, rec) => {
    if (!acc.find((r) => r.title === rec.title)) {
      acc.push(rec);
    }
    return acc;
  }, [] as Recommendation[]);

  // Count strengths, issues, and quick wins
  const strengthsCount = scorecard.strengths?.length || 0;
  const issuesCount = scorecard.weaknesses?.length || 0;
  const quickWinsCount = uniqueRecs.filter((r) =>
    isQuickWin(r.impact, r.effort)
  ).length;

  // Determine which sections to show based on available data
  const visibleSections = ['summary'];
  if (Object.keys(scores || {}).length > 0) visibleSections.push('seo', 'social', 'brand', 'ux', 'ai', 'content', 'team', 'channels');
  if (uniqueRecs.length > 0) visibleSections.push('action-plan');

  return (
    <main className="min-h-screen bg-slate-50">
      {/* Fixed Header */}
      <ReportHeader
        analysisId={id}
        url={url}
        generatedAt={created_at}
      />

      {/* Main content with sidebar navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex gap-8">
          {/* Sticky sidebar nav - hidden on mobile */}
          <ReportNav
            visibleSections={visibleSections}
            className="py-8"
          />

          {/* Main content area */}
          <div className="flex-1 min-w-0">
            {/* Executive Summary */}
            <ExecutiveSummary
              score={overall_score || 0}
              summary={scorecard.summary}
              strengthsCount={strengthsCount}
              issuesCount={issuesCount}
              quickWinsCount={quickWinsCount}
              url={url}
            />

            {/* Score Overview with Radar Chart */}
            <ScoreOverview scores={scores || {}} />

            {/* Module Sections */}
            {report?.seo && (
              <SEOSection data={{ ...report.seo, score: scores?.seo }} />
            )}

            {report?.social_media && (
              <SocialSection data={{ ...report.social_media, score: scores?.social_media }} />
            )}

            {report?.brand_messaging && (
              <BrandSection data={{ ...report.brand_messaging, score: scores?.brand_messaging }} />
            )}

            {report?.website_ux && (
              <UXSection data={{ ...report.website_ux, score: scores?.website_ux }} />
            )}

            {report?.ai_discoverability && (
              <AISection data={{ ...report.ai_discoverability, score: scores?.ai_discoverability }} />
            )}

            {report?.content && (
              <ContentSection data={{ ...report.content, score: scores?.content }} />
            )}

            {report?.team_presence && (
              <TeamSection data={{ ...report.team_presence, score: scores?.team_presence }} />
            )}

            {report?.channel_fit && (
              <ChannelSection data={{ ...report.channel_fit, score: scores?.channel_fit }} />
            )}

            {/* Action Plan with all recommendations */}
            <ActionPlan recommendations={uniqueRecs} />
          </div>
        </div>
      </div>

      {/* Footer with methodology */}
      <ReportFooter
        analysisId={id}
        processingTime={processing_time}
      />
    </main>
  );
}
