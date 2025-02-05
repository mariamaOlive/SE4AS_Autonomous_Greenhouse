import paho.mqtt.client as mqtt
from threading import Thread
import time 
import json
import random

class FanSimulation:
    def __init__(self, sector):
        self.sector = sector
        self.running = False # The fan is OFF
        self.client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.client_mqtt.on_connect = self.on_connect
        self.client_mqtt.on_message = self.on_message
        self.client_mqtt.connect("mosquitto", 1883)
        thread = Thread(target=self.client_mqtt.loop_forever)
        thread.start()
        
    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"Fan in {self.sector.name} connected")
            client.subscribe(f"execute/{self.sector.name}")
        else:
            print(f"Failed to connect fan in {self.sector.name}, error {rc}")


    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        
        try:
            # Parse JSON message
            data = json.loads(payload)
            command = data.get("fan")  # Extract "fan" key from JSON

            print(f"Fan in {self.sector.name} received command: {command}")

            if command == "ON":
                self.start_fan(10)  # Default power 5
            elif command == "OFF":
                self.stop_fan()

        except json.JSONDecodeError:
            print(f"Error: Received invalid JSON: {payload}")


    def start_fan(self, power):
        if not self.running:
            self.running = True
            self.power = max(1, min(10, power))  # Ensure power is between 1 and 10
            print(f"Fan started in {self.sector.name} at power {self.power}")
            Thread(target=self.cooling_effect).start() # Use a thread to simulate the effect

        self.client_mqtt.publish(f"greenhouse/feedback/{self.sector.name}/fan", f"ON")


    def stop_fan(self):
        self.running = False
        print(f"Fan stopped in {self.sector.name}")
        self.client_mqtt.publish(f"greenhouse/feedback/{self.sector.name}/fan", "OFF")


    def cooling_effect(self):
        k = 0.005  # Cooling efficiency factor

        while self.running:
            # Adjust Temperature
            temp_drop = -k * self.power * self.sector.temperature  # Cooling based on current temp & fan power
            self.sector.temperature += temp_drop*random.uniform(0.1, 1)  # Apply cooling
            
            # Adjust Humidiy
            hum_drop = -k * self.power * self.sector.humidity  # Cooling based on current temp & fan power
            self.sector.humidity += hum_drop*random.uniform(0.1, 1)  # Apply cooling

            # Publish new temperature to MQTT
            self.client_mqtt.publish(f"greenhouse/{self.sector.name}/temperature", self.sector.temperature)
            self.client_mqtt.publish(f"greenhouse/{self.sector.name}/humidity", self.sector.humidity)

            time.sleep(5)  # Update every 5 seconds