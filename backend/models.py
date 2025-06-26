from sqlalchemy import Boolean, Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from .database import Base

class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(String, unique=True, index=True, nullable=False)
    designated_bus_id = Column(String, nullable=False)
    camera_id = Column(String, nullable=False)

    coordinates_json = Column(JSON, nullable=True)

class ParkingLog(Base):
    __tablename__ = "parking_log"

    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(String, index=True, nullable=False)
    designated_bus_id = Column(String, nullable=False)
    camera_id = Column(String, nullable=False)
    is_error = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
