# -*- coding: utf-8 -*-
"""MQTT management."""
# --------------------------------------------------------
# Module Name : power recording API
# Version : 1.0
#
# Copyright © 2022 Orange
# This software is distributed under the Apache 2 license
# <http://www.apache.org/licenses/LICENSE-2.0.html>
#
# -------------------------------------------------------
# Created     : 2022-06
# Authors     : Benoit HERARD <benoit.herard(at)orange.com>
#
# Description :
#     Scenarios and scenarios steps management.

import datetime
import json
import logging

# import paho.mqtt.client as mqtt

import settings
import wiotp.sdk.device

class MQTTService:

    _logger = logging.getLogger(__name__)

    _mqtt_client = None

    _config_template = {
        "identity": {
            "orgId": "masdev",
            "typeId": "1th-building",
            "deviceId": "t-sensor-1"
        },
        "auth": {
            "token": "1qaz2wsx"
        },
        "options": {
            "domain": "masdev.messaging.iot.iccce.apps.maximodemo.poc.icc",
            "mqtt": {
                "port": 443,
                "transport": "tcp",
                "cleanStart": True,
                "sessionExpiry": 3600,
                "keepAlive": 60,
                # come from mas-ibmce-iot/ibmce-public-tls(secret)
                "caFile": "/usr/local/energyrecorder/recording-api/conf"
            },
            "http": {"verify": False}
        }
    }   
    def _complete_config(self, typeID, deviceID):
        config = self._config_template
        # config['auth']['token'] = self.server_conf['apikey']
        # config['options']['domain'] = settings.MQTT["host"]
        # config['options']['mqtt']['port'] = settings.MQTT["port"]
        # config['options']['mqtt']['caFile'] = self.cacert_path
        config['identity']['typeId'] = typeID
        config['identity']['deviceId'] = deviceID
        return config

    def _commandCallback(self, cmd):
        self.logger.info("Command received: %s" % cmd.data)  

    def publish(
        self,
        environment,
        equipement,
        scenario,
        step,
        sensor,
        unit,
        value,
        time,
        topology=None
    ):
        """Publish a data to MQTT

        :param environment: related environmenet
        :type environment: str
        :param equipement: related equipement
        :type equipement: str
        :param scenario: current running scenario
        :type scenario: str
        :param step: Current scenaio step
        :type step: str
        :param sensor: related sensor
        :type sensor: str
        :param unit: sensor unit
        :type unit: str
        :param value: data value
        :type value: any
        :param time: Measurement timestamp
        :type time: int
        :param topology: DOC Topology
        :type unit: disct
        """

        if settings.MQTT:
            if not self._mqtt_client:
                # self._mqtt_client = mqtt.Client(str(datetime.datetime.now().timestamp()))
                # if "user" in settings.MQTT and settings.MQTT["user"]:
                #     self._mqtt_client.username_pw_set(
                #         settings.MQTT["user"],
                #         settings.MQTT["pass"]
                #     )
                # self._mqtt_client.connect(
                #     settings.MQTT["host"],
                #     settings.MQTT["port"],
                # )
                self._mqtt_client = wiotp.sdk.device.DeviceClient(
                    config=self._complete_config("lenovoRS_Devicetype", equipement), logHandlers=None)

                self._mqtt_client.commandCallback = self._commandCallback

            # Connect
            self._mqtt_client.connect()


            data = {
                "environment": environment,
                "equipement": equipement,
                "scenario": scenario,
                "step": step,
                "sensor": sensor,
                "unit": unit,
                "value": value,
                "timestamp": time if time else int(datetime.datetime.now().timestamp())
            }
            if topology:
                data["topology"] = topology
            # self._mqtt_client.publish(
            #     F'{settings.MQTT["base_path"]}/{environment}/{equipement}/{sensor}',
            #     json.dumps(
            #         data
            #     )
            # )

            # Send Data
            self._mqtt_client.publishEvent(eventId="serverstatus",
                                msgFormat="json", data=data, qos=0, onPublish=None)

            # Disconnect
            self._mqtt_client.disconnect()
