from kivy.app import App
from kivy.uix.button import Button
from kivy.core.window import Window
import paho.mqtt.client as mqtt
import json

# MQTT Settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "smart_wardrobe/light_button"

# Initialize the light status
light_status = False


class LightButtonApp(App):
    def build(self):
        self.client = mqtt.Client("Light_Button_Emulator_GUI")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()

        Window.size = (150, 120)
        self.button = Button(text='Turn On')
        self.button.bind(on_press=self.publish_light_status)
        return self.button

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(MQTT_TOPIC)

    def on_message(self, client, userdata, msg):
        global light_status
        message = json.loads(msg.payload.decode("utf-8"))
        if message['light_status'] == 'on':
            light_status = True
        else:
            light_status = False
        # Update the button's text based on the received message
        self.button.text = "Turn Off" if light_status else "Turn On"
        print(f"Light status updated from message: {'on' if light_status else 'off'}")

    def publish_light_status(self, instance):
        global light_status
        light_status = not light_status
        message = json.dumps({"light_status": "on" if light_status else "off"})
        self.client.publish(MQTT_TOPIC, message)
        self.button.text = "Turn Off" if light_status else "Turn On"
        print(f"Light status published: {'on' if light_status else 'off'}")


if __name__ == '__main__':
    LightButtonApp().run()
