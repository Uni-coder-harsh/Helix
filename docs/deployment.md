# Deployment Guide

This document outlines the current production architecture and deployment steps for the Helix project.

## Production Architecture

Helix employs a decoupled modern stack deployed across specialized cloud providers:

- **Frontend Application**: Vercel (Next.js Edge Network)
- **Backend Services**: Railway (FastAPI Python Application)
- **Database**: Neon (Serverless PostgreSQL)
- **AI / LLM Integration**: Google Gemini API
- **Spatial / Maps**: MapLibre GL JS + OpenStreetMap (OSM)
- **Documentation**: GitHub Pages (MkDocs)

## Deployment Order

To ensure a seamless deployment without broken references, services must be provisioned and deployed in the following order:

1. **Database** (Neon)
2. **Backend API** (Railway)
3. **Frontend App** (Vercel)

---

## 1. Database Deployment (Neon)

1. Create a new project in [Neon](https://neon.tech).
2. Provision a PostgreSQL database.
3. Obtain the connection string.
   - Example: `postgresql://user:password@ep-cold-shadow-1234.us-east-2.aws.neon.tech/neondb?sslmode=require`

## 2. Backend Deployment (Railway)

1. Connect your GitHub repository to [Railway](https://railway.app).
2. Create a new service from the repository and set the root directory to `/backend`.
3. Configure the start command (if not automatically detected):
   `uvicorn services.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   Configure the following variables in the Railway dashboard:
   - `DATABASE_URL`: The Neon connection string.
   - `GEMINI_API_KEY`: Your Google Gemini API Key.
   - `ENVIRONMENT`: `production`
5. Deploy the backend and capture the generated public URL (e.g., `https://helix-production.up.railway.app`).

## 3. Frontend Deployment (Vercel)

1. Import your GitHub repository into [Vercel](https://vercel.com).
2. Set the Root Directory to `frontend`.
3. Ensure the Build Command is `npm run build` and Output Directory is `.next`.
4. **Environment Variables**:
   Configure the following variables in the Vercel dashboard:
   - `NEXT_PUBLIC_API_URL`: The URL of your Railway backend.
5. Deploy the frontend.

## 4. Documentation (GitHub Pages)

Documentation is hosted via GitHub Pages using MkDocs. To deploy documentation changes:

1. Install MkDocs with `pip install mkdocs-material`.
2. Run `mkdocs gh-deploy` from the project root.

---

## Required Environment Variables Summary

### Backend (.env)
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Full PostgreSQL connection string (Neon). |
| `GEMINI_API_KEY` | Secret key for Gemini LLM endpoints. |
| `ENVIRONMENT` | Used to toggle production vs dev behavior (`production` or `development`). |

### Frontend (.env.local)
| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Base URL for the backend API, enabling Vercel rewrites. |
