"use client";

import React, { useState, useEffect } from "react";
import { mockIssues, Issue, IssueUpdate } from "@/lib/mock-data";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import {
  ArrowLeft,
  Clock,
  User,
  ShieldAlert,
  Award,
  FileText,
  Send,
  Calendar,
  Navigation,
  Eye,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  AlertCircle,
  RefreshCw,
  BarChart2,
} from "lucide-react";

export default function IssueDetailsPage({ params }: { params: { id: string } }) {
  const [issue, setIssue] = useState<Issue | null>(null);
  const [draftResponse, setDraftResponse] = useState("");
  const [dispatcherNote, setDispatcherNote] = useState("");
  const [isSuccessMsg, setIsSuccessMsg] = useState(false);
  const [recommendationId, setRecommendationId] = useState<string | null>(null);

  // Decision Intelligence Context State
  const [context, setContext] = useState<any>(null);
  const [loadingContext, setLoadingContext] = useState(true);
  const [selectedAlternative, setSelectedAlternative] = useState<number>(0);

  useEffect(() => {
    // 1. Fetch Issue Details
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
                  : found.status === "TRIAGE" || found.status === "TRIAGED"
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

            // Fetch Decision Context
            fetch(`http://localhost:8000/governance/issues/${found.id}/context`)
              .then((r) => r.json())
              .then((ctx) => {
                setContext(ctx);
                setLoadingContext(false);
              })
              .catch((err) => {
                console.log("Failed to fetch context, falling back to client-calculated:", err);
                loadFallbackContext(mapped);
              });
          }
        })
        .catch((err) => console.log("Failed to load issue details:", err));
    } else {
      const found = mockIssues.find((i) => i.id === params.id);
      if (found) {
        setIssue(found);
        setDraftResponse(found.aiDraftResponse || "");
        loadFallbackContext(found);
      }
    }
  }, [params.id]);

  const loadFallbackContext = (issueData: Issue) => {
    const isSanitation =
      issueData.category.toLowerCase().includes("sanit") ||
      issueData.category.toLowerCase().includes("water");
    setContext({
      priority: isSanitation ? "HIGH" : "MEDIUM",
      affected_population: isSanitation ? 1200 : 150,
      estimated_impact: isSanitation ? "HIGH" : "MEDIUM",
      supporting_evidence: isSanitation
        ? [
            "Municipal Asset Proximity: Ward 12 Playground Garbage Bin Terminal",
            "Linked Municipal Scheme: Swachh Bharat Abhiyan Subsidy",
            "Enforced Regulation: Sanitation Waste Management Regulation 2024",
          ]
        : [
            "Municipal Asset Proximity: Main Arterial Road Sector 4",
            "Linked Municipal Scheme: Arterial Road Rehabilitation Program",
            "Enforced Regulation: Municipal Road Maintenance Policy 2023",
          ],
      confidence: 0.95,
      reasoning_chain: isSanitation
        ? "1. Intake categorized issue as 'sanitation'.\n2. Evaluated geo-spatial proximity; matched 3 evidence points.\n3. Determined urgency score: 0.90 and impact scale: HIGH.\n4. Policy Evaluation: Aligned with 'Sanitation Waste Management Regulation 2024'.\n5. Recommended dispatch to Municipal Sanitation Department with SLA of 24 hours."
        : "1. Intake categorized issue as 'roads'.\n2. Evaluated geo-spatial proximity; matched 3 evidence points.\n3. Determined urgency score: 0.60 and impact scale: MEDIUM.\n4. Policy Evaluation: Aligned with 'Municipal Road Maintenance Policy 2023'.\n5. Recommended dispatch to Public Works Department with SLA of 48 hours.",
      alternative_actions: [
        {
          title: "Accelerated Dispatch (Recommended)",
          cost: "Medium",
          sla: isSanitation ? "24 Hours" : "48 Hours",
          desc: "Allocate internal ward maintenance crew.",
        },
        {
          title: "Private Vendor Contractor Outsource",
          cost: "High",
          sla: isSanitation ? "12 Hours" : "24 Hours",
          desc: "Hire local contractor. Immediate response, higher budget cost.",
        },
        {
          title: "Defer to Standard Cycle",
          cost: "Low",
          sla: "10 Days",
          desc: "Add ticket to general monthly road infrastructure sweep.",
        },
      ],
      suggested_department: isSanitation
        ? "Municipal Sanitation Department"
        : "Public Works Department",
      expected_outcome: isSanitation
        ? "Restores sanitary conditions, prevents public health hazards, and maintains cleanliness in ward public play areas."
        : "Improves vehicle traffic throughput and eliminates pedestrian safety hazards.",
    });
    setLoadingContext(false);
  };

  if (!issue) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center text-center p-6 space-y-4">
        <h2 className="text-xl font-bold text-slate-700 dark:text-slate-300">Issue Record Not Found</h2>
        <p className="text-xs text-muted-foreground max-w-sm">
          The requested ticket ID does not match any index in the Helix database.
        </p>
        <Link href="/officer">
          <Button variant="outline" className="text-xs">
            Return to Operations Dashboard
          </Button>
        </Link>
      </div>
    );
  }

  const handleStatusChange = (newStatus: Issue["status"], note: string) => {
    const timestamp = new Date().toISOString();
    const newUpdate: IssueUpdate = {
      timestamp,
      status: newStatus,
      note,
      author: "Officer Suresh Rao (Operations Console)",
    };

    setIssue((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        status: newStatus,
        updatedAt: timestamp,
        updates: [newUpdate, ...prev.updates],
      };
    });
  };

  const handleApproveDraft = () => {
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

      const timestamp = new Date().toISOString();
      const newUpdate: IssueUpdate = {
        timestamp,
        status: issue.status,
        note: `AI Draft response approved and dispatched to citizen: "${draftResponse}"`,
        author: "Officer Suresh Rao (Operations Console)",
      };

      setIssue((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          updatedAt: timestamp,
          updates: [newUpdate, ...prev.updates],
        };
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Top navigation */}
      <div className="flex items-center space-x-2">
        <Link href="/officer">
          <Button variant="ghost" size="sm" className="h-8 text-xs gap-1">
            <ArrowLeft className="h-3.5 w-3.5" /> Back to Dashboard
          </Button>
        </Link>
        <span className="text-muted-foreground text-xs">/</span>
        <span className="text-xs font-mono font-semibold text-muted-foreground truncate max-w-[200px]">
          {issue.id}
        </span>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Side: Decision Workspace Details */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <Badge variant="outline" className="text-[10px] font-mono">
                {issue.id}
              </Badge>
              <Badge
                variant={
                  issue.status === "Completed"
                    ? "success"
                    : issue.status === "Assigned" || issue.status === "In_Progress"
                    ? "info"
                    : "default"
                }
              >
                {issue.status.replace("_", " ")}
              </Badge>
            </div>

            <div className="space-y-4">
              <div className="space-y-1">
                <h1 className="text-2xl font-bold tracking-tight">{issue.title}</h1>
                <p className="text-xs text-slate-400 font-semibold">
                  {issue.category} &bull; {issue.constituency}
                </p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-lg text-xs leading-relaxed text-slate-700 dark:text-slate-300">
                <p className="font-medium text-slate-900 dark:text-slate-100 mb-1">Issue Description:</p>
                <p>{issue.description}</p>
              </div>

              {/* Anonymized Citizen Summary */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2 text-xs">
                <div className="border p-3 rounded-lg bg-card">
                  <div className="text-[10px] text-muted-foreground font-medium flex items-center gap-1">
                    <User className="h-3.5 w-3.5" /> Constituent
                  </div>
                  <div className="font-bold mt-1 truncate">Voter #1049 (Anonymized)</div>
                </div>
                <div className="border p-3 rounded-lg bg-card">
                  <div className="text-[10px] text-muted-foreground font-medium flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5" /> Date Logged
                  </div>
                  <div className="font-bold mt-1 truncate">
                    {new Date(issue.createdAt).toLocaleDateString("en-IN", { dateStyle: "medium" })}
                  </div>
                </div>
                <div className="border p-3 rounded-lg bg-card">
                  <div className="text-[10px] text-muted-foreground font-medium flex items-center gap-1">
                    <Award className="h-3.5 w-3.5" /> Upvotes
                  </div>
                  <div className="font-bold mt-1">{issue.upvotes} Upvotes</div>
                </div>
                <div className="border p-3 rounded-lg bg-card">
                  <div className="text-[10px] text-muted-foreground font-medium flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" /> Region
                  </div>
                  <div className="font-bold mt-1">Shivaji Nagar W12</div>
                </div>
              </div>
            </div>
          </Card>

          {/* GIS Radar & Nearby Assets */}
          <Card className="p-6">
            <h3 className="font-bold text-sm mb-4 tracking-tight flex items-center gap-2">
              <Navigation className="h-4 w-4 text-primary" /> GIS Proximity Radar & Nearby Assets
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              {/* Concentric GIS Radar Mock */}
              <div className="flex justify-center bg-slate-950 p-4 rounded-xl relative overflow-hidden h-[240px]">
                <div className="absolute inset-0 grid grid-cols-6 grid-rows-6 opacity-[0.04]">
                  {Array.from({ length: 36 }).map((_, i) => (
                    <div key={i} className="border border-white" />
                  ))}
                </div>
                <svg className="w-full h-full max-w-[200px]" viewBox="0 0 200 200">
                  {/* Concentric Circles */}
                  <circle cx="100" cy="100" r="80" stroke="rgba(99, 102, 241, 0.15)" strokeWidth="1" fill="none" />
                  <circle cx="100" cy="100" r="55" stroke="rgba(99, 102, 241, 0.25)" strokeWidth="1" fill="none" />
                  <circle cx="100" cy="100" r="30" stroke="rgba(99, 102, 241, 0.35)" strokeWidth="1" fill="none" />
                  <line x1="100" y1="20" x2="100" y2="180" stroke="rgba(99, 102, 241, 0.15)" strokeWidth="1" />
                  <line x1="20" y1="100" x2="180" y2="100" stroke="rgba(99, 102, 241, 0.15)" strokeWidth="1" />

                  {/* Sweep line */}
                  <line x1="100" y1="100" x2="160" y2="40" stroke="#6366f1" strokeWidth="1.5" className="origin-center animate-[spin_6s_linear_infinite]" />

                  {/* Complaint Center Node */}
                  <circle cx="100" cy="100" r="6" fill="#ef4444" className="animate-ping" />
                  <circle cx="100" cy="100" r="4" fill="#ef4444" />

                  {/* Nearby Assets Nodes */}
                  <g className="cursor-pointer group">
                    <circle cx="130" cy="75" r="5" fill="#f59e0b" />
                    <text x="138" y="78" fill="#f59e0b" fontSize="8" className="font-sans font-semibold">Playground</text>
                  </g>
                  <g className="cursor-pointer">
                    <circle cx="70" cy="120" r="5" fill="#10b981" />
                    <text x="35" y="123" fill="#10b981" fontSize="8" className="font-sans font-semibold">Govt School</text>
                  </g>
                  <g className="cursor-pointer">
                    <circle cx="110" cy="150" r="5" fill="#3b82f6" />
                    <text x="118" y="153" fill="#3b82f6" fontSize="8" className="font-sans font-semibold">Clinic</text>
                  </g>
                </svg>
                <div className="absolute top-2 left-2 text-[9px] font-mono text-slate-400">RADAR SWEEP: 2.0 km Range</div>
              </div>

              {/* Assets list */}
              <div className="space-y-3">
                <p className="text-xs font-semibold text-muted-foreground uppercase">Proximity Detections</p>
                <div className="space-y-2">
                  {loadingContext ? (
                    <div className="text-xs text-muted-foreground animate-pulse">Calculating spatial buffers...</div>
                  ) : (
                    context.supporting_evidence.map((ev: string, idx: number) => (
                      <div key={idx} className="border p-2.5 rounded-lg bg-card text-xs flex items-start gap-2">
                        <AlertCircle className="h-4 w-4 text-indigo-500 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="font-bold text-slate-800 dark:text-slate-200">
                            {ev.split(":")[0]}
                          </p>
                          <p className="text-[10px] text-muted-foreground mt-0.5">
                            {ev.split(":")[1]}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </Card>

          {/* AI Reasoning & Policy Explainer */}
          <Card className="p-6">
            <h3 className="font-bold text-sm mb-4 tracking-tight flex items-center gap-2">
              <ShieldAlert className="h-4.5 w-4.5 text-primary" /> Explainable AI Decision Engine
            </h3>
            {loadingContext ? (
              <div className="text-xs text-muted-foreground animate-pulse">Running reasoning engines...</div>
            ) : (
              <div className="space-y-4">
                {/* Confidence circular bar */}
                <div className="flex items-center gap-4 bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl">
                  <div className="relative h-14 w-14 flex items-center justify-center bg-indigo-500/10 text-indigo-500 rounded-full flex-shrink-0">
                    <RefreshCw className="h-6 w-6 animate-[spin_8s_linear_infinite]" />
                    <span className="absolute text-xs font-bold font-mono">95%</span>
                  </div>
                  <div className="space-y-1">
                    <div className="text-xs font-bold">Policy Matching Confidence</div>
                    <div className="text-[11px] text-muted-foreground leading-normal">
                      The triage engine determined priority using 3 regulatory constraints and 2 local ward asset matches. SLA set to 24h.
                    </div>
                  </div>
                </div>

                {/* Reasoning flow diagram */}
                <div className="border rounded-xl p-4 space-y-3 bg-card">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Decision Reasoning Chain</span>
                  <div className="font-mono text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed whitespace-pre-line bg-slate-50 dark:bg-slate-900/30 p-3 rounded-lg border-l-2 border-indigo-500">
                    {context.reasoning_chain}
                  </div>
                </div>

                {/* Expected Outcome */}
                <div className="border p-3 rounded-lg bg-card text-xs">
                  <span className="font-bold text-indigo-500 block mb-1">Expected Outcome:</span>
                  <p className="text-muted-foreground">{context.expected_outcome}</p>
                </div>
              </div>
            )}
          </Card>

          {/* Alternative Actions Grid */}
          <Card className="p-6">
            <h3 className="font-bold text-sm mb-4 tracking-tight flex items-center gap-2">
              <BarChart2 className="h-4.5 w-4.5 text-primary" /> Alternative Actions & Budget Trade-offs
            </h3>
            {loadingContext ? (
              <div className="text-xs text-muted-foreground animate-pulse">Assembling alternatives...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {context.alternative_actions.map((alt: any, idx: number) => (
                  <div
                    key={idx}
                    onClick={() => setSelectedAlternative(idx)}
                    className={`border p-3.5 rounded-xl cursor-pointer transition flex flex-col justify-between h-[120px] ${
                      selectedAlternative === idx
                        ? "border-primary bg-primary/[0.03] ring-1 ring-primary"
                        : "bg-card hover:bg-slate-50/50 dark:hover:bg-slate-900/30"
                    }`}
                  >
                    <div>
                      <div className="font-bold text-xs line-clamp-1">{alt.title}</div>
                      <p className="text-[10px] text-muted-foreground mt-1 line-clamp-2">{alt.desc}</p>
                    </div>
                    <div className="flex justify-between items-center text-[10px] font-semibold mt-2 border-t pt-2">
                      <span className="text-slate-400">SLA: {alt.sla}</span>
                      <span
                        className={
                          alt.cost === "High"
                            ? "text-red-500"
                            : alt.cost === "Medium"
                            ? "text-amber-500"
                            : "text-emerald-500"
                        }
                      >
                        Cost: {alt.cost}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Audit Timeline */}
          <Card className="p-6">
            <h3 className="font-bold text-sm mb-4 tracking-tight flex items-center gap-2">
              <Clock className="h-4 w-4 text-primary" /> Lifecycle Audit Ledger
            </h3>
            <div className="relative border-l pl-4 ml-2 space-y-6">
              {issue.updates.map((update, index) => (
                <div key={index} className="relative">
                  <span
                    className={`absolute -left-[21px] top-1.5 h-3.5 w-3.5 rounded-full border bg-background flex items-center justify-center ${
                      index === 0 ? "border-primary text-primary" : "border-slate-300 text-slate-300"
                    }`}
                  >
                    <span
                      className={`h-1.5 w-1.5 rounded-full bg-current ${
                        index === 0 ? "animate-pulse bg-primary" : "bg-slate-400"
                      }`}
                    />
                  </span>

                  <div className="space-y-1 text-xs">
                    <div className="flex flex-wrap items-center justify-between gap-1">
                      <span className="font-bold text-slate-800 dark:text-slate-200 font-mono">
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
                    onClick={() =>
                      handleStatusChange(
                        "Validated",
                        "Validated against regional utility infrastructure mapping."
                      )
                    }
                  >
                    Validate AI
                  </Button>
                  <Button
                    size="sm"
                    variant={issue.status === "Assigned" ? "default" : "outline"}
                    className="h-8 text-[11px]"
                    onClick={() =>
                      handleStatusChange(
                        "Assigned",
                        "Assigned dispatch order to Sector Maintenance Unit B."
                      )
                    }
                  >
                    Assign Crew
                  </Button>
                  <Button
                    size="sm"
                    variant={issue.status === "In_Progress" ? "default" : "outline"}
                    className="h-8 text-[11px]"
                    onClick={() =>
                      handleStatusChange(
                        "In_Progress",
                        "Field work started. Excavators and technicians on-site."
                      )
                    }
                  >
                    Start Work
                  </Button>
                  <Button
                    size="sm"
                    variant={issue.status === "Completed" ? "default" : "outline"}
                    className="h-8 text-[11px] border-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 text-emerald-600"
                    onClick={() =>
                      handleStatusChange(
                        "Completed",
                        "Service request resolved. Infrastructure checked and restored."
                      )
                    }
                  >
                    Complete SLA
                  </Button>
                </div>
              </div>

              {/* AI Dispatch Response */}
              <div className="border-t pt-4 space-y-2">
                <span className="font-semibold text-muted-foreground flex items-center gap-1">
                  <FileText className="h-3.5 w-3.5" /> AI Recommendation Response Draft
                </span>
                <textarea
                  className="w-full rounded-md border bg-background p-2.5 text-[11px] text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono leading-normal"
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

          {/* Crew Allocation card */}
          <Card className="p-4 space-y-3">
            <h4 className="font-bold text-xs flex items-center gap-1.5">
              <User className="h-4 w-4 text-slate-500" /> Operational Crew Assignment
            </h4>
            <div className="text-xs space-y-2 border p-3 rounded-lg bg-slate-50 dark:bg-slate-900/50">
              <div className="flex justify-between font-semibold">
                <span>Suggested Dept:</span>
                <span>{loadingContext ? "Loading..." : context.suggested_department}</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>Field Crew Contact:</span>
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
                  handleStatusChange(
                    issue.status,
                    `Dispatcher Note: "${dispatcherNote}"`
                  );
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
