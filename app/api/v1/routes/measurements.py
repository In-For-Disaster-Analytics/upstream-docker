from typing import Optional

from fastapi import APIRouter

from app.api.v1.schemas.measurement import MeasurementIn, MeasurementOut
from app.db.models.measurement import Measurement
from app.db.session import SessionLocal

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.get("/measurement")
async def read_measurement(min_measurement_value: Optional[float] = None):
    with SessionLocal() as session:
        measurements = session.query(Measurement)
        if min_measurement_value is not None:
            measurements = measurements.filter(
                Measurement.measurementvalue > min_measurement_value
            )
        return measurements.all()


@router.post("/measurement", response_model=MeasurementOut)
async def post_measurement(measurement: MeasurementIn):
    with SessionLocal() as session:
        db_measurement = Measurement(**measurement.dict())
        session.add(db_measurement)
        session.commit()
        session.refresh(db_measurement)
        return db_measurement
