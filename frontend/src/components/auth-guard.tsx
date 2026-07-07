"use client";

import React from "react";
import { useAuth, getRequiredPermissionForPath } from "@/lib/auth-context";
import { usePathname, useRouter } from "next/navigation";
import { ShieldAlert } from "lucide-react";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { role, hasPermission } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const requiredPermission = getRequiredPermissionForPath(pathname);
  const isAuthorized = requiredPermission
    ? hasPermission(requiredPermission)
    : true;

  if (!isAuthorized) {
    return (
      <div className="flex min-h-[50vh] flex-col items-center justify-center text-center p-8 space-y-4">
        <div className="h-16 w-16 rounded-2xl bg-red-100 dark:bg-red-950/30 text-red-600 flex items-center justify-center">
          <ShieldAlert className="h-8 w-8" />
        </div>
        <h1 className="text-2xl font-extrabold tracking-tight text-red-600 dark:text-red-500">
          Access Denied
        </h1>
        <p className="text-muted-foreground text-sm max-w-md">
          Your current role{" "}
          <span className="font-semibold text-foreground">"{role}"</span> does
          not have the required permissions to access{" "}
          <span className="font-semibold text-foreground">"{pathname}"</span>.
        </p>
        <button
          onClick={() => router.push("/")}
          className="h-9 px-4 rounded-md bg-primary text-primary-foreground text-xs font-semibold hover:bg-primary/90 transition shadow"
        >
          Return to Dashboard Home
        </button>
      </div>
    );
  }

  return <>{children}</>;
}
