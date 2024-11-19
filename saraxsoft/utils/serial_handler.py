"""Serial handler to communicate with external devices."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import serial
from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Generator


class SerialHandler:
    def __init__(self, port: str, baud_rate: int) -> None:
        """
        Initialize the SerialHandler.

        Parameters
        ----------
        port : str
            The port the device is connected to.
        baud_rate : int
            The baud rate to use for the serial device.
        """
        self.ser = serial.Serial(port, baud_rate, timeout=1)
        self.thread = threading.Thread(target=self.read_serial)
        self.thread.daemon = True

    def start(self) -> None:
        """Start a new thread to read the data input."""
        self.thread.start()

    def read_serial(self) -> Generator[str, None, None]:
        """
        Read the serial data from the device.

        Yields
        ------
        Generator[str, None, None]
            Generator that returns the data read from the serial port.
        """
        while True:
            try:
                line = self.ser.readline().decode("utf-8").rstrip()
                yield line
            except serial.SerialException as e:
                logger.error(f"Serial error: {e}")
                yield ""
