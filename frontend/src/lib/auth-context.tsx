"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";

export type Role =
  | "System Administrator"
  | "Platform Administrator"
  | "MLA"
  | "MP"
  | "Officer"
  | "Field Engineer"
  | "Citizen";

export const ROLE_PERMISSIONS: Record<Role, string[]> = {
  "System Administrator": [
    "issues:create",
    "issues:read",
    "issues:list_pending",
    "recommendations:read",
    "recommendations:write",
    "planning:read",
    "planning:write",
    "spatial:read",
    "copilot:query",
    "proactive:read",
    "pipeline:read",
    "brief:read",
    "timeline:read",
    "constituency:read",
    "incidents:read",
    "incidents:write",
    "audit:read",
    "audit:write",
    "system:admin",
  ],
  "Platform Administrator": [
    "issues:create",
    "issues:read",
    "issues:list_pending",
    "recommendations:read",
    "recommendations:write",
    "planning:read",
    "planning:write",
    "spatial:read",
    "copilot:query",
    "proactive:read",
    "pipeline:read",
    "brief:read",
    "timeline:read",
    "constituency:read",
    "incidents:read",
    "incidents:write",
    "audit:read",
    "system:admin",
  ],
  "MLA": [
    "issues:read",
    "issues:list_pending",
    "recommendations:read",
    "planning:read",
    "planning:write",
    "spatial:read",
    "copilot:query",
    "proactive:read",
    "pipeline:read",
    "brief:read",
    "timeline:read",
    "constituency:read",
  ],
  "MP": [
    "issues:read",
    "issues:list_pending",
    "recommendations:read",
    "planning:read",
    "spatial:read",
    "copilot:query",
    "proactive:read",
    "pipeline:read",
    "brief:read",
    "timeline:read",
    "constituency:read",
  ],
  "Officer": [
    "issues:create",
    "issues:read",
    "issues:list_pending",
    "recommendations:read",
    "recommendations:write",
    "planning:read",
    "planning:write",
    "spatial:read",
    "copilot:query",
    "proactive:read",
    "pipeline:read",
    "brief:read",
    "timeline:read",
    "constituency:read",
    "incidents:read",
    "incidents:write",
  ],
  "Field Engineer": [
    "issues:read",
    "spatial:read",
    "timeline:read",
  ],
  "Citizen": [
    "issues:create",
    "issues:read",
    "spatial:read",
    "timeline:read",
  ],
};

interface AuthContextType {
  role: Role;
  permissions: string[];
  setRole: (role: Role) => void;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function getRequiredPermissionForPath(path: string): string | null {
  if (path.startsWith("/officer")) return "issues:list_pending";
  if (path.startsWith("/planning")) return "planning:read";
  if (path.startsWith("/analytics")) return "constituency:read";
  if (path.startsWith("/settings")) return "audit:read";
  if (path.startsWith("/map")) return "spatial:read";
  if (path.startsWith("/citizen")) return "issues:create";
  return null;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [role, setRoleState] = useState<Role>("Officer");
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const savedRole = localStorage.getItem("helix-user-role") as Role;
    if (savedRole && Object.keys(ROLE_PERMISSIONS).includes(savedRole)) {
      setRoleState(savedRole);
    }
  }, []);

  // Global window.fetch hook to inject custom X-User-Role header
  useEffect(() => {
    const originalFetch = window.fetch;
    window.fetch = async (input, init) => {
      const headers = new Headers(init?.headers);
      headers.set("X-User-Role", role);
      return originalFetch(input, {
        ...init,
        headers,
      });
    };

    return () => {
      window.fetch = originalFetch;
    };
  }, [role]);

  const setRole = (newRole: Role) => {
    setRoleState(newRole);
    localStorage.setItem("helix-user-role", newRole);

    const requiredPermission = getRequiredPermissionForPath(pathname);
    if (
      requiredPermission &&
      !ROLE_PERMISSIONS[newRole].includes(requiredPermission)
    ) {
      router.push("/");
    }
  };

  const hasPermission = (permission: string) => {
    return ROLE_PERMISSIONS[role].includes(permission);
  };

  const permissions = ROLE_PERMISSIONS[role];

  return (
    <AuthContext.Provider value={{ role, permissions, setRole, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
