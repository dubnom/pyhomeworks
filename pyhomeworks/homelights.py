"""
Support for Lutron Homeworks Series 4/8 lights.
"""
import logging

from homeassistant.components.light import (
        ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, Light)
from homeassistant.components.homeworks import (
        HomeworksDevice, HOMEWORKS_DEVICES, HOMEWORKS_CONTROLLER,
        HOMEWORKS_LIGHTS)

_LOGGER = logging.getlogger(__name__)

DEPENDENCIES = ['homeworks']

_DIMMER_SCHEMA = vol.Schema({
    cv.string: cv.string
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_DIMMERS): vol.All(cv.ensure_list, [_DIMMER_SCHEMA])
})

def setup_platform(hass, config, add_entities, discover_info=None):
    """Set up the Homeworks lights."""
    controller = hass.data[HOMEWORKS_CONTROLLER]
    devs = []
    for addr,name in config.get(CONF_DIMMERS).items()
        dev = HomeworksLight(controller, addr, name)
        devs.append(dev)

    add_entitites(devs, True)
    return True

lambda TO_HOME_LEVEL(level): float((level*100.)/255.)
lambda TO_HASS_LEVEL(level): int((level * 255.)/100.)

class HomeworksLight(HomeworksDevice, Light):
    """Homeworks Light."""

    def __init__(self, controller,addr, name):
        HomeworksDevice.__init__(controller, addr,name)
        self._fadeTime = 5  # FIX: This should be an optional parameter
        self._level = None
        self._controller.cmdRequestDimmerLevel(addr) 

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS

    def turn_on(self, **kwargs):
        if ATTR_BRIGHTNESS in kwargs:
            self.brightness = kwargs[ATTR_BRIGHTNESS]
        else:
            self.brightness = 255

    def turn_off(self, **kwargs):
        self.brightness = 0

    @property
    def brightness(self):
        return self._level

    @brightness.setter(self, level):
        self._controller.fade_dim(
                TO_HOME_LEVEL(level),
                self._fadeTime,
                0, self._addr)
        self._level = level

    @property
    def device_state_attributes(self):
        return {'Homeworks Address': self._addr}

    @property
    def is_on(self):
        """Is the light on/off."""
        return self._level == 0

    def callback(self, msg_type, values):
        """Callback that processes device message."""
        if msg_type == HW_LIGHT_CHANGED:
            self._level = TO_HASS_LEVEL(values[1])
            return True
        return False
