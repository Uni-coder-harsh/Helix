---
owner: "@harsh"
version: "1.0.0"
status: "Release"
last_updated: "2026-07-07"
reviewer: "@harsh"
dependencies: []
---

# Production Deployment Guide

This document outlines the step-by-step instructions to deploy the Helix Governance Monolith to cloud environments.

## 1. Cloud Architecture Overview

```mermaid
graph TD
    User[Citizen / Officer] --> Vercel[Vercel: Next.js Frontend]
    Vercel --> Railway[Railway: FastAPI Backend Monolith]
    Railway --> Neon[Neon: Cloud PostgreSQL Database]
```

---

## 2. Step-by-Step Deployment Instructions

### Step 1: Provision database (Neon PostgreSQL)
1. Register/Login to [Neon Console](https://neon.tech/).
2. Create a new project and select **PostgreSQL 16+**.
3. Copy the generated `DATABASE_URL` connection string (e.g., `postgresql://user:password@endpoint.neon.tech/neondb?sslmode=require`).

### Step 2: Deploy Backend to Railway
1. Create a new project on [Railway](https://railway.app/).
2. Deploy using the GitHub repository integration, pointing to the `/backend` sub-directory containing the `Dockerfile`.
3. Expose port `8000`.
4. Configure the following environment variables:
   * `DATABASE_URL`: `<Your Neon connection string>`
   * `GEMINI_API_KEY`: `<Your Google Gemini API Key>`
   * `APP_ENV`: `production`
   * `LOG_LEVEL`: `INFO`
5. Configure health check path targets:
   * **Liveness Probe:** `/live` (returns HTTP 200 `{"status": "alive"}`)
   * **Readiness Probe:** `/ready` (verifies DB connection; returns HTTP 200 `{"status": "ready"}`)

### Step 3: Deploy Frontend to Vercel
1. Create a new project on [Vercel](https://vercel.com/).
2. Import the GitHub repository and set the root directory to `frontend/`.
3. Configure the environment variable:
   * `NEXT_PUBLIC_API_URL`: `<The public domain URL of the deployed Railway backend>`
4. Deploy the project (Vercel automatically compiles the static Next.js pages).

### Step 4: Seed Demo Data
Once the database and backend are operational, seed the cloud database with 350 realistic Shivaji Nagar citizen reports:
```bash
# From the repository root
PYTHONPATH=backend/:backend/services/ai-platform/src DATABASE_URL=<YOUR_NEON_DATABASE_URL> .venv/bin/python demo-data/seed.py
```

---

## 3. Operations & Smoke Testing

Verify the deployed application by hitting the following public endpoints:
* **Swagger OpenAPI:** `https://<your-railway-url>/docs`
* **Liveness Endpoint:** `https://<your-railway-url>/live`
* **Readiness Endpoint:** `https://<your-railway-url>/ready`
* **Pending Issues API:** `https://<your-railway-url>/governance/issues/pending`
