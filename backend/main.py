"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.connection import init_db
from backend.routes import documents, memory, chat, query, users, audit, demo


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title="Change Impact Memory",
    description="AI that reconstructs enterprise decision reasoning from fragmented evidence",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(documents.router)
app.include_router(memory.router)
app.include_router(chat.router)
app.include_router(query.router)
app.include_router(users.router)
app.include_router(audit.router)
app.include_router(demo.router)


@app.get("/")
def root():
    return {
        "name": "Change Impact Memory",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}
