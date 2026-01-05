// =============================================================================
// Brand Analytics - TypeScript Type Definitions
// =============================================================================
// Generated from backend Pydantic models to ensure type safety between
// frontend and backend. Keep in sync with backend/app/models/*.py
// =============================================================================

// =============================================================================
// Common Types
// =============================================================================

export type SeverityLevel = "critical" | "high" | "medium" | "low" | "info";
export type ImpactLevel = "high" | "medium" | "low";
export type EffortLevel = "high" | "medium" | "low";

export interface Recommendation {
  title: string;
  description: string;
  priority: SeverityLevel;
  category: string;
  impact: ImpactLevel;
  effort: EffortLevel;
}

export interface Finding {
  title: string;
  detail: string;
  severity: SeverityLevel;
  data?: Record<string, unknown>;
}

// =============================================================================
// Analysis Status & Progress
// =============================================================================

export type AnalysisStatus = "pending" | "processing" | "completed" | "failed";
export type ModuleStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "skipped";

export interface AnalysisProgress {
  seo: ModuleStatus;
  social_media: ModuleStatus;
  brand_messaging: ModuleStatus;
  website_ux: ModuleStatus;
  ai_discoverability: ModuleStatus;
  content: ModuleStatus;
  team_presence: ModuleStatus;
  channel_fit: ModuleStatus;
  scorecard: ModuleStatus;
}

export interface AnalysisRequest {
  url: string;
  description?: string;
  industry?: string;
  email?: string;
}

export interface AnalysisResponse {
  id: string;
  url: string;
  status: AnalysisStatus;
  progress?: AnalysisProgress;
  scores?: Record<string, number>;
  overall_score?: number;
  created_at: string;
  completed_at?: string;
  processing_time_seconds?: number;
  pdf_url?: string;
  message?: string;
}

// =============================================================================
// SEO Report
// =============================================================================

export interface CoreWebVitals {
  lcp?: number; // Largest Contentful Paint (seconds)
  fid?: number; // First Input Delay (milliseconds)
  cls?: number; // Cumulative Layout Shift (score)
  fcp?: number; // First Contentful Paint (seconds)
  ttfb?: number; // Time to First Byte (seconds)
}

export interface MetaTagAnalysis {
  title?: string;
  title_length?: number;
  title_quality?: "good" | "too_short" | "too_long" | "missing";
  description?: string;
  description_length?: number;
  description_quality?: "good" | "too_short" | "too_long" | "missing";
  has_og_tags: boolean;
  has_twitter_cards: boolean;
  has_canonical: boolean;
}

export interface SEOReport {
  score: number;
  performance_score?: number;
  accessibility_score?: number;
  best_practices_score?: number;
  seo_score?: number;
  core_web_vitals?: CoreWebVitals;
  page_load_time?: number;
  mobile_friendly?: boolean;
  meta_tags?: MetaTagAnalysis;
  pages_indexed?: number;
  ranks_for_brand_name?: boolean;
  has_knowledge_panel?: boolean;
  has_schema_markup: boolean;
  schema_types_found: string[];
  domain_authority?: number;
  page_authority?: number;
  spam_score?: number;
  linking_domains?: number;
  total_backlinks?: number;
  findings: Finding[];
  recommendations: Recommendation[];
}

// =============================================================================
// Social Media Report
// =============================================================================

export interface SocialPlatformMetrics {
  platform: string;
  url?: string;
  handle?: string;
  followers?: number;
  following?: number;
  posts_count?: number;
  posts_last_30_days?: number;
  engagement_rate?: number;
  avg_likes?: number;
  avg_comments?: number;
  avg_shares?: number;
  avg_views?: number;
  last_post_date?: string;
  is_verified: boolean;
  profile_bio?: string;
  subscribers?: number;
  total_views?: number;
}

export interface SocialMediaReport {
  score: number;
  platforms: SocialPlatformMetrics[];
  total_followers: number;
  platforms_active: number;
  platforms_dormant: number;
  platforms_missing: string[];
  overall_engagement_rate?: number;
  engagement_trend?: "improving" | "stable" | "declining";
  average_posts_per_week?: number;
  posting_consistency?: "consistent" | "irregular" | "dormant";
  has_discord: boolean;
  discord_members?: number;
  discord_url?: string;
  has_telegram: boolean;
  telegram_members?: number;
  telegram_url?: string;
  findings: Finding[];
  recommendations: Recommendation[];
}

