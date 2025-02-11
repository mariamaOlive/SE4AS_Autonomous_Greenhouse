import paho.mqtt.client as mqtt
from threading import Thread
import time 
import random
import json

class HeaterSimulation:
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
            print(f"Heater in {self.sector.name} connected")
            client.subscribe(f"greenhouse/execute/{self.sector.name}")
        else:
            print(f"Failed to connect heater in {self.sector.name}, error {rc}")


    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
                
        try:
            # Parse JSON message
            data = json.loads(payload)
            command = data.get("heater")  # Extract "heater" key from JSON

            print(f"Heater in {self.sector.name} received command: {command}")

            if command == "ON":
                self.start_heater() # Default power 5
            elif command == "OFF":
                self.stop_heater()

        except json.JSONDecodeError:
            print(f"Error: Received invalid JSON: {payload}")


    def start_heater(self):
        if not self.running:
            self.running = True
            print(f"Heater started in {self.sector.name}")
            Thread(target=self.heater_effect).start() # Use a thread to simulate the effect

        self.client_mqtt.publish(f"greenhouse/actuator_status/{self.sector.name}/heater", f"ON")


    def stop_heater(self):
        self.running = False
        print(f"Heater stopped in {self.sector.name}")
        self.client_mqtt.publish(f"greenhouse/actuator_status/{self.sector.name}/heater", "OFF")


    def heater_effect(self):
        k = 0.1  # Efficiency factor

        while self.running:
            temperature_increase = k * self.sector.temperature  
            self.sector.temperature += temperature_increase*random.uniform(0.1, 1)  # Apply heating
            
            # Publish new value to MQTT
            self.client_mqtt.publish(f"greenhouse/sensor_raw/{self.sector.name}/temperature", self.sector.temperature)
            time.sleep(3)  # Update every 3 seconds