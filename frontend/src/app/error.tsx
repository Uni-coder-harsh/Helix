"use client";

import React from "react";
import { AlertOctagon, RefreshCw, Home } from "lucide-react";
import Link from "next/link";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  React.useEffect(() => {
    console.error("Route boundary error caught:", error);
  }, [error]);

  return (
    <div className="flex min-h-[500px] flex-col items-center justify-center text-center px-6 py-12 max-w-xl mx-auto space-y-6 animate-fade-in">
      <div className="h-16 w-16 rounded-2xl bg-destructive/10 text-destructive flex items-center justify-center border border-destructive/20 shadow-sm animate-bounce">
        <AlertOctagon className="h-8 w-8" />
      </div>

      <div className="space-y-2">
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">Something went wrong!</h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          An unexpected error occurred while executing client operations. The Helix security core has intercepted this event.
        </p>
      </div>

      {error.message && (
        <div className="w-full p-4 rounded-xl border bg-slate-50 dark:bg-slate-900/30 text-left font-mono text-xs text-slate-605 dark:text-slate-400 break-words shadow-inner">
          <span className="font-bold text-red-500 block mb-1">Diagnostic Log:</span>
          {error.message}
        </div>
      )}

      <div className="flex flex-wrap items-center justify-center gap-3 pt-2 w-full">
        <button
          onClick={reset}
          className="h-10 inline-flex items-center justify-center rounded-lg bg-primary px-5 text-sm font-semibold text-primary-foreground hover:bg-primary/95 transition shadow-sm gap-2"
        >
          <RefreshCw className="h-4 w-4" /> Try Re-evaluating
        </button>
        <Link href="/" className="h-10 inline-flex items-center justify-center rounded-lg border px-5 text-sm font-semibold hover:bg-slate-50 dark:hover:bg-slate-900 transition gap-2 shadow-sm">
          <Home className="h-4 w-4 text-muted-foreground" /> Return Home
        </Link>
      </div>
    </div>
  );
}
