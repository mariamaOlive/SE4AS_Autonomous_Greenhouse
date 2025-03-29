import time
import os
from typing import List
import paho.mqtt.client as mqtt
import json
from sector import Sector
from light_simulation import LightSimulation
import configparser

# Load configuration file
configparser = configparser.ConfigParser()

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

configparser.read(os.path.join(BASE_FOLDER,'/shared_files/config.ini'))

DEFAULT_MQTT_BROKER = configparser.get('DEFAULTS','default_mqtt_broker_host')
DEFAULT_MQTT_PORT = configparser.get('DEFAULTS','default_mqtt_broker_port')

SIMULATION_WEATHER_TYPE = configparser.get('SIMULATION','weather_type')



if __name__ == '__main__':
    #MQTT setup
    MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", DEFAULT_MQTT_BROKER)
    MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", DEFAULT_MQTT_PORT))
    
    # Creating MQTT client
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect(MQTT_BROKER, MQTT_PORT,60)
    
    # Read Section info from JSON file
    with open(os.path.join(BASE_FOLDER,"/shared_files/sector_config.json"), "r") as file:
        sector_data = json.load(file)

    # Choosing configuration to simulate
    sectors_conf = sector_data[SIMULATION_WEATHER_TYPE]["sectors"]
    exterior_conf = sector_data[SIMULATION_WEATHER_TYPE]["exterior"]
    
    light_simulation = LightSimulation(sector_data[SIMULATION_WEATHER_TYPE]["exterior"]["light_intensity"]["value"])

    # Initialize sections array
    sectors = []
    # Load Sections
    for sector in sectors_conf:
        new_sector = Sector(sector["name"], sector["temperature"], sector["co2_levels"], sector["humidity"], exterior_conf, light_simulation,shading_factor=0.5)
        sectors.append(new_sector)
        
    # Run Simulation
    while True:
        for sector in sectors:
            sector.run_simulation(client_mqtt)
            
        time.sleep(5)


