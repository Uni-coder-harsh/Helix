import React from "react";
import { Loader2 } from "lucide-react";

export default function Loading() {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center text-center p-6 space-y-4 animate-fade-in">
      <div className="relative flex items-center justify-center">
        {/* Outer glowing pulsing ring */}
        <div className="absolute h-14 w-14 rounded-full border border-primary/20 bg-primary/5 animate-ping duration-1000" />

        {/* Inner spinning loader */}
        <div className="relative h-12 w-12 rounded-xl bg-card border shadow flex items-center justify-center text-primary">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      </div>

      <div className="space-y-1">
        <h3 className="text-sm font-bold tracking-tight text-slate-800 dark:text-slate-205">Syncing Helix Core</h3>
        <p className="text-[11px] text-muted-foreground animate-pulse font-medium">Retrieving decentralized municipal state ledger...</p>
      </div>
    </div>
  );
}
