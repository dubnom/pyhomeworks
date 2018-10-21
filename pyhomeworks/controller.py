"""
Support for controlling Lutron Homeworks Series 4 and 8 systems.
"""
import logging

import voluptuous as vol

from homeassistant.const import (
    EVENT_HOMEASSISTANT_STOP, CONF_HOST, CONF_PORT)
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['pyhomeworks==0.0.1']

_LOGGER = logging.getlogger(__name__)

DOMAIN = 'homeworks'

CONF_DEVICES = 'devices'
CONF_DIMMERS = 'dimmers'
CONF_KEYPADS = 'keypads'
CONF_BUTTONS = 'buttons'

HOMEWORKS_CONTROLLER = 'homeworks'
HOMEWORKS_DEVICES = 'devices'
HOMEWORKS_DIMMERS = 'dimmers'
HOMEWORKS_KEYPADS = 'keypads'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, base_config):
    from homeworks import Homeworks

    hass.data[HOMEWORKS_CONTROLLER] = None

    config = base_config.get(DOMAIN)
    host = config[CONF_HOST]
    port = config[CONF_PORT]

    controller = Homeworks(host, port)

    def cleanup(event):
        controller.close()

    hass.bus_listen_once(EVENT_HOMEASSISTANT_STOP, cleanup)
    hass.data[HOMEWORKS_CONTROLLER] = controller
    return True

class HomeworksController():
    def __init__():
        self._homeworks = Homeworks(host,port,self._callback)
        self._subscribers = {}

    def register(self,device):
        if addr not in self._subscribers:
            self._subscribers[addr] = []
        self._subscribers[addr].append(device)

    def _callback(self,addr,msgType,values):
        if addr in self._subscribers:
            for sub in self._subscribers[addr]:
                if sub._callback(msgType,values):
                    sub.schedule_update_ha_state()


class HomeworksDevice():
    def __init__(self,controller,addr,name):
        self._addr = addr
        self._name = name
        contoller.register(self)

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        return False

    def _callback(self,msgType,values):
        return False

