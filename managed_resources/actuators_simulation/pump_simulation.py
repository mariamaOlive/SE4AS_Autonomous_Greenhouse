import paho.mqtt.client as mqtt
from threading import Thread
import time
import random
import json

class PumpSimulation:
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
            print(f"Pump in {self.sector.name} connected")
            client.subscribe(f"greenhouse/execute/{self.sector.name}") 
        else:
            print(f"Failed to connect pump in {self.sector.name}, error {rc}")


    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
                
        try:
            # Parse JSON message
            data = json.loads(payload)
            command = data.get("pump")  # Extract "pump" key from JSON

            print(f"Pump in {self.sector.name} received command: {command}")

            if command == "ON":
                self.start_pump()
            elif command == "OFF":
                self.stop_pump()

        except json.JSONDecodeError:
            print(f"Error: Received invalid JSON: {payload}")


    def start_pump(self):
        if not self.running:
            self.running = True
            print(f"Pump started in {self.sector.name}")
            Thread(target=self.pump_effect).start()  # Simulate humidity increase

        # Publish feedback
        self.client_mqtt.publish(f"greenhouse/actuator_status/{self.sector.name}/pump", "ON")


    def stop_pump(self):
        self.running = False
        print(f"Pump stopped in {self.sector.name}")
        self.client_mqtt.publish(f"greenhouse/actuator_status/{self.sector.name}/pump", "OFF")


    def pump_effect(self):
        k = 0.1  # Humidity increase factor

        while self.running:
            humidity_increase = k * (100 - self.sector.humidity)  # More effective when humidity is low
            self.sector.humidity += humidity_increase * random.uniform(0.5, 1.2)  # Randomized increase
            
            # Prevent unrealistic values (humidity max 100%)
            self.sector.humidity = min(100, self.sector.humidity)

            # Publish new value to MQTT
            self.client_mqtt.publish(f"greenhouse/sensor_raw/{self.sector.name}/humidity", self.sector.humidity)

            time.sleep(5)  # Update every 5 seconds