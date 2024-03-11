import paho.mqtt.client as mqtt
import sqlite3
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from datetime import datetime
from gui.colored_label import ColoredLabel

# Database Setup
db_filename = 'smart_wardrobe.db'


def init_db():
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS light_status
                 (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS door_status
                 (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS dht_data
                 (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, temperature REAL, humidity REAL)''')
    conn.commit()
    conn.close()


init_db()  # Initialize the database and tables

# MQTT Settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPICS = [("smart_wardrobe/light_button", 1),
          ("smart_wardrobe/door_sensor", 1),
          ("smart_wardrobe/dht_sensor", 1)]


class SmartWardrobeApp(App):
    def build(self):
        self.client = mqtt.Client("Smart_Wardrobe_Main_App")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()

        self.main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.light_status_label = ColoredLabel(text="Light: Unknown", bg_color=[0, 0.250, 0.250, 0.92])
        self.main_layout.add_widget(self.light_status_label)

        self.door_status_label = ColoredLabel(text="Door: Unknown", bg_color=[0, 0.250, 0.250, 0.92])
        self.main_layout.add_widget(self.door_status_label)

        self.temp_hum_label = ColoredLabel(text="Temp: --°C, Hum: --%", bg_color=[0, 0.250, 0.250, 0.92])
        self.main_layout.add_widget(self.temp_hum_label)

        self.notification_label = ColoredLabel(text="notifications:", bg_color=[0.241, 0.245, 0.39, 0.8])
        self.main_layout.add_widget(self.notification_label)
        self.notifications_text = TextInput(size_hint_y=None, height=600, readonly=True)
        self.main_layout.add_widget(self.notifications_text)

        exit_button = Button(text="Exit", size_hint_y=None, height=50, background_color=[1, 0, 0, 1])
        exit_button.bind(on_press=self.exit_app)
        self.main_layout.add_widget(exit_button)

        return self.main_layout

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(TOPICS)

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode("utf-8"))
        print(f"Received `{message}` from `{msg.topic}` topic")

        conn = sqlite3.connect(db_filename)
        c = conn.cursor()

        if msg.topic == "smart_wardrobe/light_button":
            print("Updating light status in GUI")
            c.execute("INSERT INTO light_status (status) VALUES (?)", (message['light_status'],))
            self.light_status_label.text = f"Light: {message['light_status'].capitalize()}"
            self.add_notification(f"Light turned {message['light_status']}")

        elif msg.topic == "smart_wardrobe/door_sensor":
            c.execute("INSERT INTO door_status (status) VALUES (?)", (message['status'],))
            self.door_status_label.text = f"Door: {message['status'].capitalize()}"
            print("Door status updated:", message['status'])
            self.add_notification(f"Door {message['status']}")

            # Logic to turn the light on or off based on door status
            if message['status'] == 'open':
                client.publish("smart_wardrobe/light_button", json.dumps({"light_status": "on"}))
            elif message['status'] == 'closed':
                client.publish("smart_wardrobe/light_button", json.dumps({"light_status": "off"}))

        elif msg.topic == "smart_wardrobe/dht_sensor":
            c.execute("INSERT INTO dht_data (temperature, humidity) VALUES (?, ?)", (message['temperature'], message['humidity']))
            self.temp_hum_label.text = f"Temp: {message['temperature']}°C, Hum: {message['humidity']}%"
            temperature = message['temperature']
            humidity = message['humidity']
            # Check if temperature or humidity is out of the normal range
            if not (18 <= temperature <= 25) or not (30 <= humidity <= 50):
                # Alert in CAPS if out of normal range
                temp_notification_message = f"ALERT!! TEMPERATURE: {temperature}°C --- OUT OF NORMAL RANGE!"
            else:
                temp_notification_message = f"Temperature: {temperature}°C"

            if not (30 <= humidity <= 50):
                # Alert in CAPS if out of normal range
                hum_notification_message = f"ALERT!! HUMIDITY LEVEL: {humidity}% --- OUT OF NORMAL RANGE!"
            else:
                hum_notification_message = f"Humidity level: {humidity}%"

            self.add_notification(temp_notification_message)
            self.add_notification(hum_notification_message)

        conn.commit()
        conn.close()

    def add_notification(self, message):
        def update_notifications(dt):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_message = f"[{timestamp}] {message}\n"
            self.notifications_text.text = new_message + self.notifications_text.text
            self.notifications_text.scroll_y = 0

        Clock.schedule_once(update_notifications, 0)

    def test_button_pressed(self, instance):
        print("Test button pressed")

    def on_stop(self):
        self.client.loop_stop()

    def exit_app(self, instance):
        self.stop()


if __name__ == '__main__':
    SmartWardrobeApp().run()
