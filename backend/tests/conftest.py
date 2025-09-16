from __future__ import annotations

import os
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Configure a temporary SQLite database for the test session before importing the app.
tmp_fd, tmp_path = tempfile.mkstemp(prefix="plantmates-test-", suffix=".db")
os.close(tmp_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path}"

from backend.app import main  # noqa: E402  pylint: disable=wrong-import-position


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Provide a FastAPI test client backed by a temporary database."""

    with TestClient(main.app) as test_client:
        yield test_client
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
