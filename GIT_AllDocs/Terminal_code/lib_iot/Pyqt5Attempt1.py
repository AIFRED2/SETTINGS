import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QLabel, QSlider, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer

# Buscar automáticamente el puerto del Arduino
def encontrar_puerto_arduino():
    puertos = serial.tools.list_ports.comports()
    for puerto in puertos:
        if "Arduino" in puerto.description:
            return puerto.device
    return None

# Establecer conexión serial
puerto = encontrar_puerto_arduino()
if puerto is None:
    print("No se encontró Arduino.")
    sys.exit()

arduino = serial.Serial(puerto, 115200, timeout=1)

class ControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control de Extrusora")
        self.resize(300, 300)

        # Estado de los actuadores: [motor spool, fan, extrusor, heater]
        self.estado = ['0', '0', '0', '0']
        self.velocidad_extrusor = 2000  # Velocidad por defecto

        # Botones
        self.btn_spool = QPushButton("Motor Spool (OFF)")
        self.btn_fan = QPushButton("Fan (OFF)")
        self.btn_extrude = QPushButton("Extrusor (OFF)")
        self.btn_heater = QPushButton("Heater (OFF)")

        # Slider de velocidad
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(100)
        self.slider.setMaximum(3000)
        self.slider.setValue(self.velocidad_extrusor)

        self.lbl_slider = QLabel(f"Velocidad Extrusor: {self.velocidad_extrusor}")

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(self.btn_spool)
        layout.addWidget(self.btn_fan)
        layout.addWidget(self.btn_extrude)
        layout.addWidget(self.btn_heater)

        layout.addWidget(self.lbl_slider)
        layout.addWidget(self.slider)

        self.setLayout(layout)

        # Conectar señales
        self.btn_spool.clicked.connect(lambda: self.toggle(0, self.btn_spool, "Motor Spool"))
        self.btn_fan.clicked.connect(lambda: self.toggle(1, self.btn_fan, "Fan"))
        self.btn_extrude.clicked.connect(lambda: self.toggle(2, self.btn_extrude, "Extrusor"))
        self.btn_heater.clicked.connect(lambda: self.toggle(3, self.btn_heater, "Heater"))
        self.slider.valueChanged.connect(self.actualizar_velocidad)

        # Temporizador para enviar datos cada 200 ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.enviar_comandos)
        self.timer.start(200)

    def toggle(self, index, boton, nombre):
        self.estado[index] = '1' if self.estado[index] == '0' else '0'
        boton.setText(f"{nombre} ({'ON' if self.estado[index] == '1' else 'OFF'})")

    def actualizar_velocidad(self):
        self.velocidad_extrusor = self.slider.value()
        self.lbl_slider.setText(f"Velocidad Extrusor: {self.velocidad_extrusor}")

    def enviar_comandos(self):
        comando = "ACTUATE:" + ''.join(self.estado) + f"\n"
        arduino.write(comando.encode())

        # También puedes enviar la velocidad si decides leerla en Arduino
        comando_velocidad = f"SPEED:{self.velocidad_extrusor}\n"
        arduino.write(comando_velocidad.encode())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ControlGUI()
    ventana.show()
    sys.exit(app.exec_())