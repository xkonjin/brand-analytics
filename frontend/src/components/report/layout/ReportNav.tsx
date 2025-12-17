/**
 * =============================================================================
 * Report Navigation Component
 * =============================================================================
 * Sticky sidebar navigation for jumping between report sections.
 * Shows current section and progress through the report.
 * =============================================================================
 */

'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  Search,
  Share2,
  MessageSquare,
  Layout,
  Bot,
  FileText,
  Users,
  Target,
  ListChecks,
} from 'lucide-react';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface NavSection {
  id: string;
  label: string;
  icon: React.ElementType;
}

interface ReportNavProps {
  /** Currently active section ID */
  activeSection?: string;
  /** Sections that are visible in the report */
  visibleSections?: string[];
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Navigation sections configuration
// -----------------------------------------------------------------------------
const NAV_SECTIONS: NavSection[] = [
  { id: 'summary', label: 'Summary', icon: BarChart3 },
  { id: 'seo', label: 'SEO', icon: Search },
  { id: 'social', label: 'Social Media', icon: Share2 },
  { id: 'brand', label: 'Brand Messaging', icon: MessageSquare },
  { id: 'ux', label: 'Website UX', icon: Layout },
  { id: 'ai', label: 'AI Discoverability', icon: Bot },
  { id: 'content', label: 'Content', icon: FileText },
  { id: 'team', label: 'Team Presence', icon: Users },
  { id: 'channels', label: 'Channel Fit', icon: Target },
  { id: 'action-plan', label: 'Action Plan', icon: ListChecks },
];

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ReportNav({
  activeSection = 'summary',
  visibleSections,
  className = '',
}: ReportNavProps) {
  const [currentSection, setCurrentSection] = useState(activeSection);

  // Filter sections if visibleSections is provided
  const sections = visibleSections
    ? NAV_SECTIONS.filter((s) => visibleSections.includes(s.id))
    : NAV_SECTIONS;

  // Track scroll position to update active section
  useEffect(() => {
    const handleScroll = () => {
      const sectionElements = sections.map((s) => ({
        id: s.id,
        element: document.getElementById(s.id),
      }));

      // Find the section currently in view
      for (const { id, element } of sectionElements) {
        if (element) {
          const rect = element.getBoundingClientRect();
          // Consider a section "active" when its top is within the top third of viewport
          if (rect.top <= 200 && rect.bottom > 100) {
            setCurrentSection(id);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [sections]);

  // Handle click - smooth scroll to section
  const handleClick = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const offset = 80; // Header height
      const top = element.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  };

  return (
    <nav
      className={`
        sticky top-20 hidden lg:block w-56 shrink-0 no-print
        ${className}
      `}
    >
      <div className="space-y-1">
        {sections.map((section, index) => {
          const Icon = section.icon;
          const isActive = currentSection === section.id;

          return (
            <motion.button
              key={section.id}
              onClick={() => handleClick(section.id)}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.03 }}
              className={`
                w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm
                transition-all duration-200
                ${isActive
                  ? 'bg-slate-900 text-white font-medium'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }
              `}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">{section.label}</span>

              {/* Active indicator */}
              {isActive && (
                <motion.div
                  layoutId="nav-indicator"
                  className="ml-auto w-1.5 h-1.5 rounded-full bg-white"
                />
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Progress indicator */}
      <div className="mt-6 pt-6 border-t border-slate-200">
        <div className="px-3 text-xs text-slate-500 mb-2">Progress</div>
        <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-slate-900 rounded-full"
            initial={{ width: 0 }}
            animate={{
              width: `${((sections.findIndex((s) => s.id === currentSection) + 1) / sections.length) * 100}%`,
            }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>
    </nav>
  );
}

export default ReportNav;

