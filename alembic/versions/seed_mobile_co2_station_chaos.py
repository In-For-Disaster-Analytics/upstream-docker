"""seed_mobile_co2_station

Revision ID: seed_mobile_co2_station
Revises: 9e7f71ac2376
Create Date: 2024-03-28 14:00:00.000000

"""
import os
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, text
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta
import math
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = 'seed_mobile_co2_station'
down_revision: Union[str, None] = '9e7f71ac2376'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def is_dev_environment():
    return os.getenv('ENVIRONMENT') == 'development' or os.getenv('ENVIRONMENT') == 'dev'

def generate_route_points(start_lat, start_lon, day_of_week):
    """Generate points in a circular route around Austin based on day of week"""
    points = []

    # Base number of points per day
    num_points = 18000  # One point every ~5 seconds

    # Different patterns for different days
    if day_of_week in [0, 6]:  # Weekend (Saturday, Sunday)
        # Leisure driving - smaller radius but same number of points
        radius = 0.05  # ~5km radius
    else:  # Weekdays
        # Regular commute radius
        radius = 0.1  # ~10km radius

        # Longer routes for Mon, Wed, Fri
        if day_of_week in [1, 3, 5]:
            radius = 0.15  # Longer commute route

    # Generate points with higher density
    for i in range(num_points):
        angle = (2 * math.pi * i) / num_points
        # Add some randomness to the route
        random_variation = random.uniform(-0.01, 0.01)
        lat = start_lat + (radius + random_variation) * math.cos(angle)
        lon = start_lon + (radius + random_variation) * math.sin(angle)
        points.append((lat, lon))
    return points

def upgrade() -> None:
    if not is_dev_environment():
        return

    # Austin coordinates (approximate)
    AUSTIN_LAT = 30.2672
    AUSTIN_LON = -97.7431

    # Create tables
    stations_table = table('stations',
        column('stationid', sa.Integer),
        column('stationname', sa.String),
        column('description', sa.String),
        column('campaignid', sa.Integer),
        column('projectid', sa.String),
        column('contactname', sa.String),
        column('contactemail', sa.String),
        column('active', sa.Boolean),
        column('startdate', sa.DateTime),
        column('station_type', sa.String),
        column('geometry', geoalchemy2.types.Geometry("GEOMETRY", srid=4326))
    )

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

    measurements_table = table('measurements',
        column('measurementid', sa.Integer),
        column('sensorid', sa.Integer),
        column('collectiontime', sa.DateTime),
        column('measurementvalue', sa.Float),
        column('variablename', sa.String),
        column('geometry', geoalchemy2.types.Geometry("GEOMETRY", srid=4326))
    )

    # Insert mobile station
    station_data = {
        'stationname': 'Mobile CO2 Station',
        'description': 'Mobile station measuring CO2 levels around Austin',
        'campaignid': 1,  # Assuming campaign 1 exists
        'projectid': 'MOBILE_CO2_2024',
        'contactname': 'Test User',
        'contactemail': 'test@example.com',
        'active': True,
        'startdate': datetime(2024, 1, 1),
        'station_type': 'mobile',
        'geometry': f'SRID=4326;POINT({AUSTIN_LON} {AUSTIN_LAT})'
    }

    # Insert station and get its ID
    result = op.get_bind().execute(stations_table.insert().values(station_data))
    station_id = op.get_bind().execute(text('SELECT lastval()')).scalar()
    if station_id is None:
        raise Exception("Failed to insert station")
    else:
        print(f"Station inserted with id: {station_id}")

    # Insert CO2 sensor
    sensor_data = {
        'stationid': station_id,
        'alias': 'CO2',
        'description': 'Carbon dioxide sensor',
        'postprocess': True,
        'postprocessscript': 'co2_qc.py',
        'units': 'ppm',
        'variablename': 'co2'
    }

    # Insert sensor and get its ID
    result = op.get_bind().execute(sensors_table.insert().values(sensor_data))
    sensor_id = op.get_bind().execute(text('SELECT lastval()')).scalar()
    print(f"Sensor inserted with id: {sensor_id}")

    # Generate measurements for one week
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    measurements = []

    for day in range(7):  # 0 = Monday, 6 = Sunday
        current_date = start_time + timedelta(days=day)
        route_points = generate_route_points(AUSTIN_LAT, AUSTIN_LON, day)

        for i, (lat, lon) in enumerate(route_points):
            # Distribute measurements throughout the day based on patterns
            if day < 5:  # Weekdays
                if i < 6000:  # First third - morning (6 AM to 10 AM)
                    base_time = current_date.replace(hour=6) + timedelta(seconds=i)
                elif i < 12000:  # Second third - midday (10 AM to 3 PM)
                    base_time = current_date.replace(hour=10) + timedelta(seconds=(i - 6000))
                else:  # Last third - evening (3 PM to 8 PM)
                    base_time = current_date.replace(hour=15) + timedelta(seconds=(i - 12000))
            else:  # Weekends
                # Spread measurements from 8 AM to 8 PM
                base_time = current_date.replace(hour=8) + timedelta(seconds=i)

            # Add small random time variation (±30 seconds)
            time_variation = random.uniform(-30, 30)
            timestamp = base_time + timedelta(seconds=time_variation)

            # Generate CO2 values with traffic patterns
            base_co2 = 400

            # Higher CO2 during rush hours
            if day < 5:  # Weekdays
                if 7 <= timestamp.hour <= 9:  # Morning rush
                    base_co2 = 500
                elif 16 <= timestamp.hour <= 18:  # Evening rush
                    base_co2 = 550
                elif 11 <= timestamp.hour <= 14:  # Lunch time
                    base_co2 = 475

            # Add anomalies (keeping existing anomaly logic)
            if random.random() < 0.05:
                anomaly_type = random.choice(['high', 'low', 'extreme'])
                if anomaly_type == 'high':
                    co2_value = random.uniform(1000, 2000)
                elif anomaly_type == 'low':
                    co2_value = random.uniform(200, 300)
                else:  # extreme
                    co2_value = random.uniform(2000, 5000)
            else:
                # Add some noise to the base CO2 value
                variation = random.gauss(0, 50)
                co2_value = max(400, min(800, base_co2 + variation))

            measurement = {
                'sensorid': sensor_id,
                'collectiontime': timestamp,
                'measurementvalue': co2_value,
                'variablename': 'co2',
                'geometry': f'SRID=4326;POINT({lon} {lat})'
            }
            measurements.append(measurement)

    # Increase batch size for better performance with larger dataset
    batch_size = 5000
    for i in range(0, len(measurements), batch_size):
        print(f"Inserting batch {i//batch_size + 1} of {len(measurements)//batch_size}")
        batch = measurements[i:i + batch_size]
        op.get_bind().execute(measurements_table.insert().values(batch))

def downgrade() -> None:
    """Remove seed data."""
    op.get_bind().execute(text('DELETE FROM measurements WHERE measurementid > 0'))
    op.get_bind().execute(text('DELETE FROM sensors WHERE sensorid > 0'))
    op.get_bind().execute(text('DELETE FROM stations WHERE stationid > 0'))