"use client";

import React, { useState, useEffect } from "react";
import { fetchWithAuth } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { ThumbsUp, MapPin, Plus, Search, Calendar, ChevronRight, Users, Compass, AlertCircle } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function CitizenDashboard() {
  const { user } = useAuth();
  const [issues, setIssues] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [votedIssues, setVotedIssues] = useState<Record<string, boolean>>({});

  // Form states
  const [newTitle, setNewTitle] = useState("");
  const [newCategory, setNewCategory] = useState("Water Supply & Sanitation");
  const [newDescription, setNewDescription] = useState("");
  const [newPriority, setNewPriority] = useState<"Low" | "Medium" | "High" | "Critical">("Medium");
  const [newConstituency, setNewConstituency] = useState("Central Bengaluru");

  useEffect(() => {
    // Citizens do not have permission for /pending. Bypass if citizen.
    if (user?.role === "Citizen") {
      setLoading(false);
      return;
    }
    fetchWithAuth(`/governance/issues/pending`)
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          const mapped: any[] = data.map((item) => ({
            id: item.id,
            title: item.title,
            description: item.description,
            category: item.category,
            status: item.status,
            priority: item.priority,
            citizenName: "Jan Doe",
            createdAt: item.created_at || new Date().toISOString(),
            updatedAt: item.created_at || new Date().toISOString(),
            constituency: "Central Bengaluru",
            location: { lat: item.latitude, lng: item.longitude },
            upvotes: 1,
            updates: [],
            aiDraftResponse: "AI analysis completed. Standard resolution timeline initiated.",
          }));
          setIssues(mapped);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.log("Backend not running, using mock data:", err);
        setLoading(false);
      });
  }, [user]);

  const handleUpvote = (id: string) => {
    if (votedIssues[id]) return; // prevent multiple upvotes in session

    setIssues(prevIssues =>
      prevIssues.map(issue => {
        if (issue.id === id) {
          return { ...issue, upvotes: issue.upvotes + 1 };
        }
        return issue;
      })
    );
    setVotedIssues(prev => ({ ...prev, [id]: true }));
  };

  const handleCreateIssue = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || newTitle.length < 3) {
      alert("Title must be at least 3 characters");
      return;
    }
    if (!newDescription || newDescription.length < 10) {
      alert("Description must be at least 10 characters");
      return;
    }

    const payload = {
      citizen_id: user?.id || "00000000-0000-0000-0000-000000000000",
      title: newTitle,
      description: newDescription,
      category: newCategory.toLowerCase().replace(" & ", "_").replace(" ", "_"),
      latitude: 12.9716,
      longitude: 77.5946,
      formatted_address: newConstituency,
    };

    fetchWithAuth(`/governance/issues`, {
      method: "POST",
      body: JSON.stringify(payload),
    })
      .then(() => {
        window.location.reload();
      })
      .catch((err) => {
        console.log("Post failed:", err);
        setIsModalOpen(false);

        // Reset forms
        setNewTitle("");
        setNewDescription("");
        setNewPriority("Medium");
      });
  };

  const filteredIssues = issues.filter(issue =>
    issue.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    issue.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto py-2">
      {/* Hero Welcome banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-5 border-b pb-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
            Citizen Engagement Hub
          </h1>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Collaborate with municipal officers to keep our constituency working efficiently.
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2 font-semibold shadow-sm h-10 px-5">
          <Plus className="h-4.5 w-4.5" /> Report Public Issue
        </Button>
      </div>

      {/* Main Grid: Left is Search/Issues list, Right is informational banner */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Issues List Area */}
        <div className="lg:col-span-2 space-y-5">
          <div className="relative shadow-sm rounded-lg overflow-hidden border">
            <Search className="absolute left-3.5 top-3 h-4.5 w-4.5 text-slate-400" />
            <Input
              type="search"
              placeholder="Search active community concerns..."
              className="pl-11 text-xs sm:text-sm h-11 bg-card border-none focus-visible:ring-1 focus-visible:ring-primary/50"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {loading ? (
            <CitizenSkeleton />
          ) : filteredIssues.length === 0 ? (
            <CitizenEmptyState onClearSearch={() => setSearchTerm("")} />
          ) : (
            <div className="space-y-4">
              {filteredIssues.map((issue) => (
                <Card key={issue.id} className="p-5 hover:shadow-md border border-slate-100 dark:border-slate-800/80 transition-all duration-300 relative overflow-hidden bg-card">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                    <div className="space-y-3 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-[10px] font-mono text-slate-400 font-bold bg-slate-100 dark:bg-slate-800/80 p-0.5 px-1.5 rounded">{issue.id}</span>
                        <Badge variant={issue.priority === "Critical" ? "destructive" : issue.priority === "High" ? "warning" : "default"}>
                          {issue.priority}
                        </Badge>
                        <Badge variant={issue.status === "Completed" ? "success" : "info"}>
                          {issue.status.replace("_", " ")}
                        </Badge>
                      </div>

                      <div className="space-y-1">
                        <h3 className="font-bold text-base leading-snug hover:text-primary transition-colors">
                          <Link href={`/issues/${issue.id}`}>{issue.title}</Link>
                        </h3>
                        <p className="text-xs text-slate-500 font-medium flex items-center gap-1">
                          <Compass className="h-3 w-3" /> {issue.category} &bull; {issue.constituency}
                        </p>
                      </div>

                      <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed">
                        {issue.description}
                      </p>

                      <div className="flex items-center space-x-4 text-[11px] text-muted-foreground pt-1 border-t border-slate-50 dark:border-slate-800/40">
                        <span className="flex items-center gap-1.5"><Calendar className="h-3.5 w-3.5" /> {new Date(issue.createdAt).toLocaleDateString("en-IN", { dateStyle: "medium" })}</span>
                        <span className="flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5" /> Geotag Locked</span>
                      </div>
                    </div>

                    {/* Actions Column */}
                    <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center border-t sm:border-t-0 pt-3 sm:pt-0 gap-3 min-w-[120px]">
                      <Button
                        size="sm"
                        variant={votedIssues[issue.id] ? "default" : "outline"}
                        className="h-8.5 w-full flex items-center justify-center gap-1.5 text-[11px] font-semibold"
                        onClick={() => handleUpvote(issue.id)}
                        disabled={votedIssues[issue.id]}
                      >
                        <ThumbsUp className={`h-3.5 w-3.5 ${votedIssues[issue.id] ? "fill-white" : ""}`} />
                        {issue.upvotes} {votedIssues[issue.id] ? "Upvoted" : "Upvote"}
                      </Button>
                      <Link href={`/issues/${issue.id}`} className="w-full">
                        <Button size="sm" variant="ghost" className="h-8.5 w-full flex items-center justify-center gap-1 text-[11px] text-muted-foreground hover:text-foreground font-semibold">
                          Trace Progress <ChevronRight className="h-3.5 w-3.5" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Informational Panel */}
        <div className="space-y-6">
          <Card className="p-6 bg-gradient-to-br from-indigo-500/5 via-transparent to-transparent border border-indigo-500/10 shadow-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 h-24 w-24 bg-indigo-500/5 rounded-full blur-xl -mr-8 -mt-8" />
            <h3 className="font-bold text-sm mb-3 text-indigo-700 dark:text-indigo-400 flex items-center gap-1.5">
              <AlertCircle className="h-4 w-4" /> Citizen Oversight Mandate
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed mb-4 font-medium">
              Under law GDP-002 of the Helix Charter, municipal dispatch logs and status updates are publicly audit-traceable. Upvotes flag critical consensus to the Decision Intelligence service for dispatcher escalation.
            </p>
            <div className="border-t pt-4 text-xs font-mono space-y-2.5">
              <div className="flex justify-between">
                <span className="text-slate-500">Community Upvotes:</span>
                <span className="font-extrabold text-indigo-600 dark:text-indigo-400">
                  {issues.reduce((acc, curr) => acc + curr.upvotes, 0)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Active Concerns:</span>
                <span className="font-extrabold text-slate-800 dark:text-slate-200">{issues.filter(i => i.status !== "Completed").length}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Report Issue Dialog Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-md sm:max-w-lg p-6">
          <DialogHeader className="pb-3 border-b">
            <DialogTitle className="text-lg font-bold">File Municipal Service Report</DialogTitle>
            <DialogDescription className="text-xs leading-normal">
              Provide comprehensive details and geolocation coordinates. Reports are auto-validated by our AI triage layer before dispatcher queue routing.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleCreateIssue} className="space-y-4 pt-3">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Issue Title</label>
              <Input
                required
                placeholder="e.g. Broken water mains, potholes, garbage overflow"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="text-xs sm:text-sm h-9.5 bg-slate-50/50 dark:bg-slate-900/30"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full h-9.5 rounded-md border border-input bg-slate-50/50 dark:bg-slate-900/30 px-3 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option value="Water Supply & Sanitation">Water Supply & Sanitation</option>
                  <option value="Stormwater Drainage">Stormwater Drainage</option>
                  <option value="Public Lighting">Public Lighting</option>
                  <option value="Solid Waste Management">Solid Waste Management</option>
                  <option value="Roads & Sidewalks">Roads & Sidewalks</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Constituency</label>
                <select
                  value={newConstituency}
                  onChange={(e) => setNewConstituency(e.target.value)}
                  className="w-full h-9.5 rounded-md border border-input bg-slate-50/50 dark:bg-slate-900/30 px-3 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option value="Central Bengaluru">Central Bengaluru</option>
                  <option value="East Bengaluru">East Bengaluru</option>
                  <option value="South Bengaluru">South Bengaluru</option>
                  <option value="West Bengaluru">West Bengaluru</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Priority Bias</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value as "Low" | "Medium" | "High" | "Critical")}
                  className="w-full h-9.5 rounded-md border border-input bg-slate-50/50 dark:bg-slate-900/30 px-3 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option value="Low">Low (Non-urgent)</option>
                  <option value="Medium">Medium (Standard)</option>
                  <option value="High">High (Impacting block)</option>
                  <option value="Critical">Critical (Immediate danger)</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Coordinate Geotag</label>
                <Input disabled value="12.9716° N, 77.5946° E (Auto)" className="bg-slate-100 dark:bg-slate-900/80 text-slate-500 cursor-not-allowed text-xs h-9.5" />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Description</label>
              <textarea
                required
                className="w-full rounded-md border border-input bg-slate-50/50 dark:bg-slate-900/30 px-3 py-2.5 text-xs shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                rows={3}
                placeholder="Give exact locations, indicators, or visual description of the problem..."
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
              />
            </div>

            <DialogFooter className="pt-4 border-t flex items-center justify-end gap-2">
              <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)} className="h-9.5 text-xs">
                Cancel
              </Button>
              <Button type="submit" className="bg-primary text-primary-foreground h-9.5 text-xs font-semibold px-5">
                Lodge Service Ticket
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Skeleton Component
function CitizenSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <Card key={i} className="p-5 border border-slate-100 dark:border-slate-800/80 rounded-xl space-y-4 animate-pulse">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
            <div className="space-y-3 flex-1">
              <div className="flex items-center gap-2">
                <div className="h-4.5 w-16 bg-slate-200 dark:bg-slate-800 rounded" />
                <div className="h-4.5 w-12 bg-slate-200 dark:bg-slate-800 rounded-full" />
                <div className="h-4.5 w-16 bg-slate-200 dark:bg-slate-800 rounded-full" />
              </div>
              <div className="space-y-2">
                <div className="h-5.5 w-2/3 bg-slate-200 dark:bg-slate-800 rounded" />
                <div className="h-4 w-1/2 bg-slate-200 dark:bg-slate-800 rounded" />
              </div>
              <div className="h-4 w-11/12 bg-slate-200 dark:bg-slate-800 rounded" />
              <div className="flex items-center gap-4 pt-1">
                <div className="h-3.5 w-20 bg-slate-200 dark:bg-slate-800 rounded" />
                <div className="h-3.5 w-16 bg-slate-200 dark:bg-slate-800 rounded" />
              </div>
            </div>
            <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center border-t sm:border-t-0 pt-2 sm:pt-0 gap-2 min-w-[120px]">
              <div className="h-8.5 w-full bg-slate-200 dark:bg-slate-800 rounded" />
              <div className="h-8.5 w-full bg-slate-200 dark:bg-slate-800 rounded" />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}

// Empty State Component
interface EmptyStateProps {
  onClearSearch?: () => void;
}

function CitizenEmptyState({ onClearSearch }: EmptyStateProps) {
  return (
    <div className="text-center py-16 px-6 border border-dashed rounded-2xl border-slate-200 dark:border-slate-800 bg-slate-50/20 dark:bg-slate-950/10 max-w-md mx-auto space-y-4 shadow-sm">
      <div className="mx-auto h-12 w-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-muted-foreground border">
        <Search className="h-5 w-5 text-slate-500" />
      </div>
      <div className="space-y-1">
        <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">No issues found</h3>
        <p className="text-xs text-muted-foreground max-w-xs mx-auto leading-normal">
          No active municipal reports match your search query. Try typing another category, keyword, or clear search.
        </p>
      </div>
      {onClearSearch && (
        <Button size="sm" variant="outline" onClick={onClearSearch} className="h-8 px-4 text-xs font-semibold shadow-sm">
          Clear Search Filter
        </Button>
      )}
    </div>
  );
}
