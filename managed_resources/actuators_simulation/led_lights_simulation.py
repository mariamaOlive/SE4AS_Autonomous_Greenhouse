import paho.mqtt.client as mqtt
from threading import Thread
import time
import json

class LedLightSimulation:
    def __init__(self, sector):
        self.sector = sector
        self.LED_INTENSITY = 22600 # Fixed LED intensity when ON (in lux)
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
            client.subscribe(f"greenhouse/execute/{self.sector.name}") 
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
        """Activates LED lights and increases internal light intensity smoothly."""
        if not self.running:
            self.running = True
            print(f"LED Lights in {self.sector.name} turned ON.")

        self.set_led_light_intensity()
        
    def turn_off_lights(self):
        """Deactivates LED lights and gradually decreases internal light intensity."""
        if self.running:
            self.running = False
            print(f"LED Lights in {self.sector.name} turned OFF.")

        self.set_led_light_intensity()

    def set_led_light_intensity(self):
        """Smoothly adjusts the internal light intensity based on LED and Sunlight conditions."""
        
        greenhouse_sunlight_intensity = self.sector.sun_light_intensity * self.sector.shading_factor

        if self.running and greenhouse_sunlight_intensity < self.LED_INTENSITY:
            self.sector.internal_light_intensity = self.LED_INTENSITY
        else:
            self.sector.internal_light_intensity = greenhouse_sunlight_intensity
        # round to 2 decimal places
        self.sector.internal_light_intensity = round(self.sector.internal_light_intensity, 2)

        # Publish updated intensity
        self.publish_status("ON" if self.running else "OFF")
        
    def publish_status(self, status):
        self.client_mqtt.publish(
            f"greenhouse/sensor_raw/{self.sector.name}/internal_light_intensity",
            self.sector.internal_light_intensity,
        )
        self.client_mqtt.publish(
            f"greenhouse/actuator_status/{self.sector.name}/led_lights", status
        )
  

