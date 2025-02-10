import paho.mqtt.client as mqtt
from threading import Thread
import time 
import random
import json

class CO2InjectorSimulation:
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
            print(f"CO2 Injector in {self.sector.name} connected")
            client.subscribe(f"greenhouse/execute/{self.sector.name}")
        else:
            print(f"Failed to connect co2_injectors in {self.sector.name}, error {rc}")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
                
        try:
            # Parse JSON message
            data = json.loads(payload)
            command = data.get("co2_injector")  # Extract "co2_injector" key from JSON

            print(f"CO2 injector in {self.sector.name} received command: {command}")

            if command == "ON":
                self.start_co2_injection() # Default power 5
            elif command == "OFF":
                self.stop_co2_injection()

        except json.JSONDecodeError:
            print(f"Error: Received invalid JSON: {payload}")


    def start_co2_injection(self):
        if not self.running:
            self.running = True
            print(f"co2_injectors started in {self.sector.name}")
            self.client_mqtt.publish(f"greenhouse/actuator_status/{self.sector.name}/co2_injector", "ON")
            Thread(target=self.co2_injection_effect).start() # Use a thread to simulate the effect


    def stop_co2_injection(self):
        self.running = False
        print(f"co2_injectors stopped in {self.sector.name}")
        self.client_mqtt.publish(f"greenhouse/actuator_status/{self.sector.name}/co2_injector", "OFF")

    def co2_injection_effect(self):
        k = 0.05  # Efficiency factor

        while self.running:
            co2_increase = k * self.sector.co2_levels  
            self.sector.co2_levels += co2_increase*random.uniform(.5, 1) 
            
            # Publish new value to MQTT
            self.client_mqtt.publish(f"greenhouse/sensor_raw/{self.sector.name}/co2_levels", self.sector.co2_levels)
            time.sleep(5)  # Update every 5 seconds