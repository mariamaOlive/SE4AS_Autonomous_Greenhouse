from paho.mqtt.client import Client
import random
# from random import randint
from actuators_simulation.fan_simulation import FanSimulation



class Sector:
    
    name = ""
    temperature = 0
    co2_levels = 0
    humidity = 0
    light_intensity = 0
    exterior = {}

    def __init__(self, name: str, temperature: float, co2_levels: int, humidity: int, light_intensity: int, exterior: dict):
        self.name = name
        self.co2_levels = co2_levels
        self.temperature = temperature
        self.light_intensity = light_intensity
        self.humidity = humidity
        self.exterior = exterior
        self.actuators = [FanSimulation(self)]

    def run_simulation(self, client: Client):
        print("Runnning simulation")
        rand = random.randint(0, 9)
        # if rand == 0:

        print(f"Publishing values of sector {self.name}")
        self.temperature += random.randint(-1, 10)
        # Fix extreme values
        client.publish(f"greenhouse/{self.name}/temperature", self.temperature)
        