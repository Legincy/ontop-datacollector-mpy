# -*- coding:utf-8 -*-
import json

import gc
from machine import Pin, I2C
from module.Sensor import Sensor
from onewire import OneWire
import binascii
from lib.sys_helper import _map


class SensorController:
    def __init__(self, datacollector=None):
        self._datacollector = datacollector
        self._sensor_list = []
        self._adc_addr = 0x6a
        with open("/config/pin-config.json", mode="r", encoding="utf-8") as pin_config:
            self._pin_config_dict = json.load(pin_config)
        with open("/config/onewire-fc.json", mode="r", encoding="utf-8") as onewire_fc:
            self._onewire_fc = json.load(onewire_fc)
        self._i2c = I2C(scl=Pin(self._pin_config_dict["DC_I2C"]["scl"]),
                        sda=Pin(self._pin_config_dict["DC_I2C"]["sda"]))
        self._sensor_setup_dict = {
            "I2C": self.configure_i2c,
            "SPI": None,
            "ADC": self.configure_analog,
            "OneWi": self.configure_onewire
        }

        self._sensor_read_value_dict = {
            "I2C": self.read_i2c,
            "SPI": None,
            "ADC": self.read_analog,
            "OneWi": self.read_onewire
        }

    def init_sensor_list(self):
        sensor_configuration = self._datacollector.configuration
        for config in sensor_configuration:
            try:
                sensor = self.setup_sensor(config)
                self._sensor_list.append(sensor)
                print(f"[Sensor]: Registered '{sensor.name}' on port '{sensor.board_pin_name}'")
            except Exception as e:
                print(
                    f"Error while setting up sensor (name: {config['sensor']['name']} | uuid: name: {config['id']}) -- {e}")

    def setup_sensor(self, config) -> Sensor:
        sensor = Sensor(config)
        sensor.board_pin_num = self._pin_config_dict[sensor.board_pin_name]
        if type(sensor.board_pin_num) is int:
            sensor.board_pin = Pin(sensor.board_pin_num)
        if sensor.interface_name in self._sensor_setup_dict:
            self._sensor_setup_dict[sensor.interface_name](sensor)
        gc.collect()

        return sensor

    def configure_onewire(self, sensor):
        sensor.interface = OneWire(sensor.board_pin)
        onewire_slaves_binary_list = sensor.interface.scan()
        onewire_slaves_hex_list = list(map(lambda addr: binascii.hexlify(addr).decode(), onewire_slaves_binary_list))
        possible_addr_list = list(filter(lambda addr: self.onewire_fc[f"0x{str(addr)[:2]}"] == sensor.name.lower(),
                                         onewire_slaves_hex_list))
        onewire_addr_hex = self.get_unused_onewire_addr(possible_addr_list)
        onewire_addr_bin = binascii.unhexlify(onewire_addr_hex)
        sensor_class = self.get_dynamic_sensor_class(sensor)

        sensor.sensor_lib = sensor_class(sensor.interface, onewire_addr_bin)

    def configure_analog(self, sensor):
        sensor.interface = self._i2c

    def configure_i2c(self, sensor):
        sensor.interface = self._i2c
        local_i2c_config_dict = self._pin_config_dict[sensor.board_pin_name]
        sensor_i2c_hex_addr = f'0x{sensor.interface_addr}'
        sensor_i2c_int_addr = int(sensor_i2c_hex_addr)

        i2c_addr_int_list = self._i2c.scan()
        i2c_addr_hex_list = list(map(lambda addr: hex(addr), i2c_addr_int_list))

        if self.is_i2c_addr_used(sensor_i2c_hex_addr) or sensor_i2c_int_addr not in i2c_addr_int_list:
            return

        sensor_class = self.get_dynamic_sensor_class(sensor)

        sensor.sensor_lib = sensor_class(address=sensor_i2c_int_addr, i2c=self._i2c)

    def is_i2c_addr_used(self, addr_hex):
        is_used = False
        for sensor in self._sensor_list:
            if sensor.interface_addr == addr_hex:
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

    def read_onewire(self, sensor):
        if sensor.sensor_lib is None:
            return
        return sensor.sensor_lib.get_data()

    def read_i2c(self, sensor):
        if sensor.sensor_lib is None:
            return
        return sensor.sensor_lib.get_data()

    def get_data_bundle(self, sensor):
        sensor_value = self._sensor_read_value_dict[sensor.interface_name](sensor)
        data_bundle = {"timestamp": self._datacollector.current_timestamp, "uuid": sensor.uuid}
        data_bundle.update(sensor_value)
        if sensor.is_updated:
            data_bundle.update(sensor.get_meta())
            sensor.is_updated = False

        return data_bundle

    def get_dynamic_sensor_class(self, sensor):
        "Imports dynamically the responsible onewire class based on its family-code/name"
        mod_import = __import__('lib.sensor.' + sensor.name.lower(), True, False, sensor.name)
        return getattr(mod_import, sensor.name)

    def read_analog(self, sensor):
        adc_config = {
            "DC_ANLG_01": {"voltage": 3300, "config_bytes": bytes([0x10])},
            "DC_ANLG_02": {"voltage": 5000, "config_bytes": bytes([0x30])}
        }

        self._i2c.writeto(self._adc_addr, adc_config[sensor.board_pin_name]["config_bytes"])
        pin_value = self._i2c.readfrom(self._adc_addr, 2)
        pin_value_int = int.from_bytes(pin_value, "big")
        value = _map(pin_value_int, 0, 2047, 0, adc_config[sensor.board_pin_name]["voltage"])

        return {"value": value}

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
