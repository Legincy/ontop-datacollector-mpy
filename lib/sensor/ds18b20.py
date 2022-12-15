# -*- coding:utf-8 -*-
import onewire, ds18x20
import time


class DS18B20:
    def __init__(self, onewire_bus, onewire_addr_bin):
        self._sensor = ds18x20.DS18X20(onewire_bus)
        self._onewire_addr_bin = onewire_addr_bin

    def get_data(self):
        self._sensor.convert_temp()
        time.sleep_ms(750)
        return {"value": self._sensor.read_temp(self._onewire_addr_bin)}

    def get_sensor(self):
        return self._sensor

    sensor = property(get_sensor)
