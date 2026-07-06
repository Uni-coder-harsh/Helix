import React from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { ShieldAlert, Users, Compass, BarChart3, Settings } from "lucide-react";

export default function Home() {
  return (
    <div className="space-y-12 max-w-6xl mx-auto py-6">
      {/* Hero Welcome Header */}
      <section className="text-center space-y-4 max-w-3xl mx-auto">
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-primary via-purple-500 to-indigo-500 bg-clip-text text-transparent">
          Helix City Operations Portal
        </h1>
        <p className="text-muted-foreground text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
          The event-driven municipal management ecosystem. Securely connect citizens, field operators, and AI validation layers to drive high-performance urban outcomes.
        </p>
      </section>

      {/* Main Portals Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6 relative overflow-hidden group hover:border-primary/50 transition duration-300">
          <div className="absolute top-0 right-0 h-32 w-32 bg-primary/10 rounded-full blur-2xl -mr-16 -mt-16 group-hover:bg-primary/20 transition" />
          <CardHeader className="p-0 mb-4">
            <div className="h-12 w-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center mb-3">
              <ShieldAlert className="h-6 w-6" />
            </div>
            <CardTitle className="text-xl">Officer Console</CardTitle>
            <CardDescription className="text-xs">
              Secure portal for government administrators, ward officers, and municipal dispatchers.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0 space-y-4">
            <ul className="text-xs space-y-2 text-slate-600 dark:text-slate-400">
              <li className="flex items-center gap-2">🔹 Triage incoming reports verified by AI layers</li>
              <li className="flex items-center gap-2">🔹 Dispatch tasks to specific ward engineering teams</li>
              <li className="flex items-center gap-2">🔹 Edit and approve AI-generated citizen responses</li>
            </ul>
            <Link href="/officer" className="block pt-2">
              <button className="w-full h-9 inline-flex items-center justify-center rounded-md bg-primary text-primary-foreground text-xs font-semibold hover:bg-primary/90 transition shadow">
                Access Officer Workspace
              </button>
            </Link>
          </CardContent>
        </Card>

        <Card className="p-6 relative overflow-hidden group hover:border-primary/50 transition duration-300">
          <div className="absolute top-0 right-0 h-32 w-32 bg-purple-500/10 rounded-full blur-2xl -mr-16 -mt-16 group-hover:bg-purple-500/20 transition" />
          <CardHeader className="p-0 mb-4">
            <div className="h-12 w-12 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-3">
              <Users className="h-6 w-6" />
            </div>
            <CardTitle className="text-xl">Citizen Hub</CardTitle>
            <CardDescription className="text-xs">
              Public transparency interface for residents to lodge reports and track live work progress.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0 space-y-4">
            <ul className="text-xs space-y-2 text-slate-600 dark:text-slate-400">
              <li className="flex items-center gap-2">🔹 Log issues with detailed coordinates and image proofs</li>
              <li className="flex items-center gap-2">🔹 Upvote shared concerns to highlight collective urgency</li>
              <li className="flex items-center gap-2">🔹 Track live status updates from dispatchers in real-time</li>
            </ul>
            <Link href="/citizen" className="block pt-2">
              <button className="w-full h-9 inline-flex items-center justify-center rounded-md bg-secondary text-secondary-foreground text-xs font-semibold hover:bg-secondary/80 transition border shadow-sm">
                Access Citizen Workspace
              </button>
            </Link>
          </CardContent>
        </Card>
      </section>

      {/* Auxiliary Channels */}
      <section className="border-t pt-8">
        <h2 className="text-lg font-bold text-center mb-6 tracking-tight">System Core Modules</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <Link href="/map" className="group">
            <Card className="p-4 hover:border-slate-400 dark:hover:border-slate-700 transition">
              <div className="flex items-center space-x-3 mb-2">
                <Compass className="h-5 w-5 text-indigo-500 group-hover:scale-110 transition" />
                <h3 className="font-semibold text-sm">GIS Live Map</h3>
              </div>
              <p className="text-xs text-muted-foreground">Geographic mapping overlay of municipal issues and field engineer locations.</p>
            </Card>
          </Link>
          <Link href="/analytics" className="group">
            <Card className="p-4 hover:border-slate-400 dark:hover:border-slate-700 transition">
              <div className="flex items-center space-x-3 mb-2">
                <BarChart3 className="h-5 w-5 text-emerald-500 group-hover:scale-110 transition" />
                <h3 className="font-semibold text-sm">Decision Intelligence</h3>
              </div>
              <p className="text-xs text-muted-foreground">Real-time analytical trends, response latency statistics, and SLA logs.</p>
            </Card>
          </Link>
          <Link href="/settings" className="group">
            <Card className="p-4 hover:border-slate-400 dark:hover:border-slate-700 transition">
              <div className="flex items-center space-x-3 mb-2">
                <Settings className="h-5 w-5 text-slate-500 group-hover:scale-110 transition" />
                <h3 className="font-semibold text-sm">Settings & Admin</h3>
              </div>
              <p className="text-xs text-muted-foreground">Plugin runtime configs, user role settings, and audit registry controls.</p>
            </Card>
          </Link>
        </div>
      </section>
    </div>
  );
}
