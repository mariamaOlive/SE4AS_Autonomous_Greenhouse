import paho.mqtt.client as mqtt
import os
import time
import json
import threading
import math
import numpy as np

# MQTT setup
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))

# Define how often we want to fetch data from the raw topic (in seconds)
WRITE_INTERVAL = int(os.getenv("WRITE_INTERVAL", 10))  # default to 10 seconds

class Monitor:
    def __init__(self):
        self.cache = {}  # Cache to store the last n values of each sensor until it is published to the knowledge base
        self.data = {}
        self.client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        self.client_mqtt.on_connect = self.on_connect
        self.client_mqtt.on_message = self.on_message
        self.client_mqtt.on_subscribe = self.on_subscribe

        # Connect to the MQTT broker
        self.client_mqtt.connect(MQTT_BROKER, MQTT_PORT)
        self.agg_timestart = time.time()

        # Start the MQTT loop in the background using loop_start()
        self.client_mqtt.loop_start()  # Non-blocking loop to process incoming messages


    def on_connect(self, client, userdata, flags, reason_code, properties):
        '''Callback function for when the client receives a CONNACK response from the server.'''
        if reason_code == 0:
            print("Connected to MQTT Broker!")
            self.client_mqtt.subscribe("greenhouse/sensor_raw/#")  # Subscribe to the raw sensor data topics
        else:
            print(f"Failed to connect: {reason_code}")

    def on_message(self, client, userdata, msg):
        '''Callback function for when a PUBLISH message is received from the server.'''
        payload = msg.payload.decode("utf-8")
        topic_part = msg.topic.split("/")
        key = f'{topic_part[-2]}_{topic_part[-1]}'  # e.g. section1_temperature
        self.update_cache(key, float(payload))  # Update the cache with the latest value of the sensor data

        # Check if it's time to aggregate and write to the knowledge base
        time_difference = time.time() - self.agg_timestart
        if time_difference >= WRITE_INTERVAL:
            self.agg_timestart = time.time()
            self.generate_db_entry()  # Generate the database entry to be published to the knowledge base
            self.write_to_knowledge_base()  # Write the data to the knowledge base
            self.cache = {}  # Reset the cache after publishing

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        '''Callback function for when the client receives a SUBACK response from the server.'''
        if reason_code_list[0].is_failure:
            print(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def update_cache(self, key, value):
        '''Update the cache with the latest value of the sensor data'''
        if key not in self.cache:
            self.cache[key] = [value]  # Start with the first value in the list
        else:
            self.cache[key].append(value)

    def generate_db_entry(self):
        '''Generate the database entry to be published to the knowledge base'''
        data = {}
        for key in self.cache.keys():
            # Create a dictionary for each section (e.g., North Section, South Section)
            section = key.split("_")[0]  # Get the section name (e.g., North, South)
            resource = key.split("_")[1]  # Get the resource name (e.g., temperature, humidity)

            # Calculate the average value for the resource
            value = round(sum(self.cache[key]) / len(self.cache[key]), 2)
            # Generate the trend for the resource
            trend = self.generate_trend(self.cache[key])

            # Initialize section if it doesn't exist
            if section not in data:
                data[section] = {}

            # Store the resource value and trend in the section
            data[section][resource] = value
            data[section][f'{resource}_trend'] = trend

        # Store the final data
        self.data = data


    def generate_trend(self, sensor_values):
        """Generate trend based on linear regression"""
        if len(sensor_values) < 2:  # Need at least two points for linear regression
            return "STABLE"

        x = np.arange(len(sensor_values))
        slope, _ = np.polyfit(x, sensor_values, 1)  # Calculate linear regression

        if slope > 0.15: # Define threshold for increasing trend
            return "INCREASING"
        elif slope < -0.15: # Define threshold for decreasing trend
            return "DECREASING"
        else:
            return "STABLE"

        
    def write_to_knowledge_base(self):
        '''Write the data to the knowledge base (publish to MQTT)'''

        # Loop through the data for each section
        for section, section_data in self.data.items():
            # Create the base topic for measurements and trends
            value_topic = f"greenhouse/monitor/{section}/measurement/"
            state_topic = f"greenhouse/monitor/{section}/state/"

            # Initialize dictionaries to hold the data for each section
            value_data = {}
            state_data = {}

            # Loop through each field (e.g., temperature, humidity, etc.) in the section data
            for field, value in section_data.items():
                #field_name = field.split("_")[1]  # Get the field name (e.g., temperature, humidity, etc.)
                
                # Check if the field is a trend or a value
                if "_trend" in field:
                    # For trends, assign to the state topic
                    field_name = field.replace("_trend", "")
                    state_data[field_name] = value
                else:
                    # For values, assign to the measurement topic
                    value_data[field] = value

            # Publish the sensor values to the measurement topic
            self.client_mqtt.publish(value_topic, json.dumps(value_data))
            print(f"Published value data to {value_topic}: {value_data}")

            # Publish the trends (states) to the state topic
            self.client_mqtt.publish(state_topic, json.dumps(state_data))
            print(f"Published state data to {state_topic}: {state_data}")


if __name__ == '__main__':
    monitor = Monitor()

    # Keep the main thread alive so the background MQTT loop continues running
    while True:
        time.sleep(1)  # Main thread does nothing but prevents the program from exiting
