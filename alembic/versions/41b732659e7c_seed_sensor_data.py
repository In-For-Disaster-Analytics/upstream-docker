"""seed_sensor_data

Revision ID: 41b732659e7c
Revises: ad29f393da25
Create Date: 2025-03-19 16:30:39.556710

"""
import os
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column
from dotenv import load_dotenv


# revision identifiers, used by Alembic.
revision: str = '41b732659e7c'
down_revision: Union[str, None] = 'ad29f393da25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def is_dev_environment():
    return os.getenv('ENVIRONMENT') == 'development' or os.getenv('ENVIRONMENT') == 'dev'


def upgrade() -> None:
    if not is_dev_environment():
        return
    """Add seed data for sensors."""
    sensors_table = table('sensors',
        column('sensorid', sa.Integer),
        column('stationid', sa.Integer),
        column('alias', sa.String),
        column('description', sa.String),
        column('postprocess', sa.Boolean),
        column('postprocessscript', sa.String),
        column('units', sa.String),
        column('variablename', sa.String)
    )

    # Common sensor configurations for weather stations
    weather_sensors = [
        # Temperature sensor
        {
            'alias': 'TEMP',
            'description': 'Air temperature sensor',
            'postprocess': True,
            'postprocessscript': 'temperature_qc.py',
            'units': '°C',
            'variablename': 'temperature'
        },
        # Humidity sensor
        {
            'alias': 'HUM',
            'description': 'Relative humidity sensor',
            'postprocess': True,
            'postprocessscript': 'humidity_qc.py',
            'units': '%',
            'variablename': 'humidity'
        },
        # Wind speed sensor
        {
            'alias': 'WSPD',
            'description': 'Wind speed sensor',
            'postprocess': True,
            'postprocessscript': 'wind_qc.py',
            'units': 'm/s',
            'variablename': 'wind_speed'
        },
        # Wind direction sensor
        {
            'alias': 'WDIR',
            'description': 'Wind direction sensor',
            'postprocess': True,
            'postprocessscript': 'wind_qc.py',
            'units': 'degrees',
            'variablename': 'wind_direction'
        },
        # Pressure sensor
        {
            'alias': 'PRES',
            'description': 'Barometric pressure sensor',
            'postprocess': True,
            'postprocessscript': 'pressure_qc.py',
            'units': 'hPa',
            'variablename': 'pressure'
        },
        # Precipitation sensor
        {
            'alias': 'RAIN',
            'description': 'Precipitation sensor',
            'postprocess': True,
            'postprocessscript': 'precipitation_qc.py',
            'units': 'mm',
            'variablename': 'precipitation'
        },
        # Solar radiation sensor
        {
            'alias': 'SRAD',
            'description': 'Solar radiation sensor',
            'postprocess': True,
            'postprocessscript': 'radiation_qc.py',
            'units': 'W/m²',
            'variablename': 'solar_radiation'
        }
    ]

    # Add sensors for each weather station (stations 1-5)
    sensor_records = []
    sensor_id = 1
    for station_id in range(1, 6):  # Weather Network stations
        for sensor in weather_sensors:
            sensor_record = sensor.copy()
            sensor_record['sensorid'] = sensor_id
            sensor_record['stationid'] = station_id
            sensor_records.append(sensor_record)
            sensor_id += 1

    # Add basic sensors for test station (station 6)
    test_sensors = [
        {
            'sensorid': sensor_id,
            'stationid': 6,
            'alias': 'TEST-TEMP',
            'description': 'Test temperature sensor',
            'postprocess': False,
            'postprocessscript': None,
            'units': '°C',
            'variablename': 'temperature'
        },
        {
            'sensorid': sensor_id + 1,
            'stationid': 6,
            'alias': 'TEST-HUM',
            'description': 'Test humidity sensor',
            'postprocess': False,
            'postprocessscript': None,
            'units': '%',
            'variablename': 'humidity'
        }
    ]
    sensor_records.extend(test_sensors)

    # Insert all sensor records
    op.get_bind().execute(
        sensors_table.insert().values(sensor_records)
    )


def downgrade() -> None:
    """Remove seed data."""
    op.get_bind().execute(
        sa.text('DELETE FROM sensors WHERE sensorid BETWEEN 1 AND 37')
    )
