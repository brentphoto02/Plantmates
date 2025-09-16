# PlantMates API (FastAPI)

This directory contains the first iteration of the PlantMates backend API.
It follows the product spec in `instructions` and provides the core building
blocks for the marketplace MVP: user profiles, listings, swipe/match flows,
chat threads, swap lifecycle management, and trust ratings.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

The application uses SQLite by default (`plantmates.db`). Set the
`DATABASE_URL` environment variable to point at PostgreSQL or another SQLAlchemy
compatible database when you're ready to scale.

## Running the tests

```bash
pytest backend/tests
```

The tests spin up the FastAPI app against an isolated temporary SQLite
database to exercise an end-to-end swap flow.
