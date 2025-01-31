import paho.mqtt.client as mqtt
from threading import Thread
import time 

class CO2InjectorSimulation:
    def __init__(self, sector):
        self.sector = sector
        self.client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.client_mqtt.on_connect = self.on_connect
        self.client_mqtt.on_message = self.on_message
        self.client_mqtt.connect("mosquitto", 1883)
        thread = Thread(target=self.client_mqtt.loop_forever)
        thread.start()
        
    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"Fan in {self.sector.name} connected")
            client.subscribe(f"execute/{self.sector.name}/co2_injectors")
        else:
            print(f"Failed to connect co2_injectors in {self.sector.name}, error {rc}")

    def on_message(self, client, userdata, msg):
        command = msg.payload.decode("utf-8")
        print(f"Fan in {self.sector.name} received: {command}")
        if command.startswith("ON"):
            #TODO: Define if there is more than one speed
            # _, power = command.split("_") if "_" in command else ("ON", "5")  # Default to power 5 
            self.start_fan(5)
        elif command == "OFF":
            self.stop_fan()

    def start_fan(self, power):
        if not self.running:
            self.running = True
            self.power = max(1, min(10, power))  # Ensure power is between 1 and 10
            print(f"co2_injectors started in {self.sector.name} at power {self.power}")
            Thread(target=self.cooling_effect).start() # Use a thread to simulate the effect

        self.client_mqtt.publish(f"feedback/{self.sector.name}/co2_injectors", f"ON_{self.power}")

    def stop_fan(self):
        self.running = False
        print(f"co2_injectors stopped in {self.sector.name}")
        self.client_mqtt.publish(f"feedback/{self.sector.name}/co2_injectors", "OFF")

    def cooling_effect(self):
        pass
        # """Continuously reduces temperature while the fan is running."""
        # k = 0.05  # Cooling efficiency factor
        # while self.running:
            
        #     ## Use formula to simulate temperature drop
        #     if self.sector.temperature > self.sector.exterior["temperature"]:
        #         temp_drop = -k * self.power * (self.sector.temperature - self.sector.exterior["temperature"])
        #         self.sector.temperature += temp_drop 

        #         # Publish new temperature to MQTT
        #         self.client_mqtt.publish(f"greenhouse/{self.sector.name}/temperature", self.sector.temperature)

        #         print(f"Fan cooling: {self.sector.name} -> Temp: {self.sector.temperature:.2f}°C")

        #     time.sleep(5)  # Update temperature every 5 seconds