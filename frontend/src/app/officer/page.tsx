"use client";

import React, { useState } from "react";
import { mockIssues, Issue, IssueUpdate } from "@/lib/mock-data";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { Search, AlertTriangle, CheckCircle2, Clock, Play } from "lucide-react";

export default function OfficerDashboard() {
  const [issues, setIssues] = useState<Issue[]>(mockIssues);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("All");
  const [activeTab, setActiveTab] = useState<"all" | "pending_ai" | "in_progress">("all");

  React.useEffect(() => {
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
      })
      .catch((err) => console.log("Backend not running, using mock data:", err));
  }, []);

  const handleUpdateStatus = (id: string, newStatus: Issue["status"]) => {
    setIssues(prevIssues =>
      prevIssues.map(issue => {
        if (issue.id === id) {
          const timestamp = new Date().toISOString();
          const newUpdate: IssueUpdate = {
            timestamp,
            status: newStatus,
            note: `Status updated to ${newStatus.replace("_", " ")} by Officer सुरेश.`,
            author: "Officer Suresh Rao (Admin)"
          };
          return {
            ...issue,
            status: newStatus,
            updatedAt: timestamp,
            updates: [newUpdate, ...issue.updates]
          };
        }
        return issue;
      })
    );
  };

  // Filter issues based on criteria
  const filteredIssues = issues.filter(issue => {
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
          <h1 className="text-2xl font-bold tracking-tight">Officer Operations Console</h1>
          <p className="text-xs text-muted-foreground">Triage, dispatch, and resolve municipal service tickets.</p>
        </div>
      </div>

      {/* Operational Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4 flex items-center space-x-3">
          <div className="p-2 bg-red-500/10 text-red-500 rounded-lg">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground font-semibold uppercase">Pending Triage</div>
            <div className="text-xl font-bold">{issues.filter(i => i.status === "Submitted" || i.status === "Validated").length}</div>
          </div>
        </Card>
        <Card className="p-4 flex items-center space-x-3">
          <div className="p-2 bg-amber-500/10 text-amber-500 rounded-lg">
            <Clock className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground font-semibold uppercase">Active In-Progress</div>
            <div className="text-xl font-bold">{issues.filter(i => i.status === "Assigned" || i.status === "In_Progress").length}</div>
          </div>
        </Card>
        <Card className="p-4 flex items-center space-x-3">
          <div className="p-2 bg-emerald-500/10 text-emerald-500 rounded-lg">
            <CheckCircle2 className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground font-semibold uppercase">Resolved Today</div>
            <div className="text-xl font-bold">{issues.filter(i => i.status === "Completed").length}</div>
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
              activeTab === "all" ? "bg-white dark:bg-slate-900 shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            All Work Items
          </button>
          <button
            onClick={() => setActiveTab("pending_ai")}
            className={`flex-1 md:flex-none px-4 py-1.5 rounded-md text-xs font-semibold transition ${
              activeTab === "pending_ai" ? "bg-white dark:bg-slate-900 shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Requires Triage
          </button>
          <button
            onClick={() => setActiveTab("in_progress")}
            className={`flex-1 md:flex-none px-4 py-1.5 rounded-md text-xs font-semibold transition ${
              activeTab === "in_progress" ? "bg-white dark:bg-slate-900 shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
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
                <tr key={issue.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/30 transition">
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
                      timeStyle: "short"
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
                        Review
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
      </div>
    </div>
  );
}
