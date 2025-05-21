from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import numpy as np
import time

# Load YOLO model
model = YOLO("/home/fred/Documents/Vision YOLO/MODELO/train7/weights/best.pt")  # Replace with your model path
PIXEL_TO_UNIT = 0.1  # Calibration factor

# Initialize Picamera2
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

# Function to calculate diameter
def calculate_diameter(mask):
    widths = np.sum(mask, axis=0)  # Sum along rows
    max_width = np.max(widths)
    diameter = max_width * PIXEL_TO_UNIT
    return max_width, diameter

# Processing loop
print("Press 'q' to quit.")
while True:
    frame = picam2.capture_array()

    # Resize frame for faster YOLO inference
    resized_frame = cv2.resize(frame, (640, 480))

    # YOLO inference
    start_time = time.time()
    results = model(resized_frame, conf=0.5)
    end_time = time.time()
    print(f"Inference time: {end_time - start_time:.2f} seconds")

    # Annotate the frame if detections are found
    for result in results:
        if result.masks is not None:
            mask = result.masks.data[0].cpu().numpy()
            max_width, diameter = calculate_diameter(mask)
            print(f"Diameter: {max_width} pixels, {diameter:.2f} units")

            # Overlay mask and text
            annotated_frame = result.plot()
            cv2.putText(
                annotated_frame, f"Diameter: {diameter:.2f} units", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2
            )
            cv2.imshow("Live Feed", annotated_frame)
            break  # Stop after the first detection to avoid redundancy
    else:
        # Show original frame if no detections
        cv2.imshow("Live Feed", resized_frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

picam2.stop()
cv2.destroyAllWindows()