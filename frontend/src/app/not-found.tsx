import React from "react";
import { Compass, Home, Shield } from "lucide-react";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-[500px] flex-col items-center justify-center text-center px-6 py-12 max-w-md mx-auto space-y-6 animate-fade-in">
      <div className="h-16 w-16 rounded-2xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center border border-indigo-500/20 shadow-sm relative">
        <div className="absolute inset-0 bg-indigo-500/5 rounded-2xl animate-ping duration-1000" />
        <Compass className="h-8 w-8 relative" />
      </div>

      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold tracking-tight">404 - Registry Missing</h1>
        <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed max-w-sm font-medium">
          The coordinate grid or system address you requested is not mapped within the current Helix registry index.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 pt-2 w-full">
        <Link href="/" className="w-full sm:w-auto h-10 inline-flex items-center justify-center rounded-lg bg-primary px-5 text-xs sm:text-sm font-semibold text-primary-foreground hover:bg-primary/95 transition shadow-sm gap-2">
          <Home className="h-4 w-4" /> Return Home
        </Link>
      </div>
    </div>
  );
}
