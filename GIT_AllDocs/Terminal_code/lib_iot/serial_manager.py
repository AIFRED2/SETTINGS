import serial
import socket
import threading
import time

def serial_to_socket_a():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT_A))
        s.listen()
        print(f"Esperando conexión en socket {HOST}:{PORT_A}")
        conn, addr = s.accept()
        with conn:
            print(f"Conexión establecida con {addr}")
            try:
                while True:
                    if ser.in_waiting > 0:
                        data = ser.readline().decode('utf-8', errors='ignore')
                        if data.startswith("TEMP:") and "#" in data:
                            mensaje_ard = data.split(":")[1].split("#")[0]
                            a = float(mensaje_ard)
                            conn.sendall((f"{a}").encode('utf-8'))
            except KeyboardInterrupt:
                print("Interrumpido por el usuario")

def socket_b_to_serial():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT_B))
        s.listen()
        print(f"Esperando conexión en Socket B {HOST}:{PORT_B}")
        conn, addr = s.accept()
        with conn:
            print(f"Conexión establecida con {addr}")
            try:
                while True:
                    data = conn.recv(1024).decode('utf-8')
                    if data.startswith("ACTUATE:"):
                        ser.write((data + '\n').encode('utf-8'))
            except KeyboardInterrupt:
                print("Interrumpido por el usuario")

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    time.sleep(2)
    HOST = '127.0.0.1'
    PORT_A = 65432  # Puerto para enviar datos leídos del puerto serial
    PORT_B = 65433  # Puerto para recibir datos y escribirlos en el puerto serial
    if ser.is_open:
        print("El puerto serial está abierto.")
    else:
        print("No se pudo abrir el puerto serial.")

    threading.Thread(target=serial_to_socket_a, daemon=True).start()
    threading.Thread(target=socket_b_to_serial, daemon=True).start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Finalizando...")
    finally:
        ser.close()