// =============================================================================
// Brand Messaging Report
// =============================================================================

export interface BrandArchetype {
  primary: string;
  secondary?: string;
  confidence: number;
  description: string;
  example_brands: string[];
}

export interface BrandMessagingReport {
  score: number;
  archetype?: BrandArchetype;
  value_proposition?: string;
  value_proposition_clarity?: number;
  tagline?: string;
  tone_keywords: string[];
  tone_description?: string;
  tone_consistency?: number;
  readability_score?: number;
  reading_grade_level?: number;
  is_jargon_heavy: boolean;
  jargon_examples: string[];
  key_themes: string[];
  emotional_hooks: string[];
  findings: Finding[];
  recommendations: Recommendation[];
}

// =============================================================================
// Website UX Report
// =============================================================================

export interface CTAAnalysis {
  cta_text?: string;
  is_visible_above_fold: boolean;
  has_contrast: boolean;
  cta_count: number;
  primary_cta_present: boolean;
}

export interface UXReport {
  score: number;
  first_impression_clarity?: number;
  answers_what: boolean;
  answers_who: boolean;
  answers_why: boolean;
  cta_analysis?: CTAAnalysis;
  menu_items_count?: number;
  has_clear_navigation: boolean;
  has_search: boolean;
  clicks_to_pricing?: number;
  clicks_to_contact?: number;
  has_testimonials: boolean;
  has_client_logos: boolean;
  has_case_studies: boolean;
  has_security_badges: boolean;
  has_social_proof_numbers: boolean;
  trust_signals_count: number;
  mobile_responsive: boolean;
  accessibility_issues: string[];
  has_privacy_policy: boolean;
  has_terms_of_service: boolean;
  findings: Finding[];
  recommendations: Recommendation[];
}

// =============================================================================
// AI Discoverability Report
// =============================================================================

export interface AIDiscoverabilityReport {
  score: number;
  has_wikipedia_page: boolean;
  wikipedia_url?: string;
  wikipedia_quality?: "stub" | "good" | "comprehensive";
  has_knowledge_panel: boolean;
  appears_in_top_10: boolean;
  brand_search_position?: number;
  mentioned_in_major_publications: boolean;
  publication_mentions: string[];
  has_faq_schema: boolean;
  has_organization_schema: boolean;
  has_product_schema: boolean;
  schema_types: string[];
  blog_post_count?: number;
  has_documentation: boolean;
  has_help_center: boolean;
  content_depth_score?: number;
  ai_readiness_level: "high" | "medium" | "low";
  findings: Finding[];
  recommendations: Recommendation[];
}

// =============================================================================
// Content Report
// =============================================================================

export interface PostAnalysis {
  platform: string;
  date?: string;
  content_preview?: string;
  likes: number;
  comments: number;
  shares: number;
  content_type: "text" | "image" | "video" | "link";
  sentiment?: "positive" | "neutral" | "negative";
}

export interface ContentReport {
  score: number;
  recent_posts: PostAnalysis[];
  content_mix: Record<string, number>;
  overall_sentiment?: "positive" | "neutral" | "negative";
  sentiment_breakdown: Record<string, number>;
  best_performing_post?: PostAnalysis;
  worst_performing_post?: PostAnalysis;
  avg_engagement_per_post?: number;
  uses_images: boolean;
  uses_videos: boolean;
  uses_threads: boolean;
  multimedia_percentage?: number;
  common_topics: string[];
  hashtags_used: string[];
  findings: Finding[];
  recommendations: Recommendation[];
}

// =============================================================================
// Team Presence Report
// =============================================================================

export interface TeamMember {
  name: string;
  role?: string;
  linkedin_url?: string;
  twitter_url?: string;
  twitter_followers?: number;
  notable_background?: string;
}

export interface TeamPresenceReport {
  score: number;
  team_size_estimate?: string;
  team_members: TeamMember[];
  has_team_page: boolean;
  team_page_url?: string;
  linkedin_followers?: number;
  linkedin_url?: string;
  linkedin_active: boolean;
  founders_identified: number;
  founder_twitter_presence: boolean;
  founder_combined_following?: number;
  has_notable_background: boolean;
  has_advisors_listed: boolean;
  has_investors_listed: boolean;
  uses_real_identities: boolean;
  photos_on_website: boolean;
  findings: Finding[];
  recommendations: Recommendation[];
}

