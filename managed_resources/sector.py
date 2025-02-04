from paho.mqtt.client import Client
import random
# from random import randint
from actuators_simulation.fan_simulation import FanSimulation
from actuators_simulation.co2_injector_simulation import CO2InjectorSimulation
from actuators_simulation.heater_simulation import HeaterSimulation
from actuators_simulation.pump_simulation import PumpSimulation
from actuators_simulation.led_lights_simulation import LedLightSimulation
from actuators_simulation.hatch_simulation import HatchSimulation



class Sector:
    
    name = ""
    temperature = 0
    co2_levels = 0
    humidity = 0
    internal_light_intensity = 0
    sun_light_intensity = 0
    exterior = {}

    def __init__(self, name: str, temperature: float, co2_levels: int, humidity: int, exterior: dict, light_simulation):
        self.name = name
        self.light_simulation = light_simulation
        self.co2_levels = co2_levels
        self.temperature = temperature
        self.sun_light_intensity  = self.light_simulation.get_light_intensity()
        self.internal_light_intensity = self.sun_light_intensity
        self.humidity = humidity
        self.exterior = exterior
        
        ## Actuators Simulation##
        # self.fan_simulation = FanSimulation(self)
        # self.heater_simulation = HeaterSimulation(self)
        self.co2_simulation = CO2InjectorSimulation(self) 
        self.pump_simulation = PumpSimulation(self)
        self.led_simulation = LedLightSimulation(self)
        self.hatch_simulation = HatchSimulation(self)
        self.actuators = [
            # self.fan_simulation, 
                        #   self.heater_simulation,
                          self.co2_simulation, 
                          self.pump_simulation, 
                          self.led_simulation, 
                          self.hatch_simulation]

    def run_simulation(self, client: Client):
    
        trend_effect = 0.5  # Adjust sensitivity (higher = faster changes)
        
        ######### Light Adjustment #########
        self.sun_light_intensity  = self.light_simulation.get_light_intensity()
        if not (self.led_simulation.running):
            self.internal_light_intensity = self.light_simulation.get_light_intensity()
        
        ######### Temperature Adjustment #########
        normalized_intensity = self.sun_light_intensity / self.light_simulation.max_intensity
        
        # Compute external temperature based on sunlight intensity
        external_temperature = self.exterior["temperature"]["base"] + (normalized_intensity * self.exterior["temperature"]["max"] )
        # Compute internal temperature with greenhouse effect
        greenhouse_effect = 1.2  # Factor to simulate heat retention
        self.temperature = self.temperature + ((external_temperature - self.temperature) * greenhouse_effect * 0.1)
        # Add small random fluctuations
        self.temperature += random.uniform(-0.5, 0.5)
        # Round value
        self.temperature = round(self.temperature, 2)
        
        
        
        
        
        if self.exterior["temperature"]["trend"] == "up":
            self.temperature += trend_effect*random.uniform(0.1, 1.5)   # Increase temperature
        else:
            self.temperature -= trend_effect*random.uniform(0.1, 1.5)  # Decrease temperature

        # Humidity Adjustment
        if self.exterior["humidity"]["trend"] == "up":
            self.humidity += trend_effect*random.uniform(0.1, 1.5)   # Increase humidity
        else:
            self.humidity -= trend_effect*random.uniform(0.1, 1.5)   # Decrease humidity
        
        self.humidity = max(0, min(self.humidity, 100))

        # CO2 Adjustment
       
        if self.exterior["co2_levels"]["trend"] == "up":
            self.co2_levels += random.uniform(5, 15)  # Increase CO2
        else:
            self.co2_levels -= random.uniform(5, 15)  # Decrease CO2

        # Publish updated values to MQTT
        client.publish(f"greenhouse/{self.name}/temperature", self.temperature)
        client.publish(f"greenhouse/{self.name}/humidity", self.humidity)
        client.publish(f"greenhouse/{self.name}/co2_levels", self.co2_levels)
        client.publish(f"greenhouse/{self.name}/sun_light_intensity", self.sun_light_intensity)
        client.publish(f"greenhouse/{self.name}/internal_light_intensity", self.internal_light_intensity)

        # print(f"{self.name} - Temp: {self.temperature:.1f}°C, Humidity: {self.humidity:.1f}%, CO2: {self.co2_levels} ppm")