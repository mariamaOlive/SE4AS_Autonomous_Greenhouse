import configparser


config = configparser.ConfigParser()

config.add_section('DEFAULTS')
config.set('DEFAULTS', 'DEFAULT_MQTT_BROKER_HOST', 'localhost')
config.set('DEFAULTS', 'DEFAULT_MQTT_BROKER_PORT', '1883')  
config.set('DEFAULTS', 'DEFAULT_THRESHHOLD_FILE', '/shared_file/greenhouse_threshold.json')


config.add_section('SIMULATION')
config.set('SIMULATION', 'weather_type', 'Sunny')

with open('shared_files/config.ini', 'w') as configfile:
    config.write(configfile)


