import numpy as np
import matplotlib.pyplot as plt
import serial
from scipy import signal
from scipy.signal import butter, filtfilt
import pandas as pd
import re
import sys
from random import randint
from PyQt5 import QtWidgets, uic, QtCore
import pyqtgraph as pg
from threading import Thread
from pyqtgraph import PlotWidget
from PyQt5.QtWidgets import QMessageBox
import mysql.connector as mysql
from datetime import datetime, timedelta

# Updated regular expression to extract the float values
pattern = re.compile(r'Pulso: (\d+) - Temperatura: (\d+\.\d+) ºC')

# Conectar al puerto serial
ser = serial.Serial('COM4', 9600, timeout=1)  # Reemplaza 'COM4' con el puerto correcto

pulso = []
temperatura = []

class DataReader(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True

    def run(self):
        while self.running:
            if ser.in_waiting > 0:
                line = ser.readline()
                line = line.decode('utf-8', errors='ignore').strip()
                match = pattern.search(line)
                if match:
                    try:
                        valor_pulso = int(match.group(1))
                        valor_temperatura = float(match.group(2))
                        pulso.append(valor_pulso)
                        temperatura.append(valor_temperatura)
                    except ValueError:
                        print("Error al convertir los valores.")

    def stop(self):
        self.running = False

def detect_peaks(pulso, threshold=500):
    peaks = []
    for i in range(1, len(pulso) - 1):
        if pulso[i] > pulso[i - 1] and pulso[i] > pulso[i + 1] and pulso[i] > threshold:
            peaks.append(i)
    return peaks

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('Interfaz V1.1.ui', self)  # Load the .ui design

        # Connect buttons to their functions
        self.bt_menu.clicked.connect(self.toggle_menu)
        self.bt_minimizar.clicked.connect(self.showMinimized)
        self.bt_maximizar.clicked.connect(self.maximize_restore)
        self.bt_cerrar.clicked.connect(self.close)
        self.bt_inicio.clicked.connect(self.go_to_page_1)
        self.bt_monitor.clicked.connect(self.go_to_page_2)
        self.bt_busqueda.clicked.connect(self.go_to_page_3)

        # Initially collapsed
        self.frame_lateral.setMaximumWidth(0)

        # To track the state of the side menu and the maximized window
        self.menu_expanded = False
        self.is_maximized = False

        # Set page_1 as the current page at startup
        self.stackedWidget.setCurrentWidget(self.page_1)

        # Initialize widgets and timers for the first graph (Pulse)
        self.graphWidget = PlotWidget(self.gridLayoutWidget)
        self.graphWidget.setObjectName("graphWidget")
        self.gridLayout.addWidget(self.graphWidget, 0, 0, 1, 2)
        self.graphWidget.plotItem.setLabel('left', 'Pulso', units='bpm')
        self.graphWidget.plotItem.setLabel('bottom', 'Tiempo', units='s')
        self.graphWidget.setBackground('k')
        self.x1 = list(range(100))  # Initialize x-axis with dummy data
        self.y1 = [0] * 100  # Initialize y-axis with dummy data
        pen1 = pg.mkPen(color='r')
        self.data_line1 = self.graphWidget.plot(self.x1, self.y1, pen=pen1)
        self.timer1 = QtCore.QTimer()
        self.timer1.setInterval(25)
        self.timer1.timeout.connect(self.update_plot_data1)
        self.timer1.start()

        # Initialize widgets and timers for the second graph (Temperature)
        self.graphWidget_2 = PlotWidget(self.gridLayoutWidget)
        self.graphWidget_2.setObjectName("graphWidget_2")
        self.gridLayout_2.addWidget(self.graphWidget_2, 1, 0, 1, 2)
        self.graphWidget_2.plotItem.setLabel('left', 'Temperatura', units='°C')
        self.graphWidget_2.plotItem.setLabel('bottom', 'Tiempo', units='s')
        self.graphWidget_2.setBackground('k')
        self.x2 = list(range(100))  # Initialize x-axis with dummy data
        self.y2 = [0] * 100  # Initialize y-axis with dummy data
        pen2 = pg.mkPen(color='g')
        self.data_line2 = self.graphWidget_2.plot(self.x2, self.y2, pen=pen2)
        self.timer2 = QtCore.QTimer()
        self.timer2.setInterval(25)
        self.timer2.timeout.connect(self.update_plot_data2)
        self.timer2.start()

        # Initialize labels for heart rate and average temperature
        self.valueHeartRate.setText("0")
        self.valueTemperature.setText("0.0")

        # Timer to update the heart rate and average temperature every 10 seconds
        self.timerHeartRate = QtCore.QTimer()
        self.timerHeartRate.setInterval(10000)  # Update every 10 seconds
        self.timerHeartRate.timeout.connect(self.update_labels)
        self.timerHeartRate.start()

        # Start the data reader thread
        self.data_reader = DataReader()
        self.data_reader.start()

        # MySQL connection
        self.db = mysql.connect(host="localhost", user="root", database="electro_3")
        self.cur = self.db.cursor()

        # Set up search functionality
        self.searchButton.clicked.connect(self.search_data)

        self.show()

    def toggle_menu(self):
        if self.menu_expanded:
            self.frame_lateral.setMaximumWidth(0)
        else:
            self.frame_lateral.setMaximumWidth(250)
        self.menu_expanded = not self.menu_expanded

    def maximize_restore(self):
        if self.is_maximized:
            self.showNormal()
        else:
            self.showMaximized()
        self.is_maximized = not self.is_maximized

    def go_to_page_1(self):
        self.stackedWidget.setCurrentWidget(self.page_1)

    def go_to_page_2(self):
        self.stackedWidget.setCurrentWidget(self.page_2)

    def go_to_page_3(self):
        self.stackedWidget.setCurrentWidget(self.page_3)

    def update_plot_data1(self):
        if len(pulso) > 100:
            self.y1 = pulso[-100:]
        else:
            self.y1 = pulso
        self.data_line1.setData(self.x1[:len(self.y1)], self.y1)

    def update_plot_data2(self):
        if len(temperatura) > 100:
            self.y2 = temperatura[-100:]
        else:
            self.y2 = temperatura
        self.data_line2.setData(self.x2[:len(self.y2)], self.y2)

    def update_labels(self):
        if pulso:
            peaks = detect_peaks(pulso)
            peak_intervals = np.diff(peaks) * 0.13  # 0.11 seconds interval
            if len(peak_intervals) > 0:
                bpm = 60.0 / np.mean(peak_intervals)
                self.valueHeartRate.setText(f"{bpm:.2f}")
                # Insert heart rate and temperature into database
                self.insert_data(float(bpm), float(np.mean(temperatura[-10:])))
            else:
                self.valueHeartRate.setText("0")

        if temperatura:
            avg_temp = np.mean(temperatura[-400:])  # Average of last 10 seconds
            self.valueTemperature.setText(f"{avg_temp:.2f}")

    def insert_data(self, bpm, temperature):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO registros (fecha_hora, frecuencia_cardiaca, temperatura) VALUES (%s, %s, %s)"
        values = (current_time, bpm, temperature)
        self.cur.execute(query, values)
        self.db.commit()

    def search_data(self):
        date = self.dateEdit.date().toString("yyyy-MM-dd")
        time = self.timeEdit.time().toString("HH:mm:ss")
        date_time = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M:%S')

        # Calculate the time range (1 minute before and after the selected time)
        start_time = date_time - timedelta(minutes=1)
        end_time = date_time + timedelta(minutes=1)


        query = "SELECT fecha_hora, frecuencia_cardiaca, temperatura FROM registros WHERE fecha_hora BETWEEN %s AND %s ORDER BY fecha_hora ASC"
        self.cur.execute(query, (start_time, end_time))
        results = self.cur.fetchall()

        self.resultsTable.setRowCount(0)  # Clear the table before inserting new data
        self.resultsTable.setColumnCount(3)  # Ensure there are 3 columns

        self.resultsTable.setHorizontalHeaderLabels(["Fecha y Hora", "Frecuencia Cardiaca", "Temperatura"])

        if results:
            for row_number, row_data in enumerate(results):
                self.resultsTable.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(data))
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.resultsTable.setItem(row_number, column_number, item)
        else:
            QMessageBox.information(self, "Sin resultados", "No se encontraron datos para la fecha y hora seleccionadas.", QMessageBox.Ok)

    def closeEvent(self, event):
        self.data_reader.stop()
        self.data_reader.join()
        ser.close()
        self.cur.close()
        self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())