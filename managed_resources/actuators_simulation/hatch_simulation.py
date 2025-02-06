import paho.mqtt.client as mqtt
from threading import Thread
import json

class HatchSimulation:
    def __init__(self, sector):
        self.sector = sector
        self.running = False  # Indicates if the hatch is open
        self.client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.client_mqtt.on_connect = self.on_connect
        self.client_mqtt.on_message = self.on_message
        self.client_mqtt.connect("mosquitto", 1883)
        thread = Thread(target=self.client_mqtt.loop_forever)
        thread.start()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"Hatch in {self.sector.name} connected")
            client.subscribe(f"greenhouse/execute/{self.sector.name}") 
        else:
            print(f"Failed to connect hatch in {self.sector.name}, error {rc}")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        
        try:
            # Parse JSON message
            data = json.loads(payload)
            command = data.get("hatch")  # Extract hatch control command

            print(f"Hatch in {self.sector.name} received command: {command}")

            if not self.running and command == "OPEN":
                self.open_hatch()
                self.update_knowledgeBase(command)
            elif self.running and command == "CLOSE":
                self.close_hatch()
                self.update_knowledgeBase(command)
            else:
                print(f"The Hatch is already {command}")

        except json.JSONDecodeError:
            print(f"Error: Received invalid JSON: {payload}")

    def open_hatch(self):
        print(f"Opening hatch in {self.sector.name}")
        self.client_mqtt.publish(f"greenhouse/feedback/{self.sector.name}/hatch", "OPEN")
        self.running = True  # Mark as OPEN

    def close_hatch(self):
        print(f"Closing hatch in {self.sector.name}")
        self.client_mqtt.publish(f"greenhouse/feedback/{self.sector.name}/hatch", "CLOSE")
        self.running = False  # Mark as CLOSED

    
    def  update_knowledgeBase(self, command):
        self.client_mqtt.publish(f"greenhouse/actuator_status/{self.sector.name}/hatch", command)
