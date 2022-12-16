# -*- coding:utf-8 -*-
import json
import time
import machine
from lib.uweb.microWebSrv2 import MicroWebSrv2
from lib.uweb.webRoute import *


class OnTopHttp:
    def __init__(self, address, port, source):
        self._address = address
        self._port = port
        self._source = source
        self._server = MicroWebSrv2()

    def start(self):
        self._server.SetEmbeddedConfig()
        self._server.BindAddress = (self._address, self._port)
        self._server.RootPath = self._source
        self._server.NotFoundURL = '/'
        self._server.StartManaged()


#################################################################################################################ä
@WebRoute(POST, '/wifi-configuration', name="Wifi-Configuration")
def request_wifi_configuration(server, request):
    data = request.GetPostedURLEncodedForm()
    restart_device = False
    try:
        wifi_ssid, wifi_password = data['ssid'], data['password']
        print(wifi_ssid, wifi_password, len(wifi_ssid), len(wifi_password), len(wifi_ssid) > 0)
        if len(wifi_ssid) > 0 and len(wifi_password) > 0:
            data_dict = {"ssid": wifi_ssid, "password": wifi_password}
            with open("/config/network-config.json", mode="w", encoding="utf-8") as network_config:
                json.dump(data_dict, network_config)
            restart_device = True
    except:
        request.Response.ReturnBadRequest()
        return

    print(wifi_ssid, wifi_password)
    content = f"""\
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Wifi-Konfiguration</title>
                </head>
                <body>
                    <h2>Datacollector</h2>
                    <p>Wifi Konfiguration erfolgreich angelegt!</p>
                </body>
            </html>
            """
    request.Response.ReturnOk(content)
    time.sleep(5)
    if restart_device:
        machine.reset()
