import paho.mqtt.client as mqtt
from store_knowledge import StoreKnowledge
import os

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("greenhouse/#")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    key = msg.topic.split("/")
    db_knowledge.writeDB(key, payload)

    # print(f"{msg.topic}  -> {payload}")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")

if __name__ == '__main__':
    # Start Database
    MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT"))
    db_knowledge = StoreKnowledge()
    
    # Start Broker Connection
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.connect("MQTT_BROKER", MQTT_PORT)
    
    # Start listening broker messages
    client_mqtt.loop_forever()