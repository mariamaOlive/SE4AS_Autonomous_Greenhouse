import time
import os
from typing import List
import paho.mqtt.client as mqtt
import json
from sector import Sector
from light_simulation import LightSimulation



if __name__ == '__main__':
    MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT"))
    
    # Creating MQTT client
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect(MQTT_BROKER, MQTT_PORT,60)
    
    # Read Section info from JSON file
    with open("sector_config.json", "r") as file:
        sector_data = json.load(file)

    # Choosing configuration to simulate
    weather_type = "Sunny"
    sectors_conf = sector_data[weather_type]["sectors"]
    exterior_conf = sector_data[weather_type]["exterior"]
    
    light_simulation = LightSimulation(sector_data[weather_type]["exterior"]["light_intensity"]["value"])

    # Initilize sections array
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


