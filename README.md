

# Real-Time Heart Rate Monitoring System

This repository contains a real-time heart rate and temperature monitoring system. It uses a combination of Arduino for sensor data collection and a Python application with PyQt5 for data visualization and storage in a MySQL database.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Files](#files)
- [Contributing](#contributing)

## Introduction

This project monitors heart rate and temperature in real-time, displaying the data in a graphical user interface (GUI) and storing it in a MySQL database. The system consists of Arduino for sensor data collection and a Python application for data visualization and database management.

## Features

- Real-time heart rate and temperature monitoring
- Graphical visualization of data
- Data storage in MySQL database
- Search functionality to retrieve historical data

## Requirements

- Python 3.x
- Arduino IDE
- PyQt5
- numpy
- matplotlib
- pyqtgraph
- mysql-connector-python
- scipy
- pandas

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/real-time-heart-rate-monitoring.git
    cd real-time-heart-rate-monitoring
    ```

2. **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Setup MySQL Database:**

    Create a database and table using the following SQL commands:

    ```sql
    CREATE DATABASE electro_3;
    USE electro_3;

    CREATE TABLE registros (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fecha_hora DATETIME,
        frecuencia_cardiaca FLOAT,
        temperatura FLOAT
    );
    ```

4. **Upload Arduino Code:**

    Open `Sensors.ino` in the Arduino IDE and upload it to your Arduino board.

## Usage

1. **Run the Python application:**

    ```bash
    python Real-Time-Heart-Rate.py
    ```

2. **Connect the Arduino to the correct serial port and start the GUI.**

## Files

- `Real-Time-Heart-Rate.py`: Main Python application for data collection, visualization, and storage.
- `Sensors.ino`: Arduino code for collecting heart rate and temperature data from sensors.
- `Interfaz V1.1.ui`: PyQt5 UI file for the graphical interface.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

Feel free to adjust the repository URL, installation instructions, and other sections as needed.
