"""FastAPI routers exposed for application composition."""

from . import listings, matches, ratings, swaps, threads, users

__all__ = [
    "listings",
    "matches",
    "ratings",
    "swaps",
    "threads",
    "users",
]
