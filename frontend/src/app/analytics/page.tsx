import React from "react";
import { ChartsPlaceholder } from "@/components/charts-placeholder";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { BarChart3, TrendingUp, Users } from "lucide-react";

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Decision Intelligence Center</h1>
        <p className="text-xs text-muted-foreground">Analytical logs, Service Level Agreement (SLA) conformance, and ward resolution metrics.</p>
      </div>

      <ChartsPlaceholder />

      {/* SLA audit callouts */}
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
    </div>
  );
}
