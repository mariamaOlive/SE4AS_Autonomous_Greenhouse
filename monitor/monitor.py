import paho.mqtt.client as mqtt
import os
import time
import json

# MQTT setup
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))

# Monitor class
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
            self.client_mqtt.subscribe("greenhouse/actuator_status/#")  # Subscribe to the sensor status topics
        else:
            print(f"Failed to connect: {reason_code}")

    def on_message(self, client, userdata, msg):
        '''Callback function for when a PUBLISH message is received from the server.'''
        payload = msg.payload.decode("utf-8")
        topic_parts = msg.topic.split("/")
        topic_type = topic_parts[1]
        sector = topic_parts[2]
        sensor = topic_parts[3]
        
        #Veriy which topic arrived 
        value = payload if topic_type == "actuator_status" else float(payload)
   
        # Write the data to the knowledge base  
        self.write_to_knowledge_base(topic_type, sector, sensor, value_data=value)  


    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        '''Callback function for when the client receives a SUBACK response from the server.'''
        if reason_code_list[0].is_failure:
            print(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")


    def write_to_knowledge_base(self, topic_type, sector, sensor, value_data):
        '''Write the data to the knowledge base (publish to MQTT)'''
        # Construct the topic to publish the value data to
        topic = f"greenhouse/monitor/{topic_type}/{sector}/{sensor}"
        # Publish the value data to the topic
        self.client_mqtt.publish(topic, json.dumps(value_data))
        print(f"Published value data to {topic}: {value_data}")

            

if __name__ == '__main__':
    monitor = Monitor()

    # Keep the main thread alive so the background MQTT loop continues running
    while True:
        time.sleep(1)  # Main thread does nothing but prevents the program from exiting
