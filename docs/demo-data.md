# Demo Dataset & Seeding

Helix includes a fully-functional synthetic dataset seeder centered around the Shivaji Nagar constituency in Bangalore Central. This enables instant population of maps and dashboards with realistic data.

## 📂 Directory Tour

```text
demo-data/
├── issues/       # Citizen issues templates
├── evidence/     # Duplicate incident mappings & attachments
├── policies/     # In-memory policy specifications
├── assets/       # Geo-located public assets (schools, hospitals, parks)
├── boundaries/   # Ward and constituency GeoJSON coordinates
└── seed.py       # Seeder script running against SQLAlchemy engine
```

---

## 🚀 Running the Database Seeder

To seed either a local development database or a production PostgreSQL instance (such as Neon) with 350 realistic geographically-clustered citizen reports, incidents, and AI recommendations, run:

```bash
# Execute from workspace root
PYTHONPATH=backend/:backend/services/ai-platform/src .venv/bin/python demo-data/seed.py
```

### Environment Integration
The seeder dynamically respects the active environment variables:
* If `DATABASE_URL` is set, it will connect and seed that target database (e.g. Neon Cloud PostgreSQL).
* Otherwise, it defaults to the local SQLite database at `sqlite:///backend/helix.db`.
