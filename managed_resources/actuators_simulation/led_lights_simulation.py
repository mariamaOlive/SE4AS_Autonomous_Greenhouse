import paho.mqtt.client as mqtt
from threading import Thread
import time
import json

class LedLightSimulation:
    def __init__(self, sector):
        self.sector = sector
        self.running = False
        self.client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.client_mqtt.on_connect = self.on_connect
        self.client_mqtt.on_message = self.on_message
        self.client_mqtt.connect("mosquitto", 1883)
        thread = Thread(target=self.client_mqtt.loop_forever)
        thread.start()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"LED Lights in {self.sector.name} connected")
            client.subscribe(f"execute/{self.sector.name}") 
        else:
            print(f"Failed to connect LED lights in {self.sector.name}, error {rc}")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        
        try:
            # Parse JSON message
            data = json.loads(payload)
            command = data.get("led_lights")  # Extract LED control command

            print(f"LED Lights in {self.sector.name} received command: {command}")

            if command == "ON":
                self.turn_on_lights()
            elif command == "OFF":
                self.turn_off_lights()

        except json.JSONDecodeError:
            print(f"Error: Received invalid JSON: {payload}")

    def turn_on_lights(self):
        led_intensity = 60000  # Fixed LED intensity when ON (in lux)
        if self.sector.sun_light_intensity < led_intensity:
            self.sector.internal_light_intensity = led_intensity  
        
        self.client_mqtt.publish(f"greenhouse/{self.sector.name}/internal_light_intensity", led_intensity)
        # self.client_mqtt.publish(f"feedback/{self.sector.name}/led_lights", "ON")
        self.running = True  # Mark as ON
        
    def turn_off_lights(self):
        self.internal_light_intensity = self.sector.sun_light_intensity
        self.client_mqtt.publish(f"greenhouse/{self.sector.name}/internal_light_intensity", self.internal_light_intensity)
        # self.client_mqtt.publish(f"feedback/{self.sector.name}/led_lights", "OFF")
        self.running = False  # Mark as OFF