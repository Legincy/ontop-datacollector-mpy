# -*- coding:utf-8 -*-
from controller.SensorController import SensorController


class Datacollector:
    def __init__(self):
        self._sensor_controller = SensorController()
        self._board_id = None
        self._board_name = None
        self._last_seen_at = None
        self._plant_id = None
        self._bed_id = None
        self._plant = None
        self._bed = None
        self._configuration = None
        self._current_timestamp = None

    def load_config_dict(self, config_dict):
        self._board_id = config_dict["id"]
        self._board_name = config_dict["name"]
        self._last_seen_at = config_dict["last_seen_at"]
        self._plant_id = config_dict["plant_id"]
        self._bed_id = config_dict["bed_id"]
        self._configuration = config_dict["configuration"]
        self._current_timestamp = config_dict["timestamp"]

    def get_board_id(self):
        return self._board_id

    def get_board_name(self):
        return self._board_name

    def get_last_seen_at(self):
        return self._last_seen_at

    def get_plant_id(self):
        return self._plant_id

    def get_bed_id(self):
        return self._bed_id

    def get_configuration(self):
        return self._configuration

    def get_current_timestamp(self):
        return self._current_timestamp

    def set_current_timestamp(self, timestamp):
        self._current_timestamp = timestamp

    def get_sensor_controller(self):
        return self._sensor_controller

    board_id = property(get_board_id)
    board_name = property(get_board_name)
    last_seen_at = property(get_last_seen_at)
    plant_id = property(get_plant_id)
    bed_id = property(get_bed_id)
    sensor_controller = property(get_sensor_controller)
    configuration = property(get_configuration)
    current_timestamp = property(get_current_timestamp, set_current_timestamp)
