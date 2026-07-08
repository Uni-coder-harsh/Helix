"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { API_BASE_URL } from "@/config";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import Link from "next/link";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE_URL}/identity/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, name, phone })
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Registration failed");
      }
      router.push("/login?registered=true");
    } catch (err: any) {
      setError(err.message || "Failed to register");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-[70vh] items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md shadow-lg border-slate-200 dark:border-slate-800">
        <CardHeader className="space-y-2 text-center pb-6">
          <CardTitle className="text-3xl font-bold tracking-tight">Create an Account</CardTitle>
          <CardDescription className="text-muted-foreground">
            Join the Helix platform to participate in urban governance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleRegister} className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-500 bg-red-100 dark:bg-red-950/50 rounded-md">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none" htmlFor="name">Full Name</label>
              <input
                id="name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="John Doe"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none" htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="name@example.com"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none" htmlFor="phone">Phone Number</label>
              <input
                id="phone"
                type="tel"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="+1234567890"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none" htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full mt-4"
            >
              {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              {isSubmitting ? "Registering..." : "Create Account"}
            </button>
          </form>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <div className="text-sm text-center text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:underline font-semibold">
              Sign in
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
