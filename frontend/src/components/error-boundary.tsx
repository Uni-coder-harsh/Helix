"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught widget error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[300px] flex-col items-center justify-center rounded-2xl border border-red-500/20 bg-red-500/[0.02] p-8 text-center max-w-md mx-auto space-y-4 shadow-sm animate-fade-in">
          <div className="h-11 w-11 rounded-full bg-red-500/10 text-red-500 flex items-center justify-center border border-red-500/25">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div className="space-y-1">
            <h2 className="text-sm font-bold text-slate-800 dark:text-slate-205">
              Widget Interface Error
            </h2>
            <p className="text-xs text-muted-foreground max-w-xs mx-auto leading-normal">
              {this.state.error?.message || "An unexpected error occurred in this dashboard module."}
            </p>
          </div>
          <Button
            size="sm"
            onClick={() => this.setState({ hasError: false, error: null })}
            className="h-8.5 px-4 bg-red-600 hover:bg-red-750 text-white font-semibold text-xs flex items-center gap-1.5 shadow-sm"
          >
            <RotateCcw className="h-3.5 w-3.5" /> Re-initialize Module
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
