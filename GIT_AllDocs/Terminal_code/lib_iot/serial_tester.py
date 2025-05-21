import serial
import time

# Configura el puerto serial y la velocidad de comunicación
puerto_serial = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)

print("Comunicando con Arduino...")

try:
    while True:
        # Verifica si hay datos recibidos desde Arduino
        if puerto_serial.in_waiting > 0:
            mensaje = puerto_serial.readline().decode('utf-8').strip()  # Lee el mensaje
            if mensaje:
                print(f"Arduino dijo: {mensaje}")

                # Responde con un mensaje a Arduino
                if mensaje == "Hola":
                    puerto_serial.write("Buenas tardes\n".encode('utf-8'))
                    print("Enviado: Buenas tardes")

        time.sleep(1)  # Espera un segundo antes de revisar nuevamente
except KeyboardInterrupt:
    print("\nTerminando la comunicación.")
finally:
    puerto_serial.close()
