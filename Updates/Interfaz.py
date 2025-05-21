import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QLabel, QSlider)
from PyQt5.QtCore import Qt, QTimer

arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

class ControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control de Extrusora")
        self.resize(300, 300)

        self.estado = ['0', '0', '0', '0']
        self.velocidad_extrusor = 2000

        # Widgets
        self.btn_spool = QPushButton("Motor Spool (OFF)")
        self.btn_fan = QPushButton("Fan (OFF)")
        self.btn_extrude = QPushButton("Extrusor (OFF)")
        self.btn_heater = QPushButton("Heater (OFF)")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(100)
        self.slider.setMaximum(3000)
        self.slider.setValue(self.velocidad_extrusor)

        self.lbl_slider = QLabel(f"Velocidad Extrusor: {self.velocidad_extrusor}")

        layout = QVBoxLayout()
        layout.addWidget(self.btn_spool)
        layout.addWidget(self.btn_fan)
        layout.addWidget(self.btn_extrude)
        layout.addWidget(self.btn_heater)
        layout.addWidget(self.lbl_slider)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        # Conectar eventos
        self.btn_spool.clicked.connect(lambda: self.toggle(0, self.btn_spool, "Motor Spool"))
        self.btn_fan.clicked.connect(lambda: self.toggle(1, self.btn_fan, "Fan"))
        self.btn_extrude.clicked.connect(lambda: self.toggle(2, self.btn_extrude, "Extrusor"))
        self.btn_heater.clicked.connect(lambda: self.toggle(3, self.btn_heater, "Heater"))
        self.slider.valueChanged.connect(self.actualizar_velocidad)

        # Temporizador para envío y lectura
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
        comando = "ACTUATE:" + ''.join(self.estado) + "\n"
        arduino.write(comando.encode())

        comando_velocidad = f"SPEED:{self.velocidad_extrusor}\n"
        arduino.write(comando_velocidad.encode())

        # Leer y mostrar respuesta de Arduino
        if arduino.in_waiting:
            respuesta = arduino.read(arduino.in_waiting).decode(errors='ignore')
            print(respuesta)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ControlGUI()
    ventana.show()
    sys.exit(app.exec_())
