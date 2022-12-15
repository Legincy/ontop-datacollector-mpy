# -*- coding:utf-8 -*-
import json
import ubinascii
from lib.umqtt import MQTTClient


class MosquittoClient:
    def __init__(self, client_id="Datacollector"):
        self._client_id = str.encode(client_id)
        self._mqtt_client = None
        with open("/config/global.json", mode="r", encoding="utf-8") as global_config:
            global_config_dict = json.load(global_config)
            self._mqtt_host = global_config_dict["mqtt_host"]
            self._mqtt_port = global_config_dict["mqtt_port"]
            self._mqtt_user = global_config_dict["mqtt_user"]
            self._mqtt_password = global_config_dict["mqtt_password"]

    def connect(self):
        self._mqtt_client = MQTTClient(ubinascii.hexlify(self._client_id), self._mqtt_host,
                                       self._mqtt_port, self._mqtt_user, self._mqtt_password, 30)
        self._mqtt_client.connect()

        print(f'Connected to {self._mqtt_host} MQTT broker')

    def publish(self, topic, message):
        topic_bytes = str.encode(str(topic))
        message_bytes = str.encode(str(message))
        self._mqtt_client.publish(topic_bytes, message_bytes)

    def get_mqtt_client(self):
        return self._mqtt_client

    mqtt_client = property(get_mqtt_client)
