"use client";

import React, { useState } from "react";
import { API_BASE_URL } from "@/config";
import { mockIssues, Issue } from "@/lib/mock-data";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { ThumbsUp, MapPin, Plus, Search, Calendar, ChevronRight } from "lucide-react";
import Link from "next/link";

export default function CitizenDashboard() {
  const [issues, setIssues] = useState<Issue[]>(mockIssues);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [votedIssues, setVotedIssues] = useState<Record<string, boolean>>({});

  // Form states
  const [newTitle, setNewTitle] = useState("");
  const [newCategory, setNewCategory] = useState("Water Supply & Sanitation");
  const [newDescription, setNewDescription] = useState("");
  const [newPriority, setNewPriority] = useState<Issue["priority"]>("Medium");
  const [newConstituency, setNewConstituency] = useState("Central Bengaluru");

  React.useEffect(() => {
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
            status: item.status,
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
            updates: [
              {
                timestamp: item.created_at || new Date().toISOString(),
                status: item.status,
                note: `Issue ingested in ${item.status} status.`,
                author: "System Engine",
              },
            ],
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
    if (!newTitle || !newDescription) return;

    const payload = {
      citizen_id: "00000000-0000-0000-0000-000000000000",
      title: newTitle,
      description: newDescription,
      category: newCategory.toLowerCase().replace(" & ", "_").replace(" ", "_"),
      latitude: 12.9716,
      longitude: 77.5946,
      formatted_address: newConstituency,
    };

    fetch(`${API_BASE_URL}/governance/issues`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((res) => res.json())
      .then(() => {
        window.location.reload();
      })
      .catch((err) => {
        console.log("Post failed, falling back to mock simulation:", err);
        const newIssue: Issue = {
          id: `ISS-${1000 + issues.length + 1}`,
          title: newTitle,
          description: newDescription,
          category: newCategory,
          status: "Submitted",
          priority: newPriority,
          citizenName: "Jan Doe (You)",
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          constituency: newConstituency,
          location: {
            lat: 12.97 + (Math.random() - 0.5) * 0.05,
            lng: 77.59 + (Math.random() - 0.5) * 0.05,
          },
          upvotes: 1,
          updates: [
            {
              timestamp: new Date().toISOString(),
              status: "Submitted",
              note: "Issue logged by citizen via dashboard portal.",
              author: "Jan Doe (Citizen)",
            },
          ],
          aiDraftResponse:
            "AI analysis initiated. Checking regional logs and historical reports.",
        };

        setIssues([newIssue, ...issues]);
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
    <div className="space-y-6">
      {/* Hero Welcome banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Citizen Engagement Hub</h1>
          <p className="text-xs text-muted-foreground">Collaborate with municipal officers to keep our constituency working efficiently.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-2 font-semibold">
          <Plus className="h-4 w-4" /> Report Public Issue
        </Button>
      </div>

      {/* Main Grid: Left is Search/Issues list, Right is informational banner */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Issues List Area */}
        <div className="lg:col-span-2 space-y-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search active community concerns..."
              className="pl-8 text-xs h-9 bg-card"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="space-y-4">
            {filteredIssues.map((issue) => (
              <Card key={issue.id} className="p-4 hover:shadow-md transition duration-200">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono text-slate-400 font-bold">{issue.id}</span>
                      <Badge variant={issue.priority === "Critical" ? "destructive" : issue.priority === "High" ? "warning" : "default"}>
                        {issue.priority}
                      </Badge>
                      <Badge variant={issue.status === "Completed" ? "success" : "info"}>
                        {issue.status.replace("_", " ")}
                      </Badge>
                    </div>

                    <div className="space-y-0.5">
                      <h3 className="font-semibold text-sm leading-snug hover:text-primary transition">
                        <Link href={`/issues/${issue.id}`}>{issue.title}</Link>
                      </h3>
                      <p className="text-xs text-slate-500">{issue.category} &bull; {issue.constituency}</p>
                    </div>

                    <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2">
                      {issue.description}
                    </p>

                    <div className="flex items-center space-x-4 text-[10px] text-muted-foreground pt-1">
                      <span className="flex items-center gap-1"><Calendar className="h-3 w-3" /> {new Date(issue.createdAt).toLocaleDateString("en-IN")}</span>
                      <span className="flex items-center gap-1"><MapPin className="h-3 w-3" /> Pin Located</span>
                    </div>
                  </div>

                  {/* Actions Column */}
                  <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center border-t sm:border-t-0 pt-2 sm:pt-0 gap-2 min-w-[100px]">
                    <Button
                      size="sm"
                      variant={votedIssues[issue.id] ? "default" : "outline"}
                      className="h-8 w-full flex items-center justify-center gap-1.5 text-[11px]"
                      onClick={() => handleUpvote(issue.id)}
                      disabled={votedIssues[issue.id]}
                    >
                      <ThumbsUp className={`h-3.5 w-3.5 ${votedIssues[issue.id] ? "fill-white" : ""}`} />
                      {issue.upvotes} {votedIssues[issue.id] ? "Upvoted" : "Upvote"}
                    </Button>
                    <Link href={`/issues/${issue.id}`} className="w-full">
                      <Button size="sm" variant="ghost" className="h-8 w-full flex items-center justify-center gap-1 text-[11px] text-muted-foreground hover:text-foreground">
                        Trace progress <ChevronRight className="h-3.5 w-3.5" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Informational Panel */}
        <div className="space-y-6">
          <Card className="p-6 bg-gradient-to-br from-indigo-500/10 to-transparent">
            <h3 className="font-bold text-sm mb-2 text-indigo-700 dark:text-indigo-400">Citizen Oversight Mandate</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed mb-4">
              Under law GDP-002 of the Helix Charter, municipal dispatch logs and status updates are publicly audit-traceable. Upvotes flag critical consensus to the Decision Intelligence service for dispatcher escalation.
            </p>
            <div className="border-t pt-4 text-xs font-mono space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Community Upvotes:</span>
                <span className="font-bold text-indigo-600 dark:text-indigo-400">
                  {issues.reduce((acc, curr) => acc + curr.upvotes, 0)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Active issues in Ward:</span>
                <span className="font-bold">{issues.filter(i => i.status !== "Completed").length}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Report Issue Dialog Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>File Municipal Service Report</DialogTitle>
            <DialogDescription className="text-xs">
              Provide comprehensive details and geolocation coordinates. Reports are auto-validated by our AI triage layer before dispatcher queue routing.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleCreateIssue} className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs font-semibold">Issue Title</label>
              <Input
                required
                placeholder="e.g. Broken water mains, potholes, garbage overflow"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-semibold">Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs focus-visible:outline-none"
                >
                  <option value="Water Supply & Sanitation">Water Supply & Sanitation</option>
                  <option value="Stormwater Drainage">Stormwater Drainage</option>
                  <option value="Public Lighting">Public Lighting</option>
                  <option value="Solid Waste Management">Solid Waste Management</option>
                  <option value="Roads & Sidewalks">Roads & Sidewalks</option>
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold">Constituency</label>
                <select
                  value={newConstituency}
                  onChange={(e) => setNewConstituency(e.target.value)}
                  className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs focus-visible:outline-none"
                >
                  <option value="Central Bengaluru">Central Bengaluru</option>
                  <option value="East Bengaluru">East Bengaluru</option>
                  <option value="South Bengaluru">South Bengaluru</option>
                  <option value="West Bengaluru">West Bengaluru</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-semibold">Priority Bias</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value as Issue["priority"])}
                  className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs focus-visible:outline-none"
                >
                  <option value="Low">Low (Non-urgent)</option>
                  <option value="Medium">Medium (Standard)</option>
                  <option value="High">High (Impacting block)</option>
                  <option value="Critical">Critical (Immediate danger)</option>
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold">Coordinate Geotag</label>
                <Input disabled value="12.9716° N, 77.5946° E (Auto)" className="bg-slate-50 text-slate-500 cursor-not-allowed" />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold">Description</label>
              <textarea
                required
                className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-xs shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                rows={3}
                placeholder="Give exact locations, indicators, or visual description of the problem..."
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
              />
            </div>

            <DialogFooter className="pt-4 border-t">
              <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-primary text-primary-foreground">
                Lodge Service Ticket
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
