# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment file and configure
cp .env.sample .env
# Edit .env with proper values for TAS_USER, TAS_SECRET, etc.
```

### Database Operations
```bash
# Start database only
docker compose -f docker-compose.dev.yml up -d db

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback last migration
alembic downgrade -1
```

### Development Server
```bash
# Run development server (requires database running)
fastapi dev app/main.py

# Or run with Docker (full stack)
docker compose -f docker-compose.dev.yml up -d
```

### Code Quality
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Type checking
mypy app

# Code formatting
black .
isort .

# Linting
flake8

# Run pre-commit hooks
pre-commit run --all-files
```

## Architecture Overview

### Core Structure
- **FastAPI Application**: Main API server with versioned endpoints (`/api/v1/`)
- **Database Models**: SQLAlchemy models with PostGIS geometry support
- **Repository Pattern**: Data access layer in `app/db/repositories/`
- **Service Layer**: Business logic in `app/services/`
- **API Routes**: Organized by domain in `app/api/v1/routes/`

### Key Components

**Database Models** (`app/db/models/`):
- `Campaign`: Main organizing entity for data collection efforts
- `Station`: Data collection locations (static or mobile)
- `Sensor`: Individual measurement devices
- `Measurement`: Time-series sensor data with geospatial support
- `SensorStatistics`: Aggregated sensor data

**API Organization**:
- Campaigns: `/api/v1/campaigns/`
- Stations: `/api/v1/campaigns/{campaign_id}/stations/`
- Sensors: `/api/v1/campaigns/{campaign_id}/stations/{station_id}/sensors/`
- Measurements: `/api/v1/campaigns/{campaign_id}/stations/{station_id}/sensors/{sensor_id}/measurements/`

### Authentication
- Uses TACC Authentication Service (TAS) via JWT tokens
- Configuration in `app/api/dependencies/auth.py`
- PyTAS integration in `app/pytas/`

### Database
- PostgreSQL with PostGIS extension for geospatial data
- Alembic for database migrations
- GeoAlchemy2 for spatial queries
- Connection configuration in `app/db/session.py`

### Key Features
- Geospatial data support (GeoJSON, PostGIS)
- CSV file upload processing
- Time-series data with LTTB downsampling
- Campaign-based data organization
- Mobile and static station support

## Testing

Tests are organized in `tests/` directory matching the app structure:
- `conftest.py`: Test configuration and fixtures
- API tests: `tests/api/`
- Service tests: `tests/test_*_service.py`
- Repository tests: `tests/test_*_repository.py`

## Configuration

Environment variables (`.env` file):
- `DATABASE_URL`: PostgreSQL connection string
- `TAS_USER`/`TAS_SECRET`: TACC authentication credentials
- `JWT_SECRET`: JWT signing secret
- `ENVIRONMENT`: Environment identifier (dev/prod)

## Development Notes

- Code follows black formatting (88 char line length)
- Type hints enforced with mypy (strict mode)
- Pre-commit hooks ensure code quality
- API documentation auto-generated at `/docs` endpoint
- Database migrations should be reviewed before applying