# Production Deployment Specification

This document details the production deployment architecture, deployment pipelines, and environment setups for the Helix platform.

## Infrastructure Topology

```mermaid
graph TD
    User[Citizen / Officer] -->|HTTPS| DNS[Cloud DNS]
    DNS --> CDN[CDN / Load Balancer]
    CDN -->|Static Assets| Frontend[Next.js Dashboard - Vercel / Cloud Run]
    CDN -->|API Requests| Gateway[API Gateway]
    Gateway --> ServiceMesh[K8s Service Mesh / VPC]

    subgraph Backend Services
        ServiceMesh --> Gov[Governance Service]
        ServiceMesh --> AI[AI Platform Service]
        ServiceMesh --> ID[Identity Service]
        ServiceMesh --> Audit[Audit Service]
    end

    subgraph Data Tier
        Gov --> Postgres[(PostgreSQL)]
        AI --> Qdrant[(Qdrant Vector DB)]
        ID --> Redis[(Redis Cache)]
        Audit --> Mongo[(MongoDB Atlas)]
    end
```

## Continuous Deployment CI/CD (GitHub Actions)

Upon merging changes into the `main` branch, the deployment flow executes automatically:

1. **Verification & Tests:**
   * Run strict PEP-8 / Ruff python linting checks.
   * Execute unit and integration tests for backend, frontend, and AI platform.
2. **Container Build & Push:**
   * Build multi-stage optimized production Docker images.
   * Tag and push images to Google Artifact Registry.
3. **Deployment Deploy:**
   * Deploy container images to Google Cloud Run (or GKE).
   * Perform post-deployment HTTP health checks on `/health/ready` liveness endpoints.
4. **Auto-Rollback Trigger:**
   * If health checks fail or error rates exceed 1% within the first 5 minutes, automatically trigger rollback to the previous stable image tag.

## Configuration & Secrets Management
* **Never commit secrets to code repository.**
* Production configurations are injected at runtime via Environment Variables into Cloud Run / GKE containers.
* Secrets are retrieved at container startup from **Google Secret Manager** (e.g. `DATABASE_URL`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`).
