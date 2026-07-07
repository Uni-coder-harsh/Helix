"use client";

import React, { useState, useEffect } from "react";
import { API_BASE_URL } from "@/config";
import { mockIssues, Issue, IssueUpdate } from "@/lib/mock-data";
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
  const [issues, setIssues] = useState<Issue[]>(mockIssues);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("All");
  const [activeTab, setActiveTab] = useState<"all" | "pending_ai" | "in_progress">("all");
  const [loading, setLoading] = useState(true);

  // Proactive Briefing State
  const [briefing, setBriefing] = useState<any>(null);
  const [loadingBriefing, setLoadingBriefing] = useState(true);

  useEffect(() => {
    // 1. Fetch Proactive Morning Briefing
    fetch(`${API_BASE_URL}/governance/proactive/morning-brief`)
      .then((res) => res.json())
      .then((data) => {
        setBriefing(data);
        setLoadingBriefing(false);
      })
      .catch((err) => {
        console.log("Offline, falling back to mock briefing:", err);
        setBriefing({
          constituency: "Central Bengaluru Constituency",
          overall_health_score: 78,
          overall_health_trend: "UP",
          morning_brief:
            "Good Morning MLA Suresh Rao. This week: \n• Water complaints have risen by 27% due to pipeline maintenance in Sector 4.\n• Ward 12 sanitation metrics require immediate intervention.\n• PMGSY road upgrade project in Ward 8 is running stable.\n• Urgent dispatch warning: Hospital route utility block is approaching SLA breach.",
          category_forecasts: [
            {
              category: "Water & Sanitation",
              current_score: 61,
              forecast_direction: "DOWN",
              reasoning: "Substandard utility capacity under monsoon overload risk.",
            },
            {
              category: "Roads & Sidewalks",
              current_score: 82,
              forecast_direction: "UP",
              reasoning: "Recent PMGSY pothole repairs completed in Ward 5.",
            },
            {
              category: "Electricity & Power",
              current_score: 90,
              forecast_direction: "STABLE",
              reasoning: "Smart grid distribution transformers cleared standard checks.",
            },
          ],
          risk_alerts: [
            {
              issue_id: "ISSUE-001",
              title: "Broken Main Pipeline Shivaji Nagar W12",
              category: "Water Supply & Sanitation",
              risk_level: "CRITICAL",
              sla_remaining: "2.5 Hours",
              impact_weight: "4,320 Citizens",
            },
            {
              issue_id: "ISSUE-002",
              title: "Utility Dig Block near Clinic Road Sector 4",
              category: "Roads & Sidewalks",
              risk_level: "HIGH",
              sla_remaining: "5.0 Hours",
              impact_weight: "350 Citizens",
            },
          ],
        });
        setLoadingBriefing(false);
      });

    // 2. Fetch pending issues
    fetch(`${API_BASE_URL}/governance/issues/pending`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          const mapped: Issue[] = data.map((item) => ({
            id: item.id,
            title: item.title,
            description: item.description,
            category:
              item.category === "sanitation"
                ? "Water Supply & Sanitation"
                : item.category === "roads"
                ? "Roads & Sidewalks"
                : item.category,
            status:
              item.status === "INTAKE"
                ? "Submitted"
                : item.status === "TRIAGE" || item.status === "TRIAGED"
                ? "Validated"
                : item.status === "ASSIGNED"
                ? "Assigned"
                : item.status === "REJECTED"
                ? "Rejected"
                : item.status,
            priority:
              item.priority === "HIGH"
                ? "High"
                : item.priority === "MEDIUM"
                ? "Medium"
                : "Low",
            citizenName: "Jan Doe",
            createdAt: item.created_at || new Date().toISOString(),
            updatedAt: item.created_at || new Date().toISOString(),
            constituency: "Central Bengaluru",
            location: { lat: item.latitude, lng: item.longitude },
            upvotes: 1,
            updates: [],
            aiDraftResponse:
              "AI analysis completed. Standard resolution timeline initiated.",
          }));
          setIssues((prev) => {
            const mockOnly = prev.filter(
              (p) => !p.id.includes("-") && !data.some((d) => d.id === p.id)
            );
            return [...mapped, ...mockOnly];
          });
        }
        setLoading(false);
      })
      .catch((err) => {
        console.log("Backend not running, using mock data:", err);
        setLoading(false);
      });
  }, []);

  const handleUpdateStatus = (id: string, newStatus: Issue["status"]) => {
    setIssues((prevIssues) =>
      prevIssues.map((issue) => {
        if (issue.id === id) {
          const timestamp = new Date().toISOString();
          const newUpdate: IssueUpdate = {
            timestamp,
            status: newStatus,
            note: `Status updated to ${newStatus.replace("_", " ")} by Officer सुरेश.`,
            author: "Officer Suresh Rao (Admin)",
          };
          return {
            ...issue,
            status: newStatus,
            updatedAt: timestamp,
            updates: [newUpdate, ...issue.updates],
          };
        }
        return issue;
      })
    );
  };

  const filteredIssues = issues.filter((issue) => {
    const matchesSearch =
      issue.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.id.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === "All" || issue.status === statusFilter;

    let matchesTab = true;
    if (activeTab === "pending_ai") {
      matchesTab = issue.status === "Submitted" || issue.status === "Validated";
    } else if (activeTab === "in_progress") {
      matchesTab = issue.status === "Assigned" || issue.status === "In_Progress";
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

      {/* NEW: Proactive Morning Briefing & Alerts Header section */}
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
              {briefing.morning_brief}
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
              {briefing.risk_alerts.map((alert: any, idx: number) => (
                <div key={idx} className="border border-red-500/10 p-3 rounded-xl bg-card text-xs flex justify-between items-center gap-3 hover:border-red-500/30 transition shadow-sm">
                  <div className="truncate">
                    <p className="font-bold truncate text-slate-850 dark:text-slate-200">{alert.title}</p>
                    <p className="text-[10px] text-muted-foreground mt-1 font-semibold">{alert.impact_weight} affected</p>
                  </div>
                  <div className="flex-shrink-0">
                    <Badge variant="destructive" className="text-[9px] font-mono font-bold px-2 py-0.5">{alert.sla_remaining}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      ) : null}

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
              <span className="text-5xl font-extrabold tracking-tight">78</span>
              <span className="text-indigo-300/60 text-sm font-semibold">/ 100</span>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-semibold mt-4">
            <TrendingUp className="h-3.5 w-3.5" />
            <span>+2.4% positive resolution index</span>
          </div>
        </Card>

        {/* Category Health Scores */}
        <div className="lg:col-span-3 grid grid-cols-2 sm:grid-cols-5 gap-4">
          <Card className="p-4 bg-card text-card-foreground border hover:border-slate-300 dark:hover:border-slate-800 transition flex flex-col justify-between shadow-sm">
            <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Roads</span>
            <div className="text-3xl font-extrabold mt-3 tracking-tight">82</div>
            <span className="text-[10px] text-emerald-500 font-bold flex items-center gap-0.5 mt-2">
              <TrendingUp className="h-3 w-3" /> +1.2%
            </span>
          </Card>
          <Card className="p-4 bg-card border-red-500/20 text-card-foreground flex flex-col justify-between shadow-sm">
            <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Water/Sanit</span>
            <div className="text-3xl font-extrabold text-red-500 mt-3 tracking-tight">61</div>
            <span className="text-[10px] text-red-550 dark:text-red-400 font-bold flex items-center gap-0.5 mt-2">
              <TrendingDown className="h-3 w-3 animate-bounce" /> -3.5%
            </span>
          </Card>
          <Card className="p-4 bg-card text-card-foreground border hover:border-slate-300 dark:hover:border-slate-800 transition flex flex-col justify-between shadow-sm">
            <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Electricity</span>
            <div className="text-3xl font-extrabold mt-3 tracking-tight">90</div>
            <span className="text-[10px] text-slate-400 font-bold mt-2.5">Stable</span>
          </Card>
          <Card className="p-4 bg-card text-card-foreground border hover:border-slate-300 dark:hover:border-slate-800 transition flex flex-col justify-between shadow-sm">
            <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Healthcare</span>
            <div className="text-3xl font-extrabold mt-3 tracking-tight">74</div>
            <span className="text-[10px] text-emerald-500 font-bold flex items-center gap-0.5 mt-2">
              <TrendingUp className="h-3 w-3" /> +0.5%
            </span>
          </Card>
          <Card className="p-4 bg-card text-card-foreground border hover:border-slate-300 dark:hover:border-slate-800 transition flex flex-col justify-between shadow-sm">
            <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Education</span>
            <div className="text-3xl font-extrabold mt-3 tracking-tight">69</div>
            <span className="text-[10px] text-slate-400 font-bold mt-2.5">Stable</span>
          </Card>
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
              {issues.filter((i) => i.status === "Submitted" || i.status === "Validated").length}
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
              {issues.filter((i) => i.status === "Assigned" || i.status === "In_Progress").length}
            </div>
          </div>
        </Card>
        <Card className="p-5 flex items-center space-x-4 bg-card border shadow-sm hover:shadow transition">
          <div className="p-3 bg-emerald-500/10 text-emerald-500 rounded-xl border border-emerald-500/20">
            <CheckCircle2 className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Resolved Today</div>
            <div className="text-2xl font-extrabold mt-0.5 tracking-tight">{issues.filter((i) => i.status === "Completed").length}</div>
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
            <option value="Submitted">Submitted</option>
            <option value="Validated">Validated</option>
            <option value="Assigned">Assigned</option>
            <option value="In_Progress">In Progress</option>
            <option value="Completed">Completed</option>
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
                <th className="p-4">Constituency</th>
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
                    <td className="p-4 font-mono font-bold text-slate-450">{issue.id}</td>
                    <td className="p-4 max-w-[280px]">
                      <div className="font-bold text-sm text-slate-850 dark:text-slate-200 line-clamp-1 leading-snug">{issue.title}</div>
                      <div className="text-slate-400 mt-1 font-medium">{issue.category}</div>
                    </td>
                    <td className="p-4 font-bold text-slate-700 dark:text-slate-300">{issue.constituency}</td>
                    <td className="p-4">
                      <Badge
                        variant={
                          issue.priority === "Critical"
                            ? "destructive"
                            : issue.priority === "High"
                            ? "warning"
                            : "default"
                        }
                      >
                        {issue.priority}
                      </Badge>
                    </td>
                    <td className="p-4">
                      <Badge variant={issue.status === "Completed" ? "success" : "info"}>
                        {issue.status.replace("_", " ")}
                      </Badge>
                    </td>
                    <td className="p-4 text-muted-foreground font-medium">
                      {new Date(issue.updatedAt).toLocaleString("en-IN", {
                        dateStyle: "short",
                        timeStyle: "short",
                      })}
                    </td>
                    <td className="p-4 text-right space-x-1.5 whitespace-nowrap">
                      {issue.status === "Submitted" && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-8 text-[11px] font-bold"
                          onClick={() => handleUpdateStatus(issue.id, "Validated")}
                        >
                          Validate AI
                        </Button>
                      )}
                      {issue.status === "Validated" && (
                        <Button
                          size="sm"
                          variant="secondary"
                          className="h-8 text-[11px] font-bold"
                          onClick={() => handleUpdateStatus(issue.id, "Assigned")}
                        >
                          Dispatch Crew
                        </Button>
                      )}
                      {issue.status === "Assigned" && (
                        <Button
                          size="sm"
                          variant="default"
                          className="h-8 text-[11px] font-bold bg-indigo-650 hover:bg-indigo-700 text-white"
                          onClick={() => handleUpdateStatus(issue.id, "In_Progress")}
                        >
                          Start Work
                        </Button>
                      )}
                      {issue.status === "In_Progress" && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-8 text-[11px] font-bold border-emerald-500 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950/20"
                          onClick={() => handleUpdateStatus(issue.id, "Completed")}
                        >
                          Resolve SLA
                        </Button>
                      )}
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
                  <td colSpan={7} className="p-0">
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
          <div className="h-4.5 w-2/3 bg-slate-200 dark:bg-slate-800 rounded" />
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
          <div className="h-4 w-28 bg-slate-200 dark:bg-slate-800 rounded" />
          <div className="h-8.5 w-24 bg-slate-200 dark:bg-slate-800 rounded sm:self-center" />
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
        <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">No work items found</h3>
        <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-normal">
          No municipal issues match the selected filters or search keyword. Try broadening your query or selecting another status tab.
        </p>
      </div>
    </div>
  );
}
