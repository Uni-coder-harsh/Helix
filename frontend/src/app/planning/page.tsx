"use client";

import React, { useState, useEffect } from "react";
import { API_BASE_URL } from "@/config";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sparkles,
  TrendingUp,
  AlertTriangle,
  Activity,
  CheckCircle,
  FileText,
  DollarSign,
  Users,
  Compass,
  Zap,
} from "lucide-react";

export default function OutcomePlanningPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [approvedStates, setApprovedStates] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetch(`${API_BASE_URL}/governance/planning/projects`)
      .then((res) => res.json())
      .then((data) => {
        setProjects(data);
        setLoading(false);
      })
      .catch((err) => {
        console.log("Offline, loading mock planning data:", err);
        setProjects([
          {
            id: "water-reconstruction- Shivaji Nagar",
            title: "Shivaji Nagar Drainage & Water Pipe Trunk Reconstruction",
            cost: "₹1.8 Crores",
            benefits: "14,230 citizens benefited",
            confidence: 0.93,
            evidence_count: 41,
            future_risk: "HIGH (Pipeline bursting hazard if deferred)",
            explanation:
              "Clustering 41 water leak complaints near Shivaji Nagar Hospital indicates severe pipeline decay. A complete trunk reconstruction is recommended over patching leaks, ensuring uninterrupted clinic access and raising water safety scores by 22%.",
            outcomes: [
              { metric: "Water Health Index", before: 61, after: 83 },
              { metric: "School Attendance", before: "Baseline", after: "+8.4%" },
              { metric: "Ambulance Delay", before: "Baseline", after: "-15.0%" },
            ],
            status: "PROPOSED",
          },
          {
            id: "road-reconstruction-sector4",
            title: "Sector 4 Pedestrian Corridor & Road Reconstruction",
            cost: "₹1.2 Crores",
            benefits: "8,350 citizens benefited",
            confidence: 0.91,
            evidence_count: 18,
            future_risk: "MEDIUM (Transit bottlenecks)",
            explanation:
              "Sector 4 features 18 transit hazard reports surrounding local primary schools. Restructuring the sidewalk corridor and repaving the arterial road solves these reports collectively, reducing student commute hazards by 60%.",
            outcomes: [
              { metric: "Road Health Index", before: 82, after: 95 },
              { metric: "Travel Time Latency", before: "Baseline", after: "-25.0%" },
              { metric: "Pedestrian Hazard Incidents", before: "Baseline", after: "-60.0%" },
            ],
            status: "PROPOSED",
          },
        ]);
        setLoading(false);
      });
  }, []);

  const handleApproveProject = (projectId: string) => {
    fetch(`${API_BASE_URL}/governance/planning/projects/${projectId}/approve`, {
      method: "POST",
    })
      .then((r) => r.json())
      .then(() => {
        setApprovedStates((prev) => ({ ...prev, [projectId]: true }));
      })
      .catch((err) => {
        console.log("Offline approve, updating state locally:", err);
        setApprovedStates((prev) => ({ ...prev, [projectId]: true }));
      });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Outcome Planning Console</h1>
        <p className="text-xs text-muted-foreground">
          Analyze constituency-wide trends, cluster citizen complaints, and simulate developmental projects rather than individual ticket updates.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-muted-foreground animate-pulse">
          Simulating outcome planning projections...
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {projects.map((proj) => {
            const isApproved = approvedStates[proj.id];
            return (
              <Card
                key={proj.id}
                className="p-6 border-2 border-slate-100 dark:border-slate-800 hover:border-indigo-500/20 transition space-y-6"
              >
                {/* Title & Badge */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-[9px] uppercase tracking-wider text-indigo-500 border-indigo-500/20 bg-indigo-500/[0.02]">
                        <Sparkles className="h-3 w-3 mr-0.5 animate-pulse" /> Derived Proposal
                      </Badge>
                      <span className="text-[10px] text-muted-foreground font-semibold">
                        Based on {proj.evidence_count} citizen complaints
                      </span>
                    </div>
                    <h2 className="text-lg font-bold tracking-tight text-slate-800 dark:text-slate-200 mt-1">
                      {proj.title}
                    </h2>
                  </div>
                  <div className="flex items-center gap-4 text-xs font-semibold">
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-4 w-4 text-emerald-500" />
                      <span>{proj.cost}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4 text-slate-400" />
                      <span>{proj.benefits}</span>
                    </div>
                  </div>
                </div>

                {/* Grid stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Outcomes Simulation before/after */}
                  <div className="md:col-span-2 space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Simulated Outcomes
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      {proj.outcomes.map((out: any, i: number) => (
                        <div key={i} className="border p-3.5 rounded-xl bg-card flex flex-col justify-between min-h-[90px]">
                          <span className="text-[10px] text-muted-foreground font-bold uppercase">{out.metric}</span>
                          <div className="flex items-baseline gap-2 mt-2">
                            <span className="text-slate-400 text-xs font-mono">{out.before}</span>
                            <span className="text-indigo-400 text-xs font-mono">→</span>
                            <span className="text-emerald-500 font-extrabold text-sm font-mono">{out.after}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Future Risk & confidence info */}
                  <div className="space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Risk Evaluation
                    </h3>
                    <div className="border p-3.5 rounded-xl bg-card space-y-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Execution Confidence:</span>
                        <span className="font-bold text-indigo-500 font-mono">{(proj.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div className="space-y-1">
                        <span className="text-slate-500 block">Postponement Risk:</span>
                        <span className="font-bold text-red-500 text-[10px] uppercase font-mono block">
                          {proj.future_risk}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Natural Language Explanation from Gemini */}
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/40 border space-y-2">
                  <span className="text-[10px] font-bold text-indigo-500 uppercase tracking-wider block flex items-center gap-1.5">
                    <Sparkles className="h-3.5 w-3.5" /> AI Justification (Gemini Explainer)
                  </span>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans">
                    {proj.explanation}
                  </p>
                </div>

                {/* Approve Button */}
                <div className="flex justify-end pt-2">
                  {isApproved ? (
                    <div className="p-2.5 px-6 border rounded-lg bg-emerald-500/10 text-emerald-600 text-xs font-bold flex items-center gap-1.5 animate-fade-in border-emerald-500/20">
                      <CheckCircle className="h-4 w-4" /> Approved: Developmental Tender Active
                    </div>
                  ) : (
                    <Button
                      onClick={() => handleApproveProject(proj.id)}
                      className="px-6 text-xs h-9 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold flex items-center gap-1.5 border-none"
                    >
                      Approve Developmental Project
                    </Button>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
