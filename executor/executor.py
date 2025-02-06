import paho.mqtt.client as mqtt
import time
import json
import random
import os


# MQTT setup
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


class Executor:
    def __init__(self):
        self.current_actuator_state = {}
        
        self.client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.client_mqtt.on_connect = self.on_connect
        self.client_mqtt.on_message = self.on_message
        self.client_mqtt.on_subscribe = self.on_subscribe
        
        self.execution_command = {}
        # Connect to the MQTT broker
        self.client_mqtt.connect(MQTT_BROKER, MQTT_PORT)

        # Start the MQTT loop in the background using loop_start()
        self.client_mqtt.loop_start()  # Non-blocking loop to process incoming messages

        

    def on_connect(self, client, userdata, flags, reason_code, properties):
        '''Callback function for when the client receives a CONNACK response from the server.'''
        if reason_code == 0:
            print("Connected to MQTT Broker!")
            self.client_mqtt.subscribe("greenhouse/planner_strategy/#")  # Subscribe to the raw sensor data topics
        else:
            print(f"Failed to connect: {reason_code}")
            
    def on_message(self, client, userdata, msg):
        '''Callback function for when a PUBLISH message is received from the server.'''
        print(f"Received message on topic {msg.topic}: {msg.payload}")
        payload = json.loads(msg.payload)
        
        self.execution_command = payload
        self.process_commands_from_planner()
        
        
    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        '''Callback function for when the client receives a SUBACK response from the server.'''
        if reason_code_list[0].is_failure:
            print(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")
    
    def execute(self, sector):
        execution_plan = self.execution_command[sector]
        
        topic = f"greenhouse/execute/{sector}"
        self.client_mqtt.publish(topic, json.dumps(execution_plan), qos=2)
        print(f"Sent execution plan for {sector}: {execution_plan}")  
        
    def process_commands_from_planner(self,):
        for sector in self.execution_command.keys():
            self.execute(sector)
            
            
        
          
    def random_executor(self,sector):

        command_fan = random.choice(["ON", "OFF"])
        command_co2_injector = random.choice(["ON", "OFF"])
        command_heater= random.choice(["ON", "OFF"])
        command_pump= random.choice(["ON", "OFF"])
        command_lights= random.choice(["ON", "OFF"])
        command_hatch= random.choice(["OPEN", "CLOSE"])

        return {
            "fan": command_fan,
            "co2_injector": command_co2_injector,
            "heater": command_heater,
            "pump": command_pump,
            "led_lights": command_lights,
            "hatch": command_hatch,
        }

if __name__ == '__main__':
    executor = Executor()
    with open("sector_config.json", "r") as file:
        sector_data = json.load(file)
    weather_type = "Sunny"
    sectors_conf = sector_data[weather_type]["sectors"]
    exterior_conf = sector_data[weather_type]["exterior"]


    while True:
        time.sleep(1)