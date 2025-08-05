# backend/models.py

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from .database import Base

class Spot(Base):
    """
    Defines the physical parking spots in the garage.
    This table stores the spot's name and its location on the camera feed.
    """
    __tablename__ = "spots"

    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(String, unique=True, index=True, nullable=False) # e.g., "A1"
    camera_id = Column(String, nullable=False) # e.g., "cam_main_01"
    coordinates_json = Column(JSON, nullable=True) # For frontend overlays

class BusLocation(Base):
    """
    Stores the most recent, real-time location of a detected bus.
    This table is continuously updated by the detection script.
    """
    __tablename__ = "bus_locations"

    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(String, unique=True, index=True, nullable=False) # Each spot has only one current location entry
    detected_bus_id = Column(String, nullable=False) # The bus number the AI read
    camera_id = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
