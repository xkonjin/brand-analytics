/**
 * =============================================================================
 * Archetype Card Component
 * =============================================================================
 * Displays brand archetype analysis with visual icon, description,
 * confidence score, and example brands for comparison.
 * =============================================================================
 */

'use client';

import { motion } from 'framer-motion';
import { getArchetypeByName, BRAND_ARCHETYPES } from '@/lib/frameworks';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface ArchetypeCardProps {
  /** Primary archetype name */
  primary: string;
  /** Secondary archetype name (optional) */
  secondary?: string | null;
  /** Confidence score (0-1) */
  confidence: number;
  /** Detailed description/reasoning */
  description?: string;
  /** Example brands that share this archetype */
  exampleBrands?: string[];
  /** Whether to animate on mount */
  animate?: boolean;
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ArchetypeCard({
  primary,
  secondary,
  confidence,
  description,
  exampleBrands = [],
  animate = true,
  className = '',
}: ArchetypeCardProps) {
  // Get archetype info from framework definitions
  const primaryArchetype = getArchetypeByName(primary);
  const secondaryArchetype = secondary ? getArchetypeByName(secondary) : null;

  // Fallback if archetype not found
  const displayPrimary = primaryArchetype || {
    name: primary,
    icon: '✨',
    tagline: '',
    description: '',
    traits: [],
    exampleBrands: [],
    color: '#6366f1',
  };

  const content = (
    <div
      className={`bg-white rounded-xl border border-slate-200 overflow-hidden ${className}`}
    >
      {/* Header with gradient based on archetype color */}
      <div
        className="px-6 py-5"
        style={{
          background: `linear-gradient(135deg, ${displayPrimary.color}10 0%, ${displayPrimary.color}05 100%)`,
          borderBottom: `1px solid ${displayPrimary.color}20`,
        }}
      >
        <div className="flex items-center gap-4">
          {/* Archetype icon */}
          <div
            className="w-14 h-14 rounded-xl flex items-center justify-center text-2xl"
            style={{
              backgroundColor: `${displayPrimary.color}15`,
              color: displayPrimary.color,
            }}
          >
            {displayPrimary.icon}
          </div>

          {/* Archetype names */}
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold text-slate-900">
                {displayPrimary.name}
              </h3>
              {secondaryArchetype && (
                <>
                  <span className="text-slate-400">+</span>
                  <span className="text-lg font-medium text-slate-600">
                    {secondaryArchetype.name}
                  </span>
                </>
              )}
            </div>
            {displayPrimary.tagline && (
              <p className="text-sm text-slate-500 italic mt-0.5">
                "{displayPrimary.tagline}"
              </p>
            )}
          </div>

          {/* Confidence score */}
          <div className="ml-auto text-right">
            <div className="text-2xl font-bold text-slate-900">
              {Math.round(confidence * 100)}%
            </div>
            <div className="text-xs text-slate-500">confidence</div>
          </div>
        </div>
      </div>

      {/* Body content */}
      <div className="px-6 py-5 space-y-5">
        {/* Description */}
        {description && (
          <div>
            <h4 className="text-sm font-medium text-slate-500 mb-2">
              Analysis
            </h4>
            <p className="text-sm text-slate-700 leading-relaxed">
              {description}
            </p>
          </div>
        )}

        {/* Archetype traits */}
        {displayPrimary.traits && displayPrimary.traits.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-slate-500 mb-2">
              Key Traits
            </h4>
            <div className="flex flex-wrap gap-2">
              {displayPrimary.traits.map((trait) => (
                <span
                  key={trait}
                  className="px-2.5 py-1 text-sm rounded-full"
                  style={{
                    backgroundColor: `${displayPrimary.color}10`,
                    color: displayPrimary.color,
                  }}
                >
                  {trait}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Example brands */}
        {(exampleBrands.length > 0 || displayPrimary.exampleBrands.length > 0) && (
          <div>
            <h4 className="text-sm font-medium text-slate-500 mb-2">
              Similar Brands
            </h4>
            <div className="flex flex-wrap gap-2">
              {(exampleBrands.length > 0 
                ? exampleBrands 
                : displayPrimary.exampleBrands
              ).map((brand) => (
                <span
                  key={brand}
                  className="px-3 py-1.5 text-sm bg-slate-100 text-slate-700 rounded-lg"
                >
                  {brand}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
      >
        {content}
      </motion.div>
    );
  }

  return content;
}

// -----------------------------------------------------------------------------
// Mini Archetype Badge - compact version for use in headers
// -----------------------------------------------------------------------------
interface ArchetypeBadgeProps {
  archetype: string;
  size?: 'sm' | 'md';
  className?: string;
}

export function ArchetypeBadge({
  archetype,
  size = 'md',
  className = '',
}: ArchetypeBadgeProps) {
  const info = getArchetypeByName(archetype);
  
  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-3 py-1 text-sm gap-1.5',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeStyles[size]} ${className}`}
      style={{
        backgroundColor: info ? `${info.color}15` : '#f1f5f9',
        color: info?.color || '#64748b',
      }}
    >
      <span>{info?.icon || '✨'}</span>
      <span>{info?.name || archetype}</span>
    </span>
  );
}

export default ArchetypeCard;

