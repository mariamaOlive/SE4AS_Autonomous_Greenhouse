from temperature import   Temperature
from humidity import Humidity

class Plans:
    SENSOR_ACTUATOR_MAPPING = {'co2_levels':'co2_levels', 'humidity':['heater', 'pump'], 'internal_light_intensity': 'led_lights', 'temperature':['fan', 'hatch','heater']}
    def __init__(self,current_status,current_trend,past_status,_past_trend, 
                 current_actuator_state, actuator_changed_status,commands):
        self.current_status = current_status
        self.current_trend = current_trend
        self.past_status = past_status
        self._past_trend = _past_trend
        self.current_actuator_state = current_actuator_state
        self.actuator_changed_status = actuator_changed_status
        self.commands = commands
        
    def set_actuator_changed_status(self, actuator_changed_status):
        self.actuator_changed_status = actuator_changed_status
    
    def get_actuator_changed_status(self):
        return self.actuator_changed_status
   
    def set_current_status(self, current_status):
        self.current_status = current_status

    def get_current_status(self):
        return self.current_status

    def set_current_trend(self, current_trend):
        self.current_trend = current_trend

    def get_current_trend(self):
        return self.current_trend

    def set_past_status(self, past_status):
        self.past_status = past_status

    def get_past_status(self):
        return self.past_status

    def set_past_trend(self, past_trend):
        self._past_trend = past_trend

    def get_past_trend(self):
        return self._past_trend

    def set_current_actuator_state(self, current_actuator_state):
        self.current_actuator_state = current_actuator_state

    def get_current_actuator_state(self):
        return self.current_actuator_state

    def set_all(self, current_status, current_trend, past_status, past_trend, current_actuator_state, actuator_changed_status):
        self.current_status = current_status
        self.current_trend = current_trend
        self.past_status = past_status
        self._past_trend = past_trend
        self.current_actuator_state = current_actuator_state
        self.actuator_changed_status = actuator_changed_status

    def get_all(self):
        return {
            "current_status": self.current_status,
            "current_trend": self.current_trend,
            "past_status": self.past_status,
            "past_trend": self._past_trend,
            "current_actuator_state": self.current_actuator_state,
            "actuator_changed_status": self.actuator_changed_status
        }
    
    def plan_single_effect(self, section, env_var):
        """Plan actions for a single environmental variable."""
        
        actuator = self.SENSOR_ACTUATOR_MAPPING[env_var]
        # sourcery skip: low-code-quality
        if section not in self.commands:
            self.commands[section] = {}
        current_actuator_state = self.current_actuator_state[section][actuator]
        current_status = self.current_status.get(section, {}).get('temperature', 'optimal')
        if current_status is None:
            current_status = 'optimal'
        past_status = self.past_status[section][env_var]


        if section not in self.actuator_changed_status:
            self.actuator_changed_status[section] = {}
        if actuator not in self.actuator_changed_status[section]:
            self.actuator_changed_status[section][actuator] = False 


        actuator_changed_status = self.actuator_changed_status[section][actuator]    

        if actuator_changed_status:
            current_trend = self.current_trend[section][env_var]
            past_trend = self._past_trend[section][env_var]
            if current_trend == 'Stable':
                if 'high' in current_status:
                    self.commands[section][actuator] = 'OFF'
                elif 'low' in current_status:
                    self.commands[section][actuator] = 'ON'
            elif current_trend == 'Increasing' and past_trend == 'Increasing':
                if 'high' in current_status:
                    self.commands[section][actuator] = 'OFF'
                if 'low' in current_status:
                    self.commands[section][actuator] = 'ON'
            elif current_trend == 'Decreasing' and past_trend == 'Decreasing':
                if 'high' in current_status:
                    self.commands[section][actuator] = 'OFF' if actuator == 'led_lights' else 'ON'
                elif 'low' in current_status:
                    self.commands[section][actuator] = 'ON'
            elif current_trend == 'Increasing' and past_trend == 'Decreasing':
                if current_status != 'optimal':
                    if 'high' in current_status:
                        self.commands[section][actuator] = 'OFF'
                    elif 'low' in current_status:
                        self.commands[section][actuator] = 'ON'
            elif current_trend == 'Decreasing' and past_trend == 'Increasing':
                if current_status != 'optimal':
                    if 'high' in current_status:
                        self.commands[section][actuator] = 'OFF' if actuator == 'led_lights' else 'ON'
                    elif 'low' in current_status:
                        self.commands[section][actuator] = 'ON'
        elif 'high' in current_status:
            self.commands[section][actuator] = 'OFF'
        elif 'low' in current_status:
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
        past_trend = self._past_trend[section]['temperature']  # Accessing the past trend
        actuator_state = [self.current_actuator_state[section][x] for x in self.SENSOR_ACTUATOR_MAPPING['temperature']] 
        actuator_mapping = self.SENSOR_ACTUATOR_MAPPING['temperature']

        # Instantiate Temperature class with the past_trend included
        temperature = Temperature(section, current_status, current_trend, past_trend, actuator_state, actuator_mapping, self.commands)

        # Call the plan_temperature method from Temperature class
        temperature.plan_temperature()
        

        # At this point, the `commands` dictionary has been updated by the Temperature class
           
                    
    def plan_humidity(self, section):
        """Plan humidity actions for a given section using Humidity class."""
        # Retrieve current and past humidity data for the section
        for actuator in self.SENSOR_ACTUATOR_MAPPING['humidity']:
            if actuator not in self.commands[section]:
                self.commands[section][actuator] = None

        current_status = self.current_status[section]['humidity']
        current_trend = self.current_trend[section]['humidity']
        past_trend = self._past_trend[section]['humidity']  # Accessing the past trend
        actuator_state = [self.current_actuator_state[section][x] for x in self.SENSOR_ACTUATOR_MAPPING['humidity']]
        actuator_mapping = self.SENSOR_ACTUATOR_MAPPING['humidity']
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
            
        