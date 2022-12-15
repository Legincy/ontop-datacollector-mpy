# -*- coding:utf-8 -*-
import json

from module.Sensor import Sensor


class SensorController:
    def __init__(self):
        self._datacollector = None
        self._sensor_list = []
        with open("/config/pin-config.json", mode="r", encoding="utf-8") as pin_config:
            self._pin_config_dict = json.load(pin_config)
        with open("/config/onewire-fc.json", mode="r", encoding="utf-8") as onewire_fc:
            self._onewire_fc = json.load(onewire_fc)

    def setup(self, datacollector):
        self._datacollector = datacollector

    def prepare_sensor_list(self):
        board_sensor_configuration = self._datacollector.configuration
        for sensor_config in board_sensor_configuration:
            self._sensor_list.append(Sensor(self, sensor_config))

    def is_i2c_addr_used(self, addr_hex):
        is_used = False
        for sensor in self._sensor_list:
            if sensor.i2c_addr_hex == addr_hex:
                is_used = True
                break

        return is_used

    def get_unused_onewire_addr(self, onewire_possible_addr_list):
        for onewire_addr in onewire_possible_addr_list:
            is_used = False
            for sensor in self._sensor_list:
                if sensor.onewire_addr == onewire_addr:
                    is_used = True
                    break
            if is_used is False:
                return onewire_addr
        return None

    def get_datacollector(self):
        return self._datacollector

    def get_sensor_list(self):
        return self._sensor_list

    def get_pin_config(self):
        return self._pin_config_dict

    def get_onewire_fc(self):
        return self._onewire_fc

    datacollector = property(get_datacollector)
    sensor_list = property(get_sensor_list)
    pin_config = property(get_pin_config)
    onewire_fc = property(get_onewire_fc)
