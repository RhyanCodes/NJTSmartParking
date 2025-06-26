from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from pydantic import BaseModel
from . import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DetectionItem(BaseModel):
    spot_id: str
    bus_number: str

class DetectionPayload(BaseModel):
    camera_id: str
    detections: List[DetectionItem]

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/detections")
def receive_detections(payload: DetectionPayload, db: Session = Depends(get_db)):
    
    print(f"Received detections from {payload.camera_id}")

    db.query(models.ParkingLog).filter(models.ParkingLog.camera_id == payload.camera_id).delete()

    for detection in payload.detections:
        parking_spot = db.query(models.ParkingSpot).filter(models.ParkingSpot.spot_id == detection.spot_id).first()

        if not parking_spot:
            print(f"Warning: Spot Id '{detection.spot_id}' not found in database. Skipping")
            continue

        is_error = parking_spot.designated_bus_id != detection.bus_number

        new_log_entry = models.ParkingLog(
            spot_id=detection.spot_id,
            detected_bus_id=detection.bus_number,
            camera_id=payload.camera_id,
            is_error=is_error
        )
        db.add(new_log_entry)

    db.commit()
    return {"status": "success", "message": f"Processed {len(payload.detections)} detections."}


@app.get("/api/status")
def get_parking_status(db: Session = Depends(get_db)):
    all_spots = db.query(models.ParkingSpot).all()
    all_logs = db.query(models.ParkingLog).all()

    log_map = {log.spot_id: log for log in all_logs}
    status_data = []
    for spot in all_spots:
        current_log = log_map.get(spot.spot_id)

        status_data.append({
            "spotId": spot.spot_id,
            "designatedBus": spot.designated_bus_id,
            "actualBus": current_log.detected_bus_id if current_log else None, 
            "isError": current_log.is_error if current_log else False, 
            "cameraId": spot.camera_id,
            "coordinates": spot.coordinates_json,
        })

    return status_data
    