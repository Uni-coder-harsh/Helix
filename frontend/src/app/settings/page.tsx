"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { API_BASE_URL } from "@/config";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ToggleLeft, ToggleRight, Shield, Cpu, RefreshCw, Layers, CheckCircle } from "lucide-react";

export default function SettingsPage() {
  const [apiDelay, setApiDelay] = useState(true);
  const [autoTriage, setAutoTriage] = useState(false);
  const [whatsappNotify, setWhatsappNotify] = useState(true);
  const [emailNotify, setEmailNotify] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const { user, role, token } = useAuth();
  const [roleRequests, setRoleRequests] = useState([]);
  const [requestedRole, setRequestedRole] = useState("Officer");
  const [myRequests, setMyRequests] = useState([]);

  useEffect(() => {
    if (token) {
      fetchRequests();
    }
  }, [token]);

  const fetchRequests = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/identity/role-change-requests`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (role === "System Administrator") setRoleRequests(data);
        else setMyRequests(data);
      }
    } catch(e) {}
  };

  const handleRequestRole = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/identity/role-change-requests`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ requested_role: requestedRole })
      });
      if (res.ok) fetchRequests();
    } catch (e) {}
  };

  const handleApprove = async (id) => {
    try {
      const res = await fetch(`${API_BASE_URL}/identity/role-change-requests/${id}/approve`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) fetchRequests();
    } catch (e) {}
  };


  const handleSave = () => {
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2500);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings & Admin Console</h1>
        <p className="text-xs text-muted-foreground">Manage connector runtimes, AI validation parameters, and dashboard mock latency profiles.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Core Configurations */}
        <div className="md:col-span-2 space-y-6">
          <Card className="p-6">
            <h3 className="font-bold text-sm mb-4 tracking-tight">Engine Simulation & Latency Settings</h3>
            <div className="space-y-4">
              {/* Setting 1: Mock Latency */}
              <div className="flex items-center justify-between border-b pb-3">
                <div className="space-y-0.5">
                  <div className="font-semibold text-xs text-slate-800 dark:text-slate-200">Simulated Network Latency</div>
                  <p className="text-[10px] text-muted-foreground">Introduces a 500ms delay on dispatch operations to simulate remote servers.</p>
                </div>
                <button onClick={() => setApiDelay(!apiDelay)} className="text-primary focus:outline-none">
                  {apiDelay ? <ToggleRight className="h-9 w-9" /> : <ToggleLeft className="h-9 w-9 text-slate-400" />}
                </button>
              </div>

              {/* Setting 2: Auto Triage */}
              <div className="flex items-center justify-between border-b pb-3">
                <div className="space-y-0.5">
                  <div className="font-semibold text-xs text-slate-800 dark:text-slate-200">AI Auto-Triage Dispatch</div>
                  <p className="text-[10px] text-muted-foreground">Automatically dispatches verified issues with upvote score &gt; 100 without officer queue check.</p>
                </div>
                <button onClick={() => setAutoTriage(!autoTriage)} className="text-primary focus:outline-none">
                  {autoTriage ? <ToggleRight className="h-9 w-9" /> : <ToggleLeft className="h-9 w-9 text-slate-400" />}
                </button>
              </div>

              {/* Setting 3: WhatsApp Notification */}
              <div className="flex items-center justify-between border-b pb-3">
                <div className="space-y-0.5">
                  <div className="font-semibold text-xs text-slate-800 dark:text-slate-200">WhatsApp Alert Dispatcher (CON-004)</div>
                  <p className="text-[10px] text-muted-foreground">Sends outbound progress webhook templates to citizens when status shifts.</p>
                </div>
                <button onClick={() => setWhatsappNotify(!whatsappNotify)} className="text-primary focus:outline-none">
                  {whatsappNotify ? <ToggleRight className="h-9 w-9" /> : <ToggleLeft className="h-9 w-9 text-slate-400" />}
                </button>
              </div>

              {/* Setting 4: Email Notification */}
              <div className="flex items-center justify-between pb-3">
                <div className="space-y-0.5">
                  <div className="font-semibold text-xs text-slate-800 dark:text-slate-200">Email digest dispatch (CON-006)</div>
                  <p className="text-[10px] text-muted-foreground">Dispatches weekly summary logs to the respective ward MLAs and ward councilors.</p>
                </div>
                <button onClick={() => setEmailNotify(!emailNotify)} className="text-primary focus:outline-none">
                  {emailNotify ? <ToggleRight className="h-9 w-9" /> : <ToggleLeft className="h-9 w-9 text-slate-400" />}
                </button>
              </div>
            </div>

            <div className="pt-4 border-t flex items-center justify-between gap-4">
              <Button onClick={handleSave} className="bg-primary text-primary-foreground text-xs h-9 font-semibold px-6 shadow">
                Save Simulation Configurations
              </Button>
              {isSaved && (
                <span className="text-xs text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-1">
                  <CheckCircle className="h-4 w-4" /> System parameters updated.
                </span>
              )}
            </div>
          </Card>

          {/* System Info */}
          <Card className="p-6">
            <h3 className="font-bold text-sm mb-4 tracking-tight">Helix Architectural Alignment</h3>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="border p-3 rounded-lg">
                <div className="text-[10px] text-slate-400 font-semibold uppercase">Microservice Spec ID</div>
                <div className="font-bold font-mono mt-1 text-indigo-600 dark:text-indigo-400">HELIX-ARCH-007</div>
              </div>
              <div className="border p-3 rounded-lg">
                <div className="text-[10px] text-slate-400 font-semibold uppercase">Shared Value Schema</div>
                <div className="font-bold font-mono mt-1">v1.0.0 (Modular Monolith)</div>
              </div>
            </div>
          </Card>

          {/* Admin Role Approval UI */}
          {role === "System Administrator" && (
            <Card className="p-6 mt-6">
              <h3 className="font-bold text-sm mb-4 tracking-tight">Pending Role Change Requests</h3>
              <div className="space-y-4">
                {roleRequests.length === 0 && <p className="text-xs text-muted-foreground">No pending requests.</p>}
                {roleRequests.map((req) => (
                  <div key={req.id} className="flex items-center justify-between border-b pb-3">
                    <div className="space-y-0.5">
                      <div className="font-semibold text-xs text-slate-800 dark:text-slate-200">User ID: {req.user_id}</div>
                      <p className="text-[10px] text-muted-foreground">Requested Role: {req.requested_role}</p>
                    </div>
                    <Button onClick={() => handleApprove(req.id)} size="sm" className="h-7 text-[10px]">Approve</Button>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Normal User Role Request UI */}
          {role !== "System Administrator" && (
            <Card className="p-6 mt-6">
              <h3 className="font-bold text-sm mb-4 tracking-tight">Request Role Change</h3>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <select
                    value={requestedRole}
                    onChange={e => setRequestedRole(e.target.value)}
                    className="text-sm border rounded p-1"
                  >
                    <option value="Officer">Officer</option>
                    <option value="MLA">MLA</option>
                    <option value="MP">MP</option>
                  </select>
                  <Button onClick={handleRequestRole} size="sm">Submit Request</Button>
                </div>
                {myRequests.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-bold text-xs mb-2">My Requests:</h4>
                    {myRequests.map(req => (
                      <div key={req.id} className="text-xs">
                        Requested: {req.requested_role} - Status: {req.status}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          )}
</div>

        {/* Plugin and Security Adapters */}
        <div className="space-y-6">
          <Card className="p-4 space-y-4">
            <h4 className="font-bold text-xs flex items-center gap-1.5"><Layers className="h-4 w-4 text-indigo-500" /> Active Plugin Runtime</h4>
            <div className="space-y-3">
              <div className="border p-2.5 rounded-lg flex items-center justify-between text-xs">
                <div className="space-y-0.5">
                  <span className="font-bold">WhatsApp Connector</span>
                  <p className="text-[9px] text-muted-foreground font-mono">CON-004 &bull; v1.2</p>
                </div>
                <Badge variant="success">Active</Badge>
              </div>
              <div className="border p-2.5 rounded-lg flex items-center justify-between text-xs">
                <div className="space-y-0.5">
                  <span className="font-bold">SMS Connector</span>
                  <p className="text-[9px] text-muted-foreground font-mono">CON-005 &bull; v1.0</p>
                </div>
                <Badge variant="success">Active</Badge>
              </div>
              <div className="border p-2.5 rounded-lg flex items-center justify-between text-xs">
                <div className="space-y-0.5">
                  <span className="font-bold">Email Connector</span>
                  <p className="text-[9px] text-muted-foreground font-mono">CON-006 &bull; v1.4</p>
                </div>
                <Badge variant="success">Active</Badge>
              </div>
            </div>
          </Card>

          <Card className="p-4 space-y-2 text-xs">
            <h4 className="font-bold text-xs flex items-center gap-1.5"><Shield className="h-4 w-4 text-emerald-500" /> Identity Authority</h4>
            <p className="text-slate-500 leading-normal">
              Authentication and role validation managed by Helix Identity Service bounded context. Role constraints are mapped directly to municipal trust zones.
            </p>
            <div className="pt-2">
              <span className="text-[10px] text-slate-400 font-semibold uppercase">Current Role Matrix:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                <Badge variant="secondary">Officer</Badge>
                <Badge variant="secondary">Citizen</Badge>
                <Badge variant="secondary">Field Crew</Badge>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
