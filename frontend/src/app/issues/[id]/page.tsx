"use client";

import React, { useState, useEffect } from "react";
import { mockIssues, Issue, IssueUpdate } from "@/lib/mock-data";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { ArrowLeft, Clock, User, ShieldAlert, Award, FileText, Send, Calendar } from "lucide-react";

export default function IssueDetailsPage({ params }: { params: { id: string } }) {
  const [issue, setIssue] = useState<Issue | null>(null);
  const [draftResponse, setDraftResponse] = useState("");
  const [dispatcherNote, setDispatcherNote] = useState("");
  const [isSuccessMsg, setIsSuccessMsg] = useState(false);
  const [recommendationId, setRecommendationId] = useState<string | null>(null);

  useEffect(() => {
    if (params.id.includes("-")) {
      fetch("http://localhost:8000/governance/issues/pending")
        .then((res) => res.json())
        .then((data) => {
          const found = data.find((i: any) => i.id === params.id);
          if (found) {
            const mapped: Issue = {
              id: found.id,
              title: found.title,
              description: found.description,
              category:
                found.category === "sanitation"
                  ? "Water Supply & Sanitation"
                  : found.category === "roads"
                  ? "Roads & Sidewalks"
                  : found.category,
              status:
                found.status === "INTAKE"
                  ? "Submitted"
                  : found.status === "TRIAGE"
                  ? "Validated"
                  : found.status === "ASSIGNED"
                  ? "Assigned"
                  : found.status === "REJECTED"
                  ? "Rejected"
                  : found.status,
              priority:
                found.priority === "HIGH"
                  ? "High"
                  : found.priority === "MEDIUM"
                  ? "Medium"
                  : "Low",
              citizenName: "Jan Doe",
              createdAt: found.created_at || new Date().toISOString(),
              updatedAt: found.created_at || new Date().toISOString(),
              constituency: "Central Bengaluru",
              location: { lat: found.latitude, lng: found.longitude },
              upvotes: 1,
              updates: [
                {
                  timestamp: found.created_at || new Date().toISOString(),
                  status: found.status,
                  note: `Issue logged in system. Status: ${found.status}`,
                  author: "System Engine",
                },
              ],
              aiDraftResponse: "AI recommendation pending...",
            };
            setIssue(mapped);

            // Fetch Recommendation
            fetch(`http://localhost:8000/governance/recommendations/${found.id}`)
              .then((r) => r.json())
              .then((rec) => {
                setRecommendationId(rec.id);
                setDraftResponse(rec.rationale);
                setIssue((prev) =>
                  prev ? { ...prev, aiDraftResponse: rec.rationale } : null
                );
              })
              .catch((err) => console.log("Failed to fetch recommendation:", err));
          }
        })
        .catch((err) => console.log("Failed to load issue details:", err));
    } else {
      const found = mockIssues.find((i) => i.id === params.id);
      if (found) {
        setIssue(found);
        setDraftResponse(found.aiDraftResponse || "");
      }
    }
  }, [params.id]);

  if (!issue) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center text-center p-6 space-y-4">
        <h2 className="text-xl font-bold text-slate-700 dark:text-slate-300">Issue Record Not Found</h2>
        <p className="text-xs text-muted-foreground max-w-sm">
          The requested ticket ID: {params.id} does not match any index in the Helix database.
        </p>
        <Link href="/">
          <Button variant="outline" className="text-xs">
            Return to Operations Dashboard
          </Button>
        </Link>
      </div>
    );
  }

  const handleStatusChange = (newStatus: Issue["status"], note: string) => {
    if (!issue) return;

    const timestamp = new Date().toISOString();
    const newUpdate: IssueUpdate = {
      timestamp,
      status: newStatus,
      note,
      author: "Officer Suresh Rao (Operations Console)"
    };

    setIssue((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        status: newStatus,
        updatedAt: timestamp,
        updates: [newUpdate, ...prev.updates]
      };
    });
  };

  const handleApproveDraft = () => {
    if (!issue) return;

    if (issue.id.includes("-") && recommendationId) {
      fetch(`http://localhost:8000/governance/recommendations/${recommendationId}/accept`, {
        method: "POST",
      })
        .then((res) => res.json())
        .then((data) => {
          setIsSuccessMsg(true);
          setTimeout(() => setIsSuccessMsg(false), 3000);

          const timestamp = new Date().toISOString();
          const newUpdate: IssueUpdate = {
            timestamp,
            status: "Assigned",
            note: `AI recommendation approved. Decision ID: ${data.decision_id}. Dispatch SMS sent to citizen.`,
            author: "Officer Suresh Rao (Operations Console)",
          };
          setIssue((prev) =>
            prev
              ? {
                  ...prev,
                  status: "Assigned",
                  updatedAt: timestamp,
                  updates: [newUpdate, ...prev.updates],
                }
              : null
          );
        })
        .catch((err) => console.log("Failed to accept recommendation:", err));
    } else {
      setIsSuccessMsg(true);
      setTimeout(() => setIsSuccessMsg(false), 3000);

      // Append to timeline
      const timestamp = new Date().toISOString();
      const newUpdate: IssueUpdate = {
        timestamp,
        status: issue.status,
        note: `AI Draft response approved and dispatched to citizen: "${draftResponse}"`,
        author: "Officer Suresh Rao (Operations Console)"
      };

      setIssue((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          updatedAt: timestamp,
          updates: [newUpdate, ...prev.updates]
        };
      });
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top back navigation */}
      <div className="flex items-center justify-between">
        <Link href="/officer" className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground font-semibold">
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard Queue
        </Link>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-muted-foreground font-mono">Record Lock: Read/Write Access</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Side: Ticket Details and Timeline */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b pb-4 mb-4">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-slate-400">{issue.id}</span>
                <Badge variant={issue.priority === "Critical" ? "destructive" : issue.priority === "High" ? "warning" : "default"}>
                  {issue.priority} Priority
                </Badge>
              </div>
              <Badge variant={issue.status === "Completed" ? "success" : "info"} className="text-xs px-3 py-1">
                {issue.status.replace("_", " ")}
              </Badge>
            </div>

            <div className="space-y-4">
              <div className="space-y-1">
                <h1 className="text-2xl font-bold tracking-tight">{issue.title}</h1>
                <p className="text-xs text-slate-400 font-semibold">{issue.category} &bull; {issue.constituency}</p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-lg text-xs leading-relaxed text-slate-700 dark:text-slate-300">
                <p>{issue.description}</p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2 text-xs">
                <div className="border p-3 rounded-lg bg-card">
                  <div className="text-[10px] text-muted-foreground font-medium flex items-center gap-1"><User className="h-3.5 w-3.5" /> Reporter</div>
                  <div className="font-bold mt-1 truncate">{issue.citizenName}</div>
                </div>
                <div className="border p-3 rounded-lg bg-card">
                  <div className="text-[10px] text-muted-foreground font-medium flex items-center gap-1"><Calendar className="h-3.5 w-3.5" /> Date Logged</div>
                  <div className="font-bold mt-1 truncate">
                    {new Date(issue.createdAt).toLocaleDateString("en-IN", { dateStyle: "medium" })}
                  </div>
                </div>
                <div className="border p-3 rounded-lg bg-card">
                  <div className="text-[10px] text-muted-foreground font-medium flex items-center gap-1"><Award className="h-3.5 w-3.5" /> Total Votes</div>
                  <div className="font-bold mt-1">{issue.upvotes} Upvotes</div>
                </div>
                <div className="border p-3 rounded-lg bg-card">
                  <div className="text-[10px] text-muted-foreground font-medium flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> Ward Code</div>
                  <div className="font-bold mt-1">BLR-WARD-12</div>
                </div>
              </div>
            </div>
          </Card>

          {/* Audit Timeline */}
          <Card className="p-6">
            <h3 className="font-bold text-sm mb-4 tracking-tight flex items-center gap-2">
              <Clock className="h-4 w-4 text-primary" /> Lifecycle Audit Ledger
            </h3>
            <div className="relative border-l pl-4 ml-2 space-y-6">
              {issue.updates.map((update, index) => (
                <div key={index} className="relative">
                  {/* Blinking dot */}
                  <span className={`absolute -left-[21px] top-1.5 h-3.5 w-3.5 rounded-full border bg-background flex items-center justify-center ${
                    index === 0 ? "border-primary text-primary" : "border-slate-300 text-slate-300"
                  }`}>
                    <span className={`h-1.5 w-1.5 rounded-full bg-current ${index === 0 ? "animate-pulse bg-primary" : "bg-slate-400"}`} />
                  </span>

                  <div className="space-y-1 text-xs">
                    <div className="flex flex-wrap items-center justify-between gap-1">
                      <span className="font-bold text-slate-800 dark:text-slate-200">
                        {update.status.replace("_", " ")}
                      </span>
                      <span className="text-[9px] text-muted-foreground font-mono">
                        {new Date(update.timestamp).toLocaleString("en-IN")}
                      </span>
                    </div>
                    <div className="text-slate-600 dark:text-slate-400 leading-snug">
                      {update.note}
                    </div>
                    <div className="text-[9px] text-slate-400 font-semibold">
                      Action Author: {update.author}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right Side: Interactive Dispatcher Controls */}
        <div className="space-y-6">
          <Card className="p-4 border-2 border-primary/20 bg-gradient-to-b from-primary/5 to-transparent">
            <h3 className="font-bold text-sm mb-3 tracking-tight flex items-center gap-1.5">
              <ShieldAlert className="h-4.5 w-4.5 text-primary" /> Triage Control Deck
            </h3>
            <div className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <span className="font-semibold text-muted-foreground">Workflow Stage Transition</span>
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    size="sm"
                    variant={issue.status === "Validated" ? "default" : "outline"}
                    className="h-8 text-[11px]"
                    onClick={() => handleStatusChange("Validated", "Validated against regional utility infrastructure mapping.")}
                  >
                    Validate AI
                  </Button>
                  <Button
                    size="sm"
                    variant={issue.status === "Assigned" ? "default" : "outline"}
                    className="h-8 text-[11px]"
                    onClick={() => handleStatusChange("Assigned", "Assigned dispatch order to Sector Maintenance Unit B.")}
                  >
                    Assign Crew
                  </Button>
                  <Button
                    size="sm"
                    variant={issue.status === "In_Progress" ? "default" : "outline"}
                    className="h-8 text-[11px]"
                    onClick={() => handleStatusChange("In_Progress", "Field work started. Excavators and technicians on-site.")}
                  >
                    Start Work
                  </Button>
                  <Button
                    size="sm"
                    variant={issue.status === "Completed" ? "default" : "outline"}
                    className="h-8 text-[11px] border-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 text-emerald-600"
                    onClick={() => handleStatusChange("Completed", "Service request resolved. Infrastructure checked and restored.")}
                  >
                    Complete SLA
                  </Button>
                </div>
              </div>

              <div className="border-t pt-4 space-y-2">
                <span className="font-semibold text-muted-foreground flex items-center gap-1">
                  <FileText className="h-3.5 w-3.5" /> AI Recommendation Response Draft
                </span>
                <textarea
                  className="w-full rounded-md border bg-background p-2.5 text-xs text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono leading-normal"
                  rows={6}
                  value={draftResponse}
                  onChange={(e) => setDraftResponse(e.target.value)}
                />
                <Button
                  onClick={handleApproveDraft}
                  className="w-full text-xs h-9 bg-primary text-primary-foreground font-semibold flex items-center justify-center gap-1.5"
                >
                  <Send className="h-3.5 w-3.5" /> Approve & Dispatch Response
                </Button>
                {isSuccessMsg && (
                  <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold text-center animate-fade-in pt-1">
                    ✓ Notification dispatched to citizen interface.
                  </div>
                )}
              </div>
            </div>
          </Card>

          <Card className="p-4 space-y-3">
            <h4 className="font-bold text-xs">Field Crew Assignments</h4>
            <div className="text-xs space-y-2 border p-3 rounded-lg bg-slate-50 dark:bg-slate-900/50">
              <div className="flex justify-between font-semibold">
                <span>Unit:</span>
                <span>{issue.assignedUnit || "Unassigned"}</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>SLA Latency:</span>
                <span>4.0 Hours</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>Contact ID:</span>
                <span className="font-mono">CREW-1049</span>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-semibold text-slate-500 uppercase">Dispatcher Note</label>
              <Input
                placeholder="Append notes to dispatch order..."
                className="text-xs h-8"
                value={dispatcherNote}
                onChange={(e) => setDispatcherNote(e.target.value)}
              />
              <Button
                size="sm"
                variant="outline"
                className="w-full text-[11px]"
                onClick={() => {
                  if (!dispatcherNote) return;
                  handleStatusChange(issue.status, `Dispatcher Note: "${dispatcherNote}"`);
                  setDispatcherNote("");
                }}
              >
                Log Dispatcher Entry
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
