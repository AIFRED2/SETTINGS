import serial
import random
import socket
import threading
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("/home/fred/Documents/VENVsysPAK/env/lib_sd/fredfactorydb-firebase-adminsdk-wuxzx-365bf8799e.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def generate_socket(HOST,PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Esperando conexión en socket {HOST}:{PORT}")
        conn, addr = s.accept()
        return conn,addr

def temperature_socket():
    temp_collection = "sensores5"
    temp_type = "temperatura"
    conn_a,addr = generate_socket(HOST,PORT_A)
    with conn_a:
        print(f"Conexión establecida con {addr}")
        try:
            while True:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8', errors='ignore')
                    if data.startswith("TEMP:") and "#" in data:
                        temperatura = float(data.split(":")[1].split("#")[0])
                        __ = send_data_to_firebase(temperatura,temp_collection,temp_type)
                        conn_a.sendall((f"{temperatura}").encode('utf-8'))
        except KeyboardInterrupt:
            print("Interrumpido por el usuario")

def control_socket():
    conn_b,addr = generate_socket(HOST, PORT_B)
    with conn_b:
        print(f"Conexión establecida con {addr}")
        try:
            while True:
                data = conn_b.recv(1024).decode('utf-8')
                if data.startswith("ACTUATE:"):
                    ser.write((data + '\n').encode('utf-8'))
        except KeyboardInterrupt:
            print("Interrumpido por el usuario")

def diameter_socket():
    diameter_value = None
    diam_collection = "sensores4"
    diam_type = "diametro"
    conn_c,addr = generate_socket(HOST, PORT_C)
    with conn_c:
        print(f"Conexión establecida con {addr}")
        try:
            while True:
                diameter_value = send_data_to_firebase(diameter_value,diam_collection,diam_type)
                data = float(diameter_value)
                conn_c.sendall((f"{data} ").encode('utf-8'))  # Enviar dato con un espacio al final
        except KeyboardInterrupt:
            print("Interrumpido por el usuario")

def send_data_to_firebase(value,collection,type):
    if value is None:
        value = random.uniform(20.0, 30.0)
    db.collection(collection).add({
                type : value,
                "time": firestore.SERVER_TIMESTAMP
                })

if __name__ == "__main__":
    Serial_Port = '/dev/ttyACM0'
    HOST = '127.0.0.1'
    PORT_A = 65432  # Puerto para manejar datos leídos de temperatura
    PORT_B = 65433  # Puerto para manejar datos de control de actuadores
    PORT_C = 65434  # Puerto para manejar datos leídos de diametro
    ser = serial.Serial(Serial_Port, 115200, timeout=1)
    time.sleep(2)
    if ser.is_open:
        print("El puerto serial está abierto.")
    else:
        print("No se pudo abrir el puerto serial.")
    threading.Thread(target=temperature_socket, daemon=True).start()
    threading.Thread(target=control_socket,     daemon=True).start()
    threading.Thread(target=diameter_socket,    daemon=True).start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Finalizando Proceso...")
    finally:
        ser.close()