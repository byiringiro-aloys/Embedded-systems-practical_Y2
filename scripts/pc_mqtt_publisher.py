import serial
import time
import paho.mqtt.client as mqtt

# ================= Configuration =================
# Change this to match your Arduino's COM port (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux)
SERIAL_PORT = 'COM3'  
BAUD_RATE = 9600

# Replace with your VPS IP address or hostname
MQTT_BROKER = 'test.mosquitto.org'  # Using a public test broker by default
MQTT_PORT = 1883
MQTT_TOPIC = 'byiringiro_aloys/y2a/temperature'
# =================================================

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Connected to MQTT Broker at {MQTT_BROKER}")
    else:
        print(f"Failed to connect, return code {rc}")

def main():
    # Setup MQTT Client
    # Depending on paho-mqtt version, you might need to specify CallbackAPIVersion
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()
        
    client.on_connect = on_connect
    
    print("Connecting to MQTT broker...")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"Could not connect to MQTT broker: {e}")
        return

    # Setup Serial Connection
    print(f"Connecting to Arduino on {SERIAL_PORT}...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) # Wait for Arduino to reset after serial connection
        print("Successfully connected to Arduino. Listening for data...\n")
    except serial.SerialException as e:
        print(f"Serial Error: {e}")
        print("Please verify the SERIAL_PORT and ensure the Arduino is not opened in the Arduino IDE Serial Monitor.")
        client.loop_stop()
        return

    try:
        while True:
            if ser.in_waiting > 0:
                # Read line from serial and decode
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Check if it's the expected temperature format
                if line.startswith("TEMP:"):
                    try:
                        temp_str = line.split(":")[1]
                        temp_val = float(temp_str)
                        
                        # 1. Display in real time
                        print(f"[Real-Time Data] Temperature: {temp_val} °C")
                        
                        # 2. Publish to MQTT broker
                        client.publish(MQTT_TOPIC, str(temp_val))
                        print(f"  -> Published {temp_val} to topic '{MQTT_TOPIC}'")
                        
                    except ValueError:
                        print(f"Received malformed temperature data: {line}")
                else:
                    # Might be debug prints like "Error reading DHT sensor"
                    if line:
                        print(f"[Arduino]: {line}")
                        
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nExiting program...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
        client.loop_stop()
        client.disconnect()
        print("Connections closed.")

if __name__ == "__main__":
    main()
