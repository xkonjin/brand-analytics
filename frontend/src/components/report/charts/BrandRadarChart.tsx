/**
 * =============================================================================
 * Brand Radar Chart
 * =============================================================================
 * 8-axis radar visualization showing scores across all analysis modules.
 * Includes benchmark overlay for industry comparison.
 * Uses Recharts for rendering with custom styling.
 * =============================================================================
 */

'use client';

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import { MODULE_BENCHMARKS } from '@/lib/benchmarks';
import { getScoreColor } from '@/lib/scoring';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------
interface BrandRadarChartProps {
  /** Scores for each module (0-100) */
  scores: Record<string, number>;
  /** Whether to show benchmark comparison line */
  showBenchmark?: boolean;
  /** Chart height in pixels */
  height?: number;
  /** Optional className for container */
  className?: string;
}

interface DataPoint {
  module: string;
  fullName: string;
  score: number;
  benchmark: number;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------
export function BrandRadarChart({
  scores,
  showBenchmark = true,
  height = 400,
  className = '',
}: BrandRadarChartProps) {
  // Transform scores into chart data format
  // Each point has: module label, actual score, and benchmark value
  const data: DataPoint[] = MODULE_BENCHMARKS.map((benchmark) => ({
    module: benchmark.shortLabel,
    fullName: benchmark.label,
    score: scores[benchmark.key] ?? 0,
    benchmark: benchmark.benchmark,
  }));

  // Calculate average score for color theming
  const avgScore =
    Object.values(scores).reduce((sum, s) => sum + s, 0) /
    Object.keys(scores).length;
  const primaryColor = getScoreColor(avgScore);

  return (
    <div className={`w-full ${className}`} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart
          cx="50%"
          cy="50%"
          outerRadius="75%"
          data={data}
          margin={{ top: 20, right: 30, bottom: 20, left: 30 }}
        >
          {/* Grid lines - subtle styling */}
          <PolarGrid
            stroke="#e2e8f0"
            strokeDasharray="3 3"
            gridType="polygon"
          />

          {/* Axis labels - module names */}
          <PolarAngleAxis
            dataKey="module"
            tick={({ payload, x, y, textAnchor, ...rest }) => (
              <text
                {...rest}
                x={x}
                y={y}
                textAnchor={textAnchor}
                className="fill-slate-600 text-xs font-medium"
              >
                {payload.value}
              </text>
            )}
            tickLine={false}
          />

          {/* Radial axis - score scale 0-100 */}
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            tickCount={5}
            axisLine={false}
          />

          {/* Benchmark area (shown first so it's behind) */}
          {showBenchmark && (
            <Radar
              name="Industry Benchmark"
              dataKey="benchmark"
              stroke="#94a3b8"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              fill="#94a3b8"
              fillOpacity={0.1}
              dot={false}
            />
          )}

          {/* Actual scores area */}
          <Radar
            name="Your Score"
            dataKey="score"
            stroke={primaryColor}
            strokeWidth={2}
            fill={primaryColor}
            fillOpacity={0.25}
            dot={{
              r: 4,
              fill: primaryColor,
              stroke: '#fff',
              strokeWidth: 2,
            }}
            activeDot={{
              r: 6,
              fill: primaryColor,
              stroke: '#fff',
              strokeWidth: 2,
            }}
          />

          {/* Custom tooltip */}
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload || payload.length === 0) return null;
              const dataPoint = payload[0].payload as DataPoint;
              const diff = dataPoint.score - dataPoint.benchmark;
              const diffLabel =
                diff > 0
                  ? `+${diff.toFixed(0)} above`
                  : diff < 0
                  ? `${diff.toFixed(0)} below`
                  : 'At benchmark';

              return (
                <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-sm">
                  <p className="font-semibold text-slate-900 mb-1">
                    {dataPoint.fullName}
                  </p>
                  <div className="space-y-1">
                    <p className="text-slate-700">
                      Score:{' '}
                      <span className="font-medium">
                        {dataPoint.score.toFixed(0)}
                      </span>
                    </p>
                    <p className="text-slate-500">
                      Benchmark:{' '}
                      <span className="font-medium">{dataPoint.benchmark}</span>
                    </p>
                    <p
                      className={`text-xs ${
                        diff > 0
                          ? 'text-emerald-600'
                          : diff < 0
                          ? 'text-orange-600'
                          : 'text-slate-500'
                      }`}
                    >
                      {diffLabel}
                    </p>
                  </div>
                </div>
              );
            }}
          />

          {/* Legend */}
          <Legend
            wrapperStyle={{ paddingTop: 16 }}
            formatter={(value) => (
              <span className="text-sm text-slate-600">{value}</span>
            )}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BrandRadarChart;

