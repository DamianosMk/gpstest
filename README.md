# GPS NEO-6M Mapping Application for Raspberry Pi 5

This application interfaces with a NEO-6M GPS module connected to a Raspberry Pi 5, reads GPS data, and displays the location on an interactive map using a web interface.

## Features

- Real-time GPS tracking with map display
- Path tracking (shows your movement history)
- Displays detailed GPS information:
  - Latitude and Longitude
  - Speed
  - Altitude
  - Number of satellites
  - Fix quality
  - Timestamp
- Web-based interface accessible from any device on the same network

## Hardware Requirements

- Raspberry Pi 5
- NEO-6M GPS Module
- Jumper wires for connections

## Wiring Instructions

Connect the NEO-6M GPS module to the Raspberry Pi 5 as follows:

| NEO-6M Pin | Raspberry Pi 5 Pin |
|------------|--------------------|
| VCC        | 3.3V or 5V (Pin 2 or 4) |
| GND        | Ground (Pin 6) |
| TX         | RX (GPIO 15, Pin 10) |
| RX         | TX (GPIO 14, Pin 8) |

## Installation

1. Clone this repository to your Raspberry Pi 5:

```bash
git clone https://github.com/yourusername/gps-neo6m-map.git
cd gps-neo6m-map
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Enable UART on your Raspberry Pi 5:

```bash
sudo raspi-config
```

Navigate to "Interface Options" > "Serial" and:
- Disable serial login shell
- Enable serial hardware

4. Reboot your Raspberry Pi:

```bash
sudo reboot
```

## Usage

1. Run the application:

```bash
python gps_map.py
```

2. Open a web browser and navigate to:

```
http://[raspberry-pi-ip-address]:5000
```

Replace `[raspberry-pi-ip-address]` with the IP address of your Raspberry Pi 5.

## Troubleshooting

- **No GPS data**: Make sure the GPS module has a clear view of the sky. It may take a few minutes to acquire a satellite fix.
- **Serial port errors**: Check your wiring connections and ensure UART is properly enabled.
- **Web interface not accessible**: Verify that you're connecting to the correct IP address and that no firewall is blocking port 5000.

## License

MIT