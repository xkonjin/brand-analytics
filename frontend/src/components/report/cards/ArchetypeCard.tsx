/**
 * =============================================================================
 * Archetype Card Component - Apple Liquid Glass UI
 * =============================================================================
 * Displays brand archetype analysis with visual icon, description,
 * confidence score, and example brands with glassmorphism styling.
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
// Helper - Get glass-compatible color values
// -----------------------------------------------------------------------------
function getGlassColor(hexColor: string) {
  // Convert hex to RGB for glass styling
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return { r, g, b, rgb: `${r}, ${g}, ${b}` };
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

  const glassColor = getGlassColor(displayPrimary.color);

  const content = (
    <div
      className={`bg-white/[0.05] backdrop-blur-xl rounded-xl border border-white/[0.08] overflow-hidden ${className}`}
    >
      {/* Header with gradient based on archetype color */}
      <div
        className="px-6 py-5 border-b border-white/[0.08]"
        style={{
          background: `linear-gradient(135deg, rgba(${glassColor.rgb}, 0.15) 0%, rgba(${glassColor.rgb}, 0.05) 100%)`,
        }}
      >
        <div className="flex items-center gap-4">
          {/* Archetype icon */}
          <div
            className="w-14 h-14 rounded-xl flex items-center justify-center text-2xl backdrop-blur-xl"
            style={{
              backgroundColor: `rgba(${glassColor.rgb}, 0.2)`,
              boxShadow: `0 0 30px rgba(${glassColor.rgb}, 0.3)`,
            }}
          >
            {displayPrimary.icon}
          </div>

          {/* Archetype names */}
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold text-white">
                {displayPrimary.name}
              </h3>
              {secondaryArchetype && (
                <>
                  <span className="text-white/30">+</span>
                  <span className="text-lg font-medium text-white/60">
                    {secondaryArchetype.name}
                  </span>
                </>
              )}
            </div>
            {displayPrimary.tagline && (
              <p className="text-sm text-white/50 italic mt-0.5">
                &quot;{displayPrimary.tagline}&quot;
              </p>
            )}
          </div>

          {/* Confidence score */}
          <div className="ml-auto text-right">
            <div className="text-2xl font-bold text-white">
              {Math.round(confidence * 100)}%
            </div>
            <div className="text-xs text-white/40">confidence</div>
          </div>
        </div>
      </div>

      {/* Body content */}
      <div className="px-6 py-5 space-y-5">
        {/* Description */}
        {description && (
          <div>
            <h4 className="text-sm font-medium text-white/40 mb-2">
              Analysis
            </h4>
            <p className="text-sm text-white/70 leading-relaxed">
              {description}
            </p>
          </div>
        )}

        {/* Archetype traits */}
        {displayPrimary.traits && displayPrimary.traits.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-white/40 mb-2">
              Key Traits
            </h4>
            <div className="flex flex-wrap gap-2">
              {displayPrimary.traits.map((trait) => (
                <span
                  key={trait}
                  className="px-2.5 py-1 text-sm rounded-full border transition-all hover:scale-105"
                  style={{
                    backgroundColor: `rgba(${glassColor.rgb}, 0.1)`,
                    borderColor: `rgba(${glassColor.rgb}, 0.2)`,
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
            <h4 className="text-sm font-medium text-white/40 mb-2">
              Similar Brands
            </h4>
            <div className="flex flex-wrap gap-2">
              {(exampleBrands.length > 0 
                ? exampleBrands 
                : displayPrimary.exampleBrands
              ).map((brand) => (
                <span
                  key={brand}
                  className="px-3 py-1.5 text-sm bg-white/[0.05] text-white/70 rounded-lg 
                           border border-white/[0.08] hover:bg-white/[0.08] transition-all"
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
  const glassColor = info ? getGlassColor(info.color) : null;
  
  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-3 py-1 text-sm gap-1.5',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium backdrop-blur-xl 
                border transition-all ${sizeStyles[size]} ${className}`}
      style={{
        backgroundColor: glassColor ? `rgba(${glassColor.rgb}, 0.15)` : 'rgba(255,255,255,0.05)',
        borderColor: glassColor ? `rgba(${glassColor.rgb}, 0.2)` : 'rgba(255,255,255,0.08)',
        color: info?.color || 'rgba(255,255,255,0.7)',
      }}
    >
      <span>{info?.icon || '✨'}</span>
      <span>{info?.name || archetype}</span>
    </span>
  );
}

export default ArchetypeCard;
