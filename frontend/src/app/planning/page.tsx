"use client";

import React, { useState, useEffect } from "react";
import { fetchWithAuth } from "@/lib/api";
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
  ArrowRight,
} from "lucide-react";

export default function OutcomePlanningPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [approvedStates, setApprovedStates] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWithAuth("/governance/planning/projects")
      .then((data) => {
        setProjects(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load planning data:", err);
        setError("Failed to load data");
        setProjects([]);
        setLoading(false);
      });
  }, []);

  const handleApproveProject = (projectId: string) => {
    fetchWithAuth(`/governance/planning/projects/${projectId}/approve`, {
      method: "POST",
    })
      .then(() => {
        setApprovedStates((prev) => ({ ...prev, [projectId]: true }));
      })
      .catch((err) => {
        console.error("Failed to approve project:", err);
        // Only update local state if we don't want to show an error, but let's be strict
        alert("Failed to approve project. Check connection.");
      });
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-5xl mx-auto py-2">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">
          Outcome Planning Console
        </h1>
        <p className="text-sm text-muted-foreground leading-relaxed max-w-3xl">
          Analyze constituency-wide trends, cluster citizen complaints, and simulate developmental projects rather than individual ticket updates.
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-6">
          <ProjectSkeleton />
          <ProjectSkeleton />
        </div>
      ) : error || projects.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="grid grid-cols-1 gap-8">
          {projects.map((proj) => {
            const isApproved = approvedStates[proj.id] || proj.status === "APPROVED";
            return (
              <Card
                key={proj.id}
                className="p-6 md:p-8 border border-slate-100 dark:border-slate-800 hover:border-indigo-500/30 transition-all duration-300 shadow-sm hover:shadow-lg space-y-6 relative overflow-hidden bg-card"
              >
                {/* Decorative border accent */}
                <div className="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-indigo-500 to-purple-600" />

                {/* Title & Badge */}
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b pb-5">
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant="outline" className="font-mono text-[9px] uppercase tracking-wider text-indigo-600 dark:text-indigo-400 border-indigo-500/20 bg-indigo-500/[0.04] px-2 py-0.5">
                        <Sparkles className="h-3 w-3 mr-1 animate-pulse inline" /> Derived Proposal
                      </Badge>
                      <span className="text-[11px] text-muted-foreground font-medium">
                        Based on <span className="font-bold text-slate-700 dark:text-slate-300">{proj.evidence_count || 0} citizen complaints</span>
                      </span>
                    </div>
                    <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100 mt-1 leading-snug">
                      {proj.title}
                    </h2>
                  </div>
                  <div className="flex items-center gap-5 text-xs font-semibold bg-slate-50 dark:bg-slate-900/50 p-2.5 px-4 rounded-xl border">
                    <div className="flex items-center gap-1.5">
                      <DollarSign className="h-4 w-4 text-emerald-500" />
                      <span className="text-slate-800 dark:text-slate-200">{proj.cost || "N/A"}</span>
                    </div>
                    <div className="h-4 w-px bg-slate-200 dark:bg-slate-800" />
                    <div className="flex items-center gap-1.5">
                      <Users className="h-4 w-4 text-indigo-500" />
                      <span className="text-slate-800 dark:text-slate-200">{proj.benefits || "N/A"}</span>
                    </div>
                  </div>
                </div>

                {/* Grid stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Outcomes Simulation before/after */}
                  <div className="md:col-span-2 space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 flex items-center gap-1.5">
                      <Activity className="h-3.5 w-3.5" /> Simulated Outcomes
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      {proj.outcomes && proj.outcomes.map((out: any, i: number) => {
                        const isNumeric = !isNaN(Number(out.before)) && !isNaN(Number(out.after));
                        const delta = isNumeric ? Number(out.after) - Number(out.before) : null;
                        const deltaText = delta !== null && delta > 0 ? `+${delta}` : "";

                        return (
                          <div key={i} className="border p-4 rounded-xl bg-slate-50/50 dark:bg-slate-900/20 flex flex-col justify-between min-h-[100px] hover:bg-slate-50 dark:hover:bg-slate-900/40 transition">
                            <span className="text-[10px] text-muted-foreground font-bold uppercase leading-tight">{out.metric}</span>
                            <div className="mt-3">
                              <div className="flex items-baseline gap-2">
                                <span className="text-slate-400 text-xs font-mono">{out.before}</span>
                                <span className="text-indigo-400 text-xs font-mono">→</span>
                                <span className="text-emerald-500 font-extrabold text-base font-mono">{out.after}</span>
                              </div>
                              {deltaText && (
                                <span className="inline-flex items-center text-[9px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-1.5 py-0.2 rounded mt-1">
                                  <TrendingUp className="h-2.5 w-2.5 mr-0.5" /> {deltaText} pts
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Future Risk & confidence info */}
                  <div className="space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 flex items-center gap-1.5">
                      <AlertTriangle className="h-3.5 w-3.5" /> Risk Evaluation
                    </h3>
                    <div className="border p-4 rounded-xl bg-slate-50/50 dark:bg-slate-900/20 space-y-3.5 text-xs">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-500 font-medium">Confidence Score:</span>
                        <span className="font-extrabold text-indigo-600 dark:text-indigo-400 font-mono text-sm">{((proj.confidence || 0) * 100).toFixed(0)}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500" style={{ width: `${(proj.confidence || 0) * 100}%` }} />
                      </div>
                      <div className="space-y-1 pt-1.5 border-t">
                        <span className="text-slate-500 font-medium block">Postponement Risk:</span>
                        <span className="font-bold text-red-500 dark:text-red-400 text-[10px] uppercase font-mono block leading-normal">
                          {proj.future_risk || "N/A"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Natural Language Explanation from Gemini */}
                <div className="p-4 md:p-5 rounded-xl bg-slate-50 dark:bg-slate-900/40 border border-slate-100 dark:border-slate-800/80 space-y-2.5">
                  <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="h-3.5 w-3.5 animate-pulse" /> AI Justification (Gemini Explainer)
                  </span>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans font-medium">
                    {proj.explanation || "No explanation provided."}
                  </p>
                </div>

                {/* Approve Button */}
                <div className="flex justify-end pt-2 border-t">
                  {isApproved ? (
                    <div className="p-2.5 px-6 border rounded-lg bg-emerald-500/10 text-emerald-600 text-xs font-bold flex items-center gap-1.5 animate-fade-in border-emerald-500/20 shadow-sm">
                      <CheckCircle className="h-4 w-4" /> Approved: Developmental Tender Active
                    </div>
                  ) : (
                    <Button
                      onClick={() => handleApproveProject(proj.id)}
                      className="px-6 text-xs h-9.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold flex items-center gap-1.5 shadow-sm transition-all"
                    >
                      Approve Developmental Project <ArrowRight className="h-3.5 w-3.5" />
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

// Skeleton Component
function ProjectSkeleton() {
  return (
    <Card className="p-6 md:p-8 border border-slate-100 dark:border-slate-800 rounded-xl space-y-6 animate-pulse">
      <div className="flex flex-col md:flex-row justify-between gap-4 border-b pb-5">
        <div className="space-y-2 flex-1">
          <div className="flex items-center gap-2">
            <div className="h-4 w-28 bg-slate-200 dark:bg-slate-800 rounded" />
            <div className="h-3.5 w-40 bg-slate-200 dark:bg-slate-800 rounded" />
          </div>
          <div className="h-7 w-3/4 bg-slate-200 dark:bg-slate-800 rounded" />
        </div>
        <div className="h-10 w-44 bg-slate-200 dark:bg-slate-800 rounded sm:self-center" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-4">
          <div className="h-4 w-32 bg-slate-200 dark:bg-slate-800 rounded" />
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="h-24 bg-slate-100 dark:bg-slate-900/60 rounded-xl" />
            <div className="h-24 bg-slate-100 dark:bg-slate-900/60 rounded-xl" />
            <div className="h-24 bg-slate-100 dark:bg-slate-900/60 rounded-xl" />
          </div>
        </div>
        <div className="space-y-4">
          <div className="h-4 w-28 bg-slate-200 dark:bg-slate-800 rounded" />
          <div className="h-24 bg-slate-100 dark:bg-slate-900/60 rounded-xl" />
        </div>
      </div>
      <div className="h-16 bg-slate-100/50 dark:bg-slate-900/30 rounded-xl" />
      <div className="flex justify-end pt-2">
        <div className="h-9 w-48 bg-slate-200 dark:bg-slate-800 rounded" />
      </div>
    </Card>
  );
}

// Empty State Component
function EmptyState() {
  return (
    <div className="text-center py-20 px-6 border border-dashed rounded-2xl border-slate-200 dark:border-slate-800 bg-slate-50/30 dark:bg-slate-950/10 max-w-lg mx-auto space-y-4 shadow-inner">
      <div className="mx-auto h-12 w-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-muted-foreground border">
        <Compass className="h-6 w-6 text-slate-500" />
      </div>
      <div className="space-y-1">
        <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">No planning projects available</h3>
        <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-normal">
          There are currently no developmental projects under evaluation by the Outcome Planning Engine.
        </p>
      </div>
    </div>
  );
}
