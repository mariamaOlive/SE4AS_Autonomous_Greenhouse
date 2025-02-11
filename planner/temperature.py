class Temperature:
    def __init__(self, section, current_status, current_trend, past_trend, actuator_state, actuator_mapping, commands):
        """
        Initialize the Temperature class to handle temperature regulation for a given section.

        :param section: The section of the greenhouse (e.g., 'North', 'South')
        :param current_status: The current status of the temperature ('high', 'too_high', 'low', 'too_low', etc.)
        :param current_trend: The current trend of the temperature ('Increasing', 'Decreasing', 'Stable')
        :param past_trend: The previous trend of the temperature ('Increasing', 'Decreasing', 'Stable')
        :param actuator_state: Current state of the actuators (heater, fan, hatch, etc.)
        :param actuator_mapping: Mapping of actuators for controlling temperature
        :param commands: Dictionary where actuator commands will be stored
        """
        self.section = section
        self.current_status = current_status
        self.current_trend = current_trend
        self.past_trend = past_trend  # The past temperature trend
        self.actuator_state = actuator_state
        self.actuator_mapping = actuator_mapping
        self.commands = commands  # To store the actuator control commands

    def plan_temperature(self):
        """Plan temperature actions based on status and trend."""
        actuator_fan, actuator_hatch, actuator_heater = self.actuator_mapping
        self.actuator_state = dict(zip(self.actuator_mapping, self.actuator_state))
        
        current_actuator_state = self.actuator_state
        # Handle based on current status and trend
        if self.current_trend == 'Stable':
            self.handle_stable_status(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_trend == 'Increasing' and self.past_trend == 'Increasing':
            self.handle_increasing_status(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_trend == 'Decreasing' and self.past_trend == 'Decreasing':
            self.handle_decreasing_status(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_trend == 'Increasing' and self.past_trend == 'Decreasing':
            self.handle_increasing_from_decreasing(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_trend == 'Decreasing' and self.past_trend == 'Increasing':
            self.handle_decreasing_from_increasing(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)

    def handle_stable_status(self, current_actuator_state, actuator_heater, actuator_fan, actuator_hatch):
        """Handle stable status for temperature adjustment."""
        if self.current_status == 'high':
            self.handle_high_temperature(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'too_high':
            self.turn_on_fan_turn_off_heater_and_open_hatch(actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'low':
            self.handle_low_temperature(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'too_low':
            self.turn_on_heater_and_turn_off_fan_and_close_hatch(actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'optimal':
            self.turn_off_heater_and_turn_off_fan_and_close_hatch(actuator_heater, actuator_fan, actuator_hatch)
        

    def handle_increasing_status(self, current_actuator_state, actuator_heater, actuator_fan, actuator_hatch):
        """Handle increasing status for temperature adjustment."""
        if self.current_status == 'high':
            self.handle_high_temperature(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)            
        elif self.current_status == 'too_high':
            self.turn_on_fan_turn_off_heater_and_open_hatch(actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'optimal':
            self.turn_off_heater_and_turn_off_fan_and_close_hatch(actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'low':
            self.handle_low_temperature(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
            
        elif self.current_status == 'too_low':
            self.turn_on_heater_and_turn_off_fan_and_close_hatch(actuator_heater, actuator_fan, actuator_hatch)

    def handle_decreasing_status(self, current_actuator_state, actuator_heater, actuator_fan, actuator_hatch):
        """Handle decreasing status for temperature adjustment."""
        if self.current_status == 'high':
            self.handle_high_temperature(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'too_high':
            self.turn_on_fan_turn_off_heater_and_open_hatch(actuator_heater, actuator_fan,actuator_hatch)
        elif self.current_status == 'low':
            self.handle_low_temperature(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)

        elif self.current_status == 'too_low':
            self.turn_on_heater_and_turn_off_fan_and_close_hatch(actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'optimal':
            self.turn_off_heater_and_turn_off_fan_and_close_hatch(actuator_heater, actuator_fan, actuator_hatch)

    def handle_increasing_from_decreasing(self, current_actuator_state, actuator_heater, actuator_fan, actuator_hatch):
        """Handle increasing trend after decreasing trend for temperature adjustment."""
        if self.current_status == 'optimal':
            self.turn_off_heater_and_turn_off_fan_and_close_hatch(actuator_heater, actuator_fan, actuator_hatch)

        elif self.current_status == 'high':
            self.handle_high_temperature(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'low':
            self.handle_low_temperature(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'too_high':
            self.turn_on_fan_turn_off_heater_and_open_hatch(actuator_heater, actuator_fan, actuator_hatch)

        

    def handle_decreasing_from_increasing(self, current_actuator_state, actuator_heater, actuator_fan, actuator_hatch):
        """Handle decreasing trend after increasing trend for temperature adjustment."""
        if self.current_status == 'optimal':   
            self.turn_off_heater_and_turn_off_fan_and_close_hatch(actuator_heater, actuator_fan, actuator_hatch)

        elif self.current_status == 'high':
            self.handle_high_temperature(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'low':
            self.handle_low_temperature(current_actuator_state, actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'too_low':
            self.turn_on_heater_and_turn_off_fan_and_close_hatch(actuator_heater, actuator_fan, actuator_hatch)
        elif self.current_status == 'too_high':
            self.turn_on_fan_turn_off_heater_and_open_hatch(actuator_heater, actuator_fan, actuator_hatch)

    # Helper Functions for Actuator Commands
   
      
    def turn_on_fan_turn_off_heater_and_open_hatch(self, actuator_heater, actuator_fan, actuator_hatch):
        """Turn on fan and open hatch."""
        self.commands[self.section][actuator_heater] = 'OFF'
        self.commands[self.section][actuator_fan] = 'ON'
        self.commands[self.section][actuator_hatch] = 'OPEN'  

    def turn_on_heater_and_turn_off_fan_and_close_hatch(self, actuator_heater, actuator_fan, actuator_hatch):
        """Turn on heater and turn off fan and hatch."""
        self.commands[self.section][actuator_heater] = 'ON'
        self.commands[self.section][actuator_fan] = 'OFF'
        self.commands[self.section][actuator_hatch] = 'CLOSE'
    def turn_off_heater_and_turn_off_fan_and_close_hatch(self, actuator_heater, actuator_fan, actuator_hatch):
        """Turn on heater and turn off fan and hatch."""
        self.commands[self.section][actuator_heater] = 'OFF'
        self.commands[self.section][actuator_fan] = 'OFF'
        self.commands[self.section][actuator_hatch] = 'CLOSE'

    def handle_low_temperature(self, current_actuator_state, actuator_heater, actuator_fan, actuator_hatch):
        """Handle low temperature."""
        if current_actuator_state[actuator_fan] == 'ON':
            self.commands[self.section][actuator_fan] = 'OFF'
            self.commands[self.section][actuator_hatch] = 'CLOSE'
        else:
            self.commands[self.section][actuator_heater] = 'ON'
    
    def handle_high_temperature(self, current_actuator_state, actuator_heater, actuator_fan, actuator_hatch):
        """Handle high temperature."""
        if current_actuator_state[actuator_heater] == 'ON':
            self.commands[self.section][actuator_heater] = 'OFF'
        elif current_actuator_state[actuator_fan] == 'OFF':
            self.commands[self.section][actuator_fan] = 'ON'
            self.commands[self.section][actuator_hatch] = 'OPEN'
  
   

    
