# Project Synapse -- Backend (Milestone 1)

## What's implemented right now
- 5 Hyderabad localities x 4 domains (mobility, environment, health, citizen services)
- 30 days of synthetic time-series data with a deliberate anomaly in **Gachibowli**
  (used for the demo story)
- Transparent, documented risk scoring engine (see `app/services/risk_engine.py`)
- 4 domain agents + 1 coordinator producing an explainable Decision Brief
- Gemini/Vertex AI integration with an automatic rule-based fallback so the
  app runs without any Google Cloud credentials during dev

## What's simulated (be upfront about this in the demo)
- Data is **synthetic**, not live government data
- "Multi-agent" = real, working orchestration logic, not independent LLM agents
  debating -- each agent applies its own analysis function, coordinator combines them
- Gemini is OFF by default locally (`USE_VERTEX_AI=false`); flip to `true` once you
  have a GCP project + credentials for the actual submission

## Run locally

```bash
cd backend
pip install -r requirements.txt
python -m app.data.generate_data      # generates app/data/metrics.json
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for interactive API docs.

## Key endpoints (milestone 1 flow)

| Step | Endpoint |
|---|---|
| Dashboard | `GET /api/dashboard/summary` |
| Locality list | `GET /api/localities` |
| Locality risk profile | `GET /api/localities/{locality_id}` |
| Ask AI a question | `POST /api/assistant/ask` `{"locality_id": "gachibowli", "question": "..."}` |
| Decision Brief | `GET /api/assistant/decision-brief/{locality_id}` |

## Enabling real Vertex AI Gemini (before submission)

1. `pip install google-cloud-aiplatform` (already in requirements.txt, commented out)
2. Set env vars:
   ```
   export USE_VERTEX_AI=true
   export GOOGLE_CLOUD_PROJECT=<your-project-id>
   export VERTEX_LOCATION=us-central1
   ```
3. Authenticate: `gcloud auth application-default login` (local) -- on Cloud Run
   this is automatic via the service account.

## Deploy to Cloud Run

```bash
gcloud run deploy project-synapse-backend \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars USE_VERTEX_AI=true,GOOGLE_CLOUD_PROJECT=<your-project-id>
```

## Migrating from JSON to real BigQuery (Phase 3)

Only `app/services/data_access.py` needs to change. Every router and agent
calls functions in that file, not storage directly -- swap the function
bodies to `bigquery.Client().query(...)` and keep the same return shapes.
