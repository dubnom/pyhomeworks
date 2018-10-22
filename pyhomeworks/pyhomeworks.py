"""
Homeworks is a partial implementation of an interface to Lutron Homeworks
Series4 and Series8 systems.

The Series4/8 is connected to an RS232 port to an Ethernet adaptor (NPort)
and uses the telnet protocol for communication.

Michael Dubno - 2018 - New York
"""

from threading import Thread
import time
import telnetlib

POLLING_FREQ = 1.

# Response parsers
P_ADDRESS = lambda arg: arg
P_BUTTON = lambda arg: int(arg)
P_ENABLED = lambda arg: arg == 'enabled'
P_LEVEL = lambda arg: int(arg)
P_LEDSTATE = lambda arg: [int(n) for n in arg]

NORM = lambda x: (x, P_ADDRESS, P_BUTTON)

# Callback types
HW_BUTTON_DOUBLE_TAP = 'button_double_tap'
HW_BUTTON_HOLD = 'button_hold'
HW_BUTTON_PRESSED = 'button_pressed'
HW_BUTTON_RELEASED = 'button_released'
HW_KEYPAD_ENABLE_CHANGED = 'keypad_enable_changed'
HW_KEYPAD_LED_CHANGED = 'keypad_led_changed'
HW_LIGHT_CHANGED = 'light_changed'

class Homeworks(Thread):
    """Interface with a Lutron Homeworks 4/8 Series system."""
    _actions = {
        "KBP":      NORM(HW_BUTTON_PRESSED),
        "KBR":      NORM(HW_BUTTON_RELEASED),
        "KBH":      NORM(HW_BUTTON_HOLD),
        "KBDT":     NORM(HW_BUTTON_DOUBLE_TAP),
        "DBP":      NORM(HW_BUTTON_PRESSED),
        "DBR":      NORM(HW_BUTTON_RELEASED),
        "DBH":      NORM(HW_BUTTON_HOLD),
        "DBDT":     NORM(HW_BUTTON_DOUBLE_TAP),
        "SVBP":     NORM(HW_BUTTON_PRESSED),
        "SVBR":     NORM(HW_BUTTON_RELEASED),
        "SVBH":     NORM(HW_BUTTON_HOLD),
        "SVBDT":    NORM(HW_BUTTON_DOUBLE_TAP),
        "KLS":      (HW_KEYPAD_LED_CHANGED, P_ADDRESS, P_LEDSTATE),
        "DL":       (HW_LIGHT_CHANGED, P_ADDRESS, P_LEVEL),
        "KES":      (HW_KEYPAD_ENABLE_CHANGED, P_ADDRESS, P_ENABLED),
    }

    def __init__(self, host, port, callback):
        Thread.__init__(self)
        self._host = host
        self._port = port
        self._callback = callback
        self._telnet = None

        self._running = False
        self._connect()
        self.start()

    def _connect(self):
        # Add userID and password
        self._telnet = telnetlib.Telnet(self._host, self._port)
        # Setup interface and subscribe to events
        self._send('PROMPTOFF')     # No prompt is needed
        self._send('KBMON')         # Monitor keypad events
        self._send('GSMON')         # Monitor GRAFIKEYE scenes
        self._send('DLMON')         # Monitor dimmer levels
        self._send('KLMON')         # Monitor keypad LED states

    def _send(self, command):
        self._telnet.write((command+'\n').encode('utf8'))

    def fade_dim(self, intensity, fade_time, delay_time, addr):
        """Change the brightness of a light."""
        self._send('FADEDIM, %d, %d, %d, %s' % \
                (intensity, fade_time, delay_time, addr))

    def request_dinner_level(self, addr):
        """Request the controller to return brightness."""
        self._send('RDL, %s' % addr)

    def run(self):
        self._running = True
        while self._running:
            data = self._telnet.read_until(b'\r', POLLING_FREQ)
            raw_args = data.decode('utf-8').split(', ')
            action = self._actions.get(raw_args[0], None)
            if action and len(raw_args) == len(action):
                args = [parser(arg) for parser, arg in zip(action[1:], raw_args[1:])]
                self._callback(args[0], args)

    def close(self):
        """Close the connection to the controller."""
        self._running = False
        if self._telnet:
            time.sleep(POLLING_FREQ)
            self._telnet.close()
            self._telnet = None
