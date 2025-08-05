# detection/image_collector.py
#
# Description:
# This script captures video from a connected webcam, displays the live feed,
# and allows the user to save the current frame as a high-quality image file
# by pressing the 's' key. Pressing 'q' will quit the program.
#
# How to Run:
# 1. Make sure your Python virtual environment is active.
# 2. Run the script from your terminal: python detection/image_collector.py

import cv2
import os
import time

# --- Configuration ---
# The folder where you want to save your captured images.
# This folder will be created if it doesn't exist.
SAVE_PATH = "training_images"

# The source of your video camera. 
# '0' is usually the default for a built-in or USB webcam.
# If you have multiple cameras, you might need to change this to 1, 2, etc.
CAMERA_SOURCE = 2 # Keep trying 1, if it fails, try 0, 2, 3...

def main():
    """
    Main function to run the image collection process.
    """
    # Create the save directory if it doesn't already exist.
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
        print(f"Created directory: {SAVE_PATH}")

    # Initialize the camera capture object using OpenCV.
    # --- FIX APPLIED HERE ---
    # We are adding `cv2.CAP_DSHOW` to force OpenCV to use the DirectShow
    # backend, which is often more compatible with USB webcams on Windows.
    cap = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_DSHOW)

    # Check if the camera was successfully opened.
    if not cap.isOpened():
        print(f"Error: Could not open camera at index {CAMERA_SOURCE}.")
        print("If you have multiple cameras, try changing CAMERA_SOURCE to another number.")
        return

    print("\n--- Live Camera Feed ---")
    print("Press 's' to save the current frame as an image.")
    print("Press 'q' to quit.")
    
    image_count = 0

    while True:
        # Read a new frame from the camera.
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame. Exiting...")
            break

        # Display the live video frame in a window named "Live Feed".
        cv2.imshow("Live Feed - Press 's' to save, 'q' to quit", frame)

        # Wait for a key press for 1 millisecond.
        key = cv2.waitKey(1) & 0xFF

        # If the 's' key is pressed, save the frame.
        if key == ord('s'):
            # Create a unique filename using a timestamp to prevent overwriting files.
            timestamp = int(time.time() * 1000)
            filename = os.path.join(SAVE_PATH, f"bus_image_{timestamp}.jpg")
            
            cv2.imwrite(filename, frame)
            
            image_count += 1
            print(f"Saved {filename} ({image_count} images captured)")

        # If the 'q' key is pressed, break the loop and exit.
        elif key == ord('q'):
            print("Quitting program.")
            break

    # Release the camera and destroy all OpenCV windows to clean up resources.
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

