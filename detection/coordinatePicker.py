# detection/coordinate_picker.py
#
# Description:
# This script helps you find the pixel coordinates of parking spots from an image.
# It loads an image, displays it, and allows you to click and drag to draw a
# rectangle. When you release the mouse, it prints the top-left (x1, y1) and
# bottom-right (x2, y2) coordinates of the box you drew.
#
# How to Use:
# 1. Take a clear screenshot of your parking lot from your webcam feed.
#    Save it in the same directory as this script (e.g., as 'parking_lot.jpg').
# 2. Update the IMAGE_PATH variable below to match your screenshot's filename.
# 3. Run the script: python detection/coordinate_picker.py
# 4. A window will appear with your image. Click and drag to draw a box around a spot.
# 5. The coordinates for that spot will be printed in the terminal.
# 6. Press 'r' to reset and draw a new box, or 'q' to quit.

import cv2
import os

# --- Configuration ---
# Update this to the path of the screenshot of your parking lot.
IMAGE_PATH = "detection/parking_lot_screenshot.jpg" 

# Global variables to store coordinates
ref_point = []
drawing = False

def click_and_draw(event, x, y, flags, param):
    """
    Mouse callback function to handle drawing rectangles.
    """
    global ref_point, drawing, clone

    # If the left mouse button is pressed, record the starting (x, y) coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]
        drawing = True

    # If the left mouse button is released, record the ending (x, y) coordinates
    elif event == cv2.EVENT_LBUTTONUP:
        ref_point.append((x, y))
        drawing = False

        # Draw a rectangle around the region of interest
        cv2.rectangle(clone, ref_point[0], ref_point[1], (0, 255, 0), 2)
        cv2.imshow("image", clone)
        
        # Print the coordinates to the terminal
        x1, y1 = ref_point[0]
        x2, y2 = ref_point[1]
        print(f"Spot Coordinates: (x_start={x1}, y_start={y1}, x_end={x2}, y_end={y2})")

def main():
    global clone
    
    # Load the image
    try:
        image = cv2.imread(IMAGE_PATH)
        clone = image.copy()
    except Exception as e:
        print(f"Error loading image: {e}")
        print(f"Please make sure '{IMAGE_PATH}' exists in the same directory.")
        return

    # Create a window and set the mouse callback function
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_draw)

    print("\n--- Coordinate Picker ---")
    print("Click and drag to draw a box around a parking spot.")
    print("Press 'r' to reset the image and draw a new box.")
    print("Press 'q' to quit.")

    while True:
        # Display the image and wait for a keypress
        cv2.imshow("image", clone)
        key = cv2.waitKey(1) & 0xFF

        # If the 'r' key is pressed, reset the image
        if key == ord("r"):
            clone = image.copy()
            print("Image reset. Draw a new box.")

        # If the 'q' key is pressed, break from the loop
        elif key == ord("q"):
            break

    # Close all open windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

