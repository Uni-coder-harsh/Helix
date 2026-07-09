"use client";

import React, { useState, useEffect } from "react";
import { fetchWithAuth } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { TrendingUp, Users, AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function AnalyticsPage() {
  const [issues, setIssues] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWithAuth("/governance/issues/pending")
      .then((data) => {
        if (Array.isArray(data)) {
          setIssues(data);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch pending issues:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Decision Intelligence Center</h1>
        <p className="text-xs text-muted-foreground">Analytical logs, Service Level Agreement (SLA) conformance, and ward resolution metrics.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-4 flex gap-4">
          <div className="p-3 bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 rounded-xl h-fit">
            <TrendingUp className="h-6 w-6" />
          </div>
          <div className="space-y-1">
            <h4 className="font-bold text-sm">Resolution Velocity Index</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-normal">
              Municipal response latencies dropped by 18% following the activation of the AI validation pipeline. The average triage phase now completes in 12 minutes, down from 2.4 hours.
            </p>
          </div>
        </Card>
        <Card className="p-4 flex gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-xl h-fit">
            <Users className="h-6 w-6" />
          </div>
          <div className="space-y-1">
            <h4 className="font-bold text-sm">Citizen Engagement Coefficients</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-normal">
              Active citizen upvoting patterns indicate high civic consensus on roads and drainage categories. Issues with more than 50 upvotes are prioritised dynamically in the officer queues.
            </p>
          </div>
        </Card>
      </div>

      <Card className="p-6">
        <h3 className="font-bold text-sm mb-4 tracking-tight flex items-center gap-2">
          <AlertCircle className="h-4 w-4" /> Reported Issues Overview
        </h3>
        {loading ? (
          <p className="text-xs text-muted-foreground">Loading issues...</p>
        ) : issues.length === 0 ? (
          <p className="text-xs text-muted-foreground">No issues reported yet.</p>
        ) : (
          <div className="space-y-4">
            {issues.map(issue => (
              <div key={issue.id} className="border-b pb-4 last:border-0 last:pb-0">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-sm">{issue.title}</h4>
                  <Badge variant={issue.status === "COMPLETED" ? "success" : "secondary"}>
                    {issue.status}
                  </Badge>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400">{issue.description}</p>
                <div className="text-[10px] text-muted-foreground mt-2 flex gap-4">
                  <span>Category: {issue.category}</span>
                  <span>Priority: {issue.priority}</span>
                  <span>Reported: {new Date(issue.created_at || Date.now()).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
