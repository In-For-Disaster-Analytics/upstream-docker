import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.db.models.sensor import Sensor
from app.api.v1.schemas.sensor import SensorIn
from app.db.repositories.sensor_repository import SensorRepository

# Test JWT secret
TEST_JWT_SECRET = "test_secret"
TEST_JWT_ALGORITHM = "HS256"

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Create authentication headers with a JWT token"""
    # Create a test token
    payload = {
        "sub": "test_user",
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, TEST_JWT_SECRET, algorithm=TEST_JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_sensors() -> list[Sensor]:
    return [
        Sensor(
            sensorid=1,
            stationid=1,
            alias="temp_sensor",
            description="Temperature sensor with post-processing",
            postprocess=True,
            postprocessscript="temp * 1.8 + 32",
            units="°F",
            variablename="temperature"
        ),
        Sensor(
            sensorid=2,
            stationid=1,
            alias="humidity_sensor",
            description="Humidity measurement sensor",
            postprocess=False,
            postprocessscript=None,
            units="%",
            variablename="humidity"
        ),
        Sensor(
            sensorid=3,
            stationid=1,
            alias="pressure_sensor",
            description="Atmospheric pressure sensor",
            postprocess=True,
            postprocessscript="pressure * 0.000145038",
            units="psi",
            variablename="pressure"
        )
    ]

@pytest.fixture
def mock_sensor_repository(sample_sensors: list[Sensor]) -> MagicMock:
    repository = MagicMock(spec=SensorRepository)

    def get_sensors_by_station_id_mock(station_id, page=1, limit=20, variable_name=None,
                                      units=None, alias=None, description_contains=None,
                                      postprocess=None):
        # Filter sensors based on parameters
        filtered_sensors = sample_sensors.copy()

        # Apply station_id filter
        filtered_sensors = [s for s in filtered_sensors if s.stationid == station_id]

        # Apply variable_name filter
        if variable_name:
            filtered_sensors = [s for s in filtered_sensors if s.variablename and variable_name.lower() in s.variablename.lower()]

        # Apply units filter
        if units:
            filtered_sensors = [s for s in filtered_sensors if s.units == units]

        # Apply alias filter
        if alias:
            filtered_sensors = [s for s in filtered_sensors if s.alias and alias.lower() in s.alias.lower()]

        # Apply description filter
        if description_contains:
            filtered_sensors = [s for s in filtered_sensors if s.description and description_contains in s.description]

        # Apply postprocess filter
        if postprocess is not None:
            filtered_sensors = [s for s in filtered_sensors if s.postprocess == postprocess]

        # Apply pagination
        total_count = len(filtered_sensors)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_sensors = filtered_sensors[start_idx:end_idx]

        return paginated_sensors, total_count

    repository.get_sensors_by_station_id.side_effect = get_sensors_by_station_id_mock
    return repository

@patch('app.api.v1.routes.campaigns.campaign_station_sensors.SensorRepository')
@patch('app.core.config.get_settings')
def test_list_sensors_basic(mock_get_settings, mock_repository_class, client: TestClient, sample_sensors: list[Sensor], mock_sensor_repository: MagicMock, auth_headers):
    # Setup mocks
    mock_repository_class.return_value = mock_sensor_repository
    mock_settings = MagicMock()
    mock_settings.JWT_SECRET = TEST_JWT_SECRET
    mock_settings.ALG = TEST_JWT_ALGORITHM
    mock_get_settings.return_value = mock_settings

    # Make request with auth headers
    response = client.get("/api/v1/campaigns/1/stations/1/sensors", headers=auth_headers)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["size"] == 20
    assert data["pages"] == 1


@patch('app.api.v1.routes.campaigns.campaign_station_sensors.SensorRepository')
@patch('app.core.config.get_settings')
def test_list_sensors_with_variable_name_filter(mock_get_settings, mock_repository_class, client: TestClient, sample_sensors: list[Sensor], mock_sensor_repository: MagicMock, auth_headers):
    # Setup mocks
    mock_repository_class.return_value = mock_sensor_repository
    mock_settings = MagicMock()
    mock_settings.JWT_SECRET = TEST_JWT_SECRET
    mock_settings.ALG = TEST_JWT_ALGORITHM
    mock_get_settings.return_value = mock_settings

    # Make request with auth headers
    response = client.get("/api/v1/campaigns/1/stations/1/sensors?variable_name=temp", headers=auth_headers)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["variablename"] == "temperature"

@patch('app.api.v1.routes.campaigns.campaign_station_sensors.SensorRepository')
@patch('app.core.config.get_settings')
def test_list_sensors_with_units_filter(mock_get_settings, mock_repository_class, client: TestClient, sample_sensors: list[Sensor], mock_sensor_repository: MagicMock, auth_headers):
    # Setup mocks
    mock_repository_class.return_value = mock_sensor_repository
    mock_settings = MagicMock()
    mock_settings.JWT_SECRET = TEST_JWT_SECRET
    mock_settings.ALG = TEST_JWT_ALGORITHM
    mock_get_settings.return_value = mock_settings

    # Make request with auth headers
    response = client.get("/api/v1/campaigns/1/stations/1/sensors?units=%", headers=auth_headers)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["units"] == "%"


@patch('app.api.v1.routes.campaigns.campaign_station_sensors.SensorRepository')
@patch('app.core.config.get_settings')
def test_list_sensors_with_alias_filter(mock_get_settings, mock_repository_class, client: TestClient, sample_sensors: list[Sensor], mock_sensor_repository: MagicMock, auth_headers):
    # Setup mocks
    mock_repository_class.return_value = mock_sensor_repository
    mock_settings = MagicMock()
    mock_settings.JWT_SECRET = TEST_JWT_SECRET
    mock_settings.ALG = TEST_JWT_ALGORITHM
    mock_get_settings.return_value = mock_settings

    # Make request with auth headers
    response = client.get("/api/v1/campaigns/1/stations/1/sensors?alias=temp", headers=auth_headers)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["alias"] == "temp_sensor"


@patch('app.api.v1.routes.campaigns.campaign_station_sensors.SensorRepository')
@patch('app.core.config.get_settings')
def test_list_sensors_with_description_filter(mock_get_settings, mock_repository_class, client: TestClient, sample_sensors: list[Sensor], mock_sensor_repository: MagicMock, auth_headers):
    # Setup mocks
    mock_repository_class.return_value = mock_sensor_repository
    mock_settings = MagicMock()
    mock_settings.JWT_SECRET = TEST_JWT_SECRET
    mock_settings.ALG = TEST_JWT_ALGORITHM
    mock_get_settings.return_value = mock_settings

    # Make request with auth headers
    response = client.get("/api/v1/campaigns/1/stations/1/sensors?description_contains=Temperature", headers=auth_headers)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert "Temperature" in data["items"][0]["description"]


@patch('app.api.v1.routes.campaigns.campaign_station_sensors.SensorRepository')
@patch('app.core.config.get_settings')
def test_list_sensors_with_postprocess_filter(mock_get_settings, mock_repository_class, client: TestClient, sample_sensors: list[Sensor], mock_sensor_repository: MagicMock, auth_headers):
    # Setup mocks
    mock_repository_class.return_value = mock_sensor_repository
    mock_settings = MagicMock()
    mock_settings.JWT_SECRET = TEST_JWT_SECRET
    mock_settings.ALG = TEST_JWT_ALGORITHM
    mock_get_settings.return_value = mock_settings

    # Make request with auth headers
    response = client.get("/api/v1/campaigns/1/stations/1/sensors?postprocess=true", headers=auth_headers)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert all(item["postprocess"] is True for item in data["items"])

@patch('app.api.v1.routes.campaigns.campaign_station_sensors.SensorRepository')
@patch('app.core.config.get_settings')
def test_list_sensors_pagination(mock_get_settings, mock_repository_class, client: TestClient, sample_sensors: list[Sensor], mock_sensor_repository: MagicMock, auth_headers):
    # Setup mocks
    mock_repository_class.return_value = mock_sensor_repository
    mock_settings = MagicMock()
    mock_settings.JWT_SECRET = TEST_JWT_SECRET
    mock_settings.ALG = TEST_JWT_ALGORITHM
    mock_get_settings.return_value = mock_settings

    # Test first page
    response = client.get("/api/v1/campaigns/1/stations/1/sensors?page=1&limit=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["size"] == 2
    assert data["pages"] == 2

    # Test second page
    response = client.get("/api/v1/campaigns/1/stations/1/sensors?page=2&limit=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 3
    assert data["page"] == 2
    assert data["size"] == 2
    assert data["pages"] == 2


@patch('app.api.v1.routes.campaigns.campaign_station_sensors.SensorRepository')
@patch('app.core.config.get_settings')
def test_list_sensors_combined_filters(mock_get_settings, mock_repository_class, client: TestClient, sample_sensors: list[Sensor], mock_sensor_repository: MagicMock, auth_headers):
    # Setup mocks
    mock_repository_class.return_value = mock_sensor_repository
    mock_settings = MagicMock()
    mock_settings.JWT_SECRET = TEST_JWT_SECRET
    mock_settings.ALG = TEST_JWT_ALGORITHM
    mock_get_settings.return_value = mock_settings

    # Make request with auth headers
    response = client.get(
        "/api/v1/campaigns/1/stations/1/sensors"
        "?variable_name=temp"
        "&units=°F"
        "&postprocess=true",
        headers=auth_headers
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["variablename"] == "temperature"
    assert data["items"][0]["units"] == "°F"
    assert data["items"][0]["postprocess"] is True

@patch('app.api.v1.routes.campaigns.campaign_station_sensors.SensorRepository')
@patch('app.core.config.get_settings')
def test_list_sensors_unauthorized(mock_get_settings, mock_repository_class, client: TestClient):
    # Setup mocks
    mock_settings = MagicMock()
    mock_settings.JWT_SECRET = TEST_JWT_SECRET
    mock_settings.ALG = TEST_JWT_ALGORITHM
    mock_get_settings.return_value = mock_settings

    # Make request without auth headers
    response = client.get("/api/v1/campaigns/1/stations/1/sensors")

    # Verify response
    assert response.status_code == 401  # Unauthorized