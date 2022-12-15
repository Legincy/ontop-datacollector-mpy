# -*- coding:utf-8 -*-
import json
import urequests as requests


class OnTopService:
    def __init__(self):
        with open("/config/global.json", mode="r", encoding="utf-8") as global_config:
            global_config_dict = json.load(global_config)
        self.api_url = global_config_dict["api_url"]
        self.headers = {'Accept': 'application/json'}

    # == Board
    def get_board_by_uuid(self, uuid):
        response = requests.get(f"{self.api_url}/boards/{uuid}", headers=self.headers)

        return response.json()

    def post_register_board(self, id=None):
        request_body = {"id": id}
        response = requests.post(f"{self.api_url}/register", json=request_body, headers=self.headers)

        return response.json()

    def post_heartbeat(self, id):
        request_body = {"id": id}
        response = requests.post(f"{self.api_url}/heartbeat", json=request_body, headers=self.headers)

        return response.json()