"""
Homeworks.

A partial implementation of an interface to series-4 and series-8 Lutron
Homeworks systems.

The Series4/8 is connected to an RS232 port to an Ethernet adaptor (NPort).

Michael Dubno - 2018 - New York
"""

from collections.abc import Callable
import logging
import select
import socket
import time
from threading import Thread
from typing import Any

_LOGGER = logging.getLogger(__name__)

POLLING_FREQ = 1.0


def _p_address(arg: str) -> str:
    return arg


def _p_button(arg: str) -> int:
    return int(arg)


def _p_enabled(arg: str) -> bool:
    return arg == "enabled"


def _p_level(arg: str) -> int:
    return int(arg)


def _p_ledstate(arg: str) -> list[int]:
    return [int(num) for num in arg]


def _norm(x: str) -> tuple[str, Callable[[str], str], Callable[[str], int]]:
    return (x, _p_address, _p_button)


# Callback types
HW_BUTTON_DOUBLE_TAP = "button_double_tap"
HW_BUTTON_HOLD = "button_hold"
HW_BUTTON_PRESSED = "button_pressed"
HW_BUTTON_RELEASED = "button_released"
HW_KEYPAD_ENABLE_CHANGED = "keypad_enable_changed"
HW_KEYPAD_LED_CHANGED = "keypad_led_changed"
HW_LIGHT_CHANGED = "light_changed"

ACTIONS: dict[str, tuple[str, Callable[[str], str], Callable[[str], Any]]] = {
    "KBP": _norm(HW_BUTTON_PRESSED),
    "KBR": _norm(HW_BUTTON_RELEASED),
    "KBH": _norm(HW_BUTTON_HOLD),
    "KBDT": _norm(HW_BUTTON_DOUBLE_TAP),
    "DBP": _norm(HW_BUTTON_PRESSED),
    "DBR": _norm(HW_BUTTON_RELEASED),
    "DBH": _norm(HW_BUTTON_HOLD),
    "DBDT": _norm(HW_BUTTON_DOUBLE_TAP),
    "SVBP": _norm(HW_BUTTON_PRESSED),
    "SVBR": _norm(HW_BUTTON_RELEASED),
    "SVBH": _norm(HW_BUTTON_HOLD),
    "SVBDT": _norm(HW_BUTTON_DOUBLE_TAP),
    "KLS": (HW_KEYPAD_LED_CHANGED, _p_address, _p_ledstate),
    "DL": (HW_LIGHT_CHANGED, _p_address, _p_level),
    "KES": (HW_KEYPAD_ENABLE_CHANGED, _p_address, _p_enabled),
}

IGNORED = {
    "Keypad button monitoring enabled",
    "GrafikEye scene monitoring enabled",
    "Dimmer level monitoring enabled",
    "Keypad led monitoring enabled",
}


class Homeworks(Thread):
    """Interface with a Lutron Homeworks 4/8 Series system."""

    def __init__(
        self, host: str, port: int, callback: Callable[[Any, Any], None]
    ) -> None:
        """Connect to controller using host, port."""
        Thread.__init__(self)
        self._host = host
        self._port = port
        self._callback = callback
        self._socket: socket.socket | None = None

        self._running = False
        self._connect()
        if self._socket is None:
            raise ConnectionError(f"Couldn't connect to '{host}:{port}'")
        self.start()

    def _connect(self) -> None:
        try:
            self._socket = socket.create_connection((self._host, self._port))
            # Setup interface and subscribe to events
            self._subscribe()
            _LOGGER.info("Connected to %s:%d", self._host, self._port)
        except (BlockingIOError, ConnectionError, TimeoutError):
            pass

    def _send(self, command: str) -> bool:
        _LOGGER.debug("send: %s", command)
        try:
            self._socket.send((command + "\r").encode("utf8"))  # type: ignore[union-attr]
            return True
        except (ConnectionError, AttributeError):
            self._close()
            return False

    def fade_dim(
        self, intensity: float, fade_time: float, delay_time: float, addr: str
    ) -> None:
        """Change the brightness of a light."""
        self._send(f"FADEDIM, {intensity}, {fade_time}, {delay_time}, {addr}")

    def request_dimmer_level(self, addr: str) -> None:
        """Request the controller to return brightness."""
        self._send(f"RDL, {addr}")

    def run(self) -> None:
        """Read and dispatch messages from the controller."""
        self._running = True
        data = b""
        while self._running:  # pylint: disable=too-many-nested-blocks
            if self._socket is None:
                time.sleep(POLLING_FREQ)
                self._connect()
            else:
                try:
                    readable, _, _ = select.select([self._socket], [], [], POLLING_FREQ)
                    if len(readable) != 0:
                        byte = self._socket.recv(1)
                        if byte == b"\r":
                            if len(data) > 0:
                                self._process_received_data(data)
                                data = b""
                        elif byte != b"\n":
                            data += byte
                except (ConnectionError, AttributeError):
                    _LOGGER.warning("Lost connection.")
                    self._close()
                except UnicodeDecodeError:
                    data = b""

        self._close()

    def _process_received_data(self, data_b: bytes) -> None:
        _LOGGER.debug("Raw: %s", data_b)
        try:
            data = data_b.decode("utf-8")
        except UnicodeDecodeError:
            _LOGGER.warning("Invalid data: %s", data_b)
            return
        if data in IGNORED:
            return
        try:
            raw_args = data.split(", ")
            action = ACTIONS.get(raw_args[0], None)
            if action and len(raw_args) == len(action):
                args = [parser(arg) for parser, arg in zip(action[1:], raw_args[1:])]
                self._callback(action[0], args)
            else:
                _LOGGER.warning("Not handling: %s", raw_args)
        except ValueError:
            _LOGGER.warning("Weird data: %s", data)

    def close(self) -> None:
        """Close the connection to the controller."""
        self._running = False
        self._close()

    def _close(self) -> None:
        """Close the connection to the controller."""
        if self._socket:
            time.sleep(POLLING_FREQ)
            self._socket.close()
            self._socket = None

    def _subscribe(self) -> None:
        # Setup interface and subscribe to events
        self._send("PROMPTOFF")  # No prompt is needed
        self._send("KBMON")  # Monitor keypad events
        self._send("GSMON")  # Monitor GRAFIKEYE scenes
        self._send("DLMON")  # Monitor dimmer levels
        self._send("KLMON")  # Monitor keypad LED states
