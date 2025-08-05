# detection/qr_code_engine.py
#
# Description:
# This script uses multithreading for smooth video display. The main thread handles
# capturing and showing video frames, while a separate worker thread handles the
# slow QR code detection and network requests in the background. It now includes
# persistence logic to prevent flickering detections.
#
# How to Run:
# 1. Make sure your Python virtual environment is active.
# 2. Update the BACKEND_URL and PARKING_SPOT_ZONES with your specific configuration.
# 3. Run the script from your terminal: python detection/qr_code_engine.py

import cv2
import requests
import json
import time
import threading
from queue import Queue
import numpy as np

# --- Configuration ---

BACKEND_URL = "http://localhost:8000/api/detections"
CAMERA_ID = "cam_main_01"
CAMERA_SOURCE = 2 
PARKING_SPOT_ZONES = {
    "A1": (63, 291, 243, 454), 
    "A2": (60, 11, 227, 189),
    "B1": (382, 304, 544, 452),
    "B2": (380, 160, 541, 300),
    "B3": (381, 9, 542, 156),
}

# --- Threading & Persistence Setup ---
frame_queue = Queue(maxsize=1) 
# This list will only contain detections from the CURRENT frame for drawing
latest_detections_for_drawing = []
detections_lock = threading.Lock()

# --- DEBUGGING SETUP ---
# A queue to pass the processed debug frame back to the main thread
debug_frame_queue = Queue(maxsize=1)

bus_persistence = {}
PERSISTENCE_SECONDS = 35.0 


def get_spot_for_qr(points):
    """Determines which parking spot a QR code is in."""
    if points is None or len(points) == 0:
        return None
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    qr_center_x = (x_min + x_max) / 2
    qr_center_y = (y_min + y_max) / 2

    for spot_id, zone in PARKING_SPOT_ZONES.items():
        x_start, y_start, x_end, y_end = zone
        if x_start < qr_center_x < x_end and y_start < qr_center_y < y_end:
            return spot_id
    return None

def detection_worker():
    """
    This function runs in a separate thread. It processes frames for QR codes,
    maintains a persistent list of recently seen buses, and sends the stable
    data to the backend.
    """
    global latest_detections_for_drawing
    detector = cv2.QRCodeDetector()
    
    while True:
        frame = frame_queue.get()
        if frame is None: # Sentinel value to stop the thread
            break
        
        current_time = time.time()
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply a bilateral filter to reduce noise while preserving sharp edges.
        filtered_frame = cv2.bilateralFilter(gray_frame, 9, 75, 75)
        
        # Apply adaptive thresholding to the filtered image to create a high-contrast version.
        thresh_frame = cv2.adaptiveThreshold(filtered_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        if not debug_frame_queue.full():
            debug_frame_queue.put(thresh_frame)

        ok = False
        decoded_info = None
        points = None

        # --- FIX APPLIED HERE ---
        # Wrap detection calls in try/except blocks to prevent crashes from low-level OpenCV errors.
        try:
            # First, attempt to detect on the clean, processed image.
            ok, decoded_info, points, _ = detector.detectAndDecodeMulti(thresh_frame)
        except cv2.error as e:
            print(f"OpenCV error on thresholded frame: {e}")
            ok = False

        try:
            # If that fails, fall back to the simple grayscale image.
            if not ok or points is None:
                ok, decoded_info, points, _ = detector.detectAndDecodeMulti(gray_frame)
        except cv2.error as e:
            print(f"OpenCV error on grayscale frame: {e}")
            ok = False


        # This list will only contain detections from this specific frame
        current_frame_draw_data = []

        if ok and points is not None:
            for i, bus_data in enumerate(decoded_info):
                if bus_data:
                    bus_number = bus_data.split('/')[-1] if bus_data.startswith('http') else bus_data
                    qr_points = points[i]
                    spot_id = get_spot_for_qr(qr_points)
                    if spot_id:
                        # Update the persistence tracker for stable backend data
                        bus_persistence[bus_number] = { "spot_id": spot_id, "timestamp": current_time }
                        # Add to the list for drawing in this frame
                        current_frame_draw_data.append({
                            "spot_id": spot_id,
                            "bus_number": bus_number,
                            "points": qr_points.astype(int).reshape(-1, 1, 2)
                        })

        stale_buses = [bus for bus, data in bus_persistence.items() if current_time - data["timestamp"] > PERSISTENCE_SECONDS]
        for bus in stale_buses:
            del bus_persistence[bus]

        # The data sent to the server is based on the stable, persisted list
        final_detections_for_server = [{"spot_id": data["spot_id"], "bus_number": bus} for bus, data in bus_persistence.items()]
        
        # The data for drawing is based ONLY on the current frame
        with detections_lock:
            latest_detections_for_drawing = current_frame_draw_data

        payload = { "camera_id": CAMERA_ID, "detections": final_detections_for_server }
        try:
            requests.post(BACKEND_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            print(f"Sent {len(final_detections_for_server)} stable detections to server.")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data to server: {e}")

def main():
    """
    Main function to run the video capture and display loop.
    """
    cap = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Error: Could not open camera at index {CAMERA_SOURCE}.")
        return
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("--- Live QR Code Detection Engine Started ---")
    
    cv2.namedWindow("Live Feed", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Debug View (What the Detector Sees)", cv2.WINDOW_NORMAL) # New debug window
    
    worker_thread = threading.Thread(target=detection_worker, daemon=True)
    worker_thread.start()

    last_frame_sent_time = time.time()
    frame_send_interval = 0.1 # Process up to 10 frames per second

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        
        current_time = time.time()
        if (current_time - last_frame_sent_time) > frame_send_interval:
            if not frame_queue.full():
                frame_queue.put(frame.copy())
                last_frame_sent_time = current_time

        # Display the debug frame if available
        if not debug_frame_queue.empty():
            debug_frame = debug_frame_queue.get()
            cv2.imshow("Debug View (What the Detector Sees)", debug_frame)

        with detections_lock:
            local_detections = latest_detections_for_drawing
            
        # This loop now only draws boxes for QR codes seen in the current frame
        for detection in local_detections:
             points = detection["points"]
             spot_id = detection["spot_id"]
             bus_number = detection["bus_number"]
             cv2.polylines(frame, [points], True, (0, 255, 0), 2)
             cv2.putText(frame, f"{bus_number} @ {spot_id}", (points[0][0][0], points[0][0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("Live Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    frame_queue.put(None)
    worker_thread.join()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
