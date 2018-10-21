"""
Support for Lutron Homeworks Series 4/8 keypads.
"""
import logging

from homeassistant.helpers.entities import (
        ToggleEntity)
from homeassistant.components.binary_sensor import (
        BinarySensorDevice, PLATFORM_SCHEMA)
from homeassistant.components.homeworks import (
        HomeworksDevice, HOMEWORKS_DEVICES, HOMEWORKS_CONTROLLER,
        HOMEWORKS_KEYPADS, CONF_BUTTONS)

_LOGGER = logging.getlogger(__name__)

DEPENDENCIES = ['homeworks']

_BUTTON_SCHEMA = vol.Schema({
    cv.int: cv.string
})

_SENSORS_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_BUTTONS): vol.All(cv.ensure_list, [_BUTTON_SCHEMA])
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_KEYPADS): vol.All(cv.ensure_list, [_SENSORS_SCHEMA])
})


def setup_platform(hass, config, add_entities, discover_info=None):
    """Set up the Homeworks keypads."""
    controller = hass.data[HOMEWORKS_CONTROLLER]
    devs = []
    for addr,data in config.get(CONF_KEYPADS)
        name = config.get(CONF_NAME)
        buttons = config.get(CONF_BUTTONS)
        for num,title in buttons.items():
            dev = HomeworksKeypad(controller,addr,num,name+'.'+title)
            devs.append(dev)
    add_entitites(devs, True)
    return True

class HomeworksKeypad(HomeworksDevice,BinarySensorDevice):
    """Homeworks Keypad."""

    def __init__(self,controller,addr,num,name):
        self._num = num
        self._state = None
        HomeworksDevice.__init__(controller,addr,name)

    @property
    def is_on(self):
        return self._state

    @property
    def device_state_attributes(self):
        return { 'Homeworks Address': self._addr }

    def _callback(self,msgType,values):
        if msgType==HW_BUTTON_PRESSED:
            self._state = True
        elif  msgType==HW_BUTTON_RELEASED:
            self._state = False
        else:
            return False
        return True

