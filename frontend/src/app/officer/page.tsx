"use client";

import React, { useState, useEffect } from "react";
import { fetchWithAuth } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import {
  Search,
  AlertTriangle,
  CheckCircle2,
  Clock,
  TrendingUp,
  TrendingDown,
  Activity,
  ArrowRight,
  ShieldAlert,
  Sun,
  Sparkles,
} from "lucide-react";

export default function OfficerDashboard() {
  const [issues, setIssues] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("All");
  const [activeTab, setActiveTab] = useState<"all" | "pending_ai" | "in_progress">("all");
  const [loading, setLoading] = useState(true);

  // Proactive Briefing State
  const [briefing, setBriefing] = useState<any>(null);
  const [loadingBriefing, setLoadingBriefing] = useState(true);

  useEffect(() => {
    // 1. Fetch Proactive Morning Briefing
    fetchWithAuth("/governance/proactive/morning-brief")
      .then((data) => {
        setBriefing(data || null);
        setLoadingBriefing(false);
      })
      .catch((err) => {
        console.error("Failed to load briefing:", err);
        setBriefing(null);
        setLoadingBriefing(false);
      });

    // 2. Fetch pending issues
    fetchWithAuth("/governance/issues/pending")
      .then((data) => {
        if (Array.isArray(data)) {
          setIssues(data);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch pending issues:", err);
        setLoading(false);
      });
  }, []);

  const filteredIssues = issues.filter((issue) => {
    const matchesSearch =
      issue.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.id?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === "All" || issue.status === statusFilter;

    let matchesTab = true;
    if (activeTab === "pending_ai") {
      matchesTab = issue.status === "INTAKE" || issue.status === "TRIAGE";
    } else if (activeTab === "in_progress") {
      matchesTab = issue.status === "ASSIGNED" || issue.status === "IN_PROGRESS";
    }

    return matchesSearch && matchesStatus && matchesTab;
  });

  return (
    <div className="space-y-8 animate-fade-in py-2">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-5">
        <div className="space-y-1">
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-primary via-indigo-500 to-purple-600 bg-clip-text text-transparent">
            Constituency Decision Dashboard
          </h1>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Proactive constituency health indexing, morning briefings, and triage logs.
          </p>
        </div>
      </div>

      {loadingBriefing ? (
        <BriefingSkeleton />
      ) : briefing ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
          {/* Proactive Greeting Card */}
          <Card className="lg:col-span-2 p-6 border border-indigo-500/20 bg-indigo-500/[0.01] dark:bg-indigo-950/[0.02] space-y-4 shadow-sm hover:shadow-md transition relative overflow-hidden">
            <div className="absolute top-0 right-0 h-24 w-24 bg-indigo-500/5 rounded-full blur-xl" />
            <div className="flex items-center gap-2 border-b pb-3 border-slate-100 dark:border-slate-800/80">
              <Sun className="h-5 w-5 text-indigo-500" />
              <h2 className="text-sm font-bold tracking-wider uppercase text-indigo-600 dark:text-indigo-400 flex items-center gap-1.5">
                <Sparkles className="h-4.5 w-4.5 animate-pulse" /> Proactive Morning Briefing
              </h2>
            </div>
            <div className="font-sans text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line bg-card p-4 rounded-xl border shadow-inner">
              {briefing.morning_brief || "No briefing available."}
            </div>
          </Card>

          {/* Risk Alerts Panel */}
          <Card className="p-6 border border-red-500/20 bg-red-500/[0.01] dark:bg-red-950/[0.02] space-y-4 shadow-sm flex flex-col justify-between hover:shadow-md transition relative overflow-hidden">
            <div className="absolute top-0 right-0 h-24 w-24 bg-red-500/5 rounded-full blur-xl" />
            <div className="flex items-center gap-2 border-b pb-3 border-slate-100 dark:border-slate-800/80">
              <ShieldAlert className="h-5 w-5 text-red-500" />
              <h3 className="text-sm font-bold text-red-600 dark:text-red-400 uppercase tracking-wider">Critical SLA Risks</h3>
            </div>
            <div className="space-y-3">
              {briefing.risk_alerts?.length > 0 ? briefing.risk_alerts.map((alert: any, idx: number) => (
                <div key={idx} className="border border-red-500/10 p-3 rounded-xl bg-card text-xs flex justify-between items-center gap-3 hover:border-red-500/30 transition shadow-sm">
                  <div className="truncate">
                    <p className="font-bold truncate text-slate-850 dark:text-slate-200">{alert.title}</p>
                    <p className="text-[10px] text-muted-foreground mt-1 font-semibold">{alert.impact_weight} affected</p>
                  </div>
                  <div className="flex-shrink-0">
                    <Badge variant="destructive" className="text-[9px] font-mono font-bold px-2 py-0.5">{alert.sla_remaining}</Badge>
                  </div>
                </div>
              )) : (
                <p className="text-xs text-muted-foreground">No critical SLA risks at this time.</p>
              )}
            </div>
          </Card>
        </div>
      ) : (
        <div className="text-sm text-muted-foreground bg-card p-4 border rounded-xl shadow-sm text-center">
          No proactive morning brief generated.
        </div>
      )}

      {/* Constituency Health score Widget */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <Card className="p-6 bg-gradient-to-br from-indigo-950/80 to-slate-900 border border-indigo-500/20 text-white flex flex-col justify-between min-h-[170px] lg:col-span-1 shadow-md relative overflow-hidden">
          <div className="absolute top-0 right-0 h-24 w-24 bg-indigo-500/10 rounded-full blur-xl" />
          <div>
            <div className="flex justify-between items-center text-[10px] text-indigo-300 font-bold tracking-wider uppercase">
              <span>Constituency Health</span>
              <Activity className="h-4.5 w-4.5 text-indigo-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-5">
              <span className="text-5xl font-extrabold tracking-tight">{briefing?.overall_health_score || "--"}</span>
              <span className="text-indigo-300/60 text-sm font-semibold">/ 100</span>
            </div>
          </div>
        </Card>

        {/* Category Health Scores */}
        <div className="lg:col-span-3 grid grid-cols-2 sm:grid-cols-5 gap-4">
          {briefing?.category_forecasts?.map((cat: any, i: number) => (
             <Card key={i} className="p-4 bg-card text-card-foreground border hover:border-slate-300 dark:hover:border-slate-800 transition flex flex-col justify-between shadow-sm">
             <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">{cat.category}</span>
             <div className="text-3xl font-extrabold mt-3 tracking-tight">{cat.current_score}</div>
             <span className="text-[10px] text-emerald-500 font-bold flex items-center gap-0.5 mt-2">
               {cat.forecast_direction}
             </span>
           </Card>
          ))}
          {!briefing?.category_forecasts && (
            <div className="col-span-full flex items-center justify-center p-4 text-sm text-muted-foreground border rounded-xl border-dashed">
              No category data available
            </div>
          )}
        </div>
      </div>

      {/* Operational Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-5 flex items-center space-x-4 bg-card border shadow-sm hover:shadow transition">
          <div className="p-3 bg-red-500/10 text-red-500 rounded-xl border border-red-500/20">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Pending Triage</div>
            <div className="text-2xl font-extrabold mt-0.5 tracking-tight">
              {issues.filter((i) => i.status === "INTAKE" || i.status === "TRIAGE").length}
            </div>
          </div>
        </Card>
        <Card className="p-5 flex items-center space-x-4 bg-card border shadow-sm hover:shadow transition">
          <div className="p-3 bg-amber-500/10 text-amber-500 rounded-xl border border-amber-500/20">
            <Clock className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Active Field Tasks</div>
            <div className="text-2xl font-extrabold mt-0.5 tracking-tight">
              {issues.filter((i) => i.status === "ASSIGNED" || i.status === "IN_PROGRESS").length}
            </div>
          </div>
        </Card>
        <Card className="p-5 flex items-center space-x-4 bg-card border shadow-sm hover:shadow transition">
          <div className="p-3 bg-emerald-500/10 text-emerald-500 rounded-xl border border-emerald-500/20">
            <CheckCircle2 className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Resolved Today</div>
            <div className="text-2xl font-extrabold mt-0.5 tracking-tight">{issues.filter((i) => i.status === "COMPLETED").length}</div>
          </div>
        </Card>
      </div>

      {/* Filters bar */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-card border p-4 rounded-xl shadow-sm">
        {/* Navigation Tabs */}
        <div className="flex bg-slate-105 dark:bg-slate-800/80 p-1 rounded-xl w-full md:w-auto border">
          <button
            onClick={() => setActiveTab("all")}
            className={`flex-1 md:flex-none px-5 py-2 rounded-lg text-xs font-bold transition-all ${
              activeTab === "all"
                ? "bg-white dark:bg-slate-900 shadow text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            All Work Items
          </button>
          <button
            onClick={() => setActiveTab("pending_ai")}
            className={`flex-1 md:flex-none px-5 py-2 rounded-lg text-xs font-bold transition-all ${
              activeTab === "pending_ai"
                ? "bg-white dark:bg-slate-900 shadow text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Requires Triage
          </button>
          <button
            onClick={() => setActiveTab("in_progress")}
            className={`flex-1 md:flex-none px-5 py-2 rounded-lg text-xs font-bold transition-all ${
              activeTab === "in_progress"
                ? "bg-white dark:bg-slate-900 shadow text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Active Field Tasks
          </button>
        </div>

        {/* Input filters */}
        <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
          <div className="relative w-full sm:w-60 shadow-sm rounded-lg overflow-hidden border">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <Input
              type="search"
              placeholder="Search issues..."
              className="pl-9 text-xs h-9 bg-background border-none focus-visible:ring-0"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="h-9 rounded-lg border border-input bg-background px-3 text-xs font-semibold focus-visible:outline-none shadow-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="All">All Statuses</option>
            <option value="INTAKE">Intake</option>
            <option value="TRIAGE">Triage</option>
            <option value="ASSIGNED">Assigned</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
          </select>
        </div>
      </div>

      {/* Issues Queue Table Layout */}
      <div className="overflow-x-auto rounded-xl border bg-card shadow-sm">
        {loading ? (
          <QueueSkeleton />
        ) : (
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b bg-slate-50/80 dark:bg-slate-900/40 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                <th className="p-4">Issue ID</th>
                <th className="p-4">Title / Category</th>
                <th className="p-4">Priority</th>
                <th className="p-4">Status</th>
                <th className="p-4">Last Updated</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredIssues.length > 0 ? (
                filteredIssues.map((issue) => (
                  <tr
                    key={issue.id}
                    className="hover:bg-slate-55/20 dark:hover:bg-slate-900/20 transition-colors duration-150"
                  >
                    <td className="p-4 font-mono font-bold text-slate-450">{issue.id.split("-")[0]}</td>
                    <td className="p-4 max-w-[280px]">
                      <div className="font-bold text-sm text-slate-850 dark:text-slate-200 line-clamp-1 leading-snug">{issue.title}</div>
                      <div className="text-slate-400 mt-1 font-medium">{issue.category}</div>
                    </td>
                    <td className="p-4">
                      <Badge variant="outline">{issue.priority || "NORMAL"}</Badge>
                    </td>
                    <td className="p-4">
                      <Badge variant="secondary">
                        {issue.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-muted-foreground font-medium">
                      {new Date(issue.updated_at || Date.now()).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-right space-x-1.5 whitespace-nowrap">
                      <Link href={`/issues/${issue.id}`}>
                        <Button size="sm" variant="ghost" className="h-8 text-[11px] font-bold">
                          Open Brief <ArrowRight className="h-3 w-3 ml-0.5" />
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="p-0">
                    <QueueEmptyState />
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

// Skeletons
function BriefingSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-pulse">
      <Card className="lg:col-span-2 p-5 border space-y-4 bg-card">
        <div className="flex items-center gap-2 border-b pb-3">
          <div className="h-5 w-5 bg-slate-200 dark:bg-slate-800 rounded-full" />
          <div className="h-4.5 w-48 bg-slate-200 dark:bg-slate-800 rounded" />
        </div>
        <div className="space-y-2">
          <div className="h-4.5 w-full bg-slate-200 dark:bg-slate-800 rounded" />
          <div className="h-4.5 w-full bg-slate-200 dark:bg-slate-800 rounded" />
          <div className="h-4.5 w-5/6 bg-slate-200 dark:bg-slate-800 rounded" />
        </div>
      </Card>
      <Card className="p-5 border space-y-4 bg-card flex flex-col justify-between">
        <div className="flex items-center gap-2 border-b pb-3">
          <div className="h-5 w-5 bg-slate-200 dark:bg-slate-800 rounded-full" />
          <div className="h-4.5 w-32 bg-slate-200 dark:bg-slate-800 rounded" />
        </div>
        <div className="space-y-3 flex-1 pt-2">
          <div className="h-12 bg-slate-200 dark:bg-slate-800 rounded-lg" />
          <div className="h-12 bg-slate-200 dark:bg-slate-800 rounded-lg" />
        </div>
      </Card>
    </div>
  );
}

function QueueSkeleton() {
  return (
    <div className="divide-y animate-pulse">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="h-4 w-12 bg-slate-200 dark:bg-slate-800 rounded" />
          <div className="space-y-1.5 flex-1 max-w-[280px]">
            <div className="h-4.5 w-full bg-slate-200 dark:bg-slate-800 rounded" />
            <div className="h-3 w-2/3 bg-slate-200 dark:bg-slate-800 rounded" />
          </div>
          <div className="h-4 w-20 bg-slate-200 dark:bg-slate-800 rounded" />
          <div className="h-5.5 w-16 bg-slate-200 dark:bg-slate-800 rounded-full" />
          <div className="h-5.5 w-16 bg-slate-200 dark:bg-slate-800 rounded-full" />
        </div>
      ))}
    </div>
  );
}

function QueueEmptyState() {
  return (
    <div className="text-center py-16 px-4 space-y-4">
      <div className="mx-auto h-12 w-12 rounded-full bg-slate-105 dark:bg-slate-800 flex items-center justify-center text-muted-foreground border">
        <Search className="h-5 w-5 text-slate-500" />
      </div>
      <div className="space-y-1">
        <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">No data available</h3>
        <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-normal">
          There are no pending tickets at this moment.
        </p>
      </div>
    </div>
  );
}
