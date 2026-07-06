"use client";

import React, { useState } from "react";
import { Issue, mockIssues } from "@/lib/mock-data";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import Link from "next/link";
import { MapPin, Info, Compass, Layers } from "lucide-react";

export function MapPlaceholder() {
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>("All");
  const [statusFilter, setStatusFilter] = useState<string>("All");

  const categories = ["All", ...Array.from(new Set(mockIssues.map(i => i.category)))];
  const statuses = ["All", "Submitted", "Validated", "Assigned", "In_Progress", "Completed"];

  // Filter issues based on select boxes
  const filteredIssues = mockIssues.filter(issue => {
    const matchesCategory = categoryFilter === "All" || issue.category === categoryFilter;
    const matchesStatus = statusFilter === "All" || issue.status === statusFilter;
    return matchesCategory && matchesStatus;
  });

  // Simple coordinate projection from lat/lng to SVG space (800x450 px)
  // Lat range: 12.90 to 13.00, Lng range: 77.55 to 77.68
  const projectCoordinates = (lat: number, lng: number) => {
    const minLat = 12.90;
    const maxLat = 13.00;
    const minLng = 77.55;
    const maxLng = 77.68;

    const x = ((lng - minLng) / (maxLng - minLng)) * 700 + 50;
    const y = 400 - ((lat - minLat) / (maxLat - minLat)) * 350 + 25; // invert Y since SVG goes top-to-bottom
    return { x, y };
  };

  return (
    <div className="flex flex-col space-y-4">
      {/* Map Control Bar */}
      <div className="flex flex-wrap gap-4 items-center justify-between rounded-lg border bg-card p-4 text-card-foreground shadow-sm">
        <div className="flex items-center space-x-2">
          <Compass className="h-5 w-5 text-primary animate-spin" style={{ animationDuration: "10s" }} />
          <h2 className="text-md font-semibold tracking-tight">Interactive GIS Map Console</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          <div className="flex items-center space-x-2">
            <span className="text-xs text-muted-foreground font-medium flex items-center gap-1">
              <Layers className="h-3.5 w-3.5" /> Category:
            </span>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="h-8 rounded-md border border-input bg-background px-2 text-xs focus-visible:outline-none"
            >
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-muted-foreground font-medium">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="h-8 rounded-md border border-input bg-background px-2 text-xs focus-visible:outline-none"
            >
              {statuses.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* SVG Map Canvas */}
        <div className="lg:col-span-3 relative h-[450px] w-full rounded-xl border bg-slate-950 overflow-hidden shadow-inner flex flex-col justify-end">
          {/* Coordinates Grid Overlay */}
          <div className="absolute inset-0 grid grid-cols-6 grid-rows-6 opacity-[0.03] pointer-events-none">
            {Array.from({ length: 36 }).map((_, i) => (
              <div key={i} className="border border-white text-[8px] p-0.5 text-white font-mono select-none" />
            ))}
          </div>

          {/* SVG Map Shape */}
          <svg className="absolute inset-0 h-full w-full" viewBox="0 0 800 450" fill="none" xmlns="http://www.w3.org/2000/svg">
            {/* Wards polygons */}
            {/* Ward East */}
            <path
              d="M500 50 L750 120 L720 380 L480 320 L500 50 Z"
              className="fill-indigo-950/20 stroke-indigo-500/20 hover:fill-indigo-500/10 transition-colors duration-300"
              strokeWidth="2"
            />
            {/* Ward West */}
            <path
              d="M50 80 L350 40 L380 250 L120 300 L50 80 Z"
              className="fill-cyan-950/20 stroke-cyan-500/20 hover:fill-cyan-500/10 transition-colors duration-300"
              strokeWidth="2"
            />
            {/* Ward Central */}
            <path
              d="M350 40 L500 50 L480 320 L380 250 Z"
              className="fill-emerald-950/20 stroke-emerald-500/20 hover:fill-emerald-500/10 transition-colors duration-300"
              strokeWidth="2"
            />
            {/* Ward South */}
            <path
              d="M380 250 L480 320 L400 430 L120 300 Z"
              className="fill-violet-950/20 stroke-violet-500/20 hover:fill-violet-500/10 transition-colors duration-300"
              strokeWidth="2"
            />

            {/* Compass Scale indicators */}
            <line x1="20" y1="420" x2="120" y2="420" stroke="#475569" strokeWidth="2" />
            <line x1="20" y1="415" x2="20" y2="425" stroke="#475569" strokeWidth="2" />
            <line x1="120" y1="415" x2="120" y2="425" stroke="#475569" strokeWidth="2" />
            <text x="35" y="410" fill="#64748B" fontSize="9" className="font-mono">Scale 1:50,000</text>
            <text x="735" y="430" fill="#64748B" fontSize="10" className="font-mono">12.9° N / 77.5° E</text>
          </svg>

          {/* Issue Location Pins */}
          {filteredIssues.map((issue) => {
            const { x, y } = projectCoordinates(issue.location.lat, issue.location.lng);
            const isSelected = selectedIssue?.id === issue.id;

            return (
              <button
                key={issue.id}
                onClick={() => setSelectedIssue(issue)}
                className="absolute -translate-x-1/2 -translate-y-1/2 group transition-all duration-300 focus:outline-none z-10 hover:z-20"
                style={{ left: `${x}px`, top: `${y}px` }}
              >
                <div className="relative flex items-center justify-center">
                  <span className={`absolute inline-flex h-6 w-6 rounded-full opacity-50 ${
                    issue.priority === "Critical"
                      ? "animate-ping bg-red-400"
                      : issue.priority === "High"
                      ? "animate-ping bg-orange-400"
                      : "bg-slate-400"
                  }`} />
                  <MapPin className={`h-6 w-6 transition-transform duration-200 group-hover:scale-125 ${
                    isSelected
                      ? "text-primary scale-125 stroke-[2.5]"
                      : issue.priority === "Critical"
                      ? "text-red-500"
                      : issue.priority === "High"
                      ? "text-orange-500"
                      : "text-amber-500"
                  }`} />
                </div>
              </button>
            );
          })}

          <div className="p-3 bg-slate-900/80 backdrop-blur-sm border-t border-slate-800 text-[10px] text-slate-400 font-mono flex justify-between z-10">
            <span>Rendering {filteredIssues.length} geo-spatial nodes</span>
            <span>Map Engine: Leaflet Mock Vector Overlay</span>
          </div>
        </div>

        {/* Info panel */}
        <div className="lg:col-span-1">
          {selectedIssue ? (
            <Card className="h-[450px] p-4 flex flex-col justify-between overflow-y-auto">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <span className="text-xs font-semibold text-slate-400">{selectedIssue.id}</span>
                  <Badge
                    variant={
                      selectedIssue.priority === "Critical"
                        ? "destructive"
                        : selectedIssue.priority === "High"
                        ? "warning"
                        : "default"
                    }
                  >
                    {selectedIssue.priority}
                  </Badge>
                </div>

                <div className="space-y-1">
                  <h3 className="font-semibold text-base leading-snug">{selectedIssue.title}</h3>
                  <p className="text-xs text-muted-foreground">{selectedIssue.category}</p>
                </div>

                <p className="text-xs text-slate-600 dark:text-slate-300 line-clamp-4">
                  {selectedIssue.description}
                </p>

                <div className="border-t pt-3 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Reporter:</span>
                    <span className="font-medium">{selectedIssue.citizenName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Status:</span>
                    <Badge variant={selectedIssue.status === "Completed" ? "success" : "info"}>
                      {selectedIssue.status.replace("_", " ")}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Constituency:</span>
                    <span>{selectedIssue.constituency}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Lat / Lng:</span>
                    <span className="font-mono text-[10px]">
                      {selectedIssue.location.lat.toFixed(4)}, {selectedIssue.location.lng.toFixed(4)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-2 pt-4">
                <Link href={`/issues/${selectedIssue.id}`} className="w-full">
                  <button className="w-full h-9 inline-flex items-center justify-center rounded-md bg-primary text-primary-foreground text-xs font-semibold hover:bg-primary/90 transition shadow">
                    View Complete Records
                  </button>
                </Link>
                <button
                  onClick={() => setSelectedIssue(null)}
                  className="w-full h-8 text-xs text-muted-foreground hover:text-foreground font-medium"
                >
                  Clear Selection
                </button>
              </div>
            </Card>
          ) : (
            <Card className="h-[450px] p-6 flex flex-col items-center justify-center text-center text-muted-foreground border-dashed">
              <Info className="h-10 w-10 mb-3 text-muted-foreground/50 animate-bounce" style={{ animationDuration: "3s" }} />
              <h3 className="font-semibold text-sm mb-1 text-slate-700 dark:text-slate-300">No Location Selected</h3>
              <p className="text-xs max-w-[200px]">
                Click on any map marker node on the left to pull real-time telemetry metrics and updates.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
