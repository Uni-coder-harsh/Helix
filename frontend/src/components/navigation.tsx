"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import {
  Compass,
  Users,
  BarChart3,
  Settings,
  Shield,
  Sparkles,
  LogOut,
  User as UserIcon,
  LayoutDashboard
} from "lucide-react";

export function Navigation() {
  const { user, role, logout } = useAuth();

  if (!user) return null;

  return (
    <nav className="hidden md:flex items-center space-x-6 text-sm font-semibold text-muted-foreground">
      {role === "Citizen" && (
        <>
          <Link href="/citizen" className="flex items-center gap-1.5 hover:text-foreground transition">
            <LayoutDashboard className="h-4 w-4" /> Dashboard
          </Link>
          <Link href="/citizen/new" className="flex items-center gap-1.5 hover:text-foreground transition">
            <Users className="h-4 w-4" /> My Complaints
          </Link>
        </>
      )}

      {role === "Officer" && (
        <>
          <Link href="/officer" className="flex items-center gap-1.5 hover:text-foreground transition">
            <Shield className="h-4 w-4" /> Dashboard
          </Link>
          <Link href="/map" className="flex items-center gap-1.5 hover:text-foreground transition">
            <Compass className="h-4 w-4" /> Map
          </Link>
          <Link href="/planning" className="flex items-center gap-1.5 hover:text-foreground transition">
            <Sparkles className="h-4 w-4 text-indigo-500" /> Planning
          </Link>
        </>
      )}

      {(role === "MLA" || role === "MP") && (
        <>
          <Link href="/analytics" className="flex items-center gap-1.5 hover:text-foreground transition">
            <BarChart3 className="h-4 w-4" /> Dashboard
          </Link>
          <Link href="/map" className="flex items-center gap-1.5 hover:text-foreground transition">
            <Compass className="h-4 w-4" /> Map
          </Link>
          <Link href="/planning" className="flex items-center gap-1.5 hover:text-foreground transition">
            <Sparkles className="h-4 w-4 text-indigo-500" /> Planning
          </Link>
        </>
      )}

      {(role === "System Administrator" || role === "Platform Administrator") && (
        <>
          <Link href="/settings" className="flex items-center gap-1.5 hover:text-foreground transition">
            <LayoutDashboard className="h-4 w-4" /> Dashboard
          </Link>
          <Link href="/analytics" className="flex items-center gap-1.5 hover:text-foreground transition">
            <BarChart3 className="h-4 w-4" /> Audit
          </Link>
          <Link href="/settings" className="flex items-center gap-1.5 hover:text-foreground transition">
            <Settings className="h-4 w-4" /> Settings
          </Link>
        </>
      )}

      <div className="flex items-center gap-4 ml-4 pl-4 border-l">
        <div className="flex items-center gap-1.5 text-foreground">
          <UserIcon className="h-4 w-4" /> <span className="max-w-[100px] truncate">{user.name || user.email}</span>
        </div>
        <button onClick={logout} className="flex items-center gap-1.5 hover:text-red-500 transition cursor-pointer">
          <LogOut className="h-4 w-4" /> Logout
        </button>
      </div>
    </nav>
  );
}
