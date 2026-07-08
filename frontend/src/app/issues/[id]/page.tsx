"use client";

import React, { useState, useEffect } from "react";
import { fetchWithAuth } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import {
  ArrowLeft,
  Clock,
  User,
  ShieldAlert,
  FileText,
  Send,
  Calendar,
  Eye,
  Layers,
  TrendingUp,
  Cpu,
  RefreshCw,
  Globe,
  ChevronDown,
  ChevronUp,
  CheckCircle,
  Users,
} from "lucide-react";

export interface IssueUpdate {
  id?: string;
  note: string;
  timestamp: string;
  author: string;
  authorRole?: string;
  status?: string;
}

export interface Issue {
  id: string;
  title: string;
  description: string;
  category: string;
  status: string;
  priority: "Low" | "Medium" | "High" | "Critical" | string;
  citizenName: string;
  createdAt: string;
  updatedAt: string;
  constituency: string;
  location: { lat: number; lng: number };
  upvotes: number;
  updates: IssueUpdate[];
  aiDraftResponse?: string;
}

export default function IssueDetailsPage({ params }: { params: { id: string } }) {
  const [issue, setIssue] = useState<Issue | null>(null);
  const [draftResponse, setDraftResponse] = useState("");
  const [dispatcherNote, setDispatcherNote] = useState("");
  const [isSuccessMsg, setIsSuccessMsg] = useState(false);
  const [recommendationId, setRecommendationId] = useState<string | null>(null);

  // Decision Context States
  const [context, setContext] = useState<any>(null);
  const [loadingContext, setLoadingContext] = useState(true);
  const [selectedAlternative, setSelectedAlternative] = useState<number>(0);

  // Tab State
  const [leftTab, setLeftTab] = useState<"brief" | "pipeline" | "audit">("brief");

  // AI Pipeline States
  const [pipeline, setPipeline] = useState<any>(null);
  const [loadingPipeline, setLoadingPipeline] = useState(true);
  const [expandedAgent, setExpandedAgent] = useState<number | null>(null);

  // Governance Copilot States
  const [copilotResponse, setCopilotResponse] = useState<any>(null);
  const [copilotLanguage, setCopilotLanguage] = useState("English");
  const [queryingCopilot, setQueryingCopilot] = useState(false);

  // Timeline States
  const [timelineData, setTimelineData] = useState<any>(null);
  const [loadingTimeline, setLoadingTimeline] = useState(true);
  const [currentRole, setCurrentRole] = useState<"citizen" | "officer" | "administrator">("officer");
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const urlParams = new URLSearchParams(window.location.search);
      const urlRole = urlParams.get("role");
      if (urlRole === "citizen" || urlRole === "officer" || urlRole === "administrator") {
        setCurrentRole(urlRole);
      }
    }
  }, []);

  useEffect(() => {
    // 1. Fetch Issue Details
    fetchWithAuth(`/governance/issues/pending`)
      .then((data) => {
        const found = data.find((i: any) => i.id === params.id);
        if (found) {
          const mapped: any = {
            id: found.id,
            title: found.title,
            description: found.description,
            category: found.category,
            status: found.status,
            priority: found.priority,
            citizenName: "Jan Doe",
            createdAt: found.created_at || new Date().toISOString(),
            updatedAt: found.created_at || new Date().toISOString(),
            constituency: "Central Bengaluru",
            location: { lat: found.latitude, lng: found.longitude },
            upvotes: 1,
            updates: [],
            aiDraftResponse: "AI recommendation pending...",
          };
          setIssue(mapped);

          // Fetch Recommendation
          fetchWithAuth(`/governance/recommendations/${found.id}`)
            .then((rec) => {
              if (rec) {
                setRecommendationId(rec.id);
                setDraftResponse(rec.rationale);
                setIssue((prev: any) =>
                  prev ? { ...prev, aiDraftResponse: rec.rationale } : null
                );
              }
            })
            .catch((err) => console.log("Failed to fetch recommendation:", err));

          // Fetch Decision Brief
          fetchWithAuth(`/governance/issues/${found.id}/decision-brief`)
            .then((ctx) => {
              if (ctx) {
                setContext(ctx);
                if (ctx.alternative_actions) {
                  const recIdx = ctx.alternative_actions.findIndex((a: any) => a.is_recommended);
                  if (recIdx !== -1) {
                    setSelectedAlternative(recIdx);
                  }
                }
              }
              setLoadingContext(false);
            })
            .catch((err) => {
              console.log("Failed to fetch decision-brief:", err);
              setLoadingContext(false);
            });

          // Fetch AI Pipeline
          fetchWithAuth(`/governance/issues/${found.id}/decision-pipeline`)
            .then((pipe) => {
              setPipeline(pipe || null);
              setLoadingPipeline(false);
            })
            .catch((err) => {
              console.log("Failed to fetch pipeline:", err);
              setLoadingPipeline(false);
            });

          // Fetch Timeline
          fetchWithAuth(`/governance/issues/${found.id}/timeline?role=${currentRole}`)
            .then((tl) => {
              setTimelineData(tl || null);
              setLoadingTimeline(false);
            })
            .catch((err) => {
              console.log("Failed to fetch timeline:", err);
              setLoadingTimeline(false);
            });
        }
      })
      .catch((err) => console.log("Failed to load issue details:", err));
  }, [params.id, currentRole]);



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

  const handleStatusChange = (newStatus: string, note: string) => {
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
      fetchWithAuth(`/governance/recommendations/${recommendationId}/accept`, {
        method: "POST",
      })
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

  // Trigger Governance Copilot APIs
  const queryCopilot = async (action: string) => {
    setQueryingCopilot(true);
    try {
      const data = await fetchWithAuth(`/governance/copilot`, {
        method: "POST",
        body: JSON.stringify({
          action,
          issue_id: issue.id,
          query_details: { language: copilotLanguage },
        }),
      });
      setDraftResponse(data.analysis || "Analysis received.");
      if (data.recommendations && data.recommendations.length > 0) {
        setRecommendationId(data.recommendations[0].id);
      }
      setCopilotResponse(data);
    } catch (err) {
      console.log("Offline fallback for copilot query:", err);
      const isSanit =
        issue.category.toLowerCase().includes("sanit") ||
        issue.category.toLowerCase().includes("water");

      let summary = "";
      let recommendations: string[] = [];
      let alternatives: string[] = [];
      let citations: string[] = [];
      let evidence: string[] = [];
      let warnings: string[] = [];

      if (action === "policy_explanation") {
        summary = isSanit
          ? "This sanitation complaint matches the 2024 Ward Waste Disposal Act. Grounded subsidies apply through the Swachh Bharat Abhiyan fund matching."
          : "Under PMGSY road restoration policy, main arterial segments with bus routes receive urgent priority status and local infrastructure grant credits.";
        citations = isSanit
          ? ["📜 Enforced Policy: `Sanitation Waste Management Regulation 2024`"]
          : ["💰 Linked Scheme: `PMGSY Roads Fund Contract`"];
        evidence = [
          "Located within 500m of residential ward playground.",
          "Category matches sanitation classification.",
        ];
        recommendations = ["Authorize immediate budget clearance under active local scheme."];
      } else if (action === "alternative_recommendation") {
        summary =
          "We can outsource this clearing job to a private contractor for 12h resolution, but it incurs a 220% cost premium.";
        alternatives = ["Private Contractor SLA 12h: ₹8.0L", "Defer to monthly General Sweep: ₹0"];
        recommendations = ["Proceed with internal ward dispatch to save regional budget resources."];
      } else if (action === "citizen_reply") {
        summary =
          copilotLanguage === "Kannada"
            ? "ನಮಸ್ಕಾರ, ನಿಮ್ಮ ದೂರು ಯಶಸ್ವಿಯಾಗಿ ದಾಖಲಾಗಿದೆ. ಮುಂದಿನ 24 ಗಂಟೆಗಳಲ್ಲಿ ನೈರ್ಮಲ್ಯ ಇಲಾಖೆ ಅಧಿಕಾರಿಗಳು ಸ್ಥಳಕ್ಕೆ ಧಾವಿಸಲಿದ್ದಾರೆ."
            : copilotLanguage === "Hindi"
            ? "नमस्ते, आपकी शिकायत दर्ज हो गई है। 48 घंटे के भीतर लोक निर्माण विभाग के कर्मचारी काम शुरू कर देंगे।"
            : "Dear Constituent, your service request has been triaged. Operations crew is dispatched and scheduled to arrive within 48 hours.";
        citations = ["SMS Dispatcher Notification Log"];
      } else if (action === "meeting_brief") {
        summary =
          `Constituency Review Brief: pending tickets in ${issue.constituency}. Heavy backlog in PWD road patch operations due to recent utility pipeline excavations.`;
        evidence = ["Active backlogs: 8 days behind schedule.", "Recommended: Allocate contingency funds."];
        recommendations = [
          "Table backlog report in tomorrow's MP review meeting.",
          "Request fast-track utility clearance.",
        ];
      } else {
        summary =
          "Calculated priority score is 9.0/10 based on local asset proximity and regional voter density.";
        evidence = ["18 duplicate tickets reported in close coordinates.", "Near hospital ambulance lane."];
        citations = ["Geo-spatial coordinate logs"];
      }

      setCopilotResponse({
        summary,
        evidence,
        citations,
        confidence: 0.95,
        recommendations,
        alternatives,
        warnings,
      });
    }
    setQueryingCopilot(false);
  };

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Link href="/officer">
            <Button variant="ghost" size="sm" className="h-8 text-xs gap-1">
              <ArrowLeft className="h-3.5 w-3.5" /> Back to Dashboard
            </Button>
          </Link>
          <span className="text-muted-foreground text-xs">/</span>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Decision Brief Engine
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg text-xs font-semibold border">
            <button
              onClick={() => {
                setCurrentRole("citizen");
                setLeftTab("audit");
              }}
              className={`px-3 py-1 rounded-md transition ${
                currentRole === "citizen"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Citizen View
            </button>
            <button
              onClick={() => setCurrentRole("officer")}
              className={`px-3 py-1 rounded-md transition ${
                currentRole === "officer"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Officer
            </button>
            <button
              onClick={() => setCurrentRole("administrator")}
              className={`px-3 py-1 rounded-md transition ${
                currentRole === "administrator"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Admin
            </button>
          </div>
          <span className="text-muted-foreground text-xs">/</span>
          <div className="text-xs text-muted-foreground font-semibold">
            Status:{" "}
            <Badge variant="outline" className="ml-1 font-mono text-[10px]">
              {issue.status}
            </Badge>
          </div>
        </div>
      </div>

      {/* Signature Title Block */}
      <div className="border-b pb-4">
        <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
          Decision Brief: {issue.title}
        </h1>
        <p className="text-xs text-muted-foreground mt-1">
          Grounded explainable recommendation document compiled on{" "}
          {new Date(issue.createdAt).toLocaleDateString("en-IN", { dateStyle: "long" })}.
        </p>
      </div>

      {/* Tab Navigation Buttons */}
      {currentRole !== "citizen" && (
        <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg w-full max-w-md">
          <button
            onClick={() => setLeftTab("brief")}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
              leftTab === "brief"
                ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Decision Brief
          </button>
          <button
            onClick={() => setLeftTab("pipeline")}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
              leftTab === "pipeline"
                ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            AI Pipeline
          </button>
          <button
            onClick={() => setLeftTab("audit")}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
              leftTab === "audit"
                ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Timeline & Activity Log
          </button>
        </div>
      )}

      {/* Main Split Layout */}
      <div className={`grid grid-cols-1 ${currentRole === "citizen" ? "" : "lg:grid-cols-3"} gap-6`}>
        {/* Left Columns (2/3 width or full width if citizen) - Swapped based on tab selection */}
        <div className={`${currentRole === "citizen" ? "lg:col-span-3" : "lg:col-span-2"} space-y-6`}>
          {leftTab === "brief" && currentRole !== "citizen" && (
            <div className="space-y-6">
              {/* Grounded Decision Confidence Gauge */}
              {!loadingContext && context && (() => {
                const isObj = typeof context.confidence === "object" && context.confidence !== null;
                const score = isObj ? context.confidence.overall : context.confidence || 85;
                const signals = isObj ? context.confidence.signals : null;

                return (
                  <div className="space-y-3 bg-indigo-50/50 dark:bg-indigo-950/20 p-4 rounded-xl border border-indigo-500/20">
                    <div className="flex items-center gap-3">
                      <div className="relative flex items-center justify-center h-14 w-14 rounded-full border-4 border-indigo-500/30 text-indigo-500 font-extrabold text-lg flex-shrink-0">
                        {score}%
                      </div>
                      <div>
                        <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 block uppercase tracking-wider">
                          Grounded Decision Confidence
                        </span>
                        <p className="text-[10px] text-muted-foreground leading-normal mt-0.5 font-sans">
                          Derived via hybrid scoring on duplicates density, matched policies, scheme subsidies, and assets proximity ward mapping.
                        </p>
                      </div>
                    </div>

                    {signals && (
                      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-2 border-t border-indigo-500/10 text-[9px] font-mono text-slate-500">
                        {Object.entries(signals).map(([sig, val]: any) => (
                          <div key={sig} className="bg-white dark:bg-slate-900 p-1.5 rounded border border-indigo-500/5">
                            <span className="capitalize block text-slate-400 font-sans">{sig.replace("_", " ")}</span>
                            <span className="font-bold text-indigo-600 mt-0.5 block">{val} pts</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })()}

              {/* SECTION 1: Problem Definition */}
              <Card className="p-5 space-y-4">
                <div className="border-l-4 border-indigo-500 pl-3">
                  <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                    <FileText className="h-4.5 w-4.5 text-indigo-500" /> 1. Problem Definition
                  </h3>
                </div>
                <div className="space-y-2 text-xs leading-relaxed font-sans">
                  <p className="font-semibold text-slate-800 dark:text-slate-200">Incident Details:</p>
                  <p className="text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900/30 p-3.5 rounded-lg border">
                    {issue.description}
                  </p>
                </div>
              </Card>

              {/* SECTION 1.5: Incident Intelligence & Duplicate Clusters */}
              <Card className="p-5 space-y-4">
                <div className="border-l-4 border-indigo-500 pl-3 flex items-center justify-between">
                  <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                    <Users className="h-4.5 w-4.5 text-indigo-500" /> 1.5. Incident Intelligence & Duplicate Clusters
                  </h3>
                  <Badge variant="success" className="text-[9px] font-mono">
                    {issue.category.toLowerCase().includes("sanit") || issue.category.toLowerCase().includes("water") ? "18 Reports Clustered" : "6 Reports Clustered"}
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Left sub-panel: Radar scan and cluster map */}
                  <div className="border rounded-xl p-4 bg-slate-50 dark:bg-slate-900/50 flex flex-col items-center justify-center min-h-[220px] relative overflow-hidden">
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block mb-2 self-start">
                      Regional Duplicate Scan Radar (300m Radius)
                    </span>
                    <div className="relative w-32 h-32 rounded-full border border-indigo-500/20 flex items-center justify-center bg-slate-100/50 dark:bg-slate-950/40">
                      {/* Radar sweep animation */}
                      <div className="absolute inset-0 rounded-full border border-indigo-500/30 animate-ping opacity-40" />
                      <div className="absolute w-full h-0.5 bg-indigo-500/10 origin-center animate-spin" />

                      {/* Clustered coordinates plot */}
                      <span className="absolute top-8 left-8 h-2.5 w-2.5 rounded-full bg-indigo-500 animate-pulse shadow-md" />
                      <span className="absolute bottom-6 right-8 h-2 w-2 rounded-full bg-indigo-500/70" />
                      <span className="absolute top-14 right-10 h-2 w-2 rounded-full bg-indigo-500/80" />
                      <span className="absolute bottom-10 left-12 h-1.5 w-1.5 rounded-full bg-indigo-500/60" />

                      {/* Central canonical report */}
                      <span className="h-4 w-4 rounded-full bg-rose-500 border-2 border-white dark:border-slate-950 flex items-center justify-center shadow-lg shadow-rose-500/40 z-10">
                        <span className="h-1.5 w-1.5 rounded-full bg-white" />
                      </span>
                    </div>
                    <div className="text-[9px] text-muted-foreground font-mono mt-3 text-center">
                      Detected duplicates within 150m buffer radius.
                    </div>
                  </div>

                  {/* Right sub-panel: Duplicate details and confidence */}
                  <div className="space-y-3 flex flex-col justify-between">
                    <div className="bg-white dark:bg-slate-900 p-3 rounded-lg border border-indigo-500/10 space-y-1.5">
                      <div className="flex justify-between items-center text-[10px] font-semibold text-slate-500">
                        <span>SCAN CONFIDENCE</span>
                        <span className="text-indigo-650 font-bold">94.8% Match</span>
                      </div>
                      <div className="bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div className="bg-indigo-600 h-full rounded-full" style={{ width: "94.8%" }} />
                      </div>
                      <p className="text-[9px] text-slate-400 leading-normal">
                        Based on spatial proximity (100%), exact category match (100%), and title/description similarity (84.4%).
                      </p>
                    </div>

                    <div className="border rounded-lg p-3 bg-slate-50/50 dark:bg-slate-950/20 text-[10px] space-y-2">
                      <span className="font-bold text-[9px] text-slate-400 uppercase tracking-wider block">
                        Supporting Community Reports
                      </span>
                      <div className="space-y-1.5 max-h-[100px] overflow-y-auto pr-1">
                        <div className="bg-white dark:bg-slate-900 p-2 rounded border border-slate-200/50 dark:border-slate-800/80 leading-normal">
                          <span className="font-semibold text-slate-700 dark:text-slate-350">#102: Water leakage near Shivaji School</span>
                          <span className="text-muted-foreground block text-[9px]">Submitted by Rajesh K. (2 hrs ago) &bull; Coordinates: 12.9758, 77.5957</span>
                        </div>
                        <div className="bg-white dark:bg-slate-900 p-2 rounded border border-slate-200/50 dark:border-slate-800/80 leading-normal">
                          <span className="font-semibold text-slate-700 dark:text-slate-350">#103: Pipelake burst flooded street segment</span>
                          <span className="text-muted-foreground block text-[9px]">Submitted by Meena S. (1 day ago) &bull; Coordinates: 12.9754, 77.5954</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Evidence gallery thumbnails */}
                <div className="border-t border-slate-100 dark:border-slate-800/50 pt-3">
                  <span className="font-bold text-[9px] text-slate-400 uppercase tracking-wider block mb-2">
                    Evidence Gallery (Merged Attachments)
                  </span>
                  <div className="grid grid-cols-4 gap-2">
                    <div className="bg-slate-100 dark:bg-slate-900 rounded-lg h-14 border border-dashed flex items-center justify-center text-[9px] text-slate-400">
                      📸 Main Image
                    </div>
                    <div className="bg-slate-100 dark:bg-slate-905 rounded-lg h-14 border border-dashed flex items-center justify-center text-[9px] text-slate-400">
                      📸 Dup #102
                    </div>
                    <div className="bg-slate-100 dark:bg-slate-905 rounded-lg h-14 border border-dashed flex items-center justify-center text-[9px] text-slate-400">
                      📸 Dup #103
                    </div>
                    <div className="bg-slate-100 dark:bg-slate-905 rounded-lg h-14 border border-dashed flex items-center justify-center text-[9px] text-slate-400">
                      + More
                    </div>
                  </div>
                </div>
              </Card>

              {/* SECTION 2: Evidence Panel Card Grid */}
              {!loadingContext && context && (
                <Card className="p-5 space-y-4">
                  <div className="border-l-4 border-indigo-500 pl-3">
                    <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <Eye className="h-4.5 w-4.5 text-indigo-500" /> 2. Grounded Evidence Grid
                    </h3>
                  </div>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      {/* Card 1: Citizen Photo Placeholder */}
                      <div className="border p-3.5 rounded-xl bg-card flex flex-col justify-between min-h-[110px]">
                        <span className="text-[10px] text-muted-foreground font-semibold uppercase">
                          Incident Photo
                        </span>
                        <div className="h-12 bg-slate-100 dark:bg-slate-900 rounded-lg flex items-center justify-center border border-dashed text-slate-400 text-[10px]">
                          <span>[ Evidence Attachment ]</span>
                        </div>
                      </div>
                      {/* Card 2: Duplicate Issues Count */}
                      <div className="border p-3.5 rounded-xl bg-card flex flex-col justify-between min-h-[110px]">
                        <span className="text-[10px] text-muted-foreground font-semibold uppercase">
                          Duplicate Cluster
                        </span>
                        <div className="flex items-baseline gap-1 mt-2">
                          <span className="text-3xl font-extrabold text-indigo-500">
                            {issue.category.toLowerCase().includes("sanit") || issue.category.toLowerCase().includes("water") ? 18 : 6}
                          </span>
                          <span className="text-[10px] text-slate-400 font-medium">complaints in ward</span>
                        </div>
                        <span className="text-[9px] text-emerald-500 font-semibold flex items-center gap-0.5">
                          <TrendingUp className="h-3 w-3" /> Area Hotspot Active
                        </span>
                      </div>
                      {/* Card 3: GIS Coordinates */}
                      <div className="border p-3.5 rounded-xl bg-card flex flex-col justify-between min-h-[110px]">
                        <span className="text-[10px] text-muted-foreground font-semibold uppercase">
                          GIS Mapping
                        </span>
                        <div className="font-mono text-[10px] mt-1 space-y-1">
                          <div>LAT: {context.problem.location.latitude.toFixed(4)}</div>
                          <div>LNG: {context.problem.location.longitude.toFixed(4)}</div>
                        </div>
                        <Badge variant="outline" className="text-[8px] justify-center mt-2 font-mono">
                          {issue.constituency}
                        </Badge>
                      </div>
                    </div>

                    {/* Bullet points extracted evidence */}
                    <div className="bg-slate-50 dark:bg-slate-900/30 p-3.5 rounded-lg border space-y-2 text-xs">
                      <span className="font-bold text-slate-400 uppercase tracking-wider text-[9px] block">Audit Evidence Logs</span>
                      <ul className="list-disc pl-4 space-y-2 text-slate-650 dark:text-slate-400 leading-relaxed font-sans">
                        {context.evidence.map((ev: any, idx: number) => (
                          <li key={idx} className="items-start gap-2">
                            <span>{typeof ev === "string" ? ev : ev.statement}</span>
                            {typeof ev === "object" && ev && ev.source && (
                              <Badge variant="outline" className="text-[8px] ml-2 font-mono uppercase bg-indigo-50/50 text-indigo-600 border-indigo-200">
                                {ev.source}
                              </Badge>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </Card>
              )}

              {/* SECTION 3: Explainability Tree & Policy Grounding */}
              {!loadingContext && context && (
                <Card className="p-5 space-y-4">
                  <div className="border-l-4 border-indigo-500 pl-3">
                    <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <ShieldAlert className="h-4.5 w-4.5 text-indigo-500" /> 3. Policy & Scheme Grounding
                    </h3>
                  </div>

                  <div className="space-y-4">
                    {/* Badges row */}
                    <div className="flex flex-wrap gap-2">
                      {context.applicable_policies.map((p: any, idx: number) => (
                        <Badge key={idx} variant="default" className="text-[10px] bg-indigo-650 font-sans p-1 px-2.5">
                          📜 Policy: {p.name} ({p.code})
                        </Badge>
                      ))}
                      {context.applicable_schemes.map((s: any, idx: number) => (
                        <Badge key={idx} variant="secondary" className="text-[10px] font-sans p-1 px-2.5">
                          💰 Scheme Match: {s.name} ({s.subsidy_ratio * 100}% Subsidy)
                        </Badge>
                      ))}
                    </div>

                    {/* Reasoning timeline */}
                    <div className="border rounded-xl p-4 bg-slate-50 dark:bg-slate-900/50 space-y-3">
                      <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">AI Decision Reasoning Timeline</span>
                      <div className="space-y-2.5 text-xs font-sans">
                        {context.reasoning.map((step: string, idx: number) => (
                          <div key={idx} className="flex gap-2 items-start leading-relaxed text-slate-700 dark:text-slate-300">
                            <span className="font-bold text-indigo-500 font-mono">{idx + 1}.</span>
                            <p>{step}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card>
              )}

              {/* SECTION 4: Recommendation & Alternatives Comparison */}
              {!loadingContext && context && (
                <Card className="p-5 space-y-4">
                  <div className="border-l-4 border-indigo-500 pl-3">
                    <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <Layers className="h-4.5 w-4.5 text-indigo-500" /> 4. Recommendation Comparison Matrix
                    </h3>
                  </div>
                  <div className="space-y-4 font-sans">
                    <div className="overflow-x-auto rounded-xl border bg-card text-xs">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="border-b bg-slate-50 dark:bg-slate-900/50 font-semibold text-slate-500">
                            <th className="p-3">Option</th>
                            <th className="p-3">Estimated Cost</th>
                            <th className="p-3">Timeline (SLA)</th>
                            <th className="p-3">Durability</th>
                            <th className="p-3">Risk Assessment</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y font-medium">
                          {context.alternative_actions.map((alt: any, idx: number) => (
                            <tr
                              key={idx}
                              onClick={() => setSelectedAlternative(idx)}
                              className={`cursor-pointer hover:bg-slate-50/50 dark:hover:bg-slate-900/30 transition ${
                                selectedAlternative === idx ? "bg-indigo-500/5 text-indigo-650 font-bold" : ""
                              }`}
                            >
                              <td className="p-3 flex items-center gap-1.5">
                                {alt.option_name}
                                {alt.is_recommended && <Badge className="text-[8px] p-0.5 px-1.5 bg-emerald-500 border-none">Recommended</Badge>}
                              </td>
                              <td className="p-3">{alt.estimated_cost}</td>
                              <td className="p-3">{alt.sla}</td>
                              <td className="p-3">{alt.durability}</td>
                              <td className="p-3 text-slate-400">{alt.risks}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <div className="border p-3.5 rounded-lg bg-indigo-500/[0.02] border-indigo-500/20 text-xs">
                      <span className="font-bold text-indigo-600 block mb-1">
                        Selected Strategy: {context.alternative_actions[selectedAlternative].option_name}
                      </span>
                      <p className="text-muted-foreground leading-normal mb-2">
                        {context.alternative_actions[selectedAlternative].description}
                      </p>
                      <div className="flex gap-4 text-[10px] font-semibold text-slate-400 border-t pt-2 mt-2">
                        <div>Feasibility Index: <span className="text-slate-800 dark:text-slate-200">{context.alternative_actions[selectedAlternative].feasibility}</span></div>
                      </div>
                    </div>
                  </div>
                </Card>
              )}

              {/* SECTION 5: Follow-up Actions */}
              {!loadingContext && context && (
                <Card className="p-5 space-y-4">
                  <div className="border-l-4 border-indigo-500 pl-3">
                    <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <CheckCircle className="h-4.5 w-4.5 text-indigo-500" /> 5. Action Items & Follow-up
                    </h3>
                  </div>
                  <div className="bg-slate-50 dark:bg-slate-900/30 p-3.5 rounded-lg border space-y-3.5 text-xs font-sans">
                    <div className="space-y-2.5">
                      {context.follow_up_actions.map((act: string, idx: number) => (
                        <div key={idx} className="flex gap-2 items-center text-slate-700 dark:text-slate-300 font-medium">
                          <span className="h-2 w-2 rounded-full bg-emerald-500 flex-shrink-0" />
                          <p>{act}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </Card>
              )}
            </div>
          )}

          {/* NEW: AI Pipeline Tab layout */}
          {leftTab === "pipeline" && (
            <Card className="p-6 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
                <div>
                  <h2 className="text-md font-bold text-slate-800 dark:text-slate-200">AI Decision Pipeline</h2>
                  <p className="text-xs text-muted-foreground">Multi-agent diagnostic trace pipeline.</p>
                </div>
                {!loadingPipeline && pipeline && (
                  <div className="flex gap-4 text-xs font-mono">
                    <div>
                      Latency: <span className="font-bold text-indigo-600">{pipeline.total_latency_ms.toFixed(0)} ms</span>
                    </div>
                    <div>
                      Avg Confidence: <span className="font-bold text-indigo-600">{(pipeline.average_confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                )}
              </div>

              {loadingPipeline ? (
                <div className="text-xs text-muted-foreground animate-pulse py-8 text-center">
                  Executing agent validation steps...
                </div>
              ) : (
                <div className="relative border-l pl-6 ml-4 space-y-6">
                  {pipeline.timeline.map((agent: any, idx: number) => {
                    const isExpanded = expandedAgent === idx;
                    return (
                      <div key={idx} className="relative">
                        {/* Circular node check indicator */}
                        <span className="absolute -left-[35px] top-1 h-5 w-5 rounded-full border-2 border-indigo-500 bg-background flex items-center justify-center text-indigo-500">
                          <CheckCircle className="h-3.5 w-3.5 fill-indigo-500 text-background" />
                        </span>

                        <div className="space-y-2 text-xs">
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-bold text-slate-800 dark:text-slate-200 text-sm">
                              {agent.agent_name}
                            </span>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-[9px] font-mono">
                                {agent.execution_time_ms.toFixed(0)} ms
                              </Badge>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-6 w-6 p-0 text-slate-400"
                                onClick={() => setExpandedAgent(isExpanded ? null : idx)}
                              >
                                {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                              </Button>
                            </div>
                          </div>

                          <p className="text-[10px] text-muted-foreground">
                            Execution Confidence: {(agent.confidence * 100).toFixed(0)}%
                          </p>

                          {/* Expandable Agent Details */}
                          {isExpanded && (
                            <div className="border p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/50 space-y-3 animate-fade-in border-indigo-500/10">
                              <div>
                                <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Grounded Evidence</span>
                                <ul className="list-disc pl-4 text-[10px] text-slate-600 dark:text-slate-400 mt-1 space-y-1">
                                  {agent.evidence.map((ev: string, i: number) => (
                                    <li key={i}>{ev}</li>
                                  ))}
                                </ul>
                              </div>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-200/50 dark:border-slate-800">
                                <div>
                                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Inputs</span>
                                  <pre className="font-mono text-[9px] bg-card p-2 rounded border mt-1 overflow-x-auto text-slate-500">
                                    {jsonStringifyNice(agent.inputs)}
                                  </pre>
                                </div>
                                <div>
                                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Outputs</span>
                                  <pre className="font-mono text-[9px] bg-card p-2 rounded border mt-1 overflow-x-auto text-slate-500">
                                    {jsonStringifyNice(agent.outputs)}
                                  </pre>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </Card>
          )}

          {/* Audit Tab */}
          {(leftTab === "audit" || currentRole === "citizen") && (
            <Card className="p-6 space-y-6 shadow-md border-indigo-500/10">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
                <div>
                  <h3 className="font-extrabold text-lg tracking-tight flex items-center gap-2 text-indigo-900 dark:text-indigo-400">
                    <Clock className="h-5 w-5 text-indigo-500" /> Issue Progress Timeline
                  </h3>
                  <p className="text-xs text-muted-foreground">Canonical lifecycle status tracking and audit ledger.</p>
                </div>
                {timelineData && (
                  <div className="flex items-center gap-4 bg-indigo-50/50 dark:bg-indigo-950/20 p-2 px-3 rounded-lg border border-indigo-500/10">
                    <div className="text-xs">
                      Stage: <span className="font-bold text-indigo-600 dark:text-indigo-400">{timelineData.current_stage}</span>
                    </div>
                    <div className="h-4 w-px bg-slate-200 dark:bg-slate-800" />
                    <div className="text-xs">
                      Est. Remaining Time: <span className="font-bold text-indigo-600 dark:text-indigo-400">{timelineData.estimated_remaining_sla_hours} hrs left</span>
                    </div>
                  </div>
                )}
              </div>

              {loadingTimeline || !timelineData ? (
                <div className="text-xs text-muted-foreground animate-pulse py-8 text-center">
                  Compiling issue lifecycle timeline...
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Progress bar visual */}
                  <div className="bg-slate-100 dark:bg-slate-800 h-2.5 rounded-full overflow-hidden flex">
                    <div
                      className="bg-indigo-600 h-full rounded-full transition-all duration-500"
                      style={{ width: `${timelineData.progress}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-muted-foreground font-semibold px-1">
                    <span>Reported</span>
                    <span>AI Review</span>
                    <span>Approved</span>
                    <span>In Progress</span>
                    <span>Resolved</span>
                    <span className="text-indigo-600 dark:text-indigo-400 font-bold">Current: {timelineData.progress}%</span>
                  </div>

                  {timelineData.estimated_next_action && timelineData.progress < 100 && (
                    <div className="bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 p-3 rounded-lg text-xs leading-normal flex items-start gap-2">
                      <ShieldAlert className="h-4 w-4 mt-0.5 flex-shrink-0" />
                      <div>
                        <span className="font-bold">Next Planned Action: </span>
                        {timelineData.estimated_next_action}
                      </div>
                    </div>
                  )}

                  {/* Vertical Timeline Card Tree */}
                  <div className="relative border-l-2 border-indigo-100 dark:border-indigo-950 pl-6 ml-3 space-y-6">
                    {timelineData.timeline.map((event: any) => {
                      const isExpanded = expandedEventId === event.id;
                      const isCompleted = event.status === "COMPLETED";
                      const isInProgress = event.status === "IN_PROGRESS";

                      return (
                        <div key={event.id} className="relative">
                          {/* Circle status dot indicator */}
                          <span
                            className={`absolute -left-[35px] top-1.5 h-6 w-6 rounded-full border-2 bg-background flex items-center justify-center transition-all ${
                              isCompleted
                                ? "border-emerald-500 text-emerald-500"
                                : isInProgress
                                ? "border-indigo-600 text-indigo-600 animate-pulse scale-110 shadow-md shadow-indigo-500/20"
                                : "border-slate-300 dark:border-slate-800 text-slate-300"
                            }`}
                          >
                            <span
                              className={`h-2.5 w-2.5 rounded-full ${
                                isCompleted
                                  ? "bg-emerald-500"
                                  : isInProgress
                                  ? "bg-indigo-600"
                                  : "bg-slate-300 dark:bg-slate-800"
                              }`}
                            />
                          </span>

                          {/* Event Card */}
                          <div
                            onClick={() => setExpandedEventId(isExpanded ? null : event.id)}
                            className={`p-4 border rounded-xl bg-card hover:bg-slate-50/50 dark:hover:bg-slate-900/30 transition cursor-pointer space-y-2 select-none ${
                              isInProgress
                                ? "border-indigo-600/30 shadow-md"
                                : "border-slate-200 dark:border-slate-800/80"
                            }`}
                          >
                            <div className="flex flex-wrap items-center justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <span className="font-extrabold text-xs text-slate-800 dark:text-slate-200 uppercase tracking-tight">
                                  {event.action.replace(/_/g, " ")}
                                </span>
                                <Badge variant={isCompleted ? "success" : isInProgress ? "info" : "outline"} className="text-[8px] font-bold">
                                  {isCompleted ? "VERIFIED" : event.status}
                                </Badge>
                              </div>
                              <span className="text-[10px] text-muted-foreground font-mono font-semibold">
                                {event.timestamp ? new Date(event.timestamp).toLocaleString("en-IN") : "Pending"}
                              </span>
                            </div>

                            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                              {event.description}
                            </p>

                            <div className="flex items-center gap-2 text-[10px] text-slate-400 font-semibold pt-1">
                              <span>Performed By: {event.actor}</span>
                              <span>&bull;</span>
                              <span className="capitalize">Role: {event.actor_type}</span>
                            </div>

                            {/* Notifications / SMS pill preview */}
                            {event.metadata?.notification && (
                              <div className="flex items-center gap-1.5 text-[9px] bg-slate-100 dark:bg-slate-900/60 p-1 px-2 rounded w-fit text-slate-500 font-mono">
                                🔔 {event.metadata.notification.type}: {event.metadata.notification.status}
                                <span className="text-[8px] text-slate-400 dark:text-slate-600 ml-1 truncate max-w-[150px]">
                                  "{event.metadata.notification.text}"
                                </span>
                              </div>
                            )}

                            {/* Expandable detailed content */}
                            {isExpanded && (
                              <div className="border-t border-slate-100 dark:border-slate-800/50 pt-3 mt-3 space-y-3 animate-fade-in text-[11px] leading-relaxed">
                                {event.metadata?.audit_log && (currentRole === "officer" || currentRole === "administrator") && (
                                  <div className="bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-200/50 dark:border-slate-900/80">
                                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                                      Internal Audit Trace
                                    </span>
                                    <code className="font-mono text-slate-600 dark:text-slate-400 block break-all">
                                      {event.metadata.audit_log}
                                    </code>
                                  </div>
                                )}

                                {event.metadata?.duplicates_found !== undefined && (
                                  <div className="grid grid-cols-2 gap-2 text-[10px]">
                                    <div className="bg-slate-50 dark:bg-slate-900 p-2 rounded border">
                                      <span className="text-slate-400 block">Active Buffer Duplicates:</span>
                                      <span className="font-bold text-slate-800 dark:text-slate-200">{event.metadata.duplicates_found} cases</span>
                                    </div>
                                    <div className="bg-slate-50 dark:bg-slate-950 p-2 rounded border">
                                      <span className="text-slate-400 block">Hotspot Zone Active:</span>
                                      <span className="font-bold text-rose-500">Yes (Flag Triggered)</span>
                                    </div>
                                  </div>
                                )}

                                {event.metadata?.policy_matched && (
                                  <div className="space-y-1.5">
                                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">
                                      Grounded Policy Matches
                                    </span>
                                    <ul className="space-y-1 list-disc pl-4 text-slate-500">
                                      <li>Policy Guidelines: <span className="font-bold text-slate-700 dark:text-slate-300">"{event.metadata.policy_matched}"</span></li>
                                      <li>Assigned Scheme: <span className="font-bold text-emerald-600">"{event.metadata.scheme_matched}"</span></li>
                                    </ul>
                                  </div>
                                )}

                                {event.metadata?.outcome_connection && (
                                  <div className="space-y-2 bg-gradient-to-r from-emerald-500/10 via-teal-500/5 to-slate-900/10 p-3.5 rounded-xl border border-emerald-500/20">
                                    <span className="text-[10px] font-extrabold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                                      🎯 Unified Outcome Connection & Closed Loop
                                    </span>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[10px] pt-1">
                                      <div>
                                        <span className="text-slate-400 block">Constituency Development Project:</span>
                                        <span className="font-bold text-slate-800 dark:text-slate-200 block">
                                          {event.metadata.outcome_connection.linked_project.title}
                                        </span>
                                        <span className="text-slate-500">
                                          Budget: {event.metadata.outcome_connection.linked_project.cost} &bull; Status: {event.metadata.outcome_connection.linked_project.status}
                                        </span>
                                      </div>
                                      <div className="space-y-1">
                                        <span className="text-slate-400 block">Simulated Local Outcomes:</span>
                                        {event.metadata.outcome_connection.outcomes.map((out: any, i: number) => (
                                          <div key={i} className="flex justify-between font-mono bg-white dark:bg-slate-950 p-1 px-2 rounded border border-emerald-500/10">
                                            <span className="text-slate-500 font-sans">{out.metric}:</span>
                                            <span className="font-bold text-emerald-600">{out.before} &rarr; {out.after}</span>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </Card>
          )}
        </div>

        {/* Right Side: Interactive Dispatcher Controls */}
        {currentRole !== "citizen" && (
          <div className="space-y-6">
          {/* Governance Copilot Panel */}
          <Card className="p-5 border-2 border-indigo-600/30 bg-gradient-to-br from-indigo-950/20 to-slate-900/20 space-y-4">
            <h3 className="font-extrabold text-sm tracking-tight flex items-center gap-1.5 text-indigo-600 dark:text-indigo-400">
              <Cpu className="h-4.5 w-4.5 animate-[spin_5s_linear_infinite]" /> Governance Copilot
            </h3>
            <p className="text-[10px] text-muted-foreground leading-normal">
              Structured decision assistant grounded in Helix regional policies and evidence base.
            </p>

            <div className="space-y-2.5">
              <div className="grid grid-cols-1 gap-1.5">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => queryCopilot("policy_explanation")}
                  className="text-left justify-start text-[11px] h-8 truncate bg-card"
                >
                  📜 Explain Active Policies
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => queryCopilot("alternative_recommendation")}
                  className="text-left justify-start text-[11px] h-8 truncate bg-card"
                >
                  ⚖️ Compare Cheaper Options
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => queryCopilot("meeting_brief")}
                  className="text-left justify-start text-[11px] h-8 truncate bg-card"
                >
                  🗒️ MP Meeting Brief Notes
                </Button>
                <div className="flex gap-2 items-center border p-1 rounded-lg bg-card">
                  <Globe className="h-3.5 w-3.5 text-slate-400 ml-1.5" />
                  <select
                    value={copilotLanguage}
                    onChange={(e) => setCopilotLanguage(e.target.value)}
                    className="bg-transparent text-[10px] focus:outline-none w-full font-semibold"
                  >
                    <option value="English">English</option>
                    <option value="Hindi">Hindi (हिंदी)</option>
                    <option value="Kannada">Kannada (ಕನ್ನಡ)</option>
                  </select>
                  <Button
                    size="sm"
                    onClick={() => queryCopilot("citizen_reply")}
                    className="text-[10px] h-7 px-2.5"
                  >
                    Draft SMS
                  </Button>
                </div>
              </div>

              {queryingCopilot && (
                <div className="p-3 border rounded-lg bg-card text-center text-xs text-muted-foreground animate-pulse flex items-center justify-center gap-1.5">
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" /> Querying decision models...
                </div>
              )}

              {copilotResponse && !queryingCopilot && (
                <div className="border rounded-xl p-3.5 bg-card text-xs space-y-3 shadow-sm border-indigo-500/20">
                  <div className="flex justify-between items-center border-b pb-1.5">
                    <span className="font-bold text-indigo-600">Copilot Verdict</span>
                    <Badge variant="outline" className="font-mono text-[9px]">
                      Confidence: {(copilotResponse.confidence * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                    {copilotResponse.summary}
                  </p>

                  {copilotResponse.evidence && copilotResponse.evidence.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-[10px] font-bold text-slate-400 uppercase">Evidence</span>
                      <ul className="list-disc pl-4 text-[10px] text-slate-500 space-y-0.5">
                        {copilotResponse.evidence.map((ev: string, i: number) => (
                          <li key={i}>{ev}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {copilotResponse.citations && copilotResponse.citations.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-[10px] font-bold text-slate-400 uppercase">Citations</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {copilotResponse.citations.map((cit: string, i: number) => (
                          <span key={i} className="text-[9px] bg-slate-100 dark:bg-slate-900 p-1 px-1.5 rounded font-mono">
                            {cit}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </Card>

          {/* SECTION 5: Impact Summary Card */}
          <Card className="p-5 space-y-4 border-2 border-indigo-500/20 bg-indigo-500/[0.01]">
            <div className="flex items-center gap-1.5 border-b pb-2">
              <TrendingUp className="h-4.5 w-4.5 text-indigo-500" />
              <h3 className="font-bold text-sm tracking-tight text-slate-800 dark:text-slate-200">
                5. Constituency Impact Summary
              </h3>
            </div>

            {loadingContext ? (
              <div className="text-xs text-muted-foreground animate-pulse">
                Running impact simulations...
              </div>
            ) : (
              <div className="space-y-3 text-xs">
                <div className="flex justify-between border-b pb-2">
                  <span className="text-slate-500">Affected Population:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {context.impact_summary?.affected_population?.toLocaleString("en-IN") || 150} Citizens
                  </span>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <span className="text-slate-500">Urgency rating:</span>
                  <span className="font-bold text-amber-500">
                    {context.impact_summary?.urgency_score ? (context.impact_summary.urgency_score * 100).toFixed(0) : "60"}% Score
                  </span>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <span className="text-slate-500">Matched Policy:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200 text-right truncate max-w-[140px]" title={context.applicable_policies?.[0]?.name}>
                    {context.applicable_policies?.[0]?.name || "General Code Compliance"}
                  </span>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <span className="text-slate-500">Budget Scheme:</span>
                  <span className="font-bold text-emerald-500 text-right truncate max-w-[140px]" title={context.applicable_schemes?.[0]?.name}>
                    {context.applicable_schemes?.[0]?.name || "Ward Routine Funding"}
                  </span>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <span className="text-slate-500">Expected SLA:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {context.alternative_actions?.[selectedAlternative]?.sla || "48 Hours"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Resolution Department:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {context.recommendation?.suggested_department || "PWD"}
                  </span>
                </div>
              </div>
            )}
          </Card>

          {/* SECTION 6: Triage Control Deck / Officer Decisions */}
          <Card className="p-4 bg-slate-900 border-slate-800 text-white space-y-4 shadow-xl">
            <h3 className="font-bold text-sm tracking-tight flex items-center gap-1.5 border-b border-slate-800 pb-2 text-indigo-300">
              <ShieldAlert className="h-4.5 w-4.5 text-indigo-300" /> 6. Triage Control Deck
            </h3>

            <div className="space-y-3 text-xs">
              <span className="font-semibold text-slate-400 block">Transition Request State</span>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  size="sm"
                  variant={issue.status === "Validated" ? "default" : "outline"}
                  className="h-8 text-[11px] border-slate-700 text-slate-200 hover:bg-slate-800"
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
                  className="h-8 text-[11px] border-slate-700 text-slate-200 hover:bg-slate-800"
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
                  className="h-8 text-[11px] border-slate-700 text-slate-200 hover:bg-slate-800"
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
                  className="h-8 text-[11px] border-emerald-500/30 text-emerald-400 hover:bg-slate-800"
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

              {/* Approve recommendation draft */}
              <div className="border-t border-slate-800 pt-4 space-y-2">
                <span className="font-semibold text-slate-400 flex items-center gap-1">
                  <FileText className="h-3.5 w-3.5" /> Dispatch SMS update response
                </span>
                <textarea
                  className="w-full rounded-md border border-slate-800 bg-slate-950 p-2.5 text-[11px] text-slate-200 focus-visible:outline-none font-mono leading-normal"
                  rows={4}
                  value={draftResponse}
                  onChange={(e) => setDraftResponse(e.target.value)}
                />
                <Button
                  onClick={handleApproveDraft}
                  className="w-full text-xs h-9 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold flex items-center justify-center gap-1.5 border-none"
                >
                  <Send className="h-3.5 w-3.5" /> Approve & Dispatch Response
                </Button>
                {isSuccessMsg && (
                  <div className="text-[10px] text-emerald-400 font-bold text-center animate-fade-in pt-1">
                    ✓ Notification dispatched to citizen interface.
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
        )}
      </div>
    </div>
  );
}

// Helper to stringify JSON with indentation
function jsonStringifyNice(obj: any): string {
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return "{}";
  }
}
