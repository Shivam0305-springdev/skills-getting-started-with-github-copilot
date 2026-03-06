import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def sample_activities():
    """Fixture providing sample test activities with known data."""
    return {
        "Test Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": ["student1@test.edu", "student2@test.edu"]
        },
        "Test Programming": {
            "description": "Learn programming fundamentals",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 5,
            "participants": ["student3@test.edu"]
        },
        "Test Gym": {
            "description": "Physical education activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 2,
            "participants": []
        }
    }


@pytest.fixture
def client(monkeypatch, sample_activities):
    """Fixture providing a TestClient with isolated test data for each test.
    
    Uses monkeypatch to replace the app's global activities dictionary
    with fresh test data for each test, ensuring test isolation.
    """
    # Replace the app's global activities with test data
    monkeypatch.setattr("src.app.activities", sample_activities)
    
    # Return a TestClient for making HTTP requests
    return TestClient(app)
