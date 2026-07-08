<div align="center">
  <h1>Helix 🧬</h1>
  <p><strong>AI Governance Operating System</strong></p>

  <p>
    <a href="https://helix-sigma-kohl.vercel.app"><strong>Live Demo</strong></a> ·
    <a href="https://helix-sigma-kohl.vercel.app/docs"><strong>Documentation</strong></a>
  </p>
</div>

---

## 🌍 What is Helix?

Helix is a secure, transparent, event-driven governance system designed for modern cities. We bridge the gap between citizens reporting issues and the field operations repairing them, using spatial intelligence and AI-driven decision support to create smarter, more responsive cities.

## 🚨 What problem does it solve?

Traditional civic platforms are fragmented, slow, and opaque. Citizens report potholes, broken streetlights, or sanitation issues into a black hole, and officers struggle to prioritize them without real context or spatial awareness.

Helix solves this by providing:
- **Instant Triage:** AI categorizes and prioritizes issues instantly.
- **Spatial Intelligence:** Map-based visualizations help officers see hotspots (e.g., clusters of water logging).
- **Proactive Interventions:** Helix doesn't just manage tickets; it drafts decision briefs, suggests interventions, and generates dispatch plans using LLMs.
- **Full Transparency:** Citizens can track the exact status and timeline of their reports.

## 🚀 Can I try it?

Yes! The platform is live and fully functional.

- **Frontend (Citizen & Officer Portals):** [https://helix-sigma-kohl.vercel.app](https://helix-sigma-kohl.vercel.app)
- **Backend API (FastAPI):** [https://helix-production-a8c2.up.railway.app/docs](https://helix-production-a8c2.up.railway.app/docs)

*(Note: The platform is seeded with mock data for demonstrations. You can log in as a Citizen or Officer to explore the different dashboards.)*

## 📚 Where are the docs?

Detailed technical documentation, API specifications, and deployment guides are available in our Engineering Portal.
You can read the docs locally using `mkdocs serve` or browse the `docs/` folder in this repository.

## ✨ How is it different?

Helix is not just a CRUD application for issue tracking. It is a modern **Event-Driven AI platform**:
- **Next.js App Router Frontend:** A premium, dynamic, glassmorphic UI built for speed.
- **FastAPI Backend:** High-performance async Python backend.
- **Gemini AI Integration:** Automated morning briefings for officers, AI decision briefs, and automated dispatch routing.
- **MapLibre Spatial Integration:** Real-time spatial clustering and geographic analysis.

---

## 🛠️ Technology Stack

- **Frontend:** Next.js 14, React, TailwindCSS, Lucide Icons, MapLibre
- **Backend:** FastAPI, Python, SQLAlchemy
- **Database:** Neon Serverless PostgreSQL
- **AI / Intelligence:** Google Gemini Pro
- **Deployment:** Vercel (Frontend), Railway (Backend)

---

## 🏗️ Repository Structure

```text
Helix/
├── backend/            # FastAPI application & AI Agents
├── frontend/           # Next.js web application
├── docs/               # MkDocs Engineering Portal
└── mkdocs.yml          # Documentation configuration
```

## 💻 Local Development

### Prerequisites
- Node.js 20+
- Python 3.12+
- PostgreSQL database

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Configure your DB and Gemini API Key
uvicorn services.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## 📄 License
This project is licensed under the MIT License.
