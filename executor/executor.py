import paho.mqtt.client as mqtt
import time
import json
import random
import os


def execute(client, sector):
    execution_plan = {}
    
    # fan - : on/off
    # heater - : on/off
    # Hatches  - : open/close
    # pumps  - : on/off
    # led_lights  - : on/off
    # co2_injectors: on/of
    message_key = f"execute/{sector}" 

    command_fan = random.choice(["ON", "OFF"])
    command_co2_injector = random.choice(["ON", "OFF"])
    command_heater= random.choice(["ON", "OFF"])
    command_pump= random.choice(["ON", "OFF"])
    command_lights= random.choice(["ON", "OFF"])
    command_hatch= random.choice(["OPEN", "CLOSE"])
    
    execution_plan["fan"] = command_fan
    execution_plan["co2_injector"] = command_co2_injector
    execution_plan["heater"] = command_heater
    execution_plan["pump"] = command_pump
    execution_plan["led_lights"] = command_lights
    execution_plan["hatch"] = command_hatch
    
    print(f"Publishing to {message_key}: {execution_plan}")
    client.publish(message_key, json.dumps(execution_plan))


if __name__ == '__main__':
    MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT"))
    # Message broker connection
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)
    
    
    #REMOVE: Here for testing pur
    with open("sector_config.json", "r") as file:
        sector_data = json.load(file)
    weather_type = "Sunny"
    sectors_conf = sector_data[weather_type]["sectors"]
    exterior_conf = sector_data[weather_type]["exterior"]


    while True:
        for sector in sectors_conf:
            execute(client_mqtt, sector["name"])
        time.sleep(60)