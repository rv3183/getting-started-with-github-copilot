"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive soccer team training and matches",
            "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Pickup games, drills, and interschool competitions",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "mason@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu", "charlotte@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops, rehearsals, and stage productions",
            "schedule": "Fridays, 4:00 PM - 6:30 PM",
            "max_participants": 25,
            "participants": ["ethan@mergington.edu", "mia@mergington.edu"]
        },
        "Math Club": {
            "description": "Problem solving, competitions, and math enrichment",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["oliver@mergington.edu", "sophia.b@mergington.edu"]
        },
        "Debate Team": {
            "description": "Public speaking, argumentation practice, and tournaments",
            "schedule": "Tuesdays, 5:00 PM - 6:30 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu", "grace@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test (reset again)
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Should have 9 activities
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Chess Club structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_participants_count(self, client):
        """Test that activities return correct participant counts"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Programming Class"]["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signup is rejected"""
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response1.status_code == 400
        
        data = response1.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_with_special_characters(self, client):
        """Test signup with email containing special characters"""
        email = "test.student+1@mergington.edu"
        # Properly encode the + character as %2B for URL
        encoded_email = email.replace("+", "%2B")
        
        response = client.post(
            f"/activities/Programming%20Class/signup?email={encoded_email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Programming Class"]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_remove_participant_success(self, client):
        """Test successfully removing a participant"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
        assert "michael@mergington.edu" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_remove_participant_activity_not_found(self, client):
        """Test removing participant from non-existent activity"""
        response = client.delete(
            "/activities/NonExistent%20Club/participants?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_remove_participant_not_enrolled(self, client):
        """Test removing participant who is not enrolled"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=notaparticipant@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Participant not found" in data["detail"]
    
    def test_remove_participant_reduces_count(self, client):
        """Test that removing participant reduces the count"""
        # Get initial count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()["Drama Club"]["participants"])
        
        # Remove a participant
        response = client.delete(
            "/activities/Drama%20Club/participants?email=ethan@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify count decreased
        activities_response = client.get("/activities")
        final_count = len(activities_response.json()["Drama Club"]["participants"])
        assert final_count == initial_count - 1


class TestIntegrationScenarios:
    """Integration tests for common user workflows"""
    
    def test_signup_and_remove_workflow(self, client):
        """Test complete workflow: signup and then remove"""
        email = "workflow@mergington.edu"
        activity = "Math Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        
        # Remove
        remove_response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants?email={email}"
        )
        assert remove_response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]
    
    def test_multiple_signups_different_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for Soccer Team
        response1 = client.post(
            f"/activities/Soccer%20Team/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Basketball Club
        response2 = client.post(
            f"/activities/Basketball%20Club/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Soccer Team"]["participants"]
        assert email in activities_data["Basketball Club"]["participants"]
