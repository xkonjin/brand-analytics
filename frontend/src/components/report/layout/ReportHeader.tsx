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
  apiUrl = process.env.NEXT_PUBLIC_API_URL || '',
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
        sticky top-0 z-50 bg-white/95 backdrop-blur-sm
        border-b border-slate-200 no-print
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
              className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm font-medium hidden sm:inline">
                New Analysis
              </span>
            </button>

            {/* Divider */}
            <div className="h-5 w-px bg-slate-200" />

            {/* URL and metadata */}
            <div className="flex items-center gap-2">
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-slate-900 hover:text-blue-600 transition-colors"
              >
                <span className="font-medium text-sm sm:text-base truncate max-w-[200px] sm:max-w-none">
                  {displayUrl}
                </span>
                <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
              </a>

              {formattedDate && (
                <>
                  <span className="text-slate-300 hidden md:inline">·</span>
                  <span className="text-xs text-slate-500 hidden md:inline">
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
              className="hidden lg:flex items-center gap-2 px-3 py-2 text-sm text-slate-600 
                       hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <Printer className="w-4 h-4" />
              <span>Print</span>
            </button>

            {/* Share button */}
            <button
              onClick={handleShare}
              className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 
                       hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <Share2 className="w-4 h-4" />
              <span className="hidden sm:inline">Share</span>
            </button>

            {/* Download PDF button */}
            <button
              onClick={handleDownloadPDF}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium
                       bg-slate-900 text-white rounded-lg
                       hover:bg-slate-800 transition-colors"
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

