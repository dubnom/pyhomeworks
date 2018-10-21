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
pAddress    = lambda arg: arg
pButton     = lambda arg: int(arg)
pLevel      = lambda arg: int(arg)
pLedState   = lambda arg: [ int(n) for n in arg ]
pEnabled    = lambda arg: 'enabled' == arg

NORM = lambda x: (x,pAddress,pButton)

# Callback types
HW_LIGHT_CHANGED            = 'light_changed'
HW_BUTTON_PRESSED           = 'button_pressed'
HW_BUTTON_RELEASED          = 'button_released'
HW_BUTTON_HOLD              = 'button_hold'
HW_BUTTON_DOUBLE_TAP        = 'button_double_tap'
HW_KEYPAD_LED_CHANGED       = 'keypad_led_changed'
HW_LIGHT_CHANGED            = 'light_changed'
HW_KEYPAD_ENABLE_CHANGED    = 'keypad_enable_changed'

class Homeworks(Thread):
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
        "KLS":      (HW_KEYPAD_LED_CHANGED,pAddress,pLedState),
        "DL":       (HW_LIGHT_CHANGED,pAddress,pLevel),
        "KES":      (HW_KEYPAD_ENABLE_CHANGED,pAddress,pEnabled),
    }

    def __init__(self, host, port, callback, pollingFreq=1):
        Thread.__init__(self)
        self._host = host
        self._port = port
        self._callback = callback
        self._pollingFreq = pollingFreq
        
        self._running = False
        self._connect()
        self.start()

    def _connect(self):
        # Add userID and password
        self._telnet = telnetlib.Telnet(self._host,self._port)
        # Setup interface and subscribe to events
        self._send('PROMPTOFF')     # No prompt is needed
        self._send('KBMON')         # Monitor keypad events
        self._send('GSMON')         # Monitor GRAFIKEYE scenes
        self._send('DLMON')         # Monitor dimmer levels
        self._send('KLMON')         # Monitor keypad LED states

    def _send(self,command):
        self._telnet.write((command+'\n').encode('utf8'))

    def cmdFadeDim(self,intensity,fadeTime,delayTime,addr):
        self._send('FADEDIM, %d, %d, %d, %s' % (intensity,fadeTime,delayTime,addr)

    def cmdRequestDimmerLevel(self,addr):
        self._send('RDL, %s' % addr)

    def run(self):
        self._running = True
        while self._running:
            input = self._telnet.read_until(b'\r',self._pollingFreq)
            args = input.decode('utf-8').split(', ')
            action = self._actions.get(args[0],None)
            if action and len(args) == len(action):
                pArgs = [ parser(arg) for parser,arg in zip(action[1:],args[1:]) ]
                self._callback( args[0], pArgs )

    def close(self):
        self._running = False
        if self._telnet:
            time.sleep(self._pollingFreq)
            self._telnet.close()
            self._telnet = None

