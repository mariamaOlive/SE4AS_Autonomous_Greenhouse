import paho.mqtt.client as mqtt
import os
import time
import json

from plans import Plans


# MQTT setup
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))


#planner class
class Planner:
    def __init__(self):
        self.client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.client_mqtt.on_connect = self.on_connect
        self.client_mqtt.on_message = self.on_message
        self.client_mqtt.on_subscribe = self.on_subscribe

        # Connect to the MQTT broker
        self.client_mqtt.connect(MQTT_BROKER, MQTT_PORT)
        
        self.initialize_variables()

        # Start the MQTT loop in the background using loop_start()
        self.client_mqtt.loop_start()  # Non-blocking loop to process incoming messages

    def initialize_variables(self):
       
        self.prev_actuator_change_status = {}
        self.current_actuator_change_status = {}
        self.current_actuator_state = {"North Section": {"co2_injector": "OFF", "fan": "OFF", "hatch": "CLOSE", "heater": "OFF", "led_lights": "OFF", "pump": "OFF"}, 
                                            "South Section": {"co2_injector": "OFF", "fan": "OFF", "hatch": "CLOSE", "heater": "OFF", "led_lights": "OFF", "pump": "OFF"}, 
                                            "West Section": {"co2_injector": "OFF", "fan": "OFF", "hatch": "CLOSE", "heater": "OFF", "led_lights": "OFF", "pump": "OFF"}}
        
        
        self.prev_env_var_status = {'North Section': {'co2_levels': 'optimal', 'humidity': 'optimal', 'internal_light_intensity': 'optimal', 'temperature': 'optimal'},  
                                    'South Section': {'co2_levels': 'optimal', 'humidity': 'optimal', 'internal_light_intensity': 'optimal', 'temperature': 'optimal'},
                                    'West Section': {'co2_levels': 'optimal', 'humidity': 'optimal', 'internal_light_intensity': 'optimal', 'temperature': 'optimal'}}

        self.prev_env_var_trend = {'North Section': {'co2_levels': 'Stable', 'humidity': 'Stable', 'internal_light_intensity': 'Stable', 'temperature': 'Stable'},  
                                    'South Section': {'co2_levels': 'Stable', 'humidity': 'Stable', 'internal_light_intensity': 'Stable', 'temperature': 'Stable'},
                                    'West Section': {'co2_levels': 'Stable', 'humidity': 'Stable', 'internal_light_intensity': 'Stable', 'temperature': 'Stable'}}
        
        self.current_env_var_status = {'North Section': {'co2_levels': 'optimal', 'humidity': 'optimal', 'internal_light_intensity': 'optimal', 'temperature': 'optimal'},  
                                    'South Section': {'co2_levels': 'optimal', 'humidity': 'optimal', 'internal_light_intensity': 'optimal', 'temperature': 'optimal'},
                                    'West Section': {'co2_levels': 'optimal', 'humidity': 'optimal', 'internal_light_intensity': 'optimal', 'temperature': 'optimal'}}

        self.current_env_var_trend = {'North Section': {'co2_levels': 'Stable', 'humidity': 'Stable', 'internal_light_intensity': 'Stable', 'temperature': 'Stable'},  
                                    'South Section': {'co2_levels': 'Stable', 'humidity': 'Stable', 'internal_light_intensity': 'Stable', 'temperature': 'Stable'},
                                    'West Section': {'co2_levels': 'Stable', 'humidity': 'Stable', 'internal_light_intensity': 'Stable', 'temperature': 'Stable'}}
        
        self.actuator_command = {}
        
        
        
        
    def on_connect(self, client, userdata, flags, reason_code, properties):
        '''Callback function for when the client receives a CONNACK response from the server.'''
        if reason_code == 0:
            print("Connected to MQTT Broker!")
            self.client_mqtt.subscribe("greenhouse/analyzer/#")
            self.client_mqtt.subscribe('greenhouse/last_updates/+/actuators')
        else:
            print(f"Failed to connect: {reason_code}")

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        '''Callback function for when the client receives a SUBACK response from the server.'''
        if reason_code_list[0].is_failure:
            print(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_message(self, client, userdata, msg):
        '''Callback function for when a PUBLISH message is received from the server.'''
        
        print(f"Received message on topic {msg.topic}: {msg.payload}")
        payload = msg.payload.decode("utf-8")
        payload = json.loads(payload)
        topic_part = msg.topic.split("/")
        section = topic_part[2]
        
        if topic_part[1] == 'last_updates':
            self.set_sensor_current_state(section,payload)
        elif len(topic_part)==4:
            env_var = topic_part[-1]
            self.set_env_variables(section,env_var,payload)
            self.plan_environment()
            self.send_actuator_commands()
            
        
        elif  topic_part[3] == 'past':   
            if section not in self.prev_actuator_change_status.keys():
                self.prev_actuator_change_status[section] = {}
            
            if section not in self.current_actuator_change_status.keys():
                self.current_actuator_change_status[section] = {}
                self.prev_actuator_change_status[section] = payload
        elif topic_part[3] == 'current':
                self.current_actuator_change_status[section] = payload
        
                
    
    def set_sensor_current_state(self,section,payload):
        if section not in self.current_actuator_state:
            self.current_actuator_state[section] = {"co2_injector": "OFF", 
                                                    "fan": "OFF",
                                                    "hatch": "CLOSE",
                                                    "heater": "OFF", 
                                                    "led_lights": "OFF", 
                                                    "pump": "OFF"}
            # Initialize the section if it doesn't exist
            
        self.current_actuator_state[section] = payload

        
        
                
    def set_env_variables(self,section,env_var,payload):
        
        trend = payload['trend']
        status = payload['status']
        
        self.set_variables_trend(section=section, env_var=env_var, trend=trend)
        self.set_variables_status(section=section, env_var=env_var,status=status)
        

    def set_variables_status(self, section, env_var, status):
        
        if section not in self.prev_env_var_status:
            self.prev_env_var_status[section] = {}  # Initialize the section if it doesn't exist
        if section not in self.current_env_var_status:
            self.current_env_var_status[section] = {}
            
        
        if env_var not in self.prev_env_var_status[section].keys() and env_var not in self.current_env_var_status[section].keys():
            self.prev_env_var_status[section][env_var] = None
        else:
            self.prev_env_var_status[section][env_var] = self.current_env_var_status[section][env_var]

        self.current_env_var_status[section][env_var] = status
        
    
    def set_variables_trend(self, section, env_var, trend):
     
        
        if section not in self.prev_env_var_trend:
            self.prev_env_var_trend[section] = {}  # Initialize the section if it doesn't exist
        if section not in self.current_env_var_trend:
            self.current_env_var_trend[section] = {}
            
        
        if env_var not in self.prev_env_var_trend[section].keys() and env_var not in self.current_env_var_trend[section].keys():
            self.prev_env_var_trend[section][env_var] = None
        else:
            self.prev_env_var_trend[section][env_var] = self.current_env_var_trend[section][env_var]

        self.current_env_var_trend[section][env_var] = trend
                
   
    def plan_environment(self):
        plans = Plans(self.current_env_var_status, self.current_env_var_trend, 
                    self.prev_env_var_status, self.prev_env_var_trend, 
                    self.current_actuator_state, self.current_actuator_change_status,self.actuator_command)
        plans.plan_environment()
        
        
    def send_actuator_commands(self):
        for section in self.actuator_command.keys():
            for actuator in self.actuator_command[section].keys():
                if self.actuator_command[section][actuator] is None:
                    self.actuator_command[section][actuator] = self.current_actuator_state[section][actuator]   
        for section in self.actuator_command.keys():
            topic = f"greenhouse/planner_strategy/{section}"
            payload = json.dumps(self.actuator_command[section])
            self.client_mqtt.publish(topic, payload)
            print(f"Sent command to {topic}: {payload}")

    def disconnect(self):
        self.client_mqtt.loop_stop()
        self.client_mqtt.disconnect()
        print("Disconnected from MQTT broker.")
        
if __name__ == '__main__':
    planner = Planner()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Planner...")
        planner.client_mqtt.loop_stop()
        planner.client_mqtt.disconnect()
