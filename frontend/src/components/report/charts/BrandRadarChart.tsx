/**
 * =============================================================================
 * Brand Radar Chart - Apple Liquid Glass UI
 * =============================================================================
 * 8-axis radar visualization with glassmorphism tooltip and glass container.
 * Uses Recharts for rendering with custom glass-themed styling.
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
// Score-based color for Glass UI
// -----------------------------------------------------------------------------
function getScoreColor(score: number) {
  if (score >= 80) return '#34d399'; // emerald-400
  if (score >= 70) return '#4ade80'; // green-400
  if (score >= 60) return '#facc15'; // yellow-400
  if (score >= 50) return '#fb923c'; // orange-400
  return '#f87171'; // red-400
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
  const data: DataPoint[] = MODULE_BENCHMARKS.map((benchmark) => ({
    module: benchmark.shortLabel,
    fullName: benchmark.label,
    score: scores[benchmark.key] ?? 0,
    benchmark: benchmark.benchmark,
  }));

  // Calculate average score for color theming
  const avgScore =
    Object.values(scores).reduce((sum, s) => sum + s, 0) /
    (Object.keys(scores).length || 1);
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
          {/* Grid lines - glass style */}
          <PolarGrid
            stroke="rgba(255, 255, 255, 0.1)"
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
                className="fill-white/60 text-xs font-medium"
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
            tick={{ fill: 'rgba(255, 255, 255, 0.4)', fontSize: 10 }}
            tickCount={5}
            axisLine={false}
          />

          {/* Benchmark area (shown first so it's behind) */}
          {showBenchmark && (
            <Radar
              name="Industry Benchmark"
              dataKey="benchmark"
              stroke="rgba(255, 255, 255, 0.3)"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              fill="rgba(255, 255, 255, 0.05)"
              fillOpacity={1}
              dot={false}
            />
          )}

          {/* Actual scores area with glow effect */}
          <Radar
            name="Your Score"
            dataKey="score"
            stroke={primaryColor}
            strokeWidth={2}
            fill={primaryColor}
            fillOpacity={0.2}
            dot={{
              r: 4,
              fill: primaryColor,
              stroke: 'rgba(255, 255, 255, 0.8)',
              strokeWidth: 2,
            }}
            activeDot={{
              r: 6,
              fill: primaryColor,
              stroke: '#fff',
              strokeWidth: 2,
            }}
            style={{
              filter: `drop-shadow(0 0 8px ${primaryColor}80)`,
            }}
          />

          {/* Custom glass tooltip */}
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
              const diffColor =
                diff > 0 ? 'text-emerald-400' : diff < 0 ? 'text-orange-400' : 'text-white/50';

              return (
                <div className="bg-[rgb(30,30,50)]/90 backdrop-blur-xl border border-white/[0.15] rounded-xl shadow-2xl p-4 text-sm">
                  <p className="font-semibold text-white mb-2">
                    {dataPoint.fullName}
                  </p>
                  <div className="space-y-1">
                    <p className="text-white/80">
                      Score:{' '}
                      <span className="font-bold text-white">
                        {dataPoint.score.toFixed(0)}
                      </span>
                    </p>
                    <p className="text-white/50">
                      Benchmark:{' '}
                      <span className="font-medium text-white/70">{dataPoint.benchmark}</span>
                    </p>
                    <p className={`text-xs font-medium ${diffColor}`}>
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
              <span className="text-sm text-white/60">{value}</span>
            )}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BrandRadarChart;
