from paho.mqtt.client import Client
import random
# from random import randint
from actuators_simulation.fan_simulation import FanSimulation
from actuators_simulation.co2_injector_simulation import CO2InjectorSimulation
from actuators_simulation.heater_simulation import HeaterSimulation
from actuators_simulation.pump_simulation import PumpSimulation
from actuators_simulation.led_lights_simulation import LedLightSimulation



class Sector:
    
    name = ""
    temperature = 0
    co2_levels = 0
    humidity = 0
    light_intensity = 0
    exterior = {}

    def __init__(self, name: str, temperature: float, co2_levels: int, humidity: int, light_intensity: int, exterior: dict, light_simulation):
        self.name = name
        self.light_simulation = light_simulation
        self.co2_levels = co2_levels
        self.temperature = temperature
        self.light_intensity = self.light_simulation.get_light_intensity()
        self.humidity = humidity
        self.exterior = exterior
        # self.actuators = [FanSimulation(self), CO2InjectorSimulation(self)]
        self.actuators = [HeaterSimulation(self), CO2InjectorSimulation(self), PumpSimulation(self), LedLightSimulation(self)]

    def run_simulation(self, client: Client):
    
        trend_effect = 0.5  # Adjust sensitivity (higher = faster changes)
        
        # Light Adjustment
        self.light_intensity = self.light_simulation.get_light_intensity()
        
        # Temperature Adjustment
        if self.exterior["temperature"]["trend"] == "up":
            self.temperature += trend_effect*random.uniform(0.1, 1.5)   # Increase temperature
        else:
            self.temperature -= trend_effect*random.uniform(0.1, 1.5)  # Decrease temperature

        # Humidity Adjustment
        if self.exterior["humidity"]["trend"] == "up":
            self.humidity += trend_effect*random.uniform(0.1, 1.5)   # Increase humidity
        else:
            self.humidity -= trend_effect*random.uniform(0.1, 1.5)   # Decrease humidity

        # CO2 Adjustment
        if self.exterior["co2_levels"]["trend"] == "up":
            self.co2_levels += trend_effect*random.uniform(0.1, 1.5)  # Increase CO2
        else:
            self.co2_levels -= trend_effect*random.uniform(0.1, 1.5)  # Decrease CO2

        # Publish updated values to MQTT
        client.publish(f"greenhouse/{self.name}/temperature", self.temperature)
        client.publish(f"greenhouse/{self.name}/humidity", self.humidity)
        client.publish(f"greenhouse/{self.name}/co2_levels", self.co2_levels)
        client.publish(f"greenhouse/{self.name}/light_intensity", self.light_intensity)

        # print(f"{self.name} - Temp: {self.temperature:.1f}°C, Humidity: {self.humidity:.1f}%, CO2: {self.co2_levels} ppm")