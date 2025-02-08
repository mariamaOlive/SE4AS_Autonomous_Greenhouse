import math
import time

class LightSimulation:
    def __init__(self, max_intensity=100000, sunrise_hour=6, sunset_hour=18, time_speedup=580):
        """
        Simulates natural light intensity based on time of day.
        - `time_speedup`: Higher values speed up time (e.g., 60 makes 1 real hour = 1 full day).
        """
        self.max_intensity = max_intensity  # Max sunlight intensity at noon
        self.sunrise_hour = sunrise_hour    # Hour of sunrise
        self.sunset_hour = sunset_hour      # Hour of sunset
        self.day_duration = (sunset_hour - sunrise_hour) * 3600  # Convert hours to seconds
        self.start_time = time.time()  # Simulation start time
        self.time_speedup = time_speedup  # Time scaling factor

    def get_light_intensity(self):
        """Simulates natural light intensity with accelerated time."""
        # Simulated elapsed time (sped up)
        elapsed_seconds = ((time.time() - self.start_time) * self.time_speedup) % 86400  # 24h cycle

        # Determine if it's day or night
        current_sim_hour = (elapsed_seconds / 3600) % 24  # Convert to simulated hour
        if current_sim_hour < self.sunrise_hour or current_sim_hour >= self.sunset_hour:
            return 0  # No light at night

        # Calculate normalized time since sunrise (0 to 1)
        normalized_time = (elapsed_seconds - self.sunrise_hour * 3600) / self.day_duration

        # Sinusoidal function for light intensity
        light_intensity = self.max_intensity * max(0, math.sin(math.pi * normalized_time))
        
         # Factor to simulate shading from clouds, etc.

        return round(light_intensity, 2)
