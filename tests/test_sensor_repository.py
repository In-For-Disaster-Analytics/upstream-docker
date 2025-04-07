import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.db.repositories.sensor_repository import SensorRepository
from app.db.models.sensor import Sensor
from app.api.v1.schemas.sensor import SensorIn

@pytest.fixture
def sensor_repository(mock_db_session_with_query: MagicMock) -> SensorRepository:
    return SensorRepository(mock_db_session_with_query)

@pytest.fixture
def sample_sensors() -> list[Sensor]:
    return [
        Sensor(
            stationid=1,
            alias="temp_sensor",
            description="Temperature sensor with post-processing",
            postprocess=True,
            postprocessscript="temp * 1.8 + 32",
            units="°F",
            variablename="temperature"
        ),
        Sensor(
            stationid=1,
            alias="humidity_sensor",
            description="Humidity measurement sensor",
            postprocess=False,
            postprocessscript=None,
            units="%",
            variablename="humidity"
        ),
        Sensor(
            stationid=2,
            alias="pressure_sensor",
            description="Atmospheric pressure sensor",
            postprocess=True,
            postprocessscript="pressure * 0.000145038",
            units="psi",
            variablename="pressure"
        )
    ]

def test_get_sensors_by_station_id_basic(sensor_repository: SensorRepository, sample_sensors: list[Sensor], mock_query: MagicMock):
    # Setup mock to return sample sensors for station_id=1
    station_1_sensors = [s for s in sample_sensors if s.stationid == 1]
    mock_query.all.return_value = station_1_sensors
    mock_query.count.return_value = len(station_1_sensors)

    # Call the method
    sensors, total_count = sensor_repository.get_sensors_by_station_id(station_id=1)

    # Verify results
    assert len(sensors) == 2
    assert total_count == 2
    assert all(s.stationid == 1 for s in sensors)

    # Verify mock was called correctly
    mock_query.filter.assert_called_once()
    mock_query.all.assert_called_once()

def test_get_sensors_by_station_id_with_variable_name_filter(sensor_repository: SensorRepository, sample_sensors: list[Sensor], mock_query: MagicMock):
    # Setup mock to return filtered sensors
    filtered_sensors = [s for s in sample_sensors if s.stationid == 1 and "temp" in s.variablename.lower()]
    mock_query.all.return_value = filtered_sensors
    mock_query.count.return_value = len(filtered_sensors)

    # Call the method
    sensors, total_count = sensor_repository.get_sensors_by_station_id(
        station_id=1,
        variable_name="temp"
    )

    # Verify results
    assert len(sensors) == 1
    assert total_count == 1
    assert sensors[0].variablename == "temperature"

    # Verify mock was called correctly
    assert mock_query.filter.call_count >= 2  # At least station_id and variable_name filters

def test_get_sensors_by_station_id_with_units_filter(sensor_repository: SensorRepository, sample_sensors: list[Sensor], mock_query: MagicMock):
    # Setup mock to return filtered sensors
    filtered_sensors = [s for s in sample_sensors if s.stationid == 1 and s.units == "%"]
    mock_query.all.return_value = filtered_sensors
    mock_query.count.return_value = len(filtered_sensors)

    # Call the method
    sensors, total_count = sensor_repository.get_sensors_by_station_id(
        station_id=1,
        units="%"
    )

    # Verify results
    assert len(sensors) == 1
    assert total_count == 1
    assert sensors[0].units == "%"

    # Verify mock was called correctly
    assert mock_query.filter.call_count >= 2  # At least station_id and units filters

def test_get_sensors_by_station_id_with_alias_filter(sensor_repository: SensorRepository, sample_sensors: list[Sensor], mock_query: MagicMock):
    # Setup mock to return filtered sensors
    filtered_sensors = [s for s in sample_sensors if s.stationid == 1 and "temp" in s.alias.lower()]
    mock_query.all.return_value = filtered_sensors
    mock_query.count.return_value = len(filtered_sensors)

    # Call the method
    sensors, total_count = sensor_repository.get_sensors_by_station_id(
        station_id=1,
        alias="temp"
    )

    # Verify results
    assert len(sensors) == 1
    assert total_count == 1
    assert sensors[0].alias == "temp_sensor"

    # Verify mock was called correctly
    assert mock_query.filter.call_count >= 2  # At least station_id and alias filters

