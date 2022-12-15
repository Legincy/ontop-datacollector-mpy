# -*- coding:utf-8 -*-
import uasyncio as asyncio
import os
from lib.sys_helper import file_or_dir_exists
from module.Datacollector import Datacollector
from module.MosquittoClient import MosquittoClient
from module.OnTopService import OnTopService
import json


class DatacollectorController:
    def __init__(self, scope):
        self._scope = scope
        self._datacollector = Datacollector()
        self._mosquitto_client = MosquittoClient()
        self._ontop_service = OnTopService()
        self._async_loop = self._scope.async_loop
        with open("/config/global.json", mode="r", encoding="utf-8") as global_config:
            global_config_dict = json.load(global_config)
            self._device_config_path = global_config_dict["device_config_path"]

    def setup(self):
        if file_or_dir_exists(self._device_config_path):
            if os.stat(self._device_config_path)[6] == 0:
                os.remove(self._device_config_path)
                self.setup()

            try:
                self.load_device_config()
                self.register_device()
            except:
                pass

            # self._sensor_controller.setup(self)
            # self._sensor_controller.prepare_sensor_list()

            print(f"Device configuration loaded: {self._board_name} ({self._uuid})")
        else:
            self.register_device()

        # self._async_loop.create_task(self.task_test())
        # self._async_loop.create_task(self.task_test1())

    def load_device_config(self):
        try:
            with open(self._device_config_path, mode="r", encoding="utf-8") as device_config:
                device_config_dict = json.load(device_config)

            print(device_config_dict)
            self._datacollector.load_config_dict(device_config_dict)
        except FileNotFoundError:
            pass
        except:
            print("failed to load device config")

    def register_device(self):
        device_uuid = None if self._uuid is None else self._uuid
        
        try:
            response_dict = self._ontop_service.post_register_board(device_uuid)
            with open(self._device_config_path, mode="wb", encoding="utf-8") as device_config:
                json.dump(response_dict, device_config)
        except:
            print("Could not fetch config.")

        try:
            if response_dict is not None:
                self.load_config_dict(response_dict)
        except Exception as e:
            print("Could not load config.")
            print(e)

    async def task_collect_sensor_data(self):
        while True:
            for sensor in self._datacollector.sensor_controller.sensor_list:
                sensor_package_dict = sensor.get_data_bundle()
                for key in sensor_package_dict:
                    topic = key
                    if type(sensor_package_dict[key]) == dict:
                        for sub_key in sensor_package_dict[key]:
                            topic = f"{key}/{sub_key}"
                            self._mosquitto_client.publish(
                                f"datacollector/{self._datacollector.board_id}/sensors/{sensor.uuid}/{topic}",
                                sensor_package_dict[key][sub_key])
                    else:
                        self._mosquitto_client.publish(
                            f"datacollector/{self._datacollector.board_id}/sensors/{sensor.uuid}/{topic}",
                            sensor_package_dict[key])

            await asyncio.sleep(60)

    async def task_heartbeat(self):
        last_update = self._datacollector.current_timestamp
        while True:
            if self._datacollector.current_timestamp - last_update >= 60:
                response_dict = self._ontop_service.post_heartbeat(self._datacollector.board_id)
                self._datacollector.current_timestamp = response_dict["timestamp"]
                last_update = self._datacollector.current_timestamp
            else:
                self._datacollector.current_timestamp += 1

            await asyncio.sleep(1)
