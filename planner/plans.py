from temperature import   Temperature
from humidity import Humidity

class Plans:
    SENSOR_ACTUATOR_MAPPING = {'co2_levels':'co2_injector', 'humidity':['pump'], 'internal_light_intensity': 'led_lights', 'temperature':['fan', 'hatch','heater']}
    def __init__(self,current_status,current_trend,past_status,past_trend, 
                 current_actuator_state, actuator_changed_status,commands):
        self.current_status = current_status
        self.current_trend = current_trend
        self.past_status = past_status
        self.past_trend = past_trend
        self.current_actuator_state = current_actuator_state
        self.actuator_changed_status = actuator_changed_status
        self.commands = commands
        

    
    def plan_single_effect(self, section, env_var):
        """Plan actions for a single environmental variable."""
        
        actuator = self.SENSOR_ACTUATOR_MAPPING[env_var]
       
        # sourcery skip: low-code-quality
        if section not in self.commands:
            self.commands[section] = {}
        
        current_status = self.current_status.get(section, {}).get(env_var, 'None')
        if current_status is None:
            current_status = 'optimal'
            
        if actuator not in self.commands[section]:
            self.commands[section][actuator] = None

        if section not in self.actuator_changed_status:
            self.actuator_changed_status[section] = {}
        if actuator not in self.actuator_changed_status[section]:
            self.actuator_changed_status[section][actuator] = False 


        actuator_changed_status = self.actuator_changed_status[section][actuator]  
        
        if env_var == 'internal_light_intensity':
            print('inside analyzer function internal_light_intensity', current_status, 'for section', section)
            
            if current_status in ['too_high' , 'high']:
                self.commands[section][actuator] = 'OFF'
                print('sent command OFF for section ', section)
            elif  current_status in [ 'low', 'too_low', 'optimal']:
                self.commands[section][actuator] = 'ON'
                print('sent command ON for section ', section)
            
        elif env_var == 'co2_levels':
            if actuator_changed_status:
                current_trend = self.current_trend[section][env_var]
                past_trend = self.past_trend[section][env_var]
                if current_trend == 'Stable':
                    if current_status == 'high' or current_status == 'too_high':
                        self.commands[section][actuator] = 'OFF'
                    elif current_status == 'low' or current_status == 'too_low':
                        self.commands[section][actuator] = 'ON'
                elif current_trend == 'Increasing' and past_trend == 'Increasing':
                    if current_status == 'high' or current_status == 'too_high':
                        self.commands[section][actuator] = 'OFF'
                    if current_status == 'low' or current_status == 'too_low':
                        self.commands[section][actuator] = 'ON'
                elif current_trend == 'Decreasing' and past_trend == 'Decreasing':
                    if current_status == 'high' or current_status == 'too_high':
                        self.commands[section][actuator] = 'OFF' 
                    elif current_status == 'low' or current_status == 'too_low':
                        self.commands[section][actuator] = 'ON'
                elif current_trend == 'Increasing' and past_trend == 'Decreasing':
                    if current_status != 'optimal':
                        if current_status == 'high' or current_status == 'too_high':

                            self.commands[section][actuator] = 'OFF'
                        elif current_status == 'low' or current_status == 'too_low':
                            self.commands[section][actuator] = 'ON'
                elif current_trend == 'Decreasing' and past_trend == 'Increasing':
                    if current_status != 'optimal':
                        if current_status == 'too_high':
                            self.commands[section][actuator] = 'OFF' 
                        elif current_status in ['low', 'too_low', 'high']:
                            self.commands[section][actuator] = 'ON'
            elif current_status == 'high' or current_status == 'too_high':
                self.commands[section][actuator] = 'OFF'
            elif current_status == 'low' or current_status == 'too_low':
                self.commands[section][actuator] = 'ON'
            elif 'optimal' == current_status:
                self.commands[section][actuator] = 'OFF'
                
       
    def plan_temperature(self, section):
        """Plan temperature actions for a given section using Temperature class."""
        # Retrieve current and past temperature data for the section
        for actuator in self.SENSOR_ACTUATOR_MAPPING['temperature']:
            if actuator not in self.commands[section]:
                self.commands[section][actuator] = None
        
        
        current_status = self.current_status[section]['temperature'] 
        current_trend = self.current_trend[section]['temperature']
        past_trend = self.past_trend[section]['temperature']  # Accessing the past trend
        actuator_mapping = self.SENSOR_ACTUATOR_MAPPING['temperature']
        
        for actuator in actuator_mapping:
            if actuator not in self.current_actuator_state[section]:
                self.current_actuator_state[section][actuator] = 'OFF'
        
        actuator_state = [self.current_actuator_state[section][x] for x in self.SENSOR_ACTUATOR_MAPPING['temperature']] 
        
        # Instantiate Temperature class with the past_trend included
        temperature = Temperature(section, current_status, current_trend, past_trend, actuator_state, actuator_mapping, self.commands)

        # Call the plan_temperature method from Temperature class
        temperature.plan_temperature()
        print(f"commands after planning temperature for section {section} is {self.commands[section]['fan']} for fan,  {self.commands[section]['hatch']} for hatch, and {self.commands[section]['heater']} for heater")
        

        # At this point, the `commands` dictionary has been updated by the Temperature class
           
                    
    def plan_humidity(self, section):
        """Plan humidity actions for a given section using Humidity class."""
        # Retrieve current and past humidity data for the section
        for actuator in self.SENSOR_ACTUATOR_MAPPING['humidity']:
            if actuator not in self.commands[section]:
                self.commands[section][actuator] = None

        current_status = self.current_status[section]['humidity']
        current_trend = self.current_trend[section]['humidity']
        past_trend = self.past_trend[section]['humidity']  # Accessing the past trend
        actuator_mapping = self.SENSOR_ACTUATOR_MAPPING['humidity'] 
        for actuator in actuator_mapping:
            if actuator not in self.current_actuator_state[section]:
                self.current_actuator_state[section][actuator] = 'OFF'
        
        actuator_state = [self.current_actuator_state[section][x] for x in self.SENSOR_ACTUATOR_MAPPING['humidity']]
        actuator_state = dict(zip(actuator_mapping, actuator_state))

        # Instantiate Humidity class with the past_trend included
        humidity = Humidity(section, current_status, current_trend, past_trend, actuator_state, actuator_mapping, self.commands)

        # Call the plan_humidity method from Humidity class
        humidity.plan_humidity()

        
    def plan_environment(self):
        """Plan environment actions based on status and trend."""
        for section in self.current_status.keys():
            if section not in self.commands:
                self.commands[section] = {}
                
            self.plan_temperature(section)
            self.plan_humidity(section)
            self.plan_single_effect(section, 'co2_levels')
            self.plan_single_effect(section, 'internal_light_intensity')
            
        