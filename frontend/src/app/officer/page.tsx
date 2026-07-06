"use client";

import React, { useState, useEffect } from "react";
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
  ShieldAlert as AlertOctagon,
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
    fetch("http://localhost:8000/governance/proactive/morning-brief")
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
    fetch("http://localhost:8000/governance/issues/pending")
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Constituency Decision Dashboard</h1>
          <p className="text-xs text-muted-foreground">
            Proactive constituency health indexing, morning briefings, and triage logs.
          </p>
        </div>
      </div>

      {/* NEW: Proactive Morning Briefing & Alerts Header section */}
      {!loadingBriefing && briefing && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
          {/* Proactive Greeting Card */}
          <Card className="lg:col-span-2 p-5 border-2 border-indigo-500/20 bg-indigo-500/[0.01] space-y-4">
            <div className="flex items-center gap-2 border-b pb-2 border-slate-100 dark:border-slate-800">
              <Sun className="h-5 w-5 text-indigo-500" />
              <h2 className="text-sm font-bold tracking-wider uppercase text-indigo-500 flex items-center gap-1.5">
                <Sparkles className="h-4 w-4" /> Proactive Morning Briefing
              </h2>
            </div>
            <div className="font-sans text-xs text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line bg-card p-4 rounded-xl border">
              {briefing.morning_brief}
            </div>
          </Card>

          {/* Risk Alerts Panel */}
          <Card className="p-5 border-red-500/20 bg-red-500/[0.01] space-y-3 flex flex-col justify-between">
            <div className="flex items-center gap-1.5 border-b pb-2 border-slate-100 dark:border-slate-800">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <h3 className="text-sm font-bold text-red-500 uppercase tracking-wider">Critical SLA Risks</h3>
            </div>
            <div className="space-y-2">
              {briefing.risk_alerts.map((alert: any, idx: number) => (
                <div key={idx} className="border p-2.5 rounded-lg bg-card text-xs flex justify-between items-center gap-2 hover:border-red-500/30 transition">
                  <div className="truncate">
                    <p className="font-bold truncate text-slate-800 dark:text-slate-200">{alert.title}</p>
                    <p className="text-[10px] text-muted-foreground mt-0.5">{alert.impact_weight} affected</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <Badge variant="destructive" className="text-[9px] font-mono">{alert.sla_remaining}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Constituency Health score Widget */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <Card className="p-5 bg-gradient-to-br from-indigo-900/50 to-slate-900 border-indigo-500/20 text-white flex flex-col justify-between min-h-[160px] lg:col-span-1">
          <div>
            <div className="flex justify-between items-center text-xs text-indigo-300 font-semibold tracking-wider uppercase">
              <span>Constituency Health</span>
              <Activity className="h-4 w-4 text-indigo-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-4">
              <span className="text-4xl font-extrabold">78</span>
              <span className="text-slate-400 text-sm">/ 100</span>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-emerald-400 text-xs mt-4">
            <TrendingUp className="h-3.5 w-3.5" />
            <span>+2.4% positive resolution index</span>
          </div>
        </Card>

        {/* Category Health Scores */}
        <div className="lg:col-span-3 grid grid-cols-2 sm:grid-cols-5 gap-4">
          <Card className="p-4 bg-card text-card-foreground flex flex-col justify-between">
            <span className="text-[10px] text-muted-foreground font-semibold uppercase">Roads</span>
            <div className="text-2xl font-bold mt-2">82</div>
            <span className="text-[9px] text-emerald-500 font-medium flex items-center gap-0.5 mt-2">
              <TrendingUp className="h-3 w-3" /> +1.2%
            </span>
          </Card>
          <Card className="p-4 bg-card border-red-500/20 text-card-foreground flex flex-col justify-between">
            <span className="text-[10px] text-muted-foreground font-semibold uppercase">Water/Sanit</span>
            <div className="text-2xl font-bold text-red-500 mt-2">61</div>
            <span className="text-[9px] text-red-500 font-medium flex items-center gap-0.5 mt-2">
              <TrendingDown className="h-3 w-3 animate-bounce" /> -3.5%
            </span>
          </Card>
          <Card className="p-4 bg-card text-card-foreground flex flex-col justify-between">
            <span className="text-[10px] text-muted-foreground font-semibold uppercase">Electricity</span>
            <div className="text-2xl font-bold mt-2">90</div>
            <span className="text-[9px] text-slate-400 font-medium mt-2">Stable</span>
          </Card>
          <Card className="p-4 bg-card text-card-foreground flex flex-col justify-between">
            <span className="text-[10px] text-muted-foreground font-semibold uppercase">Healthcare</span>
            <div className="text-2xl font-bold mt-2">74</div>
            <span className="text-[9px] text-emerald-500 font-medium flex items-center gap-0.5 mt-2">
              <TrendingUp className="h-3 w-3" /> +0.5%
            </span>
          </Card>
          <Card className="p-4 bg-card text-card-foreground flex flex-col justify-between">
            <span className="text-[10px] text-muted-foreground font-semibold uppercase">Education</span>
            <div className="text-2xl font-bold mt-2">69</div>
            <span className="text-[9px] text-slate-400 font-medium mt-2">Stable</span>
          </Card>
        </div>
      </div>

      {/* Operational Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4 flex items-center space-x-3 bg-card">
          <div className="p-2 bg-red-500/10 text-red-500 rounded-lg">
            <AlertOctagon className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground font-semibold uppercase">Pending Triage</div>
            <div className="text-xl font-bold">
              {issues.filter((i) => i.status === "Submitted" || i.status === "Validated").length}
            </div>
          </div>
        </Card>
        <Card className="p-4 flex items-center space-x-3 bg-card">
          <div className="p-2 bg-amber-500/10 text-amber-500 rounded-lg">
            <Clock className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground font-semibold uppercase">Active Field Tasks</div>
            <div className="text-xl font-bold">
              {issues.filter((i) => i.status === "Assigned" || i.status === "In_Progress").length}
            </div>
          </div>
        </Card>
        <Card className="p-4 flex items-center space-x-3 bg-card">
          <div className="p-2 bg-emerald-500/10 text-emerald-500 rounded-lg">
            <CheckCircle2 className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground font-semibold uppercase">Resolved Today</div>
            <div className="text-xl font-bold">{issues.filter((i) => i.status === "Completed").length}</div>
          </div>
        </Card>
      </div>

      {/* Filters bar */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-card border p-4 rounded-xl">
        {/* Navigation Tabs */}
        <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg w-full md:w-auto">
          <button
            onClick={() => setActiveTab("all")}
            className={`flex-1 md:flex-none px-4 py-1.5 rounded-md text-xs font-semibold transition ${
              activeTab === "all"
                ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            All Work Items
          </button>
          <button
            onClick={() => setActiveTab("pending_ai")}
            className={`flex-1 md:flex-none px-4 py-1.5 rounded-md text-xs font-semibold transition ${
              activeTab === "pending_ai"
                ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Requires Triage
          </button>
          <button
            onClick={() => setActiveTab("in_progress")}
            className={`flex-1 md:flex-none px-4 py-1.5 rounded-md text-xs font-semibold transition ${
              activeTab === "in_progress"
                ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Active Field Tasks
          </button>
        </div>

        {/* Input filters */}
        <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
          <div className="relative w-full sm:w-60">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search issues..."
              className="pl-8 text-xs h-9 bg-background"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="h-9 rounded-md border border-input bg-background px-3 text-xs focus-visible:outline-none"
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
      <div className="overflow-x-auto rounded-xl border bg-card">
        {loading ? (
          <div className="p-8 text-center text-xs text-muted-foreground animate-pulse">
            Loading constituency records...
          </div>
        ) : (
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b bg-slate-50 dark:bg-slate-900/50 text-slate-500 font-semibold">
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
                    className="hover:bg-slate-50/50 dark:hover:bg-slate-900/30 transition"
                  >
                    <td className="p-4 font-mono font-bold text-slate-400">{issue.id}</td>
                    <td className="p-4 max-w-[280px]">
                      <div className="font-semibold text-sm line-clamp-1">{issue.title}</div>
                      <div className="text-slate-400 mt-0.5">{issue.category}</div>
                    </td>
                    <td className="p-4 font-medium">{issue.constituency}</td>
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
                    <td className="p-4 text-muted-foreground">
                      {new Date(issue.updatedAt).toLocaleString("en-IN", {
                        dateStyle: "short",
                        timeStyle: "short",
                      })}
                    </td>
                    <td className="p-4 text-right space-x-2 whitespace-nowrap">
                      {issue.status === "Submitted" && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-8 text-[11px]"
                          onClick={() => handleUpdateStatus(issue.id, "Validated")}
                        >
                          Validate AI
                        </Button>
                      )}
                      {issue.status === "Validated" && (
                        <Button
                          size="sm"
                          variant="secondary"
                          className="h-8 text-[11px]"
                          onClick={() => handleUpdateStatus(issue.id, "Assigned")}
                        >
                          Dispatch Crew
                        </Button>
                      )}
                      {issue.status === "Assigned" && (
                        <Button
                          size="sm"
                          variant="default"
                          className="h-8 text-[11px] bg-indigo-600 hover:bg-indigo-700"
                          onClick={() => handleUpdateStatus(issue.id, "In_Progress")}
                        >
                          Start Work
                        </Button>
                      )}
                      {issue.status === "In_Progress" && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-8 text-[11px] border-emerald-500 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950/20"
                          onClick={() => handleUpdateStatus(issue.id, "Completed")}
                        >
                          Resolve SLA
                        </Button>
                      )}
                      <Link href={`/issues/${issue.id}`}>
                        <Button size="sm" variant="ghost" className="h-8 text-[11px]">
                          Open Brief <ArrowRight className="h-3 w-3 ml-0.5" />
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-muted-foreground border-dashed">
                    No municipal issues matched your search parameters.
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
