import React from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { ShieldAlert, Users, Compass, BarChart3, Settings, Sparkles, ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <div className="space-y-12 max-w-5xl mx-auto py-8 px-2 animate-fade-in">
      {/* Hero Welcome Header */}
      <section className="text-center space-y-5 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/20 bg-primary/5 text-primary text-[10px] sm:text-xs font-bold uppercase tracking-wider animate-pulse">
          <Sparkles className="h-3.5 w-3.5" /> Event-Driven Municipal Management
        </div>
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-primary via-purple-500 to-indigo-500 bg-clip-text text-transparent leading-none py-1">
          Helix Operations Portal
        </h1>
        <p className="text-muted-foreground text-xs sm:text-sm md:text-base max-w-2xl mx-auto leading-relaxed font-medium">
          The next-generation urban governance ecosystem. Securely connecting citizens, field operators, and AI validation layers to drive high-performance city outcomes.
        </p>
      </section>

      {/* Main Portals Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card className="p-6 sm:p-8 relative overflow-hidden group hover:border-primary/50 transition-all duration-300 shadow-sm hover:shadow-lg bg-card">
          <div className="absolute top-0 right-0 h-40 w-40 bg-primary/10 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-primary/15 transition-all duration-500" />
          <CardHeader className="p-0 mb-5 relative">
            <div className="h-12 w-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center mb-4 border border-primary/20 shadow-sm">
              <ShieldAlert className="h-6 w-6" />
            </div>
            <CardTitle className="text-xl sm:text-2xl font-bold tracking-tight">Officer Console</CardTitle>
            <CardDescription className="text-xs sm:text-sm font-medium mt-1 leading-normal text-slate-500">
              Secure portal for government administrators, ward officers, and municipal dispatchers.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0 space-y-6 relative">
            <ul className="text-xs sm:text-sm space-y-3 font-medium text-slate-600 dark:text-slate-400">
              <li className="flex items-center gap-2.5">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Triage incoming reports verified by AI layers
              </li>
              <li className="flex items-center gap-2.5">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Dispatch tasks to specific ward engineering teams
              </li>
              <li className="flex items-center gap-2.5">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Edit and approve AI-generated citizen responses
              </li>
            </ul>
            <Link href="/officer" className="block pt-2">
              <button className="w-full h-10 inline-flex items-center justify-center rounded-lg bg-primary text-primary-foreground text-xs sm:text-sm font-bold hover:bg-primary/95 transition-all shadow-sm gap-1.5 group/btn">
                Access Officer Workspace <ArrowRight className="h-4 w-4 group-hover/btn:translate-x-0.5 transition-transform" />
              </button>
            </Link>
          </CardContent>
        </Card>

        <Card className="p-6 sm:p-8 relative overflow-hidden group hover:border-purple-500/50 transition-all duration-300 shadow-sm hover:shadow-lg bg-card">
          <div className="absolute top-0 right-0 h-40 w-40 bg-purple-500/10 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-purple-500/15 transition-all duration-500" />
          <CardHeader className="p-0 mb-5 relative">
            <div className="h-12 w-12 rounded-xl bg-purple-500/10 text-purple-650 dark:text-purple-400 flex items-center justify-center mb-4 border border-purple-500/20 shadow-sm">
              <Users className="h-6 w-6" />
            </div>
            <CardTitle className="text-xl sm:text-2xl font-bold tracking-tight">Citizen Hub</CardTitle>
            <CardDescription className="text-xs sm:text-sm font-medium mt-1 leading-normal text-slate-500">
              Public transparency interface for residents to lodge reports and track live work progress.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0 space-y-6 relative">
            <ul className="text-xs sm:text-sm space-y-3 font-medium text-slate-600 dark:text-slate-400">
              <li className="flex items-center gap-2.5">
                <span className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                Log issues with detailed coordinates and image proofs
              </li>
              <li className="flex items-center gap-2.5">
                <span className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                Upvote shared concerns to highlight collective urgency
              </li>
              <li className="flex items-center gap-2.5">
                <span className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                Track live status updates from dispatchers in real-time
              </li>
            </ul>
            <Link href="/citizen" className="block pt-2">
              <button className="w-full h-10 inline-flex items-center justify-center rounded-lg bg-secondary text-secondary-foreground text-xs sm:text-sm font-bold hover:bg-secondary/80 transition-all border shadow-sm gap-1.5 group/btn">
                Access Citizen Workspace <ArrowRight className="h-4 w-4 group-hover/btn:translate-x-0.5 transition-transform" />
              </button>
            </Link>
          </CardContent>
        </Card>
      </section>

      {/* Auxiliary Channels */}
      <section className="border-t pt-10">
        <h2 className="text-lg sm:text-xl font-bold text-center mb-8 tracking-tight">System Core Modules</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <Link href="/map" className="group">
            <Card className="p-5 hover:border-slate-350 dark:hover:border-slate-700 hover:shadow-md transition-all duration-305 bg-card">
              <div className="flex items-center space-x-3 mb-3">
                <div className="h-9 w-9 rounded-lg bg-indigo-500/10 text-indigo-500 flex items-center justify-center border border-indigo-500/15">
                  <Compass className="h-4.5 w-4.5 group-hover:rotate-12 transition-transform duration-300" />
                </div>
                <h3 className="font-bold text-sm sm:text-base">GIS Live Map</h3>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium leading-relaxed">Geographic mapping overlay of municipal issues and field engineer locations.</p>
            </Card>
          </Link>
          <Link href="/analytics" className="group">
            <Card className="p-5 hover:border-slate-355 dark:hover:border-slate-700 hover:shadow-md transition-all duration-305 bg-card">
              <div className="flex items-center space-x-3 mb-3">
                <div className="h-9 w-9 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center border border-emerald-500/15">
                  <BarChart3 className="h-4.5 w-4.5 group-hover:scale-110 transition-transform duration-300" />
                </div>
                <h3 className="font-bold text-sm sm:text-base">Decision Intelligence</h3>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium leading-relaxed">Real-time analytical trends, response latency statistics, and SLA logs.</p>
            </Card>
          </Link>
          <Link href="/settings" className="group">
            <Card className="p-5 hover:border-slate-355 dark:hover:border-slate-700 hover:shadow-md transition-all duration-305 bg-card">
              <div className="flex items-center space-x-3 mb-3">
                <div className="h-9 w-9 rounded-lg bg-slate-500/10 text-slate-500 flex items-center justify-center border border-slate-500/15">
                  <Settings className="h-4.5 w-4.5 group-hover:rotate-45 transition-transform duration-500" />
                </div>
                <h3 className="font-bold text-sm sm:text-base">Settings & Admin</h3>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium leading-relaxed">Plugin runtime configs, user role settings, and audit registry controls.</p>
            </Card>
          </Link>
        </div>
      </section>
    </div>
  );
}
