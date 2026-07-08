"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { API_BASE_URL } from "@/config";

export type Role =
  | "System Administrator"
  | "Platform Administrator"
  | "MLA"
  | "MP"
  | "Officer"
  | "Field Engineer"
  | "Citizen";

export const ROLE_PERMISSIONS: Record<Role, string[]> = {
  "System Administrator": ["issues:create", "issues:read", "issues:list_pending", "recommendations:read", "recommendations:write", "planning:read", "planning:write", "spatial:read", "copilot:query", "proactive:read", "pipeline:read", "brief:read", "timeline:read", "constituency:read", "incidents:read", "incidents:write", "audit:read", "audit:write", "system:admin"],
  "Platform Administrator": ["issues:create", "issues:read", "issues:list_pending", "recommendations:read", "recommendations:write", "planning:read", "planning:write", "spatial:read", "copilot:query", "proactive:read", "pipeline:read", "brief:read", "timeline:read", "constituency:read", "incidents:read", "incidents:write", "audit:read", "system:admin"],
  "MLA": ["issues:read", "issues:list_pending", "recommendations:read", "planning:read", "planning:write", "spatial:read", "copilot:query", "proactive:read", "pipeline:read", "brief:read", "timeline:read", "constituency:read"],
  "MP": ["issues:read", "issues:list_pending", "recommendations:read", "planning:read", "spatial:read", "copilot:query", "proactive:read", "pipeline:read", "brief:read", "timeline:read", "constituency:read"],
  "Officer": ["issues:create", "issues:read", "issues:list_pending", "recommendations:read", "recommendations:write", "planning:read", "planning:write", "spatial:read", "copilot:query", "proactive:read", "pipeline:read", "brief:read", "timeline:read", "constituency:read", "incidents:read", "incidents:write"],
  "Field Engineer": ["issues:read", "spatial:read", "timeline:read"],
  "Citizen": ["issues:create", "issues:read", "spatial:read", "timeline:read"],
};

export interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
  status: string;
  constituency_id?: string;
  district_id?: string;
}

interface AuthContextType {
  user: User | null;
  role: Role | null;
  permissions: string[];
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
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
  if (path.startsWith("/admin")) return "system:admin";
  return null;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem("helix-token");
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/identity/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        localStorage.removeItem("helix-token");
        setUser(null);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };


  const login = async (token: string) => {
    localStorage.setItem("helix-token", token);
    await checkAuth();
    router.push("/");
  };

  const logout = () => {
    localStorage.removeItem("helix-token");
    setUser(null);
    router.push("/");
  };

  const hasPermission = (permission: string) => {
    if (!user) return false;
    return ROLE_PERMISSIONS[user.role]?.includes(permission) ?? false;
  };

  const role = user?.role ?? null;
  const permissions = role ? ROLE_PERMISSIONS[role] : [];

  return (
    <AuthContext.Provider value={{ user, role, permissions, isLoading, login, logout, hasPermission }}>
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
