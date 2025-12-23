/**
 * =============================================================================
 * Report Header Component
 * =============================================================================
 * Fixed header with brand URL, export actions, and navigation.
 * Provides consistent top-level navigation for the report.
 * =============================================================================
 */

'use client';

import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import {
  ArrowLeft,
  Download,
  Share2,
  ExternalLink,
  Printer,
  MoreHorizontal,
} from 'lucide-react';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface ReportHeaderProps {
  /** Analysis ID for API calls */
  analysisId: string;
  /** Website URL being analyzed */
  url: string;
  /** Report generation timestamp */
  generatedAt?: string | Date;
  /** API base URL for PDF download */
  apiUrl?: string;
  /** Optional className */
  className?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function ReportHeader({
  analysisId,
  url,
  generatedAt,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  className = '',
}: ReportHeaderProps) {
  const router = useRouter();

  // Format the generation date
  const formattedDate = generatedAt
    ? format(new Date(generatedAt), 'MMM d, yyyy \'at\' h:mm a')
    : null;

  // Extract domain from URL for display
  const displayUrl = url.replace(/^https?:\/\//, '').replace(/\/$/, '');

  // Handle PDF download
  const handleDownloadPDF = () => {
    window.open(`${apiUrl}/api/v1/analysis/${analysisId}/pdf`, '_blank');
  };

  // Handle print
  const handlePrint = () => {
    window.print();
  };

  // Handle share (copy link)
  const handleShare = async () => {
    const shareUrl = window.location.href;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Brand Analysis: ${displayUrl}`,
          url: shareUrl,
        });
      } catch (err) {
        // User cancelled or error
      }
    } else {
      // Fallback to clipboard
      await navigator.clipboard.writeText(shareUrl);
      // TODO: Show toast notification
    }
  };

  return (
    <header
      className={`
        sticky top-0 z-50 bg-[rgb(15,15,35)]/80 backdrop-blur-xl
        border-b border-white/[0.1] no-print
        ${className}
      `}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left section - Back button and URL */}
          <div className="flex items-center gap-4">
            {/* Back button */}
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-white/60 hover:text-white transition-colors group"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
              <span className="text-sm font-medium hidden sm:inline">
                New Analysis
              </span>
            </button>

            {/* Divider */}
            <div className="h-5 w-px bg-white/[0.1]" />

            {/* URL and metadata */}
            <div className="flex items-center gap-2">
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-white hover:text-blue-400 transition-colors"
              >
                <span className="font-medium text-sm sm:text-base truncate max-w-[200px] sm:max-w-none">
                  {displayUrl}
                </span>
                <ExternalLink className="w-3.5 h-3.5 text-white/40" />
              </a>

              {formattedDate && (
                <>
                  <span className="text-white/20 hidden md:inline">·</span>
                  <span className="text-xs text-white/50 hidden md:inline">
                    {formattedDate}
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Right section - Actions */}
          <div className="flex items-center gap-2">
            {/* Print button - desktop only */}
            <button
              onClick={handlePrint}
              className="hidden lg:flex items-center gap-2 px-3 py-2 text-sm text-white/60 
                       hover:text-white hover:bg-white/[0.08] rounded-lg transition-colors border border-transparent hover:border-white/[0.1]"
            >
              <Printer className="w-4 h-4" />
              <span>Print</span>
            </button>

            {/* Share button */}
            <button
              onClick={handleShare}
              className="flex items-center gap-2 px-3 py-2 text-sm text-white/60 
                       hover:text-white hover:bg-white/[0.08] rounded-lg transition-colors border border-transparent hover:border-white/[0.1]"
            >
              <Share2 className="w-4 h-4" />
              <span className="hidden sm:inline">Share</span>
            </button>

            {/* Download PDF button */}
            <button
              onClick={handleDownloadPDF}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium
                       bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg
                       hover:from-blue-500 hover:to-indigo-500 transition-all duration-300
                       shadow-[0_0_20px_rgba(79,70,229,0.4)] hover:shadow-[0_0_30px_rgba(79,70,229,0.6)]
                       border border-white/10"
            >
              <Download className="w-4 h-4" />
              <span className="hidden sm:inline">Download PDF</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default ReportHeader;
