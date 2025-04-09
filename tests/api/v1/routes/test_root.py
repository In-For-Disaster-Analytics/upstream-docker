import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import jwt
from app.main import app
from app.core.config import Settings

client = TestClient(app)

# Test data
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_password"
TEST_TOKEN = "test.jwt.token"
TEST_JWT_SECRET = "test_secret"

@pytest.fixture
def mock_settings():
    with patch("app.core.config.get_settings") as mock:
        settings = Settings(
            JWT_SECRET=TEST_JWT_SECRET,
            TAS_USER=TEST_USERNAME,
            TAS_SECRET=TEST_PASSWORD,
            TAS_URL='http://localhost:5432',
            ALG="HS256",
            ENV="test",
            ENVIRONMENT="test",
            # Add any missing required settings here
            POSTGRES_PASSWORD="test",  # Add this if required
            DATABASE_URL="test"        # Add this if required
        )
        mock.return_value = settings
        yield mock

@pytest.fixture
def mock_authenticate_user():
    with patch("app.api.v1.routes.root.authenticate_user") as mock:
        mock.return_value = True
        yield mock

def test_login_success(mock_settings, mock_authenticate_user):
    response = client.post(
        "/api/v1/token",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    # Verify the token is valid
    token = response.json()["access_token"]
    decoded = jwt.decode(token, TEST_JWT_SECRET, algorithms=["HS256"])
    assert decoded["username"] == TEST_USERNAME

def test_login_failure(mock_settings):
    with patch("app.api.v1.routes.root.authenticate_user") as mock:
        mock.return_value = False
        response = client.post(
            "/api/v1/token",
            data={"username": TEST_USERNAME, "password": "wrong_password"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Incorrect username or password"

def test_login_missing_credentials():
    response = client.post("/api/v1/token", data={})
    assert response.status_code == 422  # FastAPI validation error
