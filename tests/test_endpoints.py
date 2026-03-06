"""
Tests for FastAPI endpoints using the AAA (Arrange-Act-Assert) pattern.

Each test is structured as:
- Arrange: Set up test data and preconditions
- Act: Execute the endpoint
- Assert: Verify the response and side effects
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, sample_activities):
        """Test that GET /activities returns all activities with correct data.
        
        Arrange: Test data is already set up via fixtures
        Act: Make a GET request to /activities
        Assert: Verify response contains all activities with correct structure
        """
        # Arrange: already done by fixtures

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 3
        assert "Test Chess Club" in activities
        assert "Test Programming" in activities
        assert "Test Gym" in activities
        
        # Verify structure of individual activities
        chess_club = activities["Test Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["max_participants"] == 3
        assert len(chess_club["participants"]) == 2

    def test_get_activities_includes_participant_count(self, client):
        """Test that activities include participant information.
        
        Arrange: Test data with known participants
        Act: Fetch activities
        Assert: Verify participant lists are present and correct
        """
        # Arrange: using fixtures

        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        gym = activities["Test Gym"]
        assert gym["participants"] == []
        
        programming = activities["Test Programming"]
        assert len(programming["participants"]) == 1
        assert "student3@test.edu" in programming["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Test successful signup for an activity.
        
        Arrange: Test activity and new email
        Act: Sign up a new student
        Assert: Verify success response and participant added
        """
        # Arrange
        activity_name = "Test Gym"
        email = "newstudent@test.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds participant to the activity.
        
        Arrange: Get initial participant count
        Act: Sign up a new student
        Assert: Verify participant count increased
        """
        # Arrange
        activity_name = "Test Programming"
        email = "newstudent@test.edu"
        
        # Get initial participant count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity_name]["participants"])

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity_name]["participants"])
        assert final_count == initial_count + 1
        assert email in response_after.json()[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup fails when activity doesn't exist.
        
        Arrange: Non-existent activity name
        Act: Attempt signup
        Assert: Verify 404 error
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@test.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_email_rejected(self, client):
        """Test that a student cannot sign up twice for the same activity.
        
        Arrange: Student already signed up for an activity
        Act: Attempt to sign up again with same email
        Assert: Verify 400 error
        """
        # Arrange
        activity_name = "Test Chess Club"
        email = "student1@test.edu"  # Already signed up in sample_activities

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_same_email_different_activities(self, client):
        """Test that a student can sign up for multiple different activities.
        
        Arrange: Student signed up for one activity
        Act: Sign up for a different activity
        Assert: Verify success
        """
        # Arrange
        email = "student1@test.edu"
        activity1 = "Test Chess Club"
        activity2 = "Test Programming"
        
        # Verify student is already in activity1
        response = client.get("/activities")
        assert email in response.json()[activity1]["participants"]

        # Act: Sign up for activity2
        response = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        response = client.get("/activities")
        assert email in response.json()[activity2]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity.
        
        Arrange: Student currently signed up for activity
        Act: Unregister the student
        Assert: Verify success response
        """
        # Arrange
        activity_name = "Test Chess Club"
        email = "student1@test.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant from activity.
        
        Arrange: Get initial participant count
        Act: Unregister a student
        Assert: Verify participant count decreased
        """
        # Arrange
        activity_name = "Test Chess Club"
        email = "student1@test.edu"
        
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity_name]["participants"])

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity_name]["participants"])
        assert final_count == initial_count - 1
        assert email not in response_after.json()[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister fails when activity doesn't exist.
        
        Arrange: Non-existent activity name
        Act: Attempt unregister
        Assert: Verify 404 error
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@test.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_signed_up(self, client):
        """Test unregister fails when student is not signed up for activity.
        
        Arrange: Student not in activity's participants
        Act: Attempt to unregister
        Assert: Verify 400 error
        """
        # Arrange
        activity_name = "Test Gym"  # Has no participants
        email = "student@test.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_then_signup_again(self, client):
        """Test that student can sign up for activity after unregistering.
        
        Arrange: Student signed up for activity
        Act: Unregister, then sign up again
        Assert: Verify both operations succeed
        """
        # Arrange
        activity_name = "Test Chess Club"
        email = "student1@test.edu"

        # Act: Unregister
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert unregister succeeded
        assert response1.status_code == 200
        
        # Act: Sign up again
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert signup succeeded
        assert response2.status_code == 200
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
