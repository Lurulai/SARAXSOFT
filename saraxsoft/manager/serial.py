from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

import serial
import serial.tools.list_ports
from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable


class SerialManager:
    """Manages the Arduino serial connection in a separate thread."""

    def __init__(self, port: str | None = None, baudrate: int = 9600) -> None:
        """
        Initialize the SerialManager.

        Parameters
        ----------
        port : str or None, optional
            The port to connect to, by default None
        baudrate : int, optional
            The baudrate of the connection, by default 9600
        """
        self.port: str | None = port
        self.baudrate: int = baudrate
        self.serial_connection: serial.Serial | None = None
        self.connected: bool = False
        self.running: bool = False
        self._observers: list[Callable[[bool], None]] = []

        # Threshold for state changes
        self._connection_change_threshold: int = 3  # Number of checks before state change is confirmed
        self._connection_change_counter: int = 0
        self._last_known_state: bool = False

    def add_observer(self, callback: Callable[[bool], None]) -> None:
        """
        Register a callback to be notified on connection changes.

        Parameters
        ----------
        callback : Callable[[bool], None]
            The callback to be notified.
        """
        self._observers.append(callback)

    def _notify_observers(self, connected: bool) -> None:
        """Notify all observers of the connection status."""
        for callback in self._observers:
            callback(connected)

    def start(self) -> None:
        """Start the connection thread."""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_connection)
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> None:
        """Stop the connection thread."""
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

    def _monitor_connection(self) -> None:
        """Monitor the serial connection."""
        while self.running:
            try:
                # Handle connection logic
                if not self.connected:
                    self._attempt_connection()
                elif self.serial_connection and self.serial_connection.is_open:
                    self._check_connection()
                else:
                    self._handle_disconnection()
            except serial.SerialException:
                self._handle_serial_exception()

            # Track connection state changes
            if self.connected != self._last_known_state:
                # Increment counter only if state has changed
                self._connection_change_counter += 1

                # Confirm sustained change
                if self._connection_change_counter >= self._connection_change_threshold:
                    self._last_known_state = self.connected
                    self._connection_change_counter = 0
                    self._notify_observers(self.connected)
            else:
                # Reset counter only if state is stable for this iteration
                self._connection_change_counter = 0

            time.sleep(1)

    def _check_connection(self) -> None:
        """Check the connection status."""
        if not self.serial_connection or not self.serial_connection.is_open:
            self.connected = False
            return

        try:
            self.serial_connection.write(b"PING 1\n")
            self.serial_connection.flush()
            response = self.serial_connection.readline().decode("utf-8").strip()
            if response == "PONG":
                self.connected = True
            else:
                self.connected = False
        except serial.SerialException as e:
            self._handle_disconnection()
            logger.error(f"Serial error: {e}")
        except OSError as e:
            self._handle_disconnection()
            logger.error(f"OS error: Bad file descriptor during serial operation: {e}")

    def _attempt_connection(self) -> None:
        """Attempt to establish a serial connection."""
        if self.port is None:
            self._find_and_connect()
        else:
            self._connect_to_port(self.port)

    def _find_and_connect(self) -> None:
        """Find and connect to an available serial port."""
        ports = serial.tools.list_ports.comports()
        for port_info in ports:
            if self._connect_to_port(port_info.device):
                break

    def _connect_to_port(self, port: str) -> bool:
        """Attempt to connect to a specific port."""
        logger.info(f"Attempting to connect to Arduino on {port}...")
        try:
            self.serial_connection = serial.Serial(port, self.baudrate, timeout=3)
            time.sleep(2)  # Wait for the Arduino to reset
            # Read initial messages from Arduino if any
            if self.serial_connection.in_waiting:
                init_msg = self.serial_connection.readline().decode("utf-8").strip()
                logger.info(f"Received on connect: {init_msg}")

            logger.info(f"Connected to Arduino on {port}.")
            self.port = port
            self.connected = True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino on {port}: {e}")
            return False
        return True

    def _handle_disconnection(self) -> None:
        """Handle the disconnection of the serial connection."""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        self.connected = False
        time.sleep(1)

    def _handle_serial_exception(self) -> None:
        """Handle exceptions that occur during serial operations."""
        if self.connected:
            self.connected = False

    def send_command(self, command: str) -> str:
        """
        Send a command to the Arduino and return the response.

        Parameters
        ----------
        command : str
            The command to send.

        Returns
        -------
        str
            The response from the Arduino.
        """
        if not self.connected or not self.serial_connection:
            raise serial.SerialException("Not connected to any serial device.")

        try:
            self.serial_connection.write((command + "\n").encode("utf-8"))
            self.serial_connection.flush()

            # Read response
            start_time = time.time()
            response_lines: list[str] = []
            while time.time() - start_time < 3:  # noqa: PLR2004
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode("utf-8").strip()
                    response_lines.append(line)
                    # Break if we get an "OK" or an error message
                    if line.startswith(("OK", "ERROR", "INPUT_STATE")) or line == "PONG":
                        break
                else:
                    time.sleep(0.1)
            if response_lines:
                return "\n".join(response_lines)
            logger.warning("No response received from Arduino.")
        except serial.SerialException as e:
            self._handle_disconnection()
            logger.error(f"Serial error: {e}")
        return ""
