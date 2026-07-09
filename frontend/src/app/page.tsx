"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { ShieldAlert, Users, Compass, BarChart3, Settings, Sparkles, ArrowRight, Activity, Map } from "lucide-react";

export default function Home() {
  const { user, role, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && user) {
      if (role === "Citizen") router.push("/citizen");
      else if (role === "Officer") router.push("/officer");
      else if (role === "System Administrator" || role === "Platform Administrator") router.push("/settings");
      else router.push("/analytics");
    }
  }, [user, role, isLoading, router]);

  if (isLoading || user) {
    return null; // Don't flash landing page while redirecting
  }

  return (
    <div className="space-y-16 max-w-6xl mx-auto py-12 px-4 animate-fade-in">
      {/* Hero Header */}
      <section className="text-center space-y-6 max-w-4xl mx-auto mt-8">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/20 bg-primary/5 text-primary text-xs sm:text-sm font-bold uppercase tracking-wider animate-pulse">
          <Sparkles className="h-4 w-4" /> Next-Gen Event-Driven Governance
        </div>
        <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight bg-gradient-to-r from-primary via-purple-500 to-indigo-500 bg-clip-text text-transparent leading-[1.1] py-2">
          Helix Operations Portal
        </h1>
        <p className="text-muted-foreground text-base sm:text-lg md:text-xl max-w-3xl mx-auto leading-relaxed font-medium">
          A secure, transparent, event-driven governance system. We connect citizens directly to field operations using spatial intelligence and AI-driven decision support for smarter cities.
        </p>
        <div className="pt-6 flex flex-col items-center justify-center gap-4">
          <div className="flex gap-4">
            <Link href="/login">
              <button className="h-12 px-8 rounded-lg bg-primary text-primary-foreground text-sm font-bold hover:bg-primary/95 transition-all shadow-md group/btn flex items-center gap-2">
                Login to Access <ArrowRight className="h-4 w-4 group-hover/btn:translate-x-1 transition-transform" />
              </button>
            </Link>
            <Link href="/register">
              <button className="h-12 px-8 rounded-lg bg-secondary text-secondary-foreground text-sm font-bold hover:bg-secondary/80 transition-all border shadow-sm flex items-center gap-2">
                Register Account
              </button>
            </Link>
          </div>
          <p className="text-xs text-muted-foreground mt-4 max-w-lg">
            Note: New registered accounts are considered as "Citizen" unless approved by the System Administrator.
            For testing, you may use the following pre-configured dummy credentials:
            <br/><br/>
            <strong>MLA:</strong> mla@gov.ai / Password <br/>
            <strong>System Admin:</strong> system@gov.ai / System123
          </p>
        </div>
      </section>

      {/* Highlights Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-12">
        <Card className="p-8 border-slate-200 dark:border-slate-800 bg-card/50 backdrop-blur">
          <div className="h-12 w-12 rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center mb-6">
            <Map className="h-6 w-6" />
          </div>
          <h3 className="text-xl font-bold mb-3">Spatial Intelligence</h3>
          <p className="text-muted-foreground leading-relaxed">
            Real-time GIS integration maps public issues instantly, identifying hotspots and optimizing field deployment routing.
          </p>
        </Card>

        <Card className="p-8 border-slate-200 dark:border-slate-800 bg-card/50 backdrop-blur">
          <div className="h-12 w-12 rounded-xl bg-purple-500/10 text-purple-500 flex items-center justify-center mb-6">
            <Activity className="h-6 w-6" />
          </div>
          <h3 className="text-xl font-bold mb-3">Live Operations</h3>
          <p className="text-muted-foreground leading-relaxed">
            Every ticket is tracked with SLAs, providing live status updates directly to citizens and analytical dashboards for officials.
          </p>
        </Card>

        <Card className="p-8 border-slate-200 dark:border-slate-800 bg-card/50 backdrop-blur">
          <div className="h-12 w-12 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center mb-6">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <h3 className="text-xl font-bold mb-3">AI Decision Support</h3>
          <p className="text-muted-foreground leading-relaxed">
            Automated recommendations help officers triage and assign resources effectively, cutting down response times by over 40%.
          </p>
        </Card>
      </section>
    </div>
  );
}
