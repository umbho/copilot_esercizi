"""
FastAPI Tests for Mergington High School Activities API

Tests follow the AAA (Arrange-Act-Assert) pattern for clarity:
- ARRANGE: Set up test data and preconditions
- ACT: Perform the operation
- ASSERT: Verify the response and side effects
"""

import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all activities with correct structure.
        """
        # ARRANGE
        expected_activity_count = 9
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert activity_data.keys() == expected_fields

    def test_get_activities_contains_chess_club(self, client):
        """Test that Chess Club is included in activities."""
        # ARRANGE
        # (no setup needed, client fixture handles it)

        # ACT
        response = client.get("/activities")

        # ASSERT
        data = response.json()
        assert "Chess Club" in data
        assert data["Chess Club"]["max_participants"] == 12
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]

    def test_get_activities_participants_intact(self, client):
        """Test that participants lists are returned correctly."""
        # ARRANGE
        # (no setup needed)

        # ACT
        response = client.get("/activities")

        # ASSERT
        data = response.json()
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, existing_activity, valid_email):
        """
        Test that a new student can successfully sign up for an activity.
        """
        # ARRANGE
        activity_name = existing_activity
        email = valid_email

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_student(self, client, existing_activity, existing_participant):
        """
        Test that a student cannot sign up twice for the same activity (bug fix).
        """
        # ARRANGE
        activity_name = existing_activity
        email = existing_participant
        initial_count = len(activities[activity_name]["participants"])

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
        assert len(activities[activity_name]["participants"]) == initial_count

    def test_signup_activity_not_found(self, client, nonexistent_activity, valid_email):
        """
        Test that signing up for a nonexistent activity returns 404.
        """
        # ARRANGE
        activity_name = nonexistent_activity
        email = valid_email

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_adds_to_participants_list(self, client, existing_activity, valid_email):
        """
        Test that signing up actually adds the participant to the list.
        """
        # ARRANGE
        activity_name = existing_activity
        email = valid_email
        initial_count = len(activities[activity_name]["participants"])

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert email in activities[activity_name]["participants"]

    def test_signup_multiple_different_students(self, client, existing_activity):
        """
        Test that multiple different students can sign up for the same activity.
        """
        # ARRANGE
        activity_name = existing_activity
        emails = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        initial_count = len(activities[activity_name]["participants"])

        # ACT
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200

        # ASSERT
        assert len(activities[activity_name]["participants"]) == initial_count + len(emails)
        for email in emails:
            assert email in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, existing_activity, existing_participant):
        """
        Test that a participant can successfully unregister from an activity.
        """
        # ARRANGE
        activity_name = existing_activity
        email = existing_participant
        initial_count = len(activities[activity_name]["participants"])

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_not_registered(self, client, existing_activity, valid_email):
        """
        Test that unregistering a non-participant returns 400.
        """
        # ARRANGE
        activity_name = existing_activity
        email = valid_email
        initial_count = len(activities[activity_name]["participants"])

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
        assert len(activities[activity_name]["participants"]) == initial_count

    def test_unregister_activity_not_found(self, client, nonexistent_activity, valid_email):
        """
        Test that unregistering from a nonexistent activity returns 404.
        """
        # ARRANGE
        activity_name = nonexistent_activity
        email = valid_email

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_removes_from_participants_list(self, client, existing_activity, existing_participant):
        """
        Test that unregistering actually removes the participant from the list.
        """
        # ARRANGE
        activity_name = existing_activity
        email = existing_participant

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_unregister_and_reregister(self, client, existing_activity, existing_participant):
        """
        Test that a student can unregister and then register again.
        """
        # ARRANGE
        activity_name = existing_activity
        email = existing_participant

        # ACT - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT - Unregister succeeded
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]

        # ACT - Register again
        register_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT - Register succeeded
        assert register_response.status_code == 200
        assert email in activities[activity_name]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        Test that GET / redirects to /static/index.html.
        """
        # ARRANGE
        # (no setup needed)

        # ACT
        response = client.get("/", follow_redirects=False)

        # ASSERT
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_follows(self, client):
        """
        Test that following the redirect from GET / works (optional test).
        """
        # ARRANGE
        # (no setup needed)

        # ACT
        response = client.get("/", follow_redirects=True)

        # ASSERT
        assert response.status_code == 200
        assert response.text
