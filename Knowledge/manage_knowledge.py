import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.query_api import QueryApi
import paho.mqtt.client as mqtt
import os
import time
import json
import threading


class Knowledge:
    

    def __init__(self):
        """Initializes the Knowledge class.

        This sets up connections to InfluxDB and MQTT, and starts a thread to
        periodically publish the latest sensor and actuator data to MQTT.
        """
        try:
            self.bucket = os.getenv("INFLUXDB_BUCKET", "greenhouse")
            self.org = os.getenv("INFLUXDB_ORG", "univaq")
            self.token = os.getenv("INFLUXDB_TOKEN")
            self.url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
            self.mqtt_broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
            self.mqtt_broker_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
        except KeyError as e:
            raise RuntimeError(f"Missing required environment variable: {e}") from e

        # Initialize InfluxDB client
        self.influx_client = influxdb_client.InfluxDBClient(
            url=self.url, token=self.token, org=self.org
        )
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.influx_client.query_api()

        # Initialize MQTT client
        self.mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True
        )
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_subscribe = self.on_subscribe
        
        self.mqtt_client.connect(self.mqtt_broker_host, self.mqtt_broker_port)
        self.mqtt_client.loop_start()


    def on_connect(self, client, userdata, flags, reason_code, properties):
        """Callback function for when the client receives a CONNACK response from the server."""
        if reason_code == 0:
            print("Connected to MQTT Broker!")
            self.mqtt_client.subscribe(
                "greenhouse/monitor/#"
            )  # Subscribe to the raw sensor data topics
            self.mqtt_client.subscribe(
                "greenhouse/actuator_status/#"
            )  # Subscribe to the actuator status topics
        else:
            print(f"Failed to connect: {reason_code}")

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        """Callback function for when the client receives a SUBACK response from the server."""
        if reason_code_list[0].is_failure:
            print(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_message(self, client, userdata, msg):
        """Callback function for when a PUBLISH message is received from the server."""
        payload = msg.payload.decode("utf-8")
        print(f"Received message on topic: {msg.topic} with payload: {payload}")

        topic_part = msg.topic.split("/")
        if topic_part[1] == "monitor": # e.g greenhouse/monitor/West Section/temperature/
            self.writeDB(topic_part, float(payload))
        elif topic_part[1] == "actuator_status": # e.g greenhouse/actuator_status/West Section/fan
            self.writeDB(topic_part, str(payload))

        
        return None

    def writeDB(self, topic_part, value):
        """Writes the sensor data to InfluxDB."""

        if topic_part[1] == "monitor":  # Updated to handle actuator status
            data_point = (
                influxdb_client.Point("sensor_data")
                .tag("section", topic_part[2])
                .field(topic_part[3], value)
                .time(int(time.time()), "s")
            )
        elif topic_part[1] == "actuator_status":  # Updated to handle actuator status
            
            data_point = influxdb_client.Point("actuator_state").tag("section", topic_part[2]).field(topic_part[3], value).time(
                int(time.time()), "s")
    
        try:
            self.write_api.write(bucket=self.bucket, org=self.org, record=data_point)
            print("Writing in InfluxDB successfully completed!")
        except Exception as e:
            print(f"Error when writing to InfluxDB: {e}")
            
                
    def get_last_update(self):
        """Query to get the last 5 values for both sensor data and actuator data"""
        query = f"""
                from(bucket: "{self.bucket}")
                    |> range(start: -5m)  
                    |> filter(fn: (r) => r["_measurement"] == "sensor_data" )
                    |> group(columns: ["_measurement", "_field", "section"])  
                    |> tail(n: 3) 
            """


        try:
            if result := self.query_api.query(query, org=self.org):
                last_values = {}

                # Iterate through the results
                for table in result:
                    for record in table.records:
                        # Extract relevant data from the record
                        measurement = record.get_measurement()  # This will be either 'sensor_data' or 'actuator_data'
                        field = record.get_field()  # Field name (e.g., temperature, humidity)
                        section = record.values.get("section")  # Section (e.g., North Section, South Section)
                        value = record.get_value()  # The value for this field at this point in time
                        
                        # Initialize the dictionary for the section and field if not already present
                        if section not in last_values:
                            last_values[section] = {}
                            
                        if field not in last_values[section]:
                            last_values[section][field] = []

                        # Append the new value (sensor data) to the array for this field
                        last_values[section][field].append(value)
                    

                # Return the data structure containing the last 5 values for each sensor field and actuator field
                return last_values
            
            else:
                print("No data found for fields and sections.")
                return None

        except Exception as e:
            print(f"Error when retrieving last update: {e}")
            return None



    def publish_latest_values(self):
        """Publishes the latest sensor and actuator data to MQTT every 20 seconds."""

        # Get the latest updates for all fields and sections
        while True:
            last_updates = self.get_last_update()
            actuator_state =self.get_actuator_state()

            if last_updates is None:
                print("No last updates found.")
                return
            if actuator_state is None:
                print('Last actuators state are unknown at the moment')

            # Now, publish each last update for all fields and sections
            try:
                for section, field_values in actuator_state.items():
                    # Construct the MQTT topic for the section
                    topic = f"greenhouse/last_updates/{section}/actuators"

                    # Create the payload to include all fields and their latest values
                    payload = {
                        field: value for field, value in field_values.items()
                    }

                    # Publish the aggregated data (last updates) to the MQTT topic
                    self.mqtt_client.publish(topic, payload=json.dumps(payload))
                    print(f"Published last updates for {section} to {topic}: {payload}")
            except ValueError as e:
                print(f"Error when publishing last actuator state: {e}")
            except Exception as e:
                print(f"Error when publishing last actuator state: {e}")
                
           
           
            try:        
                for section, field_values in last_updates.items():
                    # Construct the MQTT topic for the section
                    topic = f"greenhouse/last_updates/{section}/sensors"

                    # Create the payload to include all fields and their latest values
                    payload = {
                        field: value for field, value in field_values.items()
                    }

                    # Publish the aggregated data (last updates) to the MQTT topic
                    self.mqtt_client.publish(topic, payload=json.dumps(payload))
                    print(f"Published last updates for {section} to {topic}: {payload}")
            except ValueError as e:
                print(f"Error when publishing last updates: {e}")  
            except Exception as e:
                print(f"Error when publishing last updates: {e}")

            # Sleep for 20 seconds before fetching and publishing again
            time.sleep(5)
            
    def get_actuator_state(self):
        """Query to get the last actuator state for a given section and actuator, including the time"""
        query = f"""
                from(bucket: "{self.bucket}")
                    |> range(start: -5m)  
                    |> filter(fn: (r) => r["_measurement"] == "actuator_state")    
                    |> sort(columns: ["_time"], desc: true) 
                    |> group(columns: ["_measurement", "_field", "section"])  
                    |> first()  
            """
        actuator_states={}
        try:
            if result := self.query_api.query(query, org=self.org):
                for table in result:
                    for record in table.records:
                        # Extract the time and value from the record
                        actuator_value = record.get_value()
                        actuator_time = record.get_time()
                        actuator_section = record.values.get("section")
                        field = record.get_field()
                        
                        if actuator_section not in actuator_states:
                            actuator_states[actuator_section]= {}
                            
                        actuator_states[actuator_section][field]=actuator_value
                            
                        

                return actuator_states
            else:
                print("No data found for the given section and actuator.")
                return None

        except Exception as e:
            print(f"Error when retrieving actuator state: {e}")
            return None




if __name__ == "__main__":
    knowledge = Knowledge()
    pooling_timer = time.time()

    while True:
        if time.time() - pooling_timer >= 5:
            knowledge.publish_latest_values()    
        time.sleep(1)
        