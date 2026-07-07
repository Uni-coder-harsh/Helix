import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import Link from "next/link";
import React from "react";
import { ThemeToggle } from "@/components/theme-toggle";
import {
  Compass,
  Users,
  LayoutDashboard,
  BarChart3,
  Settings,
  Shield,
  Sparkles,
} from "lucide-react";
import { AuthProvider } from "@/lib/auth-context";
import { AuthGuard } from "@/components/auth-guard";
import { RoleSelector } from "@/components/role-selector";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Helix Governance Platform",
  description:
    "A secure, transparent, event-driven governance system for modern cities and citizen empowerment.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.className} min-h-screen bg-background text-foreground transition-colors duration-300`}
      >
        <ThemeProvider defaultTheme="dark" storageKey="helix-ui-theme">
          <AuthProvider>
            <div className="flex min-h-screen flex-col">
              {/* Global Premium Navigation Bar */}
              <header className="sticky top-0 z-40 w-full border-b bg-background/80 backdrop-blur-md">
                <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6">
                  <div className="flex items-center gap-6">
                    <Link href="/" className="flex items-center space-x-2.5">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white shadow-md shadow-primary/20">
                        <span className="text-lg font-bold tracking-tighter">
                          H
                        </span>
                      </div>
                      <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                        Helix
                      </span>
                    </Link>
                    <nav className="hidden md:flex items-center space-x-6 text-sm font-semibold text-muted-foreground">
                      <Link
                        href="/officer"
                        className="flex items-center gap-1.5 hover:text-foreground transition"
                      >
                        <Shield className="h-4 w-4" /> Officer
                      </Link>
                      <Link
                        href="/citizen"
                        className="flex items-center gap-1.5 hover:text-foreground transition"
                      >
                        <Users className="h-4 w-4" /> Citizen
                      </Link>
                      <Link
                        href="/map"
                        className="flex items-center gap-1.5 hover:text-foreground transition"
                      >
                        <Compass className="h-4 w-4" /> Map
                      </Link>
                      <Link
                        href="/planning"
                        className="flex items-center gap-1.5 hover:text-foreground transition"
                      >
                        <Sparkles className="h-4 w-4 text-indigo-500 animate-pulse" />{" "}
                        Planning
                      </Link>
                      <Link
                        href="/analytics"
                        className="flex items-center gap-1.5 hover:text-foreground transition"
                      >
                        <BarChart3 className="h-4 w-4" /> Analytics
                      </Link>
                      <Link
                        href="/settings"
                        className="flex items-center gap-1.5 hover:text-foreground transition"
                      >
                        <Settings className="h-4 w-4" /> Settings
                      </Link>
                    </nav>
                  </div>
                  <div className="flex items-center gap-4">
                    <ThemeToggle />
                    <RoleSelector />
                  </div>
                </div>
              </header>

              {/* Main Application Container */}
              <main className="flex-1 container mx-auto px-4 py-8 sm:px-6">
                <AuthGuard>{children}</AuthGuard>
              </main>

              {/* Footer */}
              <footer className="border-t py-6 bg-slate-50 dark:bg-slate-900/50">
                <div className="container mx-auto px-4 sm:px-6 flex flex-col md:flex-row items-center justify-between text-xs text-muted-foreground gap-4">
                  <div>
                    &copy; {new Date().getFullYear()} Helix Platform. Under the
                    Governance Ethos of the Helix Constitution.
                  </div>
                  <div className="flex gap-4">
                    <a href="#" className="hover:underline">
                      Documentation
                    </a>
                    <a href="#" className="hover:underline">
                      Privacy Policy
                    </a>
                    <a href="#" className="hover:underline">
                      System Architecture (HELIX-ARCH-007)
                    </a>
                  </div>
                </div>
              </footer>
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
