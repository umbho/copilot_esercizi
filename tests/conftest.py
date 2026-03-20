"""
Pytest configuration and fixtures for FastAPI tests.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(scope="session")
def original_activities():
    """Store a deep copy of the original activities state at session start."""
    return copy.deepcopy(activities)


@pytest.fixture
def client(original_activities):
    """
    Provide a TestClient instance with activities reset before each test.
    This ensures test isolation and a clean state for each test.
    """
    # Reset activities to original state before test with a deep copy
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    
    return TestClient(app)


@pytest.fixture
def valid_email():
    """A valid email that is not pre-registered in any activity."""
    return "newstudent@mergington.edu"


@pytest.fixture
def existing_participant():
    """An email that is already registered in Chess Club."""
    return "michael@mergington.edu"


@pytest.fixture
def existing_activity():
    """The name of an existing activity."""
    return "Chess Club"


@pytest.fixture
def nonexistent_activity():
    """The name of an activity that does not exist."""
    return "Nonexistent Club"
