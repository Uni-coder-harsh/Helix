"use client";

import React, { useEffect } from "react";
import { useAuth, getRequiredPermissionForPath } from "@/lib/auth-context";
import { usePathname, useRouter } from "next/navigation";
import { ShieldAlert, Loader2 } from "lucide-react";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, role, hasPermission, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      const isPublicPath = pathname === "/" || pathname === "/login" || pathname === "/register";

      if (!user && !isPublicPath) {
        router.push("/login");
      }
    }
  }, [isLoading, user, pathname, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] flex-col items-center justify-center text-center p-8 space-y-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground text-sm">Authenticating...</p>
      </div>
    );
  }

  const isPublicPath = pathname === "/" || pathname === "/login" || pathname === "/register";
  if (isPublicPath) {
    return <>{children}</>;
  }

  if (!user) {
    return null; // Will redirect in useEffect
  }

  const requiredPermission = getRequiredPermissionForPath(pathname);
  const isAuthorized = requiredPermission ? hasPermission(requiredPermission) : true;

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
          onClick={() => {
             if (role === "Citizen") router.push("/citizen");
             else if (role === "Officer") router.push("/officer");
             else if (role === "System Administrator" || role === "Platform Administrator") router.push("/settings");
             else router.push("/analytics");
          }}
          className="h-9 px-4 rounded-md bg-primary text-primary-foreground text-xs font-semibold hover:bg-primary/90 transition shadow mt-4"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  return <>{children}</>;
}
