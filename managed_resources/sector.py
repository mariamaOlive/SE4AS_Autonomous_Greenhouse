from paho.mqtt.client import Client
# import random
# from random import randint
from actuators_simulation.fan_simulation import FanSimulation



class Sector:
    
    name = ""
    temperature = 0
    co2_levels = 0
    humidity = 0
    light_intensity = 0

    def __init__(self, name: str, temperature: float, co2_levels: int, humidity: int, light_intensity: int, exterior: dict):
        self.name = name
        self.co2_levels = co2_levels
        self.temperature = temperature
        self.light_intensity = light_intensity
        self.humidity = humidity
        self.actuators = [FanSimulation(self)]

    def run_simulation(self, client: Client):
        pass