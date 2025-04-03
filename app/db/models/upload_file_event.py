from app.db.base import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

class UploadFileEvent(Base):
    __tablename__ = "upload_file_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    time: Mapped[datetime] = mapped_column()

    # relationships
    #measurements: Mapped[list("Measurement")] = relationship(lazy="joined") # back_populates="upload_file_event",
    #sensors: Mapped[list("Sensor")] = relationship(lazy="joined") # back_populates="upload_file_event",

