import paho.mqtt.client as mqtt
import time
import json
import random

# MQTT Settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "smart_wardrobe/dht_sensor"


# MQTT Publisher Function
def publish_sensor_data(client):
    temperature = round(random.uniform(18, 22), 2)  # Simulate temperature (18-22 degrees)
    humidity = round(random.uniform(40, 60), 2)  # Simulate humidity (40-60%)
    message = json.dumps({"temperature": temperature, "humidity": humidity})
    result = client.publish(MQTT_TOPIC, message)
    status = result[0]
    if status == 0:
        print(f"Sent `{message}` to topic `{MQTT_TOPIC}`")
    else:
        print(f"Failed to send message to topic {MQTT_TOPIC}")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("DHT Sensor Emulator Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)


# Set up MQTT client for DHT Sensor Emulator
client = mqtt.Client("DHT_Sensor_Emulator")
client.on_connect = on_connect
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Publish sensor data every 10 seconds
client.loop_start()
while True:
    publish_sensor_data(client)
    time.sleep(10)
