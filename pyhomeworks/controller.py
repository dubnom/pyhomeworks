"""
Support for controlling Lutron Homeworks Series 4 and 8 systems.

Michael Dubno - 2018 - New York
"""
import logging

import voluptuous as vol

from homeassistant.const import (
    EVENT_HOMEASSISTANT_STOP, CONF_HOST, CONF_PORT)
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['pyhomeworks==0.0.1']

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'homeworks'

HOMEWORKS_CONTROLLER = 'homeworks'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, base_config):
    """Start Homeworks controller."""
    from pyhomeworks import Homeworks

    class HomeworksController(Homeworks):
        """Interface between HASS and Homeworks controller."""

        def __init__(self, host, port):
            """Host and port of Lutron Homeworks controller."""
            self._subscribers = {}
            Homeworks.__init__(host, port, self._callback)

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


class HomeworksDevice():
    """Base class of a Homeworks device."""

    def __init__(self, controller, addr, name):
        """Controller, address, and name of the device."""
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
        """Must be replaced with device callbacks."""
        return False
