/**
 * =============================================================================
 * Industry Benchmarks
 * =============================================================================
 * Benchmark data for comparing brand performance against industry averages.
 * Based on research from Sprout Social, Moz, Google, and a16z reports.
 * =============================================================================
 */

/**
 * Module benchmark data with industry context
 */
export interface ModuleBenchmark {
  key: string;
  label: string;
  shortLabel: string;
  benchmark: number;
  description: string;
  methodology: string;
  sources: string[];
}

/**
 * Benchmark data for all 8 analysis modules
 * Benchmarks represent "good" performance (70th percentile)
 */
export const MODULE_BENCHMARKS: ModuleBenchmark[] = [
  {
    key: 'seo',
    label: 'SEO Performance',
    shortLabel: 'SEO',
    benchmark: 65,
    description: 'Technical SEO health, Core Web Vitals, and search visibility',
    methodology: "Based on Google's Core Web Vitals thresholds, Moz domain authority benchmarks, and PageSpeed Insights scoring methodology.",
    sources: ['Google PageSpeed Insights', 'Moz', 'Ahrefs'],
  },
  {
    key: 'social_media',
    label: 'Social Media',
    shortLabel: 'Social',
    benchmark: 55,
    description: 'Social platform presence, engagement rates, and community activity',
    methodology: 'Engagement rate benchmarks from Sprout Social industry reports. Follower counts weighted by platform relevance.',
    sources: ['Sprout Social', 'Hootsuite', 'Buffer'],
  },
  {
    key: 'brand_messaging',
    label: 'Brand Messaging',
    shortLabel: 'Messaging',
    benchmark: 60,
    description: 'Brand archetype clarity, value proposition, and messaging consistency',
    methodology: 'StoryBrand clarity framework combined with Flesch-Kincaid readability scores and tone consistency analysis.',
    sources: ['StoryBrand', 'Nielsen Norman Group'],
  },
  {
    key: 'website_ux',
    label: 'Website UX',
    shortLabel: 'UX',
    benchmark: 70,
    description: 'User experience, conversion optimization, and trust signals',
    methodology: 'Nielsen Norman Group heuristics evaluation combined with conversion rate optimization best practices.',
    sources: ['Nielsen Norman Group', 'Baymard Institute'],
  },
  {
    key: 'ai_discoverability',
    label: 'AI Discoverability',
    shortLabel: 'AI Ready',
    benchmark: 40,
    description: 'Visibility in AI assistants, Wikipedia presence, and structured data',
    methodology: 'Schema.org adoption rates, Wikipedia notability guidelines, and testing against major AI assistants.',
    sources: ['Schema.org', 'Wikipedia', 'OpenAI'],
  },
  {
    key: 'content',
    label: 'Content Quality',
    shortLabel: 'Content',
    benchmark: 60,
    description: 'Content strategy, posting consistency, and engagement patterns',
    methodology: 'Content Marketing Institute quality criteria combined with engagement rate analysis.',
    sources: ['Content Marketing Institute', 'HubSpot'],
  },
  {
    key: 'team_presence',
    label: 'Team Presence',
    shortLabel: 'Team',
    benchmark: 50,
    description: 'Team visibility, founder presence, and professional credibility',
    methodology: 'LinkedIn company presence benchmarks and founder visibility metrics.',
    sources: ['LinkedIn', 'Crunchbase'],
  },
  {
    key: 'channel_fit',
    label: 'Channel Fit',
    shortLabel: 'Channels',
    benchmark: 55,
    description: 'Marketing channel optimization and audience alignment',
    methodology: 'a16z go-to-market framework for channel selection and optimization.',
    sources: ['a16z', 'First Round Capital'],
  },
];

/**
 * Get benchmark for a specific module
 */
export function getBenchmark(moduleKey: string): ModuleBenchmark | undefined {
  return MODULE_BENCHMARKS.find((b) => b.key === moduleKey);
}

/**
 * Get benchmark value for a module
 */
export function getBenchmarkValue(moduleKey: string): number {
  const benchmark = getBenchmark(moduleKey);
  return benchmark?.benchmark ?? 50;
}

/**
 * Compare score against benchmark
 */
export function compareToBenchmark(
  score: number,
  moduleKey: string
): {
  difference: number;
  percentile: 'above' | 'at' | 'below';
  label: string;
} {
  const benchmarkValue = getBenchmarkValue(moduleKey);
  const difference = score - benchmarkValue;
  
  let percentile: 'above' | 'at' | 'below';
  let label: string;
  
  if (difference > 5) {
    percentile = 'above';
    label = `${Math.round(difference)} pts above average`;
  } else if (difference < -5) {
    percentile = 'below';
    label = `${Math.abs(Math.round(difference))} pts below average`;
  } else {
    percentile = 'at';
    label = 'At industry average';
  }
  
  return { difference, percentile, label };
}

/**
 * Get all benchmarks as a simple key-value object
 */
export function getBenchmarksMap(): Record<string, number> {
  return MODULE_BENCHMARKS.reduce(
    (acc, b) => ({ ...acc, [b.key]: b.benchmark }),
    {} as Record<string, number>
  );
}

/**
 * Platform-specific engagement rate benchmarks
 * Based on Sprout Social and Hootsuite 2024 reports
 */
export const ENGAGEMENT_BENCHMARKS = {
  twitter: {
    good: 0.5,      // 0.5% engagement rate is good
    excellent: 1.0, // 1%+ is excellent
    average: 0.2,   // 0.2% is average
  },
  instagram: {
    good: 3.0,
    excellent: 6.0,
    average: 1.5,
  },
  linkedin: {
    good: 2.0,
    excellent: 4.0,
    average: 0.5,
  },
  facebook: {
    good: 0.5,
    excellent: 1.0,
    average: 0.1,
  },
  tiktok: {
    good: 5.0,
    excellent: 10.0,
    average: 3.0,
  },
};

/**
 * Core Web Vitals thresholds from Google
 */
export const CORE_WEB_VITALS_THRESHOLDS = {
  lcp: {
    good: 2.5,      // seconds
    needsImprovement: 4.0,
  },
  fid: {
    good: 100,      // milliseconds
    needsImprovement: 300,
  },
  cls: {
    good: 0.1,      // score
    needsImprovement: 0.25,
  },
  fcp: {
    good: 1.8,      // seconds
    needsImprovement: 3.0,
  },
  ttfb: {
    good: 0.8,      // seconds
    needsImprovement: 1.8,
  },
};

/**
 * Readability score benchmarks (Flesch Reading Ease)
 */
export const READABILITY_BENCHMARKS = {
  veryEasy: 90,     // 5th grade
  easy: 80,         // 6th grade
  fairlyEasy: 70,   // 7th grade
  standard: 60,     // 8th-9th grade (ideal for marketing)
  fairlyDifficult: 50,
  difficult: 30,
  veryDifficult: 0,
};

/**
 * Get readability interpretation
 */
export function getReadabilityLabel(score: number): string {
  if (score >= 90) return 'Very Easy (5th grade)';
  if (score >= 80) return 'Easy (6th grade)';
  if (score >= 70) return 'Fairly Easy (7th grade)';
  if (score >= 60) return 'Standard (8th-9th grade)';
  if (score >= 50) return 'Fairly Difficult';
  if (score >= 30) return 'Difficult';
  return 'Very Difficult';
}

