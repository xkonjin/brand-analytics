/**
 * =============================================================================
 * Action Plan Section - Apple Liquid Glass UI
 * =============================================================================
 * Displays prioritized recommendations with glassmorphism.
 * Quick wins highlighted with special glow effects.
 * =============================================================================
 */

'use client';

import { motion } from 'framer-motion';
import { ListChecks, Zap, Target } from 'lucide-react';
import { RecommendationCard, RecommendationList } from '../cards/RecommendationCard';
import { isQuickWin, getPriorityScore } from '@/lib/frameworks';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface Recommendation {
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
}

interface ActionPlanProps {
  /** All recommendations from all modules */
  recommendations: Recommendation[];
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ActionPlan({ recommendations, className = '' }: ActionPlanProps) {
  // Separate quick wins from other recommendations
  const quickWins = recommendations.filter((r) =>
    isQuickWin(r.impact, r.effort)
  );
  
  // Sort remaining by priority score
  const otherRecs = recommendations
    .filter((r) => !isQuickWin(r.impact, r.effort))
    .sort((a, b) => getPriorityScore(b.impact, b.effort) - getPriorityScore(a.impact, a.effort));

  // Group by priority
  const criticalRecs = otherRecs.filter((r) => r.priority === 'critical');
  const highRecs = otherRecs.filter((r) => r.priority === 'high');
  const mediumRecs = otherRecs.filter((r) => r.priority === 'medium');
  const lowRecs = otherRecs.filter((r) => r.priority === 'low');

  return (
    <section id="action-plan" className={`py-12 border-t border-white/[0.08] ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 
                          border border-blue-500/30 shadow-[0_0_30px_rgba(99,102,241,0.3)]
                          text-blue-400">
              <ListChecks className="w-6 h-6" />
            </div>
            <h2 className="text-2xl font-bold text-white">Action Plan</h2>
          </div>
          <p className="text-white/60 max-w-2xl">
            Prioritized recommendations based on impact and effort. Start with Quick Wins for
            immediate improvements with minimal effort.
          </p>
        </motion.div>

        {/* Summary stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          <div className="bg-emerald-500/10 backdrop-blur-xl rounded-xl border border-emerald-500/20 p-4 text-center
                        shadow-[0_0_20px_rgba(52,211,153,0.15)]">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Zap className="w-5 h-5 text-emerald-400" />
              <span className="text-2xl font-bold text-emerald-400">{quickWins.length}</span>
            </div>
            <span className="text-sm text-emerald-300/70">Quick Wins</span>
          </div>
          <div className="bg-red-500/10 backdrop-blur-xl rounded-xl border border-red-500/20 p-4 text-center
                        shadow-[0_0_20px_rgba(248,113,113,0.15)]">
            <div className="text-2xl font-bold text-red-400 mb-1">{criticalRecs.length}</div>
            <span className="text-sm text-red-300/70">Critical</span>
          </div>
          <div className="bg-orange-500/10 backdrop-blur-xl rounded-xl border border-orange-500/20 p-4 text-center
                        shadow-[0_0_20px_rgba(251,146,60,0.15)]">
            <div className="text-2xl font-bold text-orange-400 mb-1">{highRecs.length}</div>
            <span className="text-sm text-orange-300/70">High Priority</span>
          </div>
          <div className="bg-white/[0.05] backdrop-blur-xl rounded-xl border border-white/[0.1] p-4 text-center">
            <div className="text-2xl font-bold text-white/80 mb-1">{mediumRecs.length + lowRecs.length}</div>
            <span className="text-sm text-white/50">Other</span>
          </div>
        </motion.div>

        {/* Quick Wins section - highlighted */}
        {quickWins.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-10"
          >
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-5 h-5 text-emerald-400" />
              <h3 className="text-lg font-semibold text-white">
                Quick Wins
              </h3>
              <span className="text-sm text-white/50">
                High impact, low effort
              </span>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              {quickWins.map((rec, index) => (
                <RecommendationCard
                  key={`qw-${rec.title}-${index}`}
                  {...rec}
                  index={index + 1}
                  animate={false}
                />
              ))}
            </div>
          </motion.div>
        )}

        {/* All Recommendations by priority */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="space-y-8"
        >
          {/* Critical */}
          {criticalRecs.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-red-400 uppercase tracking-wide mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.6)]" />
                Critical Priority ({criticalRecs.length})
              </h3>
              <RecommendationList
                recommendations={criticalRecs}
                showQuickWinsFirst={false}
                animate={false}
              />
            </div>
          )}

          {/* High */}
          {highRecs.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-orange-400 uppercase tracking-wide mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-orange-400 shadow-[0_0_8px_rgba(251,146,60,0.6)]" />
                High Priority ({highRecs.length})
              </h3>
              <RecommendationList
                recommendations={highRecs}
                showQuickWinsFirst={false}
                animate={false}
              />
            </div>
          )}

          {/* Medium & Low */}
          {(mediumRecs.length > 0 || lowRecs.length > 0) && (
            <div>
              <h3 className="text-sm font-semibold text-white/50 uppercase tracking-wide mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-white/40" />
                Other Recommendations ({mediumRecs.length + lowRecs.length})
              </h3>
              <RecommendationList
                recommendations={[...mediumRecs, ...lowRecs]}
                showQuickWinsFirst={false}
                animate={false}
              />
            </div>
          )}
        </motion.div>

        {/* Empty state */}
        {recommendations.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-4
                          shadow-[0_0_30px_rgba(52,211,153,0.3)]">
              <Target className="w-8 h-8 text-emerald-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Looking Great!
            </h3>
            <p className="text-white/60 max-w-md mx-auto">
              No major recommendations at this time. Your brand is performing well
              across all analyzed dimensions.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}

export default ActionPlan;
