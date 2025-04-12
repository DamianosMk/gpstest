#!/usr/bin/env python3

import serial
import time
import folium
import pynmea2
import webbrowser
import os
import threading
import gpiod
from flask import Flask, render_template, jsonify

# Flask app for web interface
app = Flask(__name__)

# Global variables to store GPS data
gps_data = {
    "latitude": 0.0,
    "longitude": 0.0,
    "speed": 0.0,
    "timestamp": "",
    "satellites": 0,
    "altitude": 0.0,
    "fix_quality": 0
}

# Lock for thread-safe access to GPS data
data_lock = threading.Lock()

# GPS module configuration
GPS_UART_PORT = "/dev/ttyS0"  # Default UART port on Raspberry Pi
GPS_BAUD_RATE = 9600

# Function to initialize the GPS module using gpiod
def initialize_gps():
    try:
        # For Raspberry Pi 5, we're using UART for communication with NEO-6M
        # The gpiod library is used for any additional GPIO control if needed
        # For example, if we need to control a reset pin or power enable pin
        
        # Example of using gpiod to control a GPIO pin if needed
        # chip = gpiod.Chip('gpiochip0')
        # reset_line = chip.get_line(17)  # Example GPIO pin
        # reset_line.request(consumer="gps_app", type=gpiod.LINE_REQ_DIR_OUT)
        # reset_line.set_value(1)  # Set high
        # time.sleep(0.1)
        # reset_line.set_value(0)  # Set low
        # time.sleep(0.1)
        # reset_line.set_value(1)  # Set high again
        
        # Open serial connection to GPS module
        ser = serial.Serial(GPS_UART_PORT, baudrate=GPS_BAUD_RATE, timeout=1)
        print(f"GPS module initialized on {GPS_UART_PORT}")
        return ser
    except Exception as e:
        print(f"Error initializing GPS module: {e}")
        return None

# Function to parse NMEA sentences from GPS
def parse_gps_data(nmea_sentence):
    try:
        msg = pynmea2.parse(nmea_sentence)
        
        # Extract GPS data from different NMEA sentence types
        with data_lock:
            if isinstance(msg, pynmea2.GGA):
                # Global Positioning System Fix Data
                gps_data["latitude"] = msg.latitude
                gps_data["longitude"] = msg.longitude
                gps_data["altitude"] = msg.altitude
                gps_data["fix_quality"] = msg.gps_qual
                gps_data["satellites"] = msg.num_sats
                gps_data["timestamp"] = msg.timestamp.strftime("%H:%M:%S") if msg.timestamp else ""
                
            elif isinstance(msg, pynmea2.RMC):
                # Recommended Minimum Navigation Information
                gps_data["latitude"] = msg.latitude
                gps_data["longitude"] = msg.longitude
                gps_data["speed"] = msg.spd_over_grnd * 1.852  # Convert knots to km/h
                gps_data["timestamp"] = msg.datetime.strftime("%Y-%m-%d %H:%M:%S") if msg.datetime else ""
                
            elif isinstance(msg, pynmea2.GSV):
                # Satellites in View
                gps_data["satellites"] = msg.num_sv_in_view
                
        return True
    except Exception as e:
        print(f"Error parsing NMEA sentence: {e}")
        return False

# Function to continuously read GPS data
def gps_reader_thread(serial_port):
    while True:
        try:
            if serial_port is None:
                print("Serial port not available. Attempting to reconnect...")
                serial_port = initialize_gps()
                if serial_port is None:
                    time.sleep(5)  # Wait before retrying
                    continue
                    
            line = serial_port.readline().decode('ascii', errors='replace').strip()
            if line.startswith('$'):
                parse_gps_data(line)
                
        except Exception as e:
            print(f"Error reading GPS data: {e}")
            serial_port = None  # Reset serial port to trigger reconnection
            time.sleep(1)

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gps_data')
def get_gps_data():
    with data_lock:
        return jsonify(gps_data)

# Function to create the templates directory and HTML files
def create_templates():
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create index.html template
    index_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>GPS Tracker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body { margin: 0; padding: 0; }
        #map { height: 70vh; width: 100%; }
        #info { padding: 10px; background-color: #f8f9fa; }
        .data-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
        .data-label { font-weight: bold; }
    </style>
</head>
<body>
    <div id="map"></div>
    <div id="info">
        <h3>GPS Information</h3>
        <div class="data-row">
            <span class="data-label">Latitude:</span>
            <span id="latitude">--</span>
        </div>
        <div class="data-row">
            <span class="data-label">Longitude:</span>
            <span id="longitude">--</span>
        </div>
        <div class="data-row">
            <span class="data-label">Speed:</span>
            <span id="speed">--</span>
        </div>
        <div class="data-row">
            <span class="data-label">Altitude:</span>
            <span id="altitude">--</span>
        </div>
        <div class="data-row">
            <span class="data-label">Satellites:</span>
            <span id="satellites">--</span>
        </div>
        <div class="data-row">
            <span class="data-label">Fix Quality:</span>
            <span id="fix_quality">--</span>
        </div>
        <div class="data-row">
            <span class="data-label">Timestamp:</span>
            <span id="timestamp">--</span>
        </div>
    </div>

    <script>
        // Initialize map
        var map = L.map('map').setView([0, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        var marker = null;
        var path = L.polyline([], {color: 'blue'}).addTo(map);
        var positions = [];
        var firstPosition = true;
        
        // Function to update GPS data
        function updateGPSData() {
            fetch('/gps_data')
                .then(response => response.json())
                .then(data => {
                    // Update info panel
                    document.getElementById('latitude').textContent = data.latitude.toFixed(6);
                    document.getElementById('longitude').textContent = data.longitude.toFixed(6);
                    document.getElementById('speed').textContent = data.speed.toFixed(2) + ' km/h';
                    document.getElementById('altitude').textContent = data.altitude.toFixed(2) + ' m';
                    document.getElementById('satellites').textContent = data.satellites;
                    document.getElementById('fix_quality').textContent = data.fix_quality;
                    document.getElementById('timestamp').textContent = data.timestamp;
                    
                    // Update map if we have valid coordinates
                    if (data.latitude !== 0 && data.longitude !== 0) {
                        var position = [data.latitude, data.longitude];
                        positions.push(position);
                        
                        // Update marker
                        if (marker === null) {
                            marker = L.marker(position).addTo(map);
                        } else {
                            marker.setLatLng(position);
                        }
                        
                        // Update path
                        path.setLatLngs(positions);
                        
                        // Center map on first valid position
                        if (firstPosition) {
                            map.setView(position, 15);
                            firstPosition = false;
                        }
                    }
                })
                .catch(error => console.error('Error fetching GPS data:', error));
        }
        
        // Update GPS data every second
        setInterval(updateGPSData, 1000);
    </script>
</body>
</html>
'''
    
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(index_html)

# Main function
def main():
    # Create templates directory and files
    create_templates()
    
    # Initialize GPS module
    serial_port = initialize_gps()
    
    # Start GPS reader thread
    gps_thread = threading.Thread(target=gps_reader_thread, args=(serial_port,), daemon=True)
    gps_thread.start()
    
    # Start Flask server
    print("Starting web server. Open a browser and navigate to http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()