from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import numpy as np
import time
from lib_iot.serial_2 import generate_socket, send_data_to_firebase

def calculate_diameter(mask):
    """
    Function to calculate diameter
    """
    widths = np.sum(mask, axis=0)  # Sum along rows
    max_width = np.max(widths)
    diameter = max_width * PIXEL_TO_UNIT
    return max_width, diameter

def camera_loop():
    ## Primero se genera el socket para enviar datos de la càmara a thinger
    conn_c, addr = generate_socket(HOST, PORT_C)
    print(f"Conexion establecida con {addr}")
    
    ### Despues de generar el socket pasamos al proceso de la càmara
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    print("Press 'q' to quit.")
    
    try:
        while True:
            frame = picam2.capture_array()
            resized_frame = cv2.resize(frame, (640, 480))  # Resize frame for faster YOLO inference
            start_time = time.time()  # YOLO inference
            results = model(resized_frame, conf=0.5)
            end_time = time.time()  # Annotate the frame if detections are found
            #print(f"Inference time: {end_time - start_time:.2f} seconds")
            diameter = 20
            #FDFDD
            for result in results:
                if result.masks is not None:
                    mask = result.masks.data[0].cpu().numpy()
                    max_width, diameter = calculate_diameter(mask)
                    #print(f"Diameter: {max_width} pixels, {diameter:.2f} units")
                    annotated_frame = result.plot()
                    # Overlay mask and text
                    cv2.putText(
                        annotated_frame, f"Diameter: {diameter:.2f} units", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2
                    )
                    cv2.imshow("Live Feed", annotated_frame)
                    break  # Stop after the first detection to avoid redundancy
                else:
                    # Show original frame if no detections
                    cv2.imshow("Live Feed", resized_frame)
                            
            send_data_to_firebase(diameter, diam_collection, diam_type)
            data = float(diameter)
            conn_c.sendall((f"{data} ").encode('utf-8'))  # Enviar diametro a thinger
            time.sleep(0.5)

            if cv2.waitKey(1) & 0xFF == ord("q"):  # Press 'q' to quit
                break
    
    finally:
        # Asegúrate de cerrar la conexión y liberar recursos cuando termine el bucle
        picam2.stop()
        conn_c.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    model = YOLO("/home/fred/Documents/Vision YOLO/MODELO/train7/weights/best.pt")  # Replace with your model path
    PIXEL_TO_UNIT = 0.1  # Calibration factor
    HOST = '127.0.0.1'
    PORT_C = 65434  # Puerto para manejar datos leídos de diametro
    diam_collection = "sensores4"
    diam_type = "diametro"
    camera_loop()

print("Hi everyone")