class Humidity:
    def __init__(self, section, current_status, current_trend, past_trend, actuator_state, actuator_mapping, commands):
        """
        Initialize the Humidity class to handle humidity regulation for a given section.

        :param section: The section of the greenhouse (e.g., 'North', 'South')
        :param current_status: The current status of humidity ('too_low', 'optimal', 'too_high')
        :param current_trend: The current trend of humidity ('Increasing', 'Decreasing', 'Stable')
        :param past_trend: The previous trend of humidity ('Increasing', 'Decreasing', 'Stable')
        :param actuator_state: Current state of the actuators (pump)
        :param actuator_mapping: Mapping of actuators for controlling humidity
        :param commands: Dictionary where actuator commands will be stored
        """
        self.section = section
        self.current_status = current_status
        self.current_trend = current_trend
        self.past_trend = past_trend
        self.actuator_state = actuator_state
        self.actuator_pump = actuator_mapping[0]  # Extract actuators
        self.commands = commands  # Dictionary to store actuator control commands

    def plan_humidity(self):
        """Plan humidity actions based on status and trend."""
        # Handle high humidity
        if self.current_status in ['too_high', 'high']:
            self.handle_high_humidity()
        # Handle low humidity
        elif self.current_status in ['too_low', 'low']:
            self.handle_low_humidity()
        # Handle optimal humidity
        else:
            self.handle_optimal_state()  # If humidity is optimal, turn everything off

    def handle_high_humidity(self):
        """Handles cases where humidity is too high. need to decrease it. by turning off pump"""
        self.commands[self.section][self.actuator_pump] = 'OFF'
            

    def handle_low_humidity(self):
        """Handles cases where humidity is too low."""
        self.commands[self.section][self.actuator_pump] = 'ON'  # Try turning on pump 

            
    def handle_optimal_state(self):
        """Turn off pump if it is ON."""
        self.commands[self.section][self.actuator_pump] = 'OFF'
