"use client";

import React from "react";
import { useAuth, Role } from "@/lib/auth-context";
import { Shield } from "lucide-react";

export function RoleSelector() {
  const { role, setRole } = useAuth();

  const roles: Role[] = [
    "System Administrator",
    "Platform Administrator",
    "MLA",
    "MP",
    "Officer",
    "Field Engineer",
    "Citizen",
  ];

  return (
    <div className="flex items-center gap-2 border-l pl-4">
      <div className="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-700 dark:text-slate-300">
        <Shield className="h-4 w-4 text-primary" />
      </div>
      <div className="flex flex-col gap-0.5">
        <span className="text-[9px] text-muted-foreground font-bold uppercase leading-none">
          Active Role
        </span>
        <select
          value={role}
          onChange={(e) => setRole(e.target.value as Role)}
          className="text-xs font-semibold bg-transparent border-none p-0 focus:ring-0 cursor-pointer text-slate-800 dark:text-slate-200 outline-none"
        >
          {roles.map((r) => (
            <option
              key={r}
              value={r}
              className="bg-background text-foreground text-xs"
            >
              {r}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
