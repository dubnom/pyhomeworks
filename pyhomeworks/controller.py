"""
Support for controlling Lutron Homeworks Series 4 and 8 systems.
"""
import logging

import voluptuous as vol

from homeassistant.const import (
    EVENT_HOMEASSISTANT_STOP, CONF_HOST, CONF_PORT)
import homeassistant.helpers.config_validation as cv

# FIX: This is not allowed to float freely
from pyhomeworks import Homeworks

REQUIREMENTS = ['pyhomeworks==0.0.1']

_LOGGER = logging.getLogger(__name__)

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
    """Setup Homeworks controller."""

    hass.data[HOMEWORKS_CONTROLLER] = None

    config = base_config.get(DOMAIN)
    host = config[CONF_HOST]
    port = config[CONF_PORT]

    controller = HomeworksController(host, port)

    def cleanup(event):
        controller.close()

    hass.bus_listen_once(EVENT_HOMEASSISTANT_STOP, cleanup)
    hass.data[HOMEWORKS_CONTROLLER] = controller
    return True

class HomeworksController(object):
    """Interface between HASS and Homeworks controller."""

    def __init__(self, host, port):
        self._homeworks = Homeworks(host, port, self._callback)
        self._subscribers = {}

    def register(self, device):
        """Add a device to subscribe to events."""
        if device.addr not in self._subscribers:
            self._subscribers[device.addr] = []
        self._subscribers[device.addr].append(device)

    def _callback(self, addr, msg_type, values):
        if addr in self._subscribers:
            for sub in self._subscribers[addr]:
                if sub.callback(msg_type, values):
                    sub.schedule_update_ha_state()

    def close(self):
        """Close the connection."""
        self._homeworks.close()


class HomeworksDevice():
    """Base class of a Homeworks device."""
    def __init__(self, controller, addr, name):
        self._addr = addr
        self._name = name
        controller.register(self)

    @property
    def addr(self):
        """Device address."""
        return self._addr

    @property
    def name(self):
        """Device name."""
        return self._name

    @property
    def should_poll(self):
        """No need to poll."""
        return False

    def callback(self, msg_type, values):
        """Dummy callback that should be implemented by devices."""
        return False
