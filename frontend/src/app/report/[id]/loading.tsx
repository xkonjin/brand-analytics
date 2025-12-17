/**
 * =============================================================================
 * Report Loading Skeleton
 * =============================================================================
 * Displays a beautiful loading state while the report is being fetched.
 * Uses skeleton animations to provide visual feedback.
 * =============================================================================
 */

import { Loader2 } from 'lucide-react';

export default function ReportLoading() {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header skeleton */}
      <div className="h-16 bg-white border-b border-slate-200 animate-pulse" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero section skeleton */}
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          {/* Score gauge skeleton */}
          <div className="flex flex-col items-center lg:items-start">
            <div className="w-48 h-48 rounded-full bg-slate-200 animate-pulse" />
            <div className="w-32 h-8 bg-slate-200 rounded-full mt-4 animate-pulse" />
          </div>

          {/* Summary skeleton */}
          <div className="space-y-4">
            <div className="w-48 h-8 bg-slate-200 rounded animate-pulse" />
            <div className="w-full h-24 bg-slate-200 rounded-xl animate-pulse" />
          </div>
        </div>

        {/* Loading indicator */}
        <div className="flex flex-col items-center justify-center py-12">
          <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
            <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
          </div>
          <p className="text-slate-500">Loading your brand analysis...</p>
        </div>

        {/* Section skeletons */}
        <div className="space-y-8 mt-12">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-slate-200 rounded-xl animate-pulse" />
                <div className="flex-1">
                  <div className="w-40 h-6 bg-slate-200 rounded animate-pulse" />
                  <div className="w-64 h-4 bg-slate-100 rounded mt-2 animate-pulse" />
                </div>
                <div className="w-20 h-20 bg-slate-200 rounded-full animate-pulse" />
              </div>

              <div className="grid grid-cols-4 gap-4 mb-6">
                {[1, 2, 3, 4].map((j) => (
                  <div key={j} className="h-24 bg-slate-100 rounded-lg animate-pulse" />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer skeleton */}
      <div className="h-20 bg-white border-t border-slate-200 animate-pulse mt-12" />
    </div>
  );
}

