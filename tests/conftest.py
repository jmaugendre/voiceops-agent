from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import audit, erp, workflow


@pytest.fixture(autouse=True)
def reset_state():
    """Each test gets a fresh synthetic ERP, no pending transactions, no audit log."""

    erp.reset()
    workflow.reset()
    audit.reset()
    yield


@pytest.fixture()
def client():
    return TestClient(app)
