import paho.mqtt.client as mqtt
import os
import time
import json
import argparse
import numpy as np

# MQTT setup
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))

class Analyzer:
    def __init__(self, plant_thresholds_file):
        
        self.client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.client_mqtt.on_connect = self.on_connect
        self.client_mqtt.on_message = self.on_message
        self.client_mqtt.on_subscribe = self.on_subscribe
        self.plant_threshold = {}
        self.get_plant_thresholds(plant_thresholds_file)
        self.green_house_history={}
        self.daytime = False
        self.current_actuators_state ={}
        self.current_actuators_state_change = {}
        self.past_actuators_state = {}
        self.past_actuators_state_change = {}
        # Connect to the MQTT broker
        self.client_mqtt.connect(MQTT_BROKER, MQTT_PORT)
        self.client_mqtt.loop_start()
        
        
        
    def on_connect(self, client, userdata, flags, reason_code, properties):
        '''Callback function for when the client receives a CONNACK response from the server.'''
        if reason_code == 0:
            print("Connected to MQTT Broker!")
            self.client_mqtt.subscribe("greenhouse/last_updates/#")  # Subscribe to the raw sensor data topics
        else:
            print(f"Failed to connect: {reason_code}")
        
        
    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        '''Callback function for when the client receives a SUBACK response from the server.'''
        if reason_code_list[0].is_failure:
            print(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")
    
    def get_plant_thresholds(self, plant_thresholds_file):
        with open(plant_thresholds_file) as f:
            plant_thresholds = json.load(f)
            # Daytime Temperature
        
        self.plant_threshold['day_time_temp'] = {
            "temp_min": plant_thresholds['temperature']['daytime']['min'],
            "temp_max": plant_thresholds['temperature']['daytime']['max'],
            "optimal": plant_thresholds['temperature']['optimal'],
            "max_temp": plant_thresholds['temperature']['max_limit']
        }

        # Nighttime Temperature
        self.plant_threshold['night_time_temp'] = {
            "temp_min": plant_thresholds['temperature']['nighttime']['min'],
            "temp_max": plant_thresholds['temperature']['nighttime']['max'],
            "optimal": plant_thresholds['temperature']['optimal'],
            "max_temp": plant_thresholds['temperature']['max_limit']
        }

        # Humidity
        self.plant_threshold['humidity'] = {
            "min": plant_thresholds['humidity']['min'],
            "max": plant_thresholds['humidity']['max'],
            "optimal": plant_thresholds['humidity']['optimal']
        }

        # CO2
        self.plant_threshold['co2_levels'] = {
            "min": plant_thresholds['CO2']['min'],
            "max": plant_thresholds['CO2']['max'],
            "optimal": plant_thresholds['CO2']['optimal']
        }

        # Light Intensity
        self.plant_threshold['internal_light_intensity'] = {
            "min": plant_thresholds['light_intensity']['min_lux'],
            "max": plant_thresholds['light_intensity']['max_lux'],
            "optimal": plant_thresholds['light_intensity']['optimal_lux']
        }

        return 
        
    
   
    def on_message(self, client, userdata, msg):
        '''Callback function for when a PUBLISH message is received from the server.'''
        print(f"Received message on topic {msg.topic}: {msg.payload}")
        payload = msg.payload.decode("utf-8")
        payload = json.loads(payload)
        topic_part = msg.topic.split("/")
        
        
        
        if topic_part[3] == 'sensors':
            self.green_house_history[topic_part[2]] = payload
            self.get_daytime_or_nighttime(topic_part[2])
            self.analyse_env_var(topic_part[2])
        elif topic_part[3] == 'actuators':
            
            self.past_actuators_state_change[topic_part[2]] = self.analyze_actuator_state_change(section=topic_part[2])

            # assign new state
            self.past_actuators_state[topic_part[2]] = self.current_actuators_state
            self.current_actuators_state[topic_part[2]] = payload
            print(f'checking: {self.current_actuators_state[topic_part[2]] }')
            
            self.current_actuators_state_change[topic_part[2]] = self.analyze_actuator_state_change(section=topic_part[2])
            self.publish_state_change(section=topic_part[2])
        
    def get_slope(self, values):
        
        values = np.array(values, dtype=np.float64)

        # 🛠️ Step 1: Check for empty input
        if values.size < 2:
            print("Warning: Not enough data points for regression.")
            slope = 0.0

        # 🛠️ Step 2: Remove NaN and Inf values
        valid_mask = np.isfinite(values)  # Creates a mask for valid numbers
        values = values[valid_mask]

        if values.size < 2:
            print("Warning: All data points are invalid (NaN or Inf).")
            slope = 0.0
            
        x = np.arange(len(values))
        
        try:
            slope, _ = np.polyfit(x, values, 1)  # Calculate slope
            
        except np.linalg.LinAlgError as e:
            print(f"Error: {e} - Unable to compute regression.")
            slope = 0.0
        finally:
            
            return slope        
   
        
    def get_daytime_or_nighttime(self, section, daytime_threshold=5000):
        """
        Determine whether it is daytime or nighttime based on sunlight intensity.

        :param sunlight_value: The current sunlight intensity value.
        :param daytime_threshold: The threshold above which it's considered daytime.
        :return: 'Daytime' if sunlight_value > daytime_threshold, 'Nighttime' otherwise.
        """
        if 'sun_light_intensity' not in self.green_house_history[section]:
            print("Sunlight data not available yet")
            return
        sunlight_values = self.green_house_history[section]['sun_light_intensity']

        slope = self.get_slope(sunlight_values)  # Calculate linear regression

        self.daytime = slope > 0.1 and sunlight_values[-1] > daytime_threshold


    def check_temperature(self, section):
        """
        Check if the temperature is within the optimal range.

        :param temperature: The current temperature value.
        :return: 'High' if temperature > optimal, 'Low' if temperature < optimal, 'Optimal' otherwise.
        """
        temperature_values = self.green_house_history[section]['temperature']
        slope = self.get_slope(temperature_values)
        last_temperature = temperature_values[-1]

        if slope > 0:
            temperature_state = 'Increasing'
        elif slope < 0:
            temperature_state = 'Decreasing' 
        else:
            temperature_state = 'Stable'

        if self.daytime:
            temp_threshold = self.plant_threshold['day_time_temp']
        else:
            temp_threshold = self.plant_threshold['night_time_temp']
            
        print(f'checking last_temperature: {last_temperature}')
        
        if last_temperature < temp_threshold['temp_min'] : # less than 15 or 17
             temperature_status = 'too_low'
        elif last_temperature > temp_threshold['temp_min'] and last_temperature < temp_threshold['optimal']-1: # between 15- 19 or 17 -19
            temperature_status = 'low'
        elif last_temperature >= temp_threshold['optimal']-1 and last_temperature <= temp_threshold['optimal']+2: #between 19 -22 or 19-22
            temperature_status = 'optimal'
        elif last_temperature > temp_threshold['optimal']+2 and last_temperature <= temp_threshold['max_temp']-2: # between 23 and 27
            temperature_status = 'high'
        elif last_temperature > temp_threshold['max_temp']-2: # greater than 28
            temperature_status = 'too_high'
        print(f'checking temperature_status: {temperature_status}')
        print(f'checking temperature_state: {temperature_state}')
        return temperature_state, temperature_status
    
    def check_env_var(self, section, env_var):
        '''Check the state and status of the environment variable'''
        if env_var == 'temperature':
            return self.check_temperature(section)
        elif env_var in self.plant_threshold.keys():
            return self.get_state_and_status(section, env_var)
        else:
            print(f'threshold not defined for this variable{env_var}')
            return None, None

   
    def get_state_and_status(self, section, env_var):
        values = self.green_house_history[section][env_var]
        slope = self.get_slope(values)
        state = self.get_env_state(slope)
        thresholds = self.plant_threshold[env_var]
        status = self.get_status(values[-1], thresholds)
        return  state, status
    
    def get_status(self, last_value, thresholds):
        '''Get the status of the environment variable'''
        if last_value < thresholds['min']:
            return 'too_low'
        elif last_value < thresholds['optimal'] - int(thresholds['optimal'] - thresholds['min'])/3:
            return 'low'
        elif last_value <= thresholds['optimal'] + int(thresholds['max'] - thresholds['optimal'])/3:
            return 'optimal'
        elif last_value <= thresholds['max']:
            return 'high'
        else:
            return 'too_high'
    
    def get_env_state(self,slope):
        '''Get the state of the environment variable'''
        if slope > 0.2:
            return 'Increasing'
        elif slope < -0.2:
            return 'Decreasing' 
        else:
            return 'Stable'
    
    
    def analyse_env_var(self,section):
        '''Analyse the environment variables'''
        section_data = self.green_house_history[section]
        for env_var in section_data.keys():
            if env_var != 'sun_light_intensity':
                state, status = self.check_env_var(section, env_var)
                self.publish_anlysis(section, env_var, {'trend': state, 'status': status})
                
                
    def publish_anlysis(self, section, env_variable, value_data):
        '''Write the data to the knowledge base (publish to MQTT)'''

        # Loop through the data for each section
            # Create the base topic for measurements and trends
        topic = f"greenhouse/analyzer/{section}/{env_variable}"
        # Publish the value data to the topic
        self.client_mqtt.publish(topic, json.dumps(value_data))
        print(f"Published value data to {topic}: {value_data}")
        
        
    def analyze_actuator_state_change(self, section):
        ''' Validate if the status of the actuators change from the previous message.'''
        state_change = {
            _:False for _ in ['co2_levels', 'fan', 'heater', 'led_lights', 'pump']
        }
        if section in self.past_actuators_state.keys():

            actuators = list(set(list(self.past_actuators_state[section].keys()) + list(self.current_actuators_state[section].keys())))
            for actuator in actuators:
                if actuator in self.past_actuators_state[section].keys()  and actuator in self.current_actuators_state[section].keys():
                    state_change[actuator] = self.past_actuators_state[section][actuator] != self.current_actuators_state[section][actuator]
                elif actuator in self.past_actuators_state[section].keys() or actuator in self.current_actuators_state[section].keys():
                    state_change[actuator] =False
        return state_change
        
    def publish_state_change(self,section):
        past_state_topic =   f"greenhouse/analyzer/{section}/past/change_status"
        current_state_topic =   f"greenhouse/analyzer/{section}/current/change_status"
        
        self.client_mqtt.publish(past_state_topic, json.dumps(self.past_actuators_state_change))
        print(f"Published past actuators state change  data to {past_state_topic}: {self.past_actuators_state_change}")
        
        self.client_mqtt.publish(current_state_topic, json.dumps(self.current_actuators_state_change))
        print(f"Published current actuators state change  data to {current_state_topic}: {self.current_actuators_state_change}")
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Greenhouse Analyzer")
    
    # Adding argument for the threshold file
    parser.add_argument('--file_threshold', '-f', type=str, default='greenhouse_threshold.json', 
                        help='The file containing the thresholds for the plants in the greenhouse')

    # Parse the arguments
    args = parser.parse_args()
    analyzer = Analyzer(args.file_threshold)
    while True:
        time.sleep(1)
               