#!/usr/bin/env python3

import time
import random
import os
import json
from datetime import datetime

"""
This script simulates GPS data for testing the GPS mapping application
without requiring actual GPS hardware. It creates a simulated data file
that can be used by modifying the main application to read from this file
instead of the serial port.
"""

# Configuration
SIMULATION_DURATION = 300  # seconds
UPDATE_INTERVAL = 1  # seconds
OUTPUT_FILE = "simulated_gps_data.json"

# Starting position (example: Central Park, New York)
start_lat = 40.785091
start_lon = -73.968285

# Function to generate simulated GPS data
def generate_gps_data(elapsed_time):
    # Simulate movement by slightly changing coordinates
    # This creates a random walk pattern
    lat_change = random.uniform(-0.0001, 0.0001)
    lon_change = random.uniform(-0.0001, 0.0001)
    
    # Calculate new position
    latitude = start_lat + (lat_change * elapsed_time)
    longitude = start_lon + (lon_change * elapsed_time)
    
    # Simulate other GPS data
    speed = random.uniform(0, 10)  # km/h
    altitude = 50 + random.uniform(-5, 5)  # meters
    satellites = random.randint(4, 12)
    fix_quality = random.randint(1, 2)
    
    # Current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "latitude": latitude,
        "longitude": longitude,
        "speed": speed,
        "altitude": altitude,
        "satellites": satellites,
        "fix_quality": fix_quality,
        "timestamp": timestamp
    }

# Main simulation function
def run_simulation():
    print(f"Starting GPS data simulation for {SIMULATION_DURATION} seconds...")
    print(f"Data will be saved to {OUTPUT_FILE}")
    
    simulated_data = []
    
    for elapsed_time in range(0, SIMULATION_DURATION, UPDATE_INTERVAL):
        # Generate data point
        data_point = generate_gps_data(elapsed_time)
        simulated_data.append(data_point)
        
        # Print current position
        print(f"Time: {elapsed_time}s, Lat: {data_point['latitude']:.6f}, Lon: {data_point['longitude']:.6f}, Speed: {data_point['speed']:.2f} km/h")
        
        # Save current data to file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(simulated_data, f, indent=2)
        
        time.sleep(UPDATE_INTERVAL)
    
    print(f"Simulation complete. {len(simulated_data)} data points generated.")

# Instructions for using the simulated data
def print_usage_instructions():
    print("\nTo use this simulated data with the GPS mapping application:")
    print("1. Modify gps_map.py to read from the simulated_gps_data.json file")
    print("2. Add the following code to gps_reader_thread() function:")
    print("""
    # For simulation mode
    with open('simulated_gps_data.json', 'r') as f:
        simulated_data = json.load(f)
    
    for data_point in simulated_data:
        with data_lock:
            gps_data.update(data_point)
        time.sleep(1)  # Update at 1Hz
    """)

if __name__ == "__main__":
    run_simulation()
    print_usage_instructions()