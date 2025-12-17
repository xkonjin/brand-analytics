/**
 * =============================================================================
 * Marketing Frameworks
 * =============================================================================
 * Definitions for marketing theory frameworks used in the analysis.
 * Includes brand archetypes, content strategies, and channel fit models.
 * =============================================================================
 */

/**
 * The 12 Jungian Brand Archetypes
 * Based on Carl Jung's work and adapted for brand strategy
 */
export interface BrandArchetype {
  id: string;
  name: string;
  tagline: string;
  description: string;
  traits: string[];
  exampleBrands: string[];
  color: string;
  icon: string;
}

export const BRAND_ARCHETYPES: BrandArchetype[] = [
  {
    id: 'hero',
    name: 'Hero',
    tagline: 'Where there\'s a will, there\'s a way',
    description: 'Courageous, bold, and inspirational. Seeks to prove worth through mastery and achievement.',
    traits: ['Brave', 'Determined', 'Inspiring', 'Ambitious', 'Disciplined'],
    exampleBrands: ['Nike', 'FedEx', 'BMW', 'Under Armour'],
    color: '#dc2626',
    icon: '🏆',
  },
  {
    id: 'outlaw',
    name: 'Outlaw',
    tagline: 'Rules are made to be broken',
    description: 'Rebellious, disruptive, and liberating. Challenges the status quo and breaks conventions.',
    traits: ['Rebellious', 'Bold', 'Disruptive', 'Independent', 'Revolutionary'],
    exampleBrands: ['Harley-Davidson', 'Virgin', 'Diesel', 'Uber'],
    color: '#1f2937',
    icon: '⚡',
  },
  {
    id: 'magician',
    name: 'Magician',
    tagline: 'Making dreams come true',
    description: 'Visionary, transformative, and innovative. Makes the impossible possible through knowledge and vision.',
    traits: ['Innovative', 'Visionary', 'Transformative', 'Imaginative', 'Charismatic'],
    exampleBrands: ['Apple', 'Disney', 'Tesla', 'Dyson'],
    color: '#7c3aed',
    icon: '✨',
  },
  {
    id: 'everyman',
    name: 'Everyman',
    tagline: 'Everyone is created equal',
    description: 'Relatable, authentic, and down-to-earth. Connects through belonging and common values.',
    traits: ['Authentic', 'Relatable', 'Humble', 'Friendly', 'Practical'],
    exampleBrands: ['IKEA', 'Target', 'eBay', 'Budweiser'],
    color: '#78716c',
    icon: '🤝',
  },
  {
    id: 'lover',
    name: 'Lover',
    tagline: 'You\'re the only one',
    description: 'Passionate, sensual, and intimate. Creates deep emotional connections and appreciation for beauty.',
    traits: ['Passionate', 'Sensual', 'Romantic', 'Devoted', 'Appreciative'],
    exampleBrands: ['Chanel', 'Victoria\'s Secret', 'Godiva', 'Hallmark'],
    color: '#be185d',
    icon: '❤️',
  },
  {
    id: 'jester',
    name: 'Jester',
    tagline: 'You only live once',
    description: 'Fun, playful, and entertaining. Lives in the moment with joy and brings levity to life.',
    traits: ['Fun', 'Playful', 'Humorous', 'Lighthearted', 'Entertaining'],
    exampleBrands: ['Old Spice', 'M&M\'s', 'Geico', 'Dollar Shave Club'],
    color: '#f59e0b',
    icon: '🎭',
  },
  {
    id: 'caregiver',
    name: 'Caregiver',
    tagline: 'Love your neighbor as yourself',
    description: 'Nurturing, compassionate, and protective. Driven by the desire to help and protect others.',
    traits: ['Nurturing', 'Compassionate', 'Caring', 'Supportive', 'Selfless'],
    exampleBrands: ['Johnson & Johnson', 'Volvo', 'UNICEF', 'Pampers'],
    color: '#059669',
    icon: '🤲',
  },
  {
    id: 'ruler',
    name: 'Ruler',
    tagline: 'Power isn\'t everything, it\'s the only thing',
    description: 'Authoritative, refined, and successful. Provides order, stability, and leadership.',
    traits: ['Authoritative', 'Refined', 'Successful', 'Confident', 'Responsible'],
    exampleBrands: ['Mercedes-Benz', 'Rolex', 'Microsoft', 'American Express'],
    color: '#1e3a8a',
    icon: '👑',
  },
  {
    id: 'creator',
    name: 'Creator',
    tagline: 'If you can imagine it, it can be done',
    description: 'Creative, artistic, and innovative. Values self-expression and bringing visions to life.',
    traits: ['Creative', 'Artistic', 'Innovative', 'Expressive', 'Non-conformist'],
    exampleBrands: ['Lego', 'Adobe', 'Pinterest', 'Crayola'],
    color: '#ea580c',
    icon: '🎨',
  },
  {
    id: 'innocent',
    name: 'Innocent',
    tagline: 'Free to be you and me',
    description: 'Pure, optimistic, and simple. Seeks happiness, goodness, and paradise.',
    traits: ['Pure', 'Optimistic', 'Simple', 'Honest', 'Happy'],
    exampleBrands: ['Coca-Cola', 'Dove', 'Nintendo', 'Whole Foods'],
    color: '#0ea5e9',
    icon: '🌸',
  },
  {
    id: 'sage',
    name: 'Sage',
    tagline: 'The truth will set you free',
    description: 'Wise, knowledgeable, and trusted. Seeks truth and uses intelligence to understand the world.',
    traits: ['Wise', 'Knowledgeable', 'Thoughtful', 'Trusted', 'Analytical'],
    exampleBrands: ['Google', 'BBC', 'TED', 'The Economist'],
    color: '#4f46e5',
    icon: '📚',
  },
  {
    id: 'explorer',
    name: 'Explorer',
    tagline: 'Don\'t fence me in',
    description: 'Adventurous, independent, and pioneering. Seeks discovery, freedom, and new experiences.',
    traits: ['Adventurous', 'Independent', 'Curious', 'Bold', 'Pioneering'],
    exampleBrands: ['Jeep', 'The North Face', 'Starbucks', 'GoPro'],
    color: '#15803d',
    icon: '🧭',
  },
];

/**
 * Get archetype by ID
 */
export function getArchetype(id: string): BrandArchetype | undefined {
  return BRAND_ARCHETYPES.find((a) => a.id.toLowerCase() === id.toLowerCase());
}

/**
 * Get archetype by name
 */
export function getArchetypeByName(name: string): BrandArchetype | undefined {
  return BRAND_ARCHETYPES.find(
    (a) => a.name.toLowerCase() === name.toLowerCase()
  );
}

/**
 * Marketing channel definitions with suitability criteria
 */
export interface MarketingChannel {
  id: string;
  name: string;
  category: 'paid' | 'organic' | 'owned' | 'earned';
  description: string;
  bestFor: string[];
  considerations: string[];
}

export const MARKETING_CHANNELS: MarketingChannel[] = [
  {
    id: 'seo',
    name: 'SEO / Organic Search',
    category: 'organic',
    description: 'Optimizing for search engine visibility',
    bestFor: ['Information-seeking audiences', 'Long-term growth', 'High-intent users'],
    considerations: ['Requires content investment', 'Results take 3-6 months'],
  },
  {
    id: 'content',
    name: 'Content Marketing',
    category: 'owned',
    description: 'Creating valuable content to attract and engage audiences',
    bestFor: ['Thought leadership', 'Complex products', 'B2B audiences'],
    considerations: ['Consistency required', 'Distribution strategy needed'],
  },
  {
    id: 'social_organic',
    name: 'Organic Social Media',
    category: 'organic',
    description: 'Building community through unpaid social presence',
    bestFor: ['Brand awareness', 'Community building', 'Customer engagement'],
    considerations: ['Platform algorithm changes', 'Requires consistent posting'],
  },
  {
    id: 'social_paid',
    name: 'Paid Social Ads',
    category: 'paid',
    description: 'Targeted advertising on social platforms',
    bestFor: ['Quick visibility', 'Precise targeting', 'B2C products'],
    considerations: ['Ongoing budget needed', 'Ad fatigue'],
  },
  {
    id: 'email',
    name: 'Email Marketing',
    category: 'owned',
    description: 'Direct communication with subscribers',
    bestFor: ['Retention', 'Nurturing leads', 'Product updates'],
    considerations: ['List building required', 'Deliverability challenges'],
  },
  {
    id: 'pr',
    name: 'PR / Media Coverage',
    category: 'earned',
    description: 'Earning press coverage and media mentions',
    bestFor: ['Credibility building', 'Major announcements', 'B2B'],
    considerations: ['Unpredictable results', 'Story angle needed'],
  },
  {
    id: 'partnerships',
    name: 'Strategic Partnerships',
    category: 'earned',
    description: 'Collaborating with complementary brands',
    bestFor: ['Audience expansion', 'Credibility', 'Distribution'],
    considerations: ['Partner alignment needed', 'Negotiation time'],
  },
  {
    id: 'community',
    name: 'Community Building',
    category: 'owned',
    description: 'Creating spaces for audience interaction',
    bestFor: ['Loyal user base', 'Product feedback', 'Developer tools'],
    considerations: ['Moderation needed', 'Slow to build'],
  },
  {
    id: 'influencer',
    name: 'Influencer Marketing',
    category: 'paid',
    description: 'Partnering with influential voices',
    bestFor: ['Reaching new audiences', 'Product launches', 'B2C'],
    considerations: ['Authenticity concerns', 'Cost variability'],
  },
  {
    id: 'events',
    name: 'Events & Conferences',
    category: 'owned',
    description: 'Participating in or hosting events',
    bestFor: ['B2B relationships', 'Product demos', 'Networking'],
    considerations: ['High cost', 'Logistics complexity'],
  },
];

/**
 * Content mix categories and optimal ratios
 * Based on Content Marketing Institute recommendations
 */
export const CONTENT_MIX_OPTIMAL = {
  educational: 0.40,    // 40% - Teaching and informing
  entertaining: 0.20,   // 20% - Engaging and fun
  inspirational: 0.15,  // 15% - Motivating and aspirational
  promotional: 0.15,    // 15% - Product/service focused
  conversational: 0.10, // 10% - Community engagement
};

/**
 * Trust signal categories
 */
export const TRUST_SIGNALS = [
  { id: 'testimonials', name: 'Customer Testimonials', weight: 1.0 },
  { id: 'case_studies', name: 'Case Studies', weight: 1.2 },
  { id: 'client_logos', name: 'Client Logos', weight: 0.8 },
  { id: 'awards', name: 'Awards & Recognition', weight: 0.9 },
  { id: 'certifications', name: 'Certifications', weight: 0.7 },
  { id: 'social_proof', name: 'Social Proof Numbers', weight: 0.8 },
  { id: 'press_mentions', name: 'Press Mentions', weight: 1.0 },
  { id: 'security_badges', name: 'Security Badges', weight: 0.6 },
];

/**
 * Priority matrix for recommendations
 * Quick wins = High impact + Low effort
 */
export function getPriorityScore(impact: string, effort: string): number {
  const impactScore = impact === 'high' ? 3 : impact === 'medium' ? 2 : 1;
  const effortScore = effort === 'low' ? 3 : effort === 'medium' ? 2 : 1;
  return impactScore * effortScore;
}

/**
 * Determine if a recommendation is a "quick win"
 * Quick win = high impact AND low effort
 */
export function isQuickWin(impact: string, effort: string): boolean {
  return impact.toLowerCase() === 'high' && effort.toLowerCase() === 'low';
}

/**
 * Sort recommendations by priority
 */
export function sortByPriority<T extends { impact: string; effort: string }>(
  recommendations: T[]
): T[] {
  return [...recommendations].sort((a, b) => {
    const scoreA = getPriorityScore(a.impact, a.effort);
    const scoreB = getPriorityScore(b.impact, b.effort);
    return scoreB - scoreA;
  });
}

