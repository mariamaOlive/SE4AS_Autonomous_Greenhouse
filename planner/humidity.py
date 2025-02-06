class Humidity:
    def __init__(self, section, current_status, current_trend, past_trend, actuator_state, actuator_mapping, commands):
        """
        Initialize the Humidity class to handle humidity regulation for a given section.

        :param section: The section of the greenhouse (e.g., 'North', 'South')
        :param current_status: The current status of humidity ('too_low', 'optimal', 'too_high')
        :param current_trend: The current trend of humidity ('Increasing', 'Decreasing', 'Stable')
        :param past_trend: The previous trend of humidity ('Increasing', 'Decreasing', 'Stable')
        :param actuator_state: Current state of the actuators (heater, pump)
        :param actuator_mapping: Mapping of actuators for controlling humidity
        :param commands: Dictionary where actuator commands will be stored
        """
        self.section = section
        self.current_status = current_status
        self.current_trend = current_trend
        self.past_trend = past_trend
        self.actuator_state = actuator_state
        self.actuator_heater, self.actuator_pump = actuator_mapping  # Extract actuators
        self.commands = commands  # Dictionary to store actuator control commands

    def plan_humidity(self):
        """Plan humidity actions based on status and trend."""
        # Handle high humidity
        if self.current_status == 'too_high':
            self.handle_high_humidity()
        # Handle low humidity
        elif self.current_status == 'too_low':
            self.handle_low_humidity()
        # Handle optimal humidity
        else:
            self.turn_off_heater_and_pump()  # If humidity is optimal, turn everything off

    def handle_high_humidity(self):
        """Handles cases where humidity is too high."""
        heater_on = self.actuator_state[self.actuator_heater] == 'ON'
        if heater_on:
            pump_on = self.actuator_state[self.actuator_pump] == 'ON'

            if pump_on:
                # If both are ON and humidity is high, turn OFF pump first
                self.commands[self.section][self.actuator_pump] = 'OFF'
            else:
                # If heater is ON and pump is OFF but humidity is still high, turn OFF heater
                self.commands[self.section][self.actuator_heater] = 'OFF'

    def handle_low_humidity(self):
        """Handles cases where humidity is too low."""
        heater_on = self.actuator_state[self.actuator_heater] == 'ON'
        pump_on = self.actuator_state[self.actuator_pump] == 'ON'

        if self.current_trend == 'Decreasing' or self.past_trend == 'Decreasing':
            # If humidity has been decreasing, we need to increase it
            if not pump_on:
                self.commands[self.section][self.actuator_pump] = 'ON'  # Try turning on pump first
            elif not heater_on:
                self.commands[self.section][self.actuator_heater] = 'ON'  # If pump is on, also turn on heater

        elif self.current_trend == 'Stable':
            # If stable but too low, turn on at least one device
            if not heater_on and not pump_on:
                self.commands[self.section][self.actuator_pump] = 'ON'  # Try turning on pump first
            elif not heater_on:
                self.commands[self.section][self.actuator_heater] = 'ON'  # If pump is on, also turn on heater

    def turn_off_heater_and_pump(self):
        """Turn off heater and pump if they are ON."""
        if self.actuator_state[self.actuator_heater] == 'ON':
            self.commands[self.section][self.actuator_heater] = 'OFF'
        if self.actuator_state[self.actuator_pump] == 'ON':
            self.commands[self.section][self.actuator_pump] = 'OFF'
