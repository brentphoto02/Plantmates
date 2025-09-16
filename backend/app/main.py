from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .db.session import init_db
from .routers import listings, matches, ratings, swaps, threads, users

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize database tables on application start."""

    init_db()


app.include_router(users.router)
app.include_router(listings.router)
app.include_router(matches.router)
app.include_router(threads.router)
app.include_router(swaps.router)
app.include_router(ratings.router)


@app.get("/health", tags=["utility"])
def healthcheck() -> dict[str, str]:
    """Simple healthcheck endpoint for monitoring."""

    return {"status": "ok"}
