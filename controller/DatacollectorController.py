# -*- coding:utf-8 -*-
import gc
import uasyncio as asyncio
import os, errno
from lib.umqtt import MQTTClient
from machine import Pin
from lib.sys_helper import file_or_dir_exists
from module.Datacollector import Datacollector
from module.OnTopService import OnTopService
import ubinascii
import json


class DatacollectorController:
    def __init__(self, scope):
        self._scope = scope
        self._datacollector = Datacollector(self)
        self._mqtt_client = None
        self._ontop_service = OnTopService()
        self._async_loop = self._scope.async_loop
        with open("/config/global.json", mode="r", encoding="utf-8") as global_config:
            global_config_dict = json.load(global_config)
            self._device_config_path = global_config_dict["device_config_path"]
            self._mqtt_host = global_config_dict["mqtt_host"]
            self._mqtt_port = global_config_dict["mqtt_port"]
            self._mqtt_user = global_config_dict["mqtt_user"]
            self._mqtt_password = global_config_dict["mqtt_password"]
            self._mqtt_topic_subscriptions = global_config_dict["mqtt_topic_subscriptions"]

    def setup(self):
        if file_or_dir_exists(self._device_config_path):
            if os.stat(self._device_config_path)[6] == 0:
                os.remove(self._device_config_path)
                self.setup()

            try:
                self.load_device_config()
                self.register_device()
                self._datacollector.sensor_controller.init_sensor_list()
                self.mqtt_init_client()

                self._async_loop.create_task(self.task_collect_sensor_data())
                self._async_loop.create_task(self.task_heartbeat())
                self._async_loop.create_task(self.task_mqtt_topic_listener())
            except Exception as e:
                print(f"Error while setting up Datacollector - {e}")

            print(f"Device configuration loaded: {self._datacollector.board_name} ({self._datacollector.board_id})")
        else:
            self.register_device()

    def load_device_config(self):
        try:
            with open(self._device_config_path, mode="r", encoding="utf-8") as device_config:
                device_config_dict = json.load(device_config)

            self._datacollector.load_config_dict(device_config_dict)
        except OSError as e:
            if e.errno == errno.ENOENT:
                pass
        except:
            print("failed to load device config")

    def register_device(self):
        device_uuid = None if self._datacollector.board_id is None else self._datacollector.board_id
        response_dict = None

        try:
            response_dict = self._ontop_service.post_register_board(device_uuid)
            self._datacollector.current_timestamp = response_dict["timestamp"]

            with open(self._device_config_path, mode="wb", encoding="utf-8") as device_config:
                json.dump(response_dict, device_config)
            gc.collect()
        except:
            print("Could not fetch config.")

        try:
            if response_dict is not None:
                self._datacollector.load_config_dict(response_dict)
        except Exception as e:
            print(f"Could not load config. -- {e}")

    def mqtt_init_client(self):
        client_id = "Datacollector" if self._datacollector.board_name is None else self._datacollector.board_name
        self._mqtt_client = MQTTClient(ubinascii.hexlify(client_id), self._mqtt_host,
                                       self._mqtt_port, self._mqtt_user, self._mqtt_password, 60)
        self._mqtt_client.set_callback(self.mqtt_gpio_listener)
        self._mqtt_client.connect()

        print(f'Connected to MQTT broker {self._mqtt_host}:{self._mqtt_port} as {self._mqtt_user}')

        if self._mqtt_topic_subscriptions is not None and len(self._mqtt_topic_subscriptions) > 0:
            for topic in self._mqtt_topic_subscriptions:
                topic_str = topic.format(board_id=self._datacollector.board_id)
                self._mqtt_client.subscribe(topic_str.encode('ascii'))
                print(f"Datacollector::mqtt_init_client() -- Topic Subscription: {topic}")

    def mqtt_publish(self, topic, message):
        topic_bytes = str.encode(str(topic))
        message_bytes = str.encode(str(message))
        self._mqtt_client.publish(topic_bytes, message_bytes)

    def mqtt_gpio_listener(self, topic, msg):
        pin_str = topic.decode("utf-8").partition("pins/")[2].partition("/state")[0]
        pin_num = self._datacollector.sensor_controller.pin_config[pin_str]
        status = 0 if msg == b'false' else 1
        board_pin = Pin(pin_num, Pin.OUT)
        board_pin.value(status)

    def health_check(self):
        pass

    async def task_mqtt_topic_listener(self):
        print("[Thread-Pool]: Running - task_mqtt_topic_listener()")
        while True:
            try:
                self._mqtt_client.check_msg()
            except OSError as e:
                print("Lost connection to MQTT Server. Reconnecting... -- {e}")
                self.mqtt_init_client()
            await asyncio.sleep(1)

    async def task_collect_sensor_data(self):
        print("[Thread-Pool]: Running - task_collect_sensor_data()")
        while True:
            for sensor in self._datacollector.sensor_controller.sensor_list:
                try:
                    sensor_package_dict = self._datacollector.sensor_controller.get_data_bundle(sensor)
                    sensor_uuid = sensor_package_dict.pop("uuid")
                    for key in sensor_package_dict:
                        topic = key
                        if type(sensor_package_dict[key]) == dict:
                            for sub_key in sensor_package_dict[key]:
                                topic = f"{key}/{sub_key}"
                                self._mqtt_client.publish(
                                    f"boards/{self._datacollector.board_id}/sensors/{sensor_uuid}/{topic}",
                                    str(sensor_package_dict[key][sub_key]))
                        else:
                            self._mqtt_client.publish(
                                f"boards/{self._datacollector.board_id}/sensors/{sensor_uuid}/{topic}",
                                str(sensor_package_dict[key]))
                except Exception as e:
                    print(f"Error while getting data bundle -- {e}")
            await asyncio.sleep(1)

    async def task_heartbeat(self):
        print("[Thread-Pool]: Running - task_heartbeat()")
        last_web_update = -1
        last_mqtt_update = -1
        while True:
            try:
                if self._datacollector.current_timestamp - last_web_update >= 60 or last_web_update == -1:
                    previous_mem = gc.mem_free()
                    response_dict = self._ontop_service.post_heartbeat(self._datacollector.board_id)
                    self._datacollector.current_timestamp = response_dict["timestamp"]
                    last_web_update = self._datacollector.current_timestamp
                    gc.collect()
                    print(f"current_mem: {gc.mem_free()} || previous-mem: {previous_mem}")
            except Exception as e:
                print(f"Error while trying to send a heartbeat -- {e}")
                
            if self._datacollector.current_timestamp - last_mqtt_update >= 30 or last_mqtt_update == -1:
                topic = f"boards/{self._datacollector.board_id}/free_memory"
                self.mqtt_publish(topic, gc.mem_free())
                last_mqtt_update = self._datacollector.current_timestamp

            self._datacollector.current_timestamp += 1

            await asyncio.sleep(1)
