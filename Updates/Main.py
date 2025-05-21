#---------------------------------------------------------------------------------------#
#--------------------------------- Python Libraries ------------------------------------#
#---------------------------------------------------------------------------------------#
import os
import sys
import csv
import numpy as np
import serial.tools.list_ports

#------------------------------- Matplotlib Libraries ----------------------------------#
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#--------------------------------- PyQt5 Libraries -------------------------------------#
from PyQt5.QtCore import QSize, Qt, QTimer, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import (
    QAction, QApplication, QLabel,
    QMainWindow, QToolBar,
    QWidget, QVBoxLayout, QHBoxLayout, QSlider,
    QPushButton, QFileDialog
)

#---------------------------------------------------------------------------------------#
# ------------------------------ Arduino Port Detection --------------------------------#
#---------------------------------------------------------------------------------------#

# Para echar a andar el codigo como tu lo tenias, quita los """ de aqui para abajo.

"""
# Detectar automáticamente el puerto del Arduino
def encontrar_puerto_arduino():
    puertos = serial.tools.list_ports.comports()
    for puerto in puertos:
        if "Arduino" in puerto.description or "ttyACM" in puerto.device or "ttyUSB" in puerto.device:
            return puerto.device
    return None

# Configurar conexión serial
puerto = encontrar_puerto_arduino()
if puerto is None:
    print("No se encontró un Arduino conectado.")
    sys.exit()

arduino = serial.Serial(puerto, 9600)
"""
#---------------------------------------------------------------------------------------#
#----------------------- Plot Class (Dimensions for the Graphs) ------------------------#
#---------------------------------------------------------------------------------------#
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

    def plot(self, data):
        self.axes.cla()
        self.axes.plot(data)
        self.draw()

#---------------------------------------------------------------------------------------#
#--------------------------------- MainWindow Class (All) ------------------------------#
#---------------------------------------------------------------------------------------#

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.records = []
        self.update_count = 0

#---------------------------------------------------------------------------------------#
#-----------------------------------Window Properties-----------------------------------#
#---------------------------------------------------------------------------------------#

        self.setWindowTitle("AI-FrED0 Control Interface")
        self.setWindowIcon(QIcon(r"Images/tec-logo.png"))
        central = QWidget()     
        self.setCentralWidget(central)
        hbox_main = QHBoxLayout(central)

#---------------------------------------------------------------------------------------#
#------------------------------------ToolBar Config-------------------------------------#
#---------------------------------------------------------------------------------------#


        toolbar = QToolBar("Toolbar")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setFixedHeight(48)
        self.addToolBar(toolbar)

        # Thinger Button Configuration
        action_thinger = QAction(QIcon(r"Images/tec-logo.png"), "Launch Thinger", self)
        action_thinger.setStatusTip("Abrir Thinger.io")
        action_thinger.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.thinger.io")))
        toolbar.addAction(action_thinger)
        toolbar.addSeparator()

#---------------------------------------------------------------------------------------#
#------------------------------------Left Part (Plots)----------------------------------#
#---------------------------------------------------------------------------------------#

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.canvas1 = PlotCanvas(self)
        self.canvas2 = PlotCanvas(self)
        self.canvas3 = PlotCanvas(self)
        left_layout.addWidget(self.canvas1)
        left_layout.addWidget(self.canvas2)
        left_layout.addWidget(self.canvas3)

#---------------------------------------------------------------------------------------#
#------------------------------------Right  Part (Buttons)------------------------------#
#---------------------------------------------------------------------------------------#

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

#----------------------------------------Slider 1 --------------------------------------#

        self.sl1_label = QLabel("N puntos: 100")
        self.sl1 = QSlider(Qt.Horizontal)
        self.sl1.setRange(10, 1000)
        self.sl1.setValue(100)
        self.sl1.setTickInterval(100)
        self.sl1.valueChanged.connect(self.update_label1)
        right_layout.addWidget(self.sl1_label)
        right_layout.addWidget(self.sl1)

#----------------------------------------Slider 2 --------------------------------------#

        self.sl2_label = QLabel("Escala ruido: 0.10")
        self.sl2 = QSlider(Qt.Horizontal)
        self.sl2.setRange(0, 100)
        self.sl2.setValue(10)
        self.sl2.setTickInterval(10)
        self.sl2.valueChanged.connect(self.update_label2)
        right_layout.addWidget(self.sl2_label)
        right_layout.addWidget(self.sl2)

#----------------------------------------Slider 3 --------------------------------------#

        self.sl3_label = QLabel("Intervalo ms: 1000")
        self.sl3 = QSlider(Qt.Horizontal)
        self.sl3.setRange(100, 2000)
        self.sl3.setValue(1000)
        self.sl3.setTickInterval(100)
        self.sl3.valueChanged.connect(self.update_label3)
        right_layout.addWidget(self.sl3_label)
        right_layout.addWidget(self.sl3)

#---------------------------------On/Off Button for LED --------------------------------#

        self.led_button = QPushButton("Encender LED")
        self.led_button.setCheckable(True)
        self.led_button.toggled.connect(self.toggle_led)
        right_layout.addWidget(self.led_button)

#----------------------------------Download CSV Button ---------------------------------#

        self.export_button = QPushButton("Exportar CSV")
        self.export_button.clicked.connect(self.export_csv)
        right_layout.addWidget(self.export_button)
        right_layout.addStretch() # This puts all buttons to the top of the right panel

#--------------------------Add Right/Left Panels to the Main panel ---------------------#

        hbox_main.addWidget(left_widget, 3)
        hbox_main.addWidget(right_widget, 1)

        self.timer = QTimer(self) # Update the plots on real time
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(self.sl3.value())


#---------------------------------------------------------------------------------------#
#------------------------------------Diverse Functions ---------------------------------#
#---------------------------------------------------------------------------------------#

#Esto configura todo lo que se hace en el codigo, todo lo que hace cada boton.

#----------------------------------Funcion de boton on/off -----------------------------#

    def toggle_led(self, checked):
        if checked:
            self.led_button.setText("Apagar LED")
            arduino.write(b'1')
        else:
            self.led_button.setText("Encender LED")
            arduino.write(b'0')

#-------------------------------------Funcion Slider 1  -------------------------------#
    def update_label1(self, val):
        self.sl1_label.setText(f"N puntos: {val}")

#-------------------------------------Funcion Slider 2  -------------------------------#

    def update_label2(self, val):
        scale = val / 100
        self.sl2_label.setText(f"Escala ruido: {scale:.2f}")

#-------------------------------------Funcion Slider 3  -------------------------------#

    def update_label3(self, val):
        self.sl3_label.setText(f"Intervalo ms: {val}")
        self.timer.start(val)


#-------------------------------------Actualizar Graph -------------------------------#
# Use datos completamente random, en una situacion real solo se cambiarian los datos de entrada por los valores directos del FrED

    def update_plots(self):
        n = self.sl1.value()
        noise_scale = self.sl2.value() / 100
        data1 = np.random.randn(n) * noise_scale
        data2 = np.random.rand(n)
        data3 = np.cumsum(np.random.randn(n))

#-------------------------------------Plotear Graphs --------------------------------#
        self.canvas1.plot(data1)
        self.canvas2.plot(data2)
        self.canvas3.plot(data3)

#-------------------------------------Actualizar CSV ---------------------------------#
        self.update_count += 1
        for i in range(n):
            self.records.append({
                'update': self.update_count,
                'index': i,
                'data1': data1[i],
                'data2': data2[i],
                'data3': data3[i]
            })
#------------------------------------Exportar CSV -----------------------------------#
# Esta funcion se encarga de exportar el CSV, si no se pone el nombre del archivo, se guardara como data.csv
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "data.csv", "CSV Files (*.csv)")
        if path:
            try:
                with open(path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['update','index','data1','data2','data3'])
                    writer.writeheader()
                    writer.writerows(self.records)
                print(f"Datos guardados en {path}")
            except Exception as e:
                print(f"Error al guardar CSV: {e}")

#-------------------------------------------END -----------------------------------#
def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
# Abre una terminal de python en este codigo, y ejecuta:  python Main.py
# Si todo va bien, deberia abrirse la ventana del programa.