"use client";

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  MapPin,
  TrendingUp,
  AlertTriangle,
  Activity,
  Layers,
  Compass,
  Zap,
  Globe,
  Settings,
  Sparkles,
  ArrowRight,
  TrendingDown,
  Hammer,
  CheckCircle,
} from "lucide-react";

export default function SpatialMapPage() {
  const [activeTab, setActiveTab] = useState<"overview" | "map" | "health" | "projects">("overview");

  // Spatial Data states
  const [overview, setOverview] = useState<any>(null);
  const [mapData, setMapData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Map Filter layers
  const [showIssuesLayer, setShowIssuesLayer] = useState(true);
  const [showHeatmapLayer, setShowHeatmapLayer] = useState(true);
  const [showHotspotsLayer, setShowHotspotsLayer] = useState(true);

  // Selected Hotspot details
  const [selectedHotspot, setSelectedHotspot] = useState<any>(null);
  const [tenderingStates, setTenderingStates] = useState<Record<string, boolean>>({});

  useEffect(() => {
    Promise.all([
      fetch("http://localhost:8000/governance/constituency/overview").then((r) => r.json()),
      fetch("http://localhost:8000/governance/map").then((r) => r.json()),
    ])
      .then(([over, mData]) => {
        setOverview(over);
        setMapData(mData);
        if (over.hotspots && over.hotspots.length > 0) {
          setSelectedHotspot(over.hotspots[0]);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.log("Offline, loading mock spatial dataset:", err);
        const mockOverview = {
          constituency_name: "Bangalore Central Constituency",
          overall_health_score: 78,
          overall_health_trend: "UP",
          category_scores: {
            "Roads & Sidewalks": 82,
            "Water Supply & Sanitation": 61,
            "Electricity & Power": 90,
            "Healthcare Facilities": 74,
            "Education & Schools": 69,
          },
          hotspots: [
            {
              id: "hotspot-water-shivaji",
              category: "Water Supply & Sanitation",
              latitude: 12.9755,
              longitude: 77.5955,
              complaints_count: 18,
              affected_population: 4320,
              linked_complaint_ids: ["ISSUE-001"],
              proposed_project: {
                title: "Reconstruct Main Water Pipe Trunk",
                estimated_cost: "₹18 Lakhs",
                estimated_duration: "45 Days",
                impact: "Eliminates water overflow hazards inside Shivajinagar playground.",
              },
            },
            {
              id: "hotspot-road-sector4",
              category: "Roads & Sidewalks",
              latitude: 12.9810,
              longitude: 77.5910,
              complaints_count: 6,
              affected_population: 350,
              linked_complaint_ids: ["ISSUE-002"],
              proposed_project: {
                title: "Full Sidewalk & Corridor Reconstruction",
                estimated_cost: "₹12 Lakhs",
                estimated_duration: "30 Days",
                impact: "Restores school pedestrian safe paths.",
              },
            },
          ],
          risk_zones: [
            {
              name: "Shivaji Nagar Sector B",
              risk_rating: "HIGH",
              reason: "Active cluster of 18 unresolved water leakage complaints.",
            },
          ],
          total_pending_issues: 24,
        };
        setOverview(mockOverview);
        setSelectedHotspot(mockOverview.hotspots[0]);

        setMapData({
          boundaries: { type: "FeatureCollection", features: [] },
          heatmap: [
            { lat: 12.9750, lng: 77.5950, weight: 2.5 },
            { lat: 12.9760, lng: 77.5960, weight: 2.5 },
            { lat: 12.9810, lng: 77.5910, weight: 1.0 },
          ],
          clusters: [
            { type: "cluster", latitude: 12.9755, longitude: 77.5955, count: 18, ids: ["ISSUE-001"] },
            { type: "single", id: "ISSUE-002", latitude: 12.9810, longitude: 77.5910, title: "Utility Dig Block Sector 4", category: "Roads & Sidewalks" },
          ],
          hotspots: mockOverview.hotspots,
        });
        setLoading(false);
      });
  }, []);

  const handleStartTender = (hotspotId: string) => {
    setTenderingStates((prev) => ({ ...prev, [hotspotId]: true }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Spatial Intelligence Dashboard</h1>
          <p className="text-xs text-muted-foreground">
            Aggregate coordinate intelligence, derived constituency health indexes, and unified developmental project tenders.
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg w-full max-w-lg">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
            activeTab === "overview"
              ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab("map")}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
            activeTab === "map"
              ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Spatial Map
        </button>
        <button
          onClick={() => setActiveTab("health")}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
            activeTab === "health"
              ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Constituency Health
        </button>
        <button
          onClick={() => setActiveTab("projects")}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
            activeTab === "projects"
              ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Proposed Projects
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-muted-foreground animate-pulse">
          Computing spatial coordinate clusters...
        </div>
      ) : (
        <div className="space-y-6">
          {/* TAB 1: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left col: Health Score Summary & categories */}
              <div className="lg:col-span-2 space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  {/* Master health card */}
                  <Card className="p-5 bg-gradient-to-br from-indigo-950 to-slate-950 text-white flex flex-col justify-between border-indigo-500/20">
                    <div>
                      <div className="flex justify-between items-center text-xs text-indigo-300 font-bold uppercase tracking-wider">
                        <span>Derived Health Score</span>
                        <Activity className="h-4 w-4 text-indigo-400" />
                      </div>
                      <div className="flex items-baseline gap-1 mt-4">
                        <span className="text-5xl font-extrabold">{overview.overall_health_score}</span>
                        <span className="text-slate-400 text-xs">/ 100</span>
                      </div>
                    </div>
                    <div className="text-[10px] text-indigo-300 mt-4 leading-normal">
                      Score dynamically derived based on {overview.total_pending_issues} unresolved citizen complaints and priority weightings.
                    </div>
                  </Card>

                  {/* Active Risk Zones */}
                  <Card className="p-5 border-red-500/20 bg-red-500/[0.01] flex flex-col justify-between">
                    <div>
                      <span className="text-red-500 font-bold uppercase tracking-wider text-xs flex items-center gap-1">
                        <AlertTriangle className="h-4 w-4" /> Priority Risk Zones
                      </span>
                      <div className="mt-3">
                        <p className="font-bold text-sm text-slate-800 dark:text-slate-200">
                          {overview.risk_zones[0].name}
                        </p>
                        <p className="text-xs text-slate-500 mt-1 leading-normal">
                          {overview.risk_zones[0].reason}
                        </p>
                      </div>
                    </div>
                    <Badge variant="destructive" className="mt-4 justify-center w-full uppercase py-1">
                      {overview.risk_zones[0].risk_rating} Severity Rating
                    </Badge>
                  </Card>
                </div>

                {/* Hotspots Project Proposal list */}
                <Card className="p-5 space-y-4">
                  <div className="border-l-4 border-indigo-500 pl-3">
                    <h3 className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                      Hotspot Projects (2+ Complaints Aggregated)
                    </h3>
                  </div>
                  <div className="space-y-4">
                    {overview.hotspots.map((hs: any, idx: number) => (
                      <div key={idx} className="border p-4 rounded-xl bg-card space-y-3 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-indigo-500/30 transition">
                        <div className="space-y-1 max-w-md">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="font-mono text-[9px]">{hs.category}</Badge>
                            <span className="text-xs text-muted-foreground font-semibold">
                              ({hs.complaints_count} complaints merged)
                            </span>
                          </div>
                          <h4 className="font-extrabold text-sm text-slate-800 dark:text-slate-200 mt-1">
                            {hs.proposed_project.title}
                          </h4>
                          <p className="text-[11px] text-muted-foreground leading-normal">
                            Suggested Project instead of {hs.complaints_count} patch updates. Saves budget overhead.
                          </p>
                        </div>
                        <div className="text-right flex-shrink-0 space-y-2">
                          <p className="text-xs font-bold text-emerald-500">{hs.proposed_project.estimated_cost}</p>
                          <Button size="sm" onClick={() => setActiveTab("projects")} className="h-7 text-[10px] gap-1">
                            View Tender <ArrowRight className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>

              {/* Right column: Category progress overview */}
              <Card className="p-5 space-y-6">
                <h3 className="font-bold text-xs uppercase tracking-wider text-slate-500">Category Index Details</h3>
                <div className="space-y-4">
                  {Object.entries(overview.category_scores).map(([name, score]: any, idx) => (
                    <div key={idx} className="space-y-1.5">
                      <div className="flex justify-between text-xs font-bold">
                        <span className="text-slate-700 dark:text-slate-300 truncate">{name}</span>
                        <span className={score < 70 ? "text-red-500 font-mono" : "text-emerald-500 font-mono"}>
                          {score}/100
                        </span>
                      </div>
                      <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            score < 70 ? "bg-red-500" : "bg-emerald-500"
                          }`}
                          style={{ width: `${score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* TAB 2: SPATIAL MAP */}
          {activeTab === "map" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Map grid representation */}
              <div className="lg:col-span-2 space-y-4">
                <Card className="p-4 bg-slate-50 dark:bg-slate-900/30 border border-dashed rounded-xl relative min-h-[460px] flex flex-col justify-between">
                  {/* Top Layer indicators */}
                  <div className="flex flex-wrap gap-2 z-10">
                    <Button
                      size="sm"
                      variant={showIssuesLayer ? "default" : "outline"}
                      onClick={() => setShowIssuesLayer(!showIssuesLayer)}
                      className="h-7 text-[10px] rounded-full"
                    >
                      Issues ({mapData.clusters.length})
                    </Button>
                    <Button
                      size="sm"
                      variant={showHeatmapLayer ? "default" : "outline"}
                      onClick={() => setShowHeatmapLayer(!showHeatmapLayer)}
                      className="h-7 text-[10px] rounded-full"
                    >
                      Heatmap Density
                    </Button>
                    <Button
                      size="sm"
                      variant={showHotspotsLayer ? "default" : "outline"}
                      onClick={() => setShowHotspotsLayer(!showHotspotsLayer)}
                      className="h-7 text-[10px] rounded-full"
                    >
                      Projects Layer
                    </Button>
                  </div>

                  {/* Mock Visual Map Coordinate Grid */}
                  <div className="my-8 flex-1 border rounded-xl bg-card border-dashed p-6 flex flex-col justify-center items-center text-center relative overflow-hidden">
                    <div className="absolute inset-0 grid grid-cols-6 grid-rows-6 opacity-[0.03] dark:opacity-[0.07] pointer-events-none">
                      {Array.from({ length: 36 }).map((_, i) => (
                        <div key={i} className="border border-slate-700" />
                      ))}
                    </div>

                    <Compass className="h-10 w-10 text-slate-300 dark:text-slate-800 animate-spin-slow mb-3" />
                    <span className="font-bold text-xs uppercase tracking-wider text-slate-400">
                      Central Bangalore GIS Boundary Grid
                    </span>
                    <span className="text-[10px] text-muted-foreground max-w-sm mt-1 leading-normal">
                      Rendering Shivaji Nagar W12 Ward boundaries. Geotags are mapped in real-time.
                    </span>

                    {/* Styled Mock Clusters on Map */}
                    <div className="absolute top-[35%] left-[25%] cursor-pointer animate-pulse z-10" onClick={() => setSelectedHotspot(overview.hotspots[0])}>
                      <Badge className="bg-red-500 text-white font-bold p-1 px-2.5 rounded-full flex items-center gap-1 shadow-lg text-[10px] hover:scale-105 transition">
                        <MapPin className="h-3 w-3" /> W12: 18 Water Leak complaints
                      </Badge>
                    </div>

                    <div className="absolute bottom-[30%] right-[30%] cursor-pointer animate-pulse z-10" onClick={() => setSelectedHotspot(overview.hotspots[1])}>
                      <Badge className="bg-amber-500 text-white font-bold p-1 px-2.5 rounded-full flex items-center gap-1 shadow-lg text-[10px] hover:scale-105 transition">
                        <MapPin className="h-3 w-3" /> Sector-4: 6 Sidewalk complaints
                      </Badge>
                    </div>
                  </div>

                  {/* Legend */}
                  <div className="flex gap-4 text-[9px] font-semibold text-muted-foreground border-t pt-2 border-slate-200/50 dark:border-slate-800">
                    <div className="flex items-center gap-1">
                      <span className="h-2 w-2 rounded-full bg-red-500" /> Water Hotspot
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="h-2 w-2 rounded-full bg-amber-500" /> Road Hotspot
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="h-2 w-2 rounded-full bg-slate-300" /> Ward Bound Ring
                    </div>
                  </div>
                </Card>
              </div>

              {/* Right column: selected hotspot diagnostic */}
              <div className="space-y-4">
                {selectedHotspot ? (
                  <Card className="p-5 border-2 border-indigo-500/20 bg-indigo-500/[0.01] space-y-4">
                    <span className="text-[10px] text-indigo-500 font-bold uppercase tracking-wider block">Selected Project Hotspot</span>
                    <h3 className="font-extrabold text-md text-slate-800 dark:text-slate-200 border-b pb-2">
                      {selectedHotspot.proposed_project.title}
                    </h3>

                    <div className="space-y-3 text-xs">
                      <div className="flex justify-between border-b pb-2">
                        <span className="text-slate-500">Merged Complaints:</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">
                          {selectedHotspot.complaints_count} active tickets
                        </span>
                      </div>
                      <div className="flex justify-between border-b pb-2">
                        <span className="text-slate-500">Affected Population:</span>
                        <span className="font-bold text-indigo-600">
                          {selectedHotspot.affected_population.toLocaleString("en-IN")} citizens
                        </span>
                      </div>
                      <div className="flex justify-between border-b pb-2">
                        <span className="text-slate-500">Estimated Cost:</span>
                        <span className="font-bold text-emerald-500">
                          {selectedHotspot.proposed_project.estimated_cost}
                        </span>
                      </div>
                      <div className="flex justify-between border-b pb-2">
                        <span className="text-slate-500">Estimated Duration:</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">
                          {selectedHotspot.proposed_project.estimated_duration}
                        </span>
                      </div>
                      <div className="space-y-1">
                        <span className="text-slate-500 block">Developmental Impact:</span>
                        <p className="text-[11px] text-muted-foreground leading-normal bg-card p-2 rounded border font-sans">
                          {selectedHotspot.proposed_project.impact}
                        </p>
                      </div>
                    </div>

                    <div className="pt-2">
                      {tenderingStates[selectedHotspot.id] ? (
                        <div className="p-2 border rounded-lg bg-emerald-500/10 text-emerald-600 text-xs font-bold text-center flex items-center justify-center gap-1.5 animate-fade-in border-emerald-500/20">
                          <CheckCircle className="h-4 w-4" /> Project Tendering Flow Initiated
                        </div>
                      ) : (
                        <Button
                          onClick={() => handleStartTender(selectedHotspot.id)}
                          className="w-full text-xs h-9 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold flex items-center justify-center gap-1"
                        >
                          <Hammer className="h-3.5 w-3.5" /> Initiate Project Tendering
                        </Button>
                      )}
                    </div>
                  </Card>
                ) : (
                  <Card className="p-8 text-center text-xs text-muted-foreground border-dashed">
                    Select a hotspot pin on the map to evaluate developmental options.
                  </Card>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: CONSTITUENCY HEALTH */}
          {activeTab === "health" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(overview.category_scores).map(([name, score]: any, idx) => (
                <Card key={idx} className="p-5 flex flex-col justify-between min-h-[140px]">
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">{name}</span>
                    <Badge variant={score < 70 ? "destructive" : "default"} className="font-mono text-[9px]">
                      {score}/100 Score
                    </Badge>
                  </div>
                  <div className="mt-4 space-y-1">
                    <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          score < 70 ? "bg-red-500 animate-pulse" : "bg-emerald-500"
                        }`}
                        style={{ width: `${score}%` }}
                      />
                    </div>
                    <span className="text-[9px] text-muted-foreground block mt-1.5">
                      {score < 70
                        ? "⚠️ Below acceptable public index thresholds. Repair needed."
                        : "✓ Healthy infrastructure operations."}
                    </span>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* TAB 4: DEVELOPMENTAL PROJECTS */}
          {activeTab === "projects" && (
            <div className="space-y-6">
              <div className="border p-4 rounded-xl bg-indigo-500/[0.01] border-indigo-500/10 text-xs flex items-center justify-between gap-4">
                <p className="text-muted-foreground">
                  The following projects have been automatically derived by the **Spatial Intelligence Engine** to resolve overlapping citizen complaints collectively.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {overview.hotspots.map((hs: any, idx: number) => (
                  <Card key={idx} className="p-5 border-2 border-slate-100 dark:border-slate-800 hover:border-indigo-500/20 transition flex flex-col justify-between space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between items-center gap-2 border-b pb-2">
                        <span className="font-bold text-xs text-indigo-500 uppercase tracking-wider">{hs.category}</span>
                        <Badge variant="outline" className="text-[9px]">{hs.complaints_count} complaints merged</Badge>
                      </div>
                      <h4 className="font-extrabold text-md text-slate-800 dark:text-slate-200 mt-2">
                        {hs.proposed_project.title}
                      </h4>
                      <p className="text-xs text-slate-500 leading-relaxed font-sans mt-1">
                        Proposed Project: Replaces multiple individual repair logs. Coordinates are clustered within {hs.affected_population} citizen footprint zone.
                      </p>
                    </div>

                    <div className="space-y-3 pt-3 border-t">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-400">Budget Needed:</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">{hs.proposed_project.estimated_cost}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-400">Est. Duration:</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">{hs.proposed_project.estimated_duration}</span>
                      </div>

                      {tenderingStates[hs.id] ? (
                        <div className="p-2 border rounded-lg bg-emerald-500/10 text-emerald-600 text-xs font-bold text-center flex items-center justify-center gap-1.5 border-emerald-500/20">
                          <CheckCircle className="h-4 w-4" /> Tendering Process Active
                        </div>
                      ) : (
                        <Button
                          onClick={() => handleStartTender(hs.id)}
                          className="w-full text-xs h-9 bg-slate-900 hover:bg-slate-800 text-white font-semibold flex items-center justify-center gap-1 border-none"
                        >
                          <Hammer className="h-3.5 w-3.5" /> Start Tendering Process
                        </Button>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
