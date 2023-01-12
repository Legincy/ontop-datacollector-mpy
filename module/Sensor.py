# -*- coding:utf-8 -*-

class Sensor:
    def __init__(self, sensor_data):
        self._uuid = sensor_data["id"]
        self._is_connected = sensor_data["isConnected"]
        self._name = sensor_data["sensor"]["name"]
        self._type = sensor_data["sensor"]["sensorType"]["name"]
        self._interface = None
        self._interface_name = sensor_data["sensor"]["interface"]["name"]
        self._interface_addr = None if sensor_data["sensor"]["i2cAddress"] is None else sensor_data["sensor"]["i2cAddress"]
        self._board_pin_name = sensor_data["boardPin"]["pin"]
        self._board_pin_num = None
        self._board_pin = None
        self._sensor_lib = None
        self._is_updated = True

    def get_meta(self):
        return {"is_connected": self._is_connected, "name": self._name, "type": self._type,
                "interface_name": self._interface_name, "interface_addr": self._interface_addr,
                "board_pin_name": self._board_pin_name, "board_pin_num": self.board_pin_num}

    def get_uuid(self):
        return self._uuid

    def get_is_connected(self):
        return self._is_connected

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    def get_interface(self):
        return self._interface

    def set_interface(self, interface):
        self._interface = interface

    def get_interface_name(self):
        return self._interface_name

    def get_interface_addr(self):
        return self._interface_addr

    def set_interface_addr(self, addr):
        self._interface_addr = addr

    def get_board_pin(self):
        return self._board_pin

    def set_board_pin(self, pin):
        self._board_pin = pin

    def get_board_pin_num(self):
        return self._board_pin_num

    def set_board_pin_num(self, pin):
        self._board_pin_num = pin

    def get_board_pin_name(self):
        return self._board_pin_name

    def get_sensor_lib(self):
        return self._sensor_lib

    def set_sensor_lib(self, sensor_lib):
        self._sensor_lib = sensor_lib

    def get_is_updated(self):
        return self._is_updated

    def set_is_updated(self, status):
        self._is_updated = status

    uuid = property(get_uuid)
    is_connected = property(get_is_connected)
    name = property(get_name)
    type = property(get_type)
    interface = property(get_interface, set_interface)
    interface_name = property(get_interface_name)
    interface_addr = property(get_interface_addr, set_interface_addr)
    board_pin = property(get_board_pin, set_board_pin)
    board_pin_name = property(get_board_pin_name)
    board_pin_num = property(get_board_pin_num, set_board_pin_num)
    sensor_lib = property(get_sensor_lib, set_sensor_lib)
    is_updated = property(get_is_updated, set_is_updated)

