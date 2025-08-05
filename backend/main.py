# backend/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from . import models, database

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- FIX APPLIED HERE ---
# Added the default Vite port (5173) to the list of allowed origins.
# This tells the backend server that it's safe to accept requests
# from your React application.
origins = [
    "http://localhost:3000", # For create-react-app
    "http://localhost:5173", # For Vite
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class DetectionItem(BaseModel):
    spot_id: str
    bus_number: str

class DetectionPayload(BaseModel):
    camera_id: str
    detections: List[DetectionItem]

# --- Database Dependency ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.post("/api/detections")
def receive_detections(payload: DetectionPayload, db: Session = Depends(get_db)):
    """
    Receives parking detection data from the detection script and updates the
    current location of each bus. This uses an "upsert" logic.
    """
    print(f"Received detections from {payload.camera_id}")
    
    detected_spot_ids = {d.spot_id for d in payload.detections}
    spots_this_camera_sees_query = db.query(models.Spot.spot_id).filter(models.Spot.camera_id == payload.camera_id).all()
    spots_this_camera_sees_set = {s.spot_id for s in spots_this_camera_sees_query}
    
    empty_spots = spots_this_camera_sees_set - detected_spot_ids

    if empty_spots:
        db.query(models.BusLocation).filter(
            models.BusLocation.spot_id.in_(empty_spots)
        ).delete(synchronize_session=False)

    for detection in payload.detections:
        existing_location = db.query(models.BusLocation).filter(models.BusLocation.spot_id == detection.spot_id).first()
        if existing_location:
            existing_location.detected_bus_id = detection.bus_number
            existing_location.camera_id = payload.camera_id
        else:
            new_location = models.BusLocation(
                spot_id=detection.spot_id,
                detected_bus_id=detection.bus_number,
                camera_id=payload.camera_id
            )
            db.add(new_location)
        
    db.commit()
    return {"status": "success", "message": f"Updated locations for {len(payload.detections)} buses."}


@app.get("/api/status")
def get_parking_status(db: Session = Depends(get_db)):
    """
    Provides the complete, current status of all parking spots to the frontend.
    """
    all_spots = db.query(models.Spot).all()
    bus_locations = db.query(models.BusLocation).all()

    location_map = {loc.spot_id: loc.detected_bus_id for loc in bus_locations}
    
    status_data = []
    for spot in all_spots:
        status_data.append({
            "spotId": spot.spot_id,
            "actualBus": location_map.get(spot.spot_id), # Returns the bus number or None if empty
            "cameraId": spot.camera_id,
            "coordinates": spot.coordinates_json,
        })
        
    return status_data
