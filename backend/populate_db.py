# backend/populate_db.py

# This is a one-time script to add the permanent parking spot data to the database.
import sys
import os
from sqlalchemy.orm import Session
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend import models, database

def populate_spots(db: Session):
    """
    Adds the predefined list of parking spots to the database.
    """
    # --- Define Your Parking Spots Here ---
    # This list now matches your 8-spot parking lot design.
    spots_to_add = [
        'A1', 'A2',
        'B1', 'B2', 'B3', 
    ]

    camera_id_for_all = "cam_main_01"

    for spot_id in spots_to_add:
        # Check if the spot already exists to avoid duplicates
        existing_spot = db.query(models.Spot).filter(models.Spot.spot_id == spot_id).first()
        if not existing_spot:
            new_spot = models.Spot(
                spot_id=spot_id,
                camera_id=camera_id_for_all
                # Note: coordinates_json can be added later or manually in pgAdmin
            )
            db.add(new_spot)
            print(f"Adding spot: {spot_id}")
        else:
            print(f"Spot already exists: {spot_id}")

    db.commit()
    print("Database population complete.")

if __name__ == "__main__":
    print("Connecting to the database...")
    # Get a database session
    db = database.SessionLocal()
    try:
        # Create the tables if they don't exist
        print("Creating tables if they don't exist...")
        models.Base.metadata.create_all(bind=database.engine)
        # Populate the spots table
        print("Populating spots...")
        populate_spots(db)
    finally:
        # Close the session
        db.close()
        print("Database connection closed.")