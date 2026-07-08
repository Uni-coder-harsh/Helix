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
import { Navigation } from "@/components/navigation";

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
                    <Navigation />
                  </div>
                  <div className="flex items-center gap-4">
                    <ThemeToggle />
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
                      System Architecture
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
