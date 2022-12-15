# -*- coding:utf-8 -*-
import json
import os
import network
from lib.uweb import OnTopHttp
from lib.sys_helper import file_or_dir_exists


class Boot:
    def __init__(self):
        self._device = None
        self._ready = False
        with open("/config/global.json", mode="r", encoding="utf-8") as global_config:
            global_config_dict = json.load(global_config)
            self._network_config_path = global_config_dict["network_config_path"]
            self._ap_ssid = global_config_dict["ap_ssid"]
            self._ap_password = global_config_dict["ap_password"]
            self._ap_http_host = global_config_dict["ap_http_host"]
            self._ap_http_port = global_config_dict["ap_http_port"]
            self._ap_http_source = global_config_dict["ap_http_source"]

    def start(self):
        self.setup()
        while self._ready is False:
            pass

    def setup(self):
        if file_or_dir_exists(self._network_config_path):
            if os.stat(self._network_config_path)[6] == 0:
                os.remove(self._network_config_path)
                self.setup()

            self.connect()
            self._ready = True
        else:
            self.open_access_point()
            ontop_http = OnTopHttp(self._ap_http_host, self._ap_http_port, self._ap_http_source)
            ontop_http.start()

    def open_access_point(self):
        self._device = network.WLAN(network.AP_IF)
        if self._device.isconnected():
            self._device.disconnect()
        self._device.active(True)
        self._device.config(essid=self._ap_ssid, password=self._ap_password, authmode=network.AUTH_WPA_WPA2_PSK)

    def connect(self):
        self._device = network.WLAN(network.STA_IF)
        if self._device.isconnected():
            self._device.disconnect()
        self._device.active(True)

        with open(self._network_config_path, mode="r", encoding="utf-8") as network_config:
            network_config_dict = json.load(network_config)
            network_config_ssid = network_config_dict["ssid"]
            network_config_passwort = network_config_dict["password"]

        self._device.connect(network_config_ssid, network_config_passwort)

        while not self._device.isconnected():
            pass


if __name__ == '__main__':
    boot = Boot()
    boot.start()
