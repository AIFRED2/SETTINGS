import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
import time
import socket

# Inicialización de Firebase
cred = credentials.Certificate("/home/fred/Documents/VENVsysPAK/env/lib_sd/fredfactorydb-firebase-adminsdk-wuxzx-365bf8799e.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

class FirebaseToThinger:
    def __init__(self):
        self.diametro = 0
        self.host = '127.0.0.1'
        self.port = 65434

    # Función para enviar datos de sensor a Firebase 
    def enviar_datos_sensor(self,diam_value):
        if diam_value is None:
            # Genera un valor aleatorio de diámetro
            self.diametro = random.uniform(20.0, 30.0)
        else:
            self.diametro = diam_value 
        db.collection("sensores4").add({
                    "diametro": self.diametro,
                    "time": firestore.SERVER_TIMESTAMP
                })

    # Función para enviar datos a través de socket de manera continua
    def serial_to_socket_c(self,diam_value):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"Esperando conexión en socket C {self.host}:{self.port}")
            conn, addr = s.accept()
            with conn:
                print(f"Conexión establecida con {addr}")
                try:
                    while True:
                        self.enviar_datos_sensor(diam_value)
                        data = float(self.diametro)
                        conn.sendall((f"{data} ").encode('utf-8')) 
                        time.sleep(0.5)  # Retraso de medio segundo entre envíos
                except KeyboardInterrupt:
                    print("Interrumpido por el usuario")

if __name__ == "__main__":
    f = FirebaseToThinger()
    f.serial_to_socket_c(None)