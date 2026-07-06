"use client";

import React, { useState, useEffect } from "react";
import { mockIssues, Issue, IssueUpdate } from "@/lib/mock-data";
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
} from "lucide-react";

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

            // Fetch AI Pipeline
            fetch(`http://localhost:8000/governance/issues/${found.id}/decision-pipeline`)
              .then((r) => r.json())
              .then((pipe) => {
                setPipeline(pipe);
                setLoadingPipeline(false);
              })
              .catch((err) => {
                console.log("Failed to fetch pipeline, using fallback:", err);
                loadFallbackPipeline(mapped);
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
        loadFallbackPipeline(found);
      }
    }
  }, [params.id]);

  const loadFallbackContext = (issueData: Issue) => {
    const isSanitation =
      issueData.category.toLowerCase().includes("sanit") ||
      issueData.category.toLowerCase().includes("water");
    setContext({
      priority: isSanitation ? "HIGH" : "MEDIUM",
      affected_population: isSanitation ? 4320 : 350,
      estimated_impact: isSanitation ? "HIGH" : "MEDIUM",
      supporting_evidence: isSanitation
        ? [
            "Municipal Asset Proximity: Ward 12 Playground Garbage Bin Terminal",
            "Linked Municipal Scheme: Swachh Bharat Abhiyan Subsidy",
            "Enforced Regulation: Sanitation Waste Management Regulation 2024",
          ]
        : [
            "Municipal Asset Proximity: Main School Zone Arterial Road Sector 4",
            "Linked Municipal Scheme: PMGSY Road Infrastructure Upgrade Program",
            "Enforced Regulation: Municipal Road Maintenance Policy 2023",
          ],
      confidence: 0.96,
      reasoning_chain: isSanitation
        ? "1. Intake categorized issue as 'sanitation'.\n2. Evaluated geo-spatial proximity; matched 3 evidence points.\n3. Determined urgency score: 0.90 and impact scale: HIGH.\n4. Policy Evaluation: Aligned with 'Sanitation Waste Management Regulation 2024'.\n5. Recommended dispatch to Municipal Sanitation Department with SLA of 24 hours."
        : "1. Intake categorized issue as 'roads'.\n2. Evaluated geo-spatial proximity; matched 3 evidence points.\n3. Determined urgency score: 0.70 and impact scale: HIGH.\n4. Policy Evaluation: Aligned with 'Municipal Road Maintenance Policy 2023'.\n5. Recommended dispatch to Public Works Department with SLA of 48 hours.",
      alternative_actions: [
        {
          title: "Accelerated Dispatch (Recommended)",
          cost: "₹2.5 Lakhs",
          sla: isSanitation ? "24 Hours" : "48 Hours",
          impact: "SLA Compliant",
          risk: "Low Risk",
          desc: "Allocate internal ward maintenance crew under active constituency budget.",
        },
        {
          title: "Private Vendor Contractor Outsource",
          cost: "₹8.0 Lakhs",
          sla: isSanitation ? "12 Hours" : "24 Hours",
          impact: "Immediate Triage",
          risk: "Medium Budget Overrun",
          desc: "Hire third-party contractor. Accelerated timeline at premium cost.",
        },
        {
          title: "Defer to Routine Cycle",
          cost: "₹0 (Scheduled)",
          sla: "15 Days",
          impact: "SLA Breach",
          risk: "High Public Complaint Risk",
          desc: "Schedule with monthly sweeping tasks. Breaches local priority SLA.",
        },
      ],
      suggested_department: isSanitation
        ? "Municipal Sanitation Department"
        : "Public Works Department",
      expected_outcome: isSanitation
        ? "Restores sanitary conditions, prevents public health hazards, and maintains cleanliness in ward public play areas."
        : "Improves vehicle traffic throughput and eliminates pedestrian safety hazards.",
      budget_scheme: isSanitation ? "Swachh Bharat Abhiyan Subsidy" : "PMGSY Roads Fund",
    });
    setLoadingContext(false);
  };

  const loadFallbackPipeline = (issueData: Issue) => {
    const isSanit =
      issueData.category.toLowerCase().includes("sanit") ||
      issueData.category.toLowerCase().includes("water");
    setPipeline({
      pipeline_id: "simulated-pipeline-id-1049",
      overall_status: "SUCCESS",
      total_latency_ms: 472.0,
      average_confidence: 0.96,
      timeline: [
        {
          agent_name: "Intake Agent",
          status: "SUCCESS",
          confidence: 1.0,
          execution_time_ms: 12.0,
          inputs: { description: issueData.description.substring(0, 30) },
          outputs: { sanitized_description: issueData.description },
          evidence: ["Description satisfies minimum ingestion formats.", "Valid regional GPS coords."],
          warnings: [],
          errors: [],
        },
        {
          agent_name: "Classification Agent",
          status: "SUCCESS",
          confidence: 0.97,
          execution_time_ms: 92.0,
          inputs: { description_sample: issueData.description.substring(0, 40) },
          outputs: { category: isSanit ? "Water Supply & Sanitation" : "Roads & Sidewalks" },
          evidence: [
            isSanit
              ? "Matched keyword 'water' / 'leak' inside description text."
              : "Matched keyword 'road' / 'pothole' inside description text.",
          ],
          warnings: [],
          errors: [],
        },
        {
          agent_name: "Duplicate Agent",
          status: "SUCCESS",
          confidence: 0.98,
          execution_time_ms: 140.0,
          inputs: { latitude: issueData.location?.lat, longitude: issueData.location?.lng },
          outputs: { duplicate_count: isSanit ? 18 : 6 },
          evidence: [
            isSanit
              ? "18 duplicate complaints detected in शिवाजी नगर region."
              : "6 duplicate complaints detected in region Sector 4.",
          ],
          warnings: isSanit ? ["High duplicate complaints density; active hotspot warned."] : [],
          errors: [],
        },
        {
          agent_name: "Context Agent",
          status: "SUCCESS",
          confidence: 0.96,
          execution_time_ms: 60.0,
          inputs: { lat: issueData.location?.lat, lng: issueData.location?.lng },
          outputs: {
            nearby_assets: isSanit
              ? ["Ward 12 Playground Garbage Bin Terminal", "Govt School Block A"]
              : ["Main School Zone Arterial Road Sector 4", "Regional Transit Bus Hub"],
          },
          evidence: ["2 critical civic assets matched within regional buffer radius."],
          warnings: [],
          errors: [],
        },
        {
          agent_name: "Policy Agent",
          status: "SUCCESS",
          confidence: 0.94,
          execution_time_ms: 50.0,
          inputs: { category: isSanit ? "Water Supply & Sanitation" : "Roads & Sidewalks" },
          outputs: {
            matched_policy: isSanit
              ? "Sanitation Waste Management Regulation 2024"
              : "Municipal Road Maintenance Policy 2023",
            matched_scheme: isSanit ? "Swachh Bharat Abhiyan Subsidy" : "PMGSY Roads Fund",
          },
          evidence: ["Fund eligibility verified against local administration parameters."],
          warnings: [],
          errors: [],
        },
        {
          agent_name: "Impact Agent",
          status: "SUCCESS",
          confidence: 0.95,
          execution_time_ms: 68.0,
          inputs: { duplicates: isSanit ? 18 : 6 },
          outputs: {
            affected_population: isSanit ? 4320 : 350,
            urgency_score: isSanit ? 0.90 : 0.70,
            priority: isSanit ? "HIGH" : "MEDIUM",
          },
          evidence: [
            isSanit
              ? "Emergency ambulance route. Impact weight sets priority to HIGH."
              : "Standard arterial road. Impact weight sets priority to MEDIUM.",
          ],
          warnings: [],
          errors: [],
        },
        {
          agent_name: "Recommendation Agent",
          status: "SUCCESS",
          confidence: 0.96,
          execution_time_ms: 50.0,
          inputs: { priority: isSanit ? "HIGH" : "MEDIUM" },
          outputs: {
            suggested_department: isSanit ? "Municipal Sanitation Department" : "Public Works Department",
            recommended_action: isSanit
              ? "Dispatch Emergency Sanitation Leak Clearing Crew"
              : "Dispatch Road Restoration Patch Crew",
            sla: isSanit ? "24 Hours" : "48 Hours",
          },
          evidence: ["Assigned department owns SLA resolution guidelines."],
          warnings: [],
          errors: [],
        },
      ],
    });
    setLoadingPipeline(false);
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

  // Trigger Governance Copilot APIs
  const queryCopilot = async (action: string) => {
    setQueryingCopilot(true);
    try {
      const res = await fetch("http://localhost:8000/governance/copilot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action,
          issue_id: issue.id,
          query_details: { language: copilotLanguage },
        }),
      });
      const data = await res.json();
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
          "Constituency Review Brief: 18 pending tickets in Shivaji Nagar W12. Heavy backlog in PWD road patch operations due to recent utility pipeline excavations.";
        evidence = ["Active backlogs: 8 days behind schedule.", "Recommended: Allocate ₹18L contingency funds."];
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
        <div className="text-xs text-muted-foreground font-semibold">
          Status:{" "}
          <Badge variant="outline" className="ml-1 font-mono text-[10px]">
            {issue.status}
          </Badge>
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
          Audit Ledger
        </button>
      </div>

      {/* Main Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Columns (2/3 width) - Swapped based on tab selection */}
        <div className="lg:col-span-2 space-y-6">
          {leftTab === "brief" && (
            <div className="space-y-6">
              {/* SECTION 1: Problem Definition */}
              <Card className="p-5 space-y-4">
                <div className="border-l-4 border-indigo-500 pl-3">
                  <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                    <FileText className="h-4.5 w-4.5 text-indigo-500" /> 1. Problem Definition
                  </h3>
                </div>
                <div className="space-y-2 text-xs leading-relaxed">
                  <p className="font-semibold text-slate-800 dark:text-slate-200">Incident Details:</p>
                  <p className="text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900/30 p-3.5 rounded-lg border">
                    {issue.description}
                  </p>
                </div>
              </Card>

              {/* SECTION 2: Evidence Panel Card Grid */}
              <Card className="p-5 space-y-4">
                <div className="border-l-4 border-indigo-500 pl-3">
                  <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                    <Eye className="h-4.5 w-4.5 text-indigo-500" /> 2. Grounded Evidence Grid
                  </h3>
                </div>
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
                      <span className="text-3xl font-extrabold text-indigo-500">18</span>
                      <span className="text-[10px] text-slate-400 font-medium">complaints in ward</span>
                    </div>
                    <span className="text-[9px] text-emerald-500 font-semibold flex items-center gap-0.5">
                      <TrendingUp className="h-3 w-3" /> Area Hotspot Detected
                    </span>
                  </div>
                  {/* Card 3: GIS Coordinates */}
                  <div className="border p-3.5 rounded-xl bg-card flex flex-col justify-between min-h-[110px]">
                    <span className="text-[10px] text-muted-foreground font-semibold uppercase">
                      GIS Mapping
                    </span>
                    <div className="font-mono text-[10px] mt-1 space-y-1">
                      <div>LAT: {issue.location.lat.toFixed(4)}</div>
                      <div>LNG: {issue.location.lng.toFixed(4)}</div>
                    </div>
                    <Badge variant="outline" className="text-[8px] justify-center mt-2 font-mono">
                      {" "}
                      Shivaji Nagar W12
                    </Badge>
                  </div>
                </div>
              </Card>

              {/* SECTION 3: Explainability Tree */}
              <Card className="p-5 space-y-4">
                <div className="border-l-4 border-indigo-500 pl-3">
                  <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                    <ShieldAlert className="h-4.5 w-4.5 text-indigo-500" /> 3. Explainability Tree
                  </h3>
                </div>

                {loadingContext ? (
                  <div className="text-xs text-muted-foreground animate-pulse">
                    Running reasoning diagnostics...
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="border rounded-xl p-4 bg-slate-50 dark:bg-slate-900/50 flex flex-col space-y-3 relative overflow-hidden">
                      <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
                        <div className="border p-2.5 rounded-lg bg-card w-full md:w-auto text-center font-bold text-indigo-500 border-indigo-500/20">
                          Category: {issue.category}
                        </div>
                        <div className="text-slate-400 font-bold hidden md:block">→</div>
                        <div className="border p-2.5 rounded-lg bg-card w-full md:w-auto text-center font-bold text-amber-500 border-amber-500/20">
                          Nearby School/Depot (Evidence Match)
                        </div>
                        <div className="text-slate-400 font-bold hidden md:block">→</div>
                        <div className="border p-2.5 rounded-lg bg-card w-full md:w-auto text-center font-bold text-red-500 border-red-500/20">
                          Priority Level: {context.priority}
                        </div>
                      </div>

                      <div className="border-t pt-3 font-mono text-[11px] text-slate-500 leading-relaxed whitespace-pre-line bg-card p-3 rounded-lg border">
                        {context.reasoning_chain}
                      </div>
                    </div>
                  </div>
                )}
              </Card>

              {/* SECTION 4: Recommendation & Alternatives Comparison */}
              <Card className="p-5 space-y-4">
                <div className="border-l-4 border-indigo-500 pl-3">
                  <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                    <Layers className="h-4.5 w-4.5 text-indigo-500" /> 4. Recommendation Comparison Matrix
                  </h3>
                </div>
                {loadingContext ? (
                  <div className="text-xs text-muted-foreground animate-pulse">
                    Loading alternative action models...
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="overflow-x-auto rounded-xl border bg-card text-xs">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="border-b bg-slate-50 dark:bg-slate-900/50 font-semibold text-slate-500">
                            <th className="p-3">Option</th>
                            <th className="p-3">Estimated Cost</th>
                            <th className="p-3">Timeline (SLA)</th>
                            <th className="p-3">Impact</th>
                            <th className="p-3">Risk Assessment</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y font-medium">
                          {context.alternative_actions.map((alt: any, idx: number) => (
                            <tr
                              key={idx}
                              onClick={() => setSelectedAlternative(idx)}
                              className={`cursor-pointer hover:bg-slate-50/50 dark:hover:bg-slate-900/30 transition ${
                                selectedAlternative === idx ? "bg-indigo-500/5 text-indigo-600 font-bold" : ""
                              }`}
                            >
                              <td className="p-3">{alt.title}</td>
                              <td className="p-3">{alt.cost}</td>
                              <td className="p-3">{alt.sla}</td>
                              <td className="p-3">{alt.impact}</td>
                              <td className="p-3 text-slate-400">{alt.risk}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <div className="border p-3.5 rounded-lg bg-indigo-500/[0.02] border-indigo-500/20 text-xs">
                      <span className="font-bold text-indigo-600 block mb-1">
                        Selected Path: {context.alternative_actions[selectedAlternative].title}
                      </span>
                      <p className="text-muted-foreground leading-normal">
                        {context.alternative_actions[selectedAlternative].desc}
                      </p>
                    </div>
                  </div>
                )}
              </Card>
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
          {leftTab === "audit" && (
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
          )}
        </div>

        {/* Right Side: Interactive Dispatcher Controls */}
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
                    {context.affected_population.toLocaleString("en-IN")} Citizens
                  </span>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <span className="text-slate-500">Nearby Civic Assets:</span>
                  <span className="font-bold text-indigo-500">Playground & School Zone</span>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <span className="text-slate-500">Budget Scheme:</span>
                  <span className="font-bold text-emerald-500">{context.budget_scheme}</span>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <span className="text-slate-500">Expected SLA:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {context.alternative_actions[selectedAlternative].sla}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Resolution Department:</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    {context.suggested_department}
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
