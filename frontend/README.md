# Project Synapse -- Frontend (Milestone 1)

React + Vite + Tailwind. Talks to the FastAPI backend at `http://localhost:8000` by default.

## Screens implemented
1. **Community Overview Dashboard** -- KPI cards, AI daily summary, locality grid
   (each card shows a pulse line whose jaggedness scales with risk)
2. **Locality Risk Profile** -- domain score breakdown, latest metrics vs baseline
3. **AI Decision Assistant** -- grounded Q&A chat + one-click Decision Brief generation
4. **Decision Brief** -- structured evidence, contributing factors, recommended actions,
   confidence, limitations

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 -- make sure the backend is running on port 8000 first
(see backend/README.md).

## Pointing at a deployed backend

If your backend is deployed (e.g. to Cloud Run) instead of running locally, create a
`.env` file in this folder:

```
VITE_API_URL=https://your-backend-url.run.app
```

## Build for production / Cloud Run

```bash
npm run build
```

Output goes to `dist/`. You can serve this as a static site (Cloud Run with a tiny
nginx/Dockerfile, Firebase Hosting, or Cloud Storage + CDN all work).
