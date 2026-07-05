---
owner: "@harsh"
version: "0.1.0"
status: "Draft"
last_updated: "2026-07-05"
reviewer: "@harsh"
dependencies: []
---

# Deployment Architecture

This document describes how to deploy Helix to production environments.

> [!NOTE]
> Active scripts for production deployment will be validated in **Phase 8: Pilot Deployment**.

## Cloud Topology

We target deployments to Cloud Run or GKE (Google Kubernetes Engine).

```mermaid
graph TD
    Ingress[Load Balancer / Ingress] --> Web[Frontend UI]
    Ingress --> API[Backend API]
    API --> Agent[Agent Executor]
```