def test_get_sensors_by_station_id_with_description_filter(sensor_repository: SensorRepository, sample_sensors: list[Sensor], mock_query: MagicMock):
    # Setup mock to return filtered sensors
    filtered_sensors = [s for s in sample_sensors if s.stationid == 1 and s.description and "Temperature" in s.description]
    mock_query.all.return_value = filtered_sensors
    mock_query.count.return_value = len(filtered_sensors)

    # Call the method
    sensors, total_count = sensor_repository.get_sensors_by_station_id(
        station_id=1,
        description_contains="Temperature"
    )

    # Verify results
    assert len(sensors) == 1
    assert total_count == 1
    assert sensors[0].description is not None
    assert "Temperature" in sensors[0].description

    # Verify mock was called correctly
    assert mock_query.filter.call_count >= 2  # At least station_id and description filters

def test_get_sensors_by_station_id_with_postprocess_filter(sensor_repository: SensorRepository, sample_sensors: list[Sensor], mock_query: MagicMock):
    # Setup mock to return filtered sensors
    filtered_sensors = [s for s in sample_sensors if s.stationid == 1 and s.postprocess is True]
    mock_query.all.return_value = filtered_sensors
    mock_query.count.return_value = len(filtered_sensors)

    # Call the method
    sensors, total_count = sensor_repository.get_sensors_by_station_id(
        station_id=1,
        postprocess=True
    )

    # Verify results
    assert len(sensors) == 1
    assert total_count == 1
    assert sensors[0].postprocess is True

    # Verify mock was called correctly
    assert mock_query.filter.call_count >= 2  # At least station_id and postprocess filters

def test_get_sensors_by_station_id_pagination(sensor_repository: SensorRepository, sample_sensors: list[Sensor], mock_query: MagicMock):
    # Create a larger set of sensors for pagination testing
    all_sensors = sample_sensors.copy()
    for i in range(5):
        sensor = Sensor(
            stationid=1,
            alias=f"test_sensor_{i}",
            description=f"Test sensor {i}",
            postprocess=False,
            units="test",
            variablename=f"test_{i}"
        )
        all_sensors.append(sensor)

    # Setup mock to return all sensors for station_id=1
    station_1_sensors = [s for s in all_sensors if s.stationid == 1]
    mock_query.count.return_value = len(station_1_sensors)

    # Test first page
    mock_query.all.return_value = station_1_sensors[:3]
    sensors, total_count = sensor_repository.get_sensors_by_station_id(
        station_id=1,
        page=1,
        limit=3
    )
    assert len(sensors) == 3
    assert total_count == 7  # 2 original + 5 new sensors

    # Test second page
    mock_query.all.return_value = station_1_sensors[3:6]
    sensors, total_count = sensor_repository.get_sensors_by_station_id(
        station_id=1,
        page=2,
        limit=3
    )
    assert len(sensors) == 3
    assert total_count == 7

    # Test last page
    mock_query.all.return_value = station_1_sensors[6:7]
    sensors, total_count = sensor_repository.get_sensors_by_station_id(
        station_id=1,
        page=3,
        limit=3
    )
    assert len(sensors) == 1
    assert total_count == 7

    # Verify pagination methods were called
    assert mock_query.offset.call_count == 3
    assert mock_query.limit.call_count == 3

def test_get_sensors_by_station_id_combined_filters(sensor_repository: SensorRepository, sample_sensors: list[Sensor], mock_query: MagicMock):
    # Setup mock to return filtered sensors
    filtered_sensors = [
        s for s in sample_sensors
        if s.stationid == 1
        and "temp" in s.variablename.lower()
        and s.units == "°F"
        and s.postprocess is True
    ]
    mock_query.all.return_value = filtered_sensors
    mock_query.count.return_value = len(filtered_sensors)

    # Call the method
    sensors, total_count = sensor_repository.get_sensors_by_station_id(
        station_id=1,
        variable_name="temp",
        units="°F",
        postprocess=True
    )

    # Verify results
    assert len(sensors) == 1
    assert total_count == 1
    assert sensors[0].variablename == "temperature"
    assert sensors[0].units == "°F"
    assert sensors[0].postprocess is True

    # Verify mock was called correctly
    assert mock_query.filter.call_count >= 4  # At least station_id and all three filters