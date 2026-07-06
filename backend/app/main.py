from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import localities, dashboard, assistant

app = FastAPI(
    title="Project Synapse API",
    description="The Living Intelligence Layer for Communities -- Decision Intelligence backend.",
    version="0.1.0-mvp",
)

# Allow the local Vite dev server / any frontend origin during hackathon dev.
# Tighten this before submission if needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(localities.router)
app.include_router(dashboard.router)
app.include_router(assistant.router)


@app.get("/")
def root():
    return {
        "project": "Project Synapse",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
