"use client";

import React, { useState } from "react";
import { mockAnalytics } from "@/lib/mock-data";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export function ChartsPlaceholder() {
  const [hoveredTrendIndex, setHoveredTrendIndex] = useState<number | null>(null);

  // Math config for Trend Chart SVG (800x250)
  const trendWidth = 800;
  const trendHeight = 250;
  const padding = 40;
  const chartWidth = trendWidth - padding * 2;
  const chartHeight = trendHeight - padding * 2;

  const maxVal = Math.max(
    ...mockAnalytics.trends.map(t => Math.max(t.reported, t.resolved))
  );

  const getPoints = (key: "reported" | "resolved") => {
    return mockAnalytics.trends.map((item, index) => {
      const x = padding + (index / (mockAnalytics.trends.length - 1)) * chartWidth;
      const y = padding + chartHeight - (item[key] / maxVal) * chartHeight;
      return `${x},${y}`;
    }).join(" ");
  };

  const reportedPoints = getPoints("reported");
  const resolvedPoints = getPoints("resolved");

  // SVG Area paths
  const getAreaPoints = (key: "reported" | "resolved", firstPoints: string) => {
    const startX = padding;
    const startY = padding + chartHeight;
    const endX = padding + chartWidth;
    const endY = padding + chartHeight;
    return `${startX},${startY} ${firstPoints} ${endX},${endY}`;
  };

  const reportedAreaPoints = getAreaPoints("reported", reportedPoints);
  const resolvedAreaPoints = getAreaPoints("resolved", resolvedPoints);

  return (
    <div className="space-y-6">
      {/* Overview Stat Blocks */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-gradient-to-br from-indigo-500/10 to-transparent">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Issues Logged</div>
          <div className="text-3xl font-bold mt-1 text-indigo-600 dark:text-indigo-400">{mockAnalytics.totalIssuesCount}</div>
          <p className="text-[10px] text-muted-foreground mt-1">+12% increase from last week</p>
        </Card>
        <Card className="p-4 bg-gradient-to-br from-emerald-500/10 to-transparent">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Issues Resolved</div>
          <div className="text-3xl font-bold mt-1 text-emerald-600 dark:text-emerald-400">{mockAnalytics.resolvedCount}</div>
          <p className="text-[10px] text-muted-foreground mt-1">73.2% absolute resolution index</p>
        </Card>
        <Card className="p-4 bg-gradient-to-br from-amber-500/10 to-transparent">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Backlog Queue</div>
          <div className="text-3xl font-bold mt-1 text-amber-600 dark:text-amber-400">{mockAnalytics.activeCount}</div>
          <p className="text-[10px] text-muted-foreground mt-1">Avg response latency: 45 min</p>
        </Card>
        <Card className="p-4 bg-gradient-to-br from-red-500/10 to-transparent">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Resolution Days</div>
          <div className="text-3xl font-bold mt-1 text-red-600 dark:text-red-400">{mockAnalytics.averageResolutionDays}</div>
          <p className="text-[10px] text-muted-foreground mt-1">Wired to Service Level Agreement (SLA)</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Area Chart (SVG) */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Inflow vs Resolution Dynamics</CardTitle>
            <CardDescription>Visualizing reported issues versus completed workflow resolutions monthly</CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <div className="relative w-full overflow-x-auto">
              <svg width="100%" height={trendHeight} viewBox={`0 0 ${trendWidth} ${trendHeight}`} className="overflow-visible min-w-[600px]">
                <defs>
                  <linearGradient id="gradReported" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="rgb(99, 102, 241)" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="rgb(99, 102, 241)" stopOpacity="0.0" />
                  </linearGradient>
                  <linearGradient id="gradResolved" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="rgb(16, 185, 129)" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="rgb(16, 185, 129)" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Y Axis Gridlines */}
                {Array.from({ length: 5 }).map((_, i) => {
                  const y = padding + (chartHeight / 4) * i;
                  const labelVal = Math.round(maxVal - (maxVal / 4) * i);
                  return (
                    <g key={i} className="opacity-40">
                      <line x1={padding} y1={y} x2={trendWidth - padding} y2={y} stroke="currentColor" strokeDasharray="3 3" className="text-slate-200 dark:text-slate-800" />
                      <text x={padding - 10} y={y + 4} textAnchor="end" fontSize="10" className="fill-slate-400 font-mono">{labelVal}</text>
                    </g>
                  );
                })}

                {/* X Axis labels */}
                {mockAnalytics.trends.map((item, index) => {
                  const x = padding + (index / (mockAnalytics.trends.length - 1)) * chartWidth;
                  return (
                    <g key={index}>
                      <text x={x} y={trendHeight - 15} textAnchor="middle" fontSize="10" className="fill-slate-400 font-semibold">{item.month}</text>
                      {/* Vertical tracker hover boundary */}
                      <line
                        x1={x}
                        y1={padding}
                        x2={x}
                        y2={padding + chartHeight}
                        stroke="currentColor"
                        strokeWidth="1"
                        className={`transition-opacity duration-200 text-slate-200 dark:text-slate-800 ${
                          hoveredTrendIndex === index ? "opacity-100" : "opacity-0"
                        }`}
                      />
                      {/* Hover catcher */}
                      <rect
                        x={x - chartWidth / 12}
                        y={padding}
                        width={chartWidth / 6}
                        height={chartHeight}
                        fill="transparent"
                        className="cursor-pointer"
                        onMouseEnter={() => setHoveredTrendIndex(index)}
                        onMouseLeave={() => setHoveredTrendIndex(null)}
                      />
                    </g>
                  );
                })}

                {/* Area Fills */}
                <polygon points={reportedAreaPoints} fill="url(#gradReported)" />
                <polygon points={resolvedAreaPoints} fill="url(#gradResolved)" />

                {/* Stroke Lines */}
                <polyline points={reportedPoints} fill="none" stroke="rgb(99, 102, 241)" strokeWidth="3" strokeLinecap="round" />
                <polyline points={resolvedPoints} fill="none" stroke="rgb(16, 185, 129)" strokeWidth="3" strokeLinecap="round" />

                {/* Data Points */}
                {mockAnalytics.trends.map((item, index) => {
                  const x = padding + (index / (mockAnalytics.trends.length - 1)) * chartWidth;
                  const yr = padding + chartHeight - (item.reported / maxVal) * chartHeight;
                  const ys = padding + chartHeight - (item.resolved / maxVal) * chartHeight;

                  return (
                    <g key={index} className={`transition-all duration-300 ${hoveredTrendIndex === index ? "scale-110" : "scale-100"}`}>
                      {/* Reported bubble */}
                      <circle cx={x} cy={yr} r="4" fill="rgb(99, 102, 241)" stroke="white" strokeWidth="1.5" />
                      {/* Resolved bubble */}
                      <circle cx={x} cy={ys} r="4" fill="rgb(16, 185, 129)" stroke="white" strokeWidth="1.5" />
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Custom Interactive Tooltip Bar */}
            <div className="mt-4 flex items-center justify-between border-t pt-4 text-xs font-mono text-slate-500">
              <div className="flex space-x-4">
                <span className="flex items-center"><span className="h-3 w-3 bg-indigo-500 rounded-full mr-1.5 inline-block" /> Reported</span>
                <span className="flex items-center"><span className="h-3 w-3 bg-emerald-500 rounded-full mr-1.5 inline-block" /> Resolved</span>
              </div>
              <div>
                {hoveredTrendIndex !== null ? (
                  <span>
                    {mockAnalytics.trends[hoveredTrendIndex].month}:{" "}
                    <span className="text-indigo-600 font-bold">{mockAnalytics.trends[hoveredTrendIndex].reported}</span> reported /{" "}
                    <span className="text-emerald-600 font-bold">{mockAnalytics.trends[hoveredTrendIndex].resolved}</span> resolved
                  </span>
                ) : (
                  <span>Hover points to isolate datasets</span>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Category Breakdown (Vertical SVG Grid) */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Category Distribution</CardTitle>
            <CardDescription>Issue volumetric weight by categories</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockAnalytics.issuesByCategory.map((category) => (
              <div key={category.name} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold">{category.name}</span>
                  <span className="text-muted-foreground font-mono">{category.count} issues ({category.pct}%)</span>
                </div>
                {/* Custom SVG/CSS Bar */}
                <div className="h-3 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full transition-all duration-1000"
                    style={{ width: `${category.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Ward Efficiency Benchmarks */}
      <Card>
        <CardHeader>
          <CardTitle>Constituency Service Level Agreement (SLA) Benchmarks</CardTitle>
          <CardDescription>Comparing average ward resolution speed against workload density</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {mockAnalytics.efficiencyByWard.map((ward) => (
              <div key={ward.ward} className="border p-4 rounded-xl space-y-2 hover:border-slate-300 dark:hover:border-slate-700 transition">
                <div className="font-bold text-sm tracking-tight">{ward.ward}</div>
                <div className="flex justify-between items-baseline pt-1">
                  <div className="text-2xl font-bold font-mono text-indigo-600 dark:text-indigo-400">{ward.avgDays}d</div>
                  <div className="text-xs text-muted-foreground font-mono">{ward.count} total load</div>
                </div>
                <div className="text-[10px] text-muted-foreground">
                  {ward.avgDays < 2.5 ? "✅ Performing within SLA limits" : "⚠️ Backlog buildup detected"}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
