# -*- coding:utf-8 -*-
from machine import Pin, ADC, SoftI2C
from onewire import OneWire
import binascii


class Sensor:
    def __init__(self, sensor_controller, sensor_data):
        self._sensor_controller = sensor_controller
        self._sensor_data = sensor_data
        self._sensor_uuid = sensor_data["id"]
        self._sensor_name = sensor_data["sensor"]["name"]
        self._sensor_interface = sensor_data["sensor"]["interface"]["name"]
        self._sensor = None
        self._onewire_addr = None
        self._i2c_addr_hex = None
        self._sensor_setup_dict = {
            "I2C": self.setup_i2c,
            "SPI": None,
            "ADC": self.setup_analog,
            "OneWi": self.setup_onewire
        }

        self._sensor_get_value_dict = {
            "I2C": self.read_i2c,
            "SPI": None,
            "ADC": self.read_analog,
            "OneWi": self.read_onewire
        }

        self._sensor_setup_dict[self._sensor_interface]()

    def get_data_bundle(self):
        sensor_value = self._sensor_get_value_dict[self._sensor_interface]()
        result_dict = {"uuid": self._sensor_uuid, "name": self._sensor_name, "interface": self._sensor_interface, "timestamp": self._sensor_controller.datacollector.current_timestamp}
        result_dict.update(sensor_value)

        return result_dict

    def setup_analog(self):
        if self._sensor is not None:
            return

        board_pin = self._sensor_controller.pin_config[self._sensor_data["boardPin"]["pin"]]

        self._sensor = ADC(Pin(board_pin))
        # This is required so that the sensor uses the full 3V3 range
        self._sensor.atten(ADC.ATTN_11DB)

    def setup_onewire(self):
        onewire_fc = self._sensor_controller.onewire_fc
        board_pin = self._sensor_controller.pin_config[self._sensor_data["boardPin"]["pin"]]
        board_pin = Pin(board_pin)
        onewire_bus = OneWire(board_pin)

        onewire_slaves_binary_list = onewire_bus.scan()
        onewire_slaves_hex_list = list(map(lambda addr: binascii.hexlify(addr).decode(), onewire_slaves_binary_list))
        possible_addr_list = list(filter(lambda addr: onewire_fc[f"0x{str(addr)[:2]}"] == self._sensor_name.lower(),
                                         onewire_slaves_hex_list))
        onewire_addr_hex = self._sensor_controller.get_unused_onewire_addr(possible_addr_list)
        onewire_addr_bin = binascii.unhexlify(onewire_addr_hex)

        sensor_class = self.get_dynamic_sensor_class()

        self._sensor = sensor_class(onewire_bus, onewire_addr_bin)

    def setup_i2c(self):
        local_i2c_config_dict = self._sensor_controller.pin_config[self._sensor_data["boardPin"]["pin"]]
        sensor_i2c_hex_addr = f'0x{self._sensor_data["sensor"]["i2cAddress"]}'
        sensor_i2c_int_addr = int(sensor_i2c_hex_addr)

        i2c = SoftI2C(scl=Pin(local_i2c_config_dict["scl"]), sda=Pin(local_i2c_config_dict["sda"]))
        i2c_addr_int_list = i2c.scan()
        i2c_addr_hex_list = list(map(lambda addr: hex(addr), i2c_addr_int_list))

        if self._sensor_controller.is_i2c_addr_used(sensor_i2c_hex_addr) or sensor_i2c_int_addr not in i2c_addr_int_list:
            return

        sensor_class = self.get_dynamic_sensor_class()

        self._sensor = sensor_class(address=sensor_i2c_int_addr, i2c=i2c)

    def get_dynamic_sensor_class(self):
        "Imports dynamically the responsible onewire class based on its family-code/name"
        mod_import = __import__('lib.sensor.' + self._sensor_name.lower(), True, False, self._sensor_name)
        return getattr(mod_import, self._sensor_name)

    def read_analog(self):
        if self._sensor is None:
            return

        return {"value": self._sensor.read()}

    def read_onewire(self):
        if self._sensor is None:
            return
        return self._sensor.get_data()

    def read_i2c(self):
        if self._sensor is None:
            return
        return self._sensor.get_data()

    def get_sensor_uuid(self):
        return self._sensor_uuid

    def get_sensor_interface(self):
        return self._sensor_interface

    def get_onewire_addr(self):
        return self._onewire_addr

    def get_i2c_addr_hex(self):
        return self._i2c_addr_hex

    uuid = property(get_sensor_uuid)
    interface = property(get_sensor_interface)
    onewire_addr = property(get_onewire_addr)
    i2c_addr_hex = property(get_i2c_addr_hex)
