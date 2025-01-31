import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os 
import time

class StoreKnowledge:
    
    def __init__(self):
        try:
            self.bucket = os.environ["INFLUXDB_BUCKET"]
            self.org = os.environ["INFLUXDB_ORG"]
            self.token = os.environ["INFLUXDB_TOKEN"]
            self.url = os.environ["INFLUXDB_URL"]
        except KeyError as e:
            raise RuntimeError(f"Missing required environment variable: {e}")

        # Initialize InfluxDB client
        self.client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)

    def writeDB(self, topic, value):
        
        print(f"Topic {topic[2]}: {value}")
        # write_api = self.client.write_api(write_options=SYNCHRONOUS)

        # if topic[2] == 'co' or topic[2] == 'co2' or topic[2] == 'fineDust' or topic[2] == 'humidity':
        #     p = influxdb_client.Point("industry_data").tag("section", topic[1]).field(topic[2], int(value)).time(
        #         int(time.time()), "s")
        # else:
        #     p = influxdb_client.Point("industry_data").tag("section", topic[1]).field(topic[2], value).time(
        #         int(time.time()), "s")

        # try:
        #     write_api.write(bucket=self.bucket, org=self.org, record=p)
        #     print("Writing in InfluxDB successfully completed!")
        # except Exception as e:
        #     # Gestisci eventuali errori durante la scrittura
        #     print(f"Error when writing to InfluxDB: {e}")