// =============================================================================
// Channel Fit Report
// =============================================================================

export interface ChannelScore {
  channel: string;
  score: number;
  suitability: "high" | "medium" | "low";
  rationale: string;
  current_presence: boolean;
  recommendation?: string;
}

export interface ChannelFitReport {
  score: number;
  channels: ChannelScore[];
  top_channels: string[];
  underutilized_channels: string[];
  low_priority_channels: string[];
  product_type?: string;
  target_audience?: string;
  industry?: string;
  findings: Finding[];
  recommendations: Recommendation[];
}

// =============================================================================
// Scorecard & Benchmark
// =============================================================================

export interface BenchmarkComparison {
  score: number;
  benchmark: number;
  difference: number;
  percentile: "above" | "below" | "at";
  label: string;
}

export interface ScoreCard {
  overall_score: number;
  scores: Record<string, number>;
  grade: string; // A+, A, B, C, D, F
  summary: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  benchmark_comparison: Record<string, BenchmarkComparison>;
  top_recommendations: Recommendation[];
  quick_wins: Recommendation[];
}

// =============================================================================
// Full Report
// =============================================================================

export interface FullReport {
  generated_at: string;
  url: string;
  brand_name?: string;
  brand_logo_url?: string;
  seo: SEOReport;
  social_media: SocialMediaReport;
  brand_messaging: BrandMessagingReport;
  website_ux: UXReport;
  ai_discoverability: AIDiscoverabilityReport;
  content: ContentReport;
  team_presence: TeamPresenceReport;
  channel_fit: ChannelFitReport;
  scorecard: ScoreCard;
}

// =============================================================================
// API Response Types
// =============================================================================

export interface ReportResponse {
  id: string;
  url: string;
  overall_score: number;
  scores: Record<string, number>;
  report: FullReport;
}

export interface ProgressResponse {
  id: string;
  status: AnalysisStatus;
  modules: Record<string, ModuleStatus>;
  completion_percentage: number;
  overall_score?: number;
  completed?: boolean;
  error?: string;
}

// =============================================================================
// Utility Types
// =============================================================================

export type ModuleName =
  | "seo"
  | "social_media"
  | "brand_messaging"
  | "website_ux"
  | "ai_discoverability"
  | "content"
  | "team_presence"
  | "channel_fit";

export const MODULE_NAMES: ModuleName[] = [
  "seo",
  "social_media",
  "brand_messaging",
  "website_ux",
  "ai_discoverability",
  "content",
  "team_presence",
  "channel_fit",
];

export const MODULE_DISPLAY_NAMES: Record<ModuleName, string> = {
  seo: "SEO Performance",
  social_media: "Social Media",
  brand_messaging: "Brand Messaging",
  website_ux: "Website UX",
  ai_discoverability: "AI Discoverability",
  content: "Content Analysis",
  team_presence: "Team Presence",
  channel_fit: "Channel Fit",
};

export const MODULE_ICONS: Record<ModuleName, string> = {
  seo: "🔍",
  social_media: "📱",
  brand_messaging: "🎭",
  website_ux: "🎨",
  ai_discoverability: "🤖",
  content: "📝",
  team_presence: "👥",
  channel_fit: "📊",
};

// Grade utilities
export type Grade = "A+" | "A" | "B" | "C" | "D" | "F";

export function scoreToGrade(score: number): Grade {
  if (score >= 90) return "A+";
  if (score >= 80) return "A";
  if (score >= 70) return "B";
  if (score >= 60) return "C";
  if (score >= 50) return "D";
  return "F";
}

export function gradeToColor(grade: Grade): string {
  const colors: Record<Grade, string> = {
    "A+": "text-emerald-400",
    A: "text-green-400",
    B: "text-blue-400",
    C: "text-yellow-400",
    D: "text-orange-400",
    F: "text-red-400",
  };
  return colors[grade];
}

export function scoreToRating(score: number): string {
  if (score >= 90) return "excellent";
  if (score >= 75) return "good";
  if (score >= 60) return "fair";
  if (score >= 40) return "poor";
  return "critical";
}
