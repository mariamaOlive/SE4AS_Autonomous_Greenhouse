import time
from typing import List
import paho.mqtt.client as mqtt
import json
from sector import Sector



if __name__ == '__main__':
    
    # Creating MQTT client
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)
    
    # Read Section info from JSON file
    with open("sector_config.json", "r") as file:
        sector_data = json.load(file)

    # Choosing configuration to simulate
    weather_type = "Sunny"
    sectors_conf = sector_data[weather_type]["sectors"]
    exterior_conf = sector_data[weather_type]["exterior"]

    # Initilize sections array
    sectors = []
    # Load Sections
    for sector in sectors_conf:
        new_sector = Sector(sector["name"], sector["temperature"], sector["humidity"], sector["co2_levels"], sector["light_intensity"], exterior_conf)
        sectors.append(new_sector)
        
    # Run Simulation
    while True:
        for sector in sectors:
            sector.run_simulation(client_mqtt)
            
        time.sleep(10)


