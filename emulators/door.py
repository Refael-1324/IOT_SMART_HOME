from kivy.app import App
from kivy.uix.button import Button
from kivy.core.window import Window
import paho.mqtt.client as mqtt
import json

# MQTT Settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "smart_wardrobe/door_sensor"

# Initialize the door status
door_open = False


class DoorApp(App):
    def build(self):
        self.client = mqtt.Client("Door_Sensor_Emulator_GUI_Kivy")
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()

        Window.size = (150, 120)
        self.button = Button(text='Open Door')
        self.button.bind(on_press=self.publish_door_status)
        return self.button

    def publish_door_status(self, instance):
        global door_open
        door_open = not door_open  # Toggle the door status
        message = json.dumps({"status": "open" if door_open else "closed"})
        self.client.publish(MQTT_TOPIC, message)
        self.button.text = "Close Door" if door_open else "Open Door"
        print(f"Door status published: {'open' if door_open else 'closed'}")


if __name__ == '__main__':
    DoorApp().run()
