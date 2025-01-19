"""Manages the MCP2210 device connection in separate threads using a publish-subscribe pattern."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from queue import Queue
from typing import TYPE_CHECKING, Any

from loguru import logger

from saraxsoft.manager.base import ICommManager
from saraxsoft.manager.controllers.memory import MemoryController

if TYPE_CHECKING:
    from collections.abc import Callable


class MCP2210Manager(ICommManager):
    """Manages the MCP2210 device connection in separate threads using a publish-subscribe pattern."""

    EEPROM_ADDRESS_BASE = 0x0010

    def __init__(self, serial_number: str, check_interval: float = 1.0) -> None:
        """
        Initialize the MCP2210Manager.

        Parameters
        ----------
        serial_number : str
            The serial number for the MCP2210 device.
        check_interval : float
            Interval (in seconds) between connection checks, by default 1.0.
        """
        if not serial_number:
            raise NotImplementedError("Auto-discovery not implemented. Please provide a serial number.")

        self.serial_number: str = serial_number
        self.check_interval: float = check_interval
        self.connected_pin_numbers: list[int] = []

        self.memory_controller: MemoryController | None = None
        self.connected: bool = False
        self.running: bool = False

        # Track whether each CS pin is in use for an EEPROM
        # self._device_status: dict[int, bool] = dict.fromkeys(self.connected_pin_numbers, False)

        self._connection_observers: list[Callable[[bool], None]] = []
        self._command_handlers: list[Callable[[str], None]] = []
        # self._device_status_observers: list[Callable[[int, bool], None]] = []

        # Threads
        self.monitor_thread: threading.Thread | None = None
        self.eeprom_monitor_thread: threading.Thread | None = None
        self.dispatch_thread: threading.Thread | None = None

        # Events
        self.eeprom_is_active: threading.Event = threading.Event()
        self.eeprom_is_active.clear()

        # A thread-safe queue for commands/responses (if desired):
        self._command_queue: Queue[tuple[str, dict[str, Any]]] = Queue()
        self._response_queue: Queue[tuple[str, Any]] = Queue()
        self._command_lock = threading.Lock()

    def set_connected_device_lines(self, connected_device_lines: int) -> None:
        """
        Set the number of connected device lines.

        Parameters
        ----------
        connected_device_lines : int
            The number of connected device lines.
        """
        self.connected_pin_numbers = list(range(connected_device_lines))
        # self._device_status = dict.fromkeys(self.connected_pin_numbers, False)

    def add_connection_observer(self, callback: Callable[[bool], None]) -> None:
        """
        Register a callback to be notified on connection changes.

        Parameters
        ----------
        callback : Callable[[bool], None]
            A function that accepts a single boolean argument.
        """
        self._connection_observers.append(callback)

    def add_command_handler(self, handler: Callable[[str], None]) -> None:
        """
        Register a callback to process serial commands.

        Parameters
        ----------
        handler : Callable[[str], None]
            The callback to process serial commands.
        """
        self._command_handlers.append(handler)

    # def add_device_status_observer(self, callback: Callable[[int, bool], None]) -> None:
    #     """
    #     Register a callback to be notified on device status changes.

    #     Parameters
    #     ----------
    #     callback : Callable[[int, bool], None]
    #         A function that accepts a dictionary of pin numbers and their status.
    #     """
    #     self._device_status_observers.append(callback)

    def _notify_connection_observers(self, connected: bool) -> None:
        """Notify all observers of the connection status."""
        for callback in self._connection_observers:
            callback(connected)

    # def _notify_device_status_observers(self, pin: int, connected: bool) -> None:
    #     """Notify all observers of the device status."""
    #     for callback in self._device_status_observers:
    #         callback(pin, connected)

    def start(self) -> None:
        """Start the manager: spawns threads to handle connection monitoring."""
        self.running = True

        # Monitoring thread: checks connection, tries to reconnect if disconnected
        self.monitor_thread = threading.Thread(target=self._monitor_connection, name="MonitorThread")
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    # def start_eeprom_monitor(self) -> None:
    #     """Start the EEPROM monitoring thread."""
    #     self.eeprom_monitor_thread = threading.Thread(target=self._monitor_eeprom_status, name="EEPROMMonitorThread")
    #     self.eeprom_monitor_thread.daemon = True
    #     self.eeprom_monitor_thread.start()
    #     self.eeprom_is_active.set()

    def stop(self) -> None:
        """Stop the manager: signals threads to terminate and closes device."""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        if self.eeprom_monitor_thread and self.eeprom_monitor_thread.is_alive():
            self.eeprom_monitor_thread.join(timeout=2.0)
        if self.dispatch_thread and self.dispatch_thread.is_alive():
            self.dispatch_thread.join(timeout=2.0)

        # Clean up / close device
        if self.memory_controller:
            self._handle_disconnection()

    # def stop_eeprom_monitor(self) -> None:
    #     """Stop the EEPROM monitoring thread."""
    #     self.eeprom_is_active.clear()
    #     if self.eeprom_monitor_thread and self.eeprom_monitor_thread.is_alive():
    #         self.eeprom_monitor_thread.join(timeout=2.0)

    def _monitor_connection(self) -> None:
        """Monitor the device connection and handle connection logic."""
        # Delay the initial connection attempt to allow the observers to register
        time.sleep(1.0)

        while self.running:
            if not self.connected:
                self._attempt_connection()
            else:
                self._check_connection()
            time.sleep(self.check_interval)

    def _attempt_connection(self) -> None:
        """Attempt to establish a connection to the MCP2210."""
        logger.info("Attempting to connect to MCP2210 device...")

        try:
            self.memory_controller = MemoryController(
                serial_number=self.serial_number,
                connected_pins=self.connected_pin_numbers,
            )
            # If we got here, no error was raised => connection success
            self.connected = True
            self._notify_connection_observers(self.connected)
            logger.info("MCP2210 connected.")
        except (Exception, OSError) as e:
            logger.exception(f"Failed to connect to MCP2210 device: {e}")
            self.connected = False
            self.memory_controller = None
            self._notify_connection_observers(self.connected)

    def _check_connection(self) -> None:
        """Verify that the MCP2210 is still alive."""
        if not self.memory_controller:
            self.connected = False
            self._notify_connection_observers(self.connected)
            return

        try:
            # Example: read 1 byte from address 0
            _ = self.memory_controller.read_from_eeprom(
                cs_pin=0,
                address=0,
                length=1,
            )
            # If it works, great; if it raises an error => device might be gone
        except (Exception, OSError) as e:
            logger.warning(f"Lost connection to MCP2210: {e}")
            self._handle_disconnection()

    # def _monitor_eeprom_status(self) -> None:
    #     """Monitor the status of the EEPROMs connected to the MCP2210."""
    #     while self.eeprom_is_active.is_set():
    #         if not self.memory_controller:
    #             self.connected = False
    #             self._notify_connection_observers(False)
    #             time.sleep(self.check_interval)
    #             continue

    #         for pin in self.connected_pin_numbers:
    #             old_status = self._device_status[pin]
    #             new_status = self._probe_eeprom_on_pin(pin)
    #             logger.debug(f"Pin {pin} status: {new_status}")

    #             if old_status != new_status:
    #                 self._device_status[pin] = new_status
    #                 self._notify_device_status_observers(pin, new_status)

    #         time.sleep(self.check_interval)

    # def _probe_eeprom_on_pin(self, pin: int) -> bool:
    #     """
    #     Probe the EEPROM on a specific pin.

    #     Parameters
    #     ----------
    #     pin : int
    #         The chip select pin number.

    #     Returns
    #     -------
    #     bool
    #         True if an EEPROM is connected, False otherwise.
    #     """
    #     if not self.memory_controller:
    #         return False

    #     try:
    #         read_data = self.memory_controller.read_from_eeprom(pin, self.EEPROM_ADDRESS_BASE, length=1)
    #         id_val = int.from_bytes(read_data, "big")
    #     except (Exception, OSError):
    #         return False
    #     logger.debug(f"Pin {pin} received ID value: {id_val}. Expected: {self.expected_device_values[pin - 1]}")
    #     return id_val == self.expected_device_values[pin - 1]

    def probe_single_pin(self, pin: int, expected_value: int) -> bool:
        """
        Check if EEPROM hardware on 'pin' is connected.

        Parameters
        ----------
        pin : int
            The chip select pin number.
        expected_value : int
            The expected value to be read from the EEPROM.

        Returns
        -------
        bool
            True if an EEPROM is connected, False otherwise.
        """
        if not self.connected or not self.memory_controller:
            return False

        try:
            read_data = self.memory_controller.read_from_eeprom(
                cs_pin=pin,
                address=self.EEPROM_ADDRESS_BASE,
                length=1
            )
            if not read_data:
                return False

            val = int.from_bytes(read_data, "big")

            # Dispatch the command to the command handlers
            for handler in self._command_handlers:
                handler(f"Pin {pin} received ID value: {val}. Expected: {expected_value}")
        except Exception:  # noqa: BLE001
            logger.exception(f"Failed to read from EEPROM on pin {pin}.")
            return False
        return val == expected_value

    def _handle_disconnection(self) -> None:
        """Handle the disconnection of the MCP2210 device."""
        logger.info("Closing MCP2210 device...")
        self.connected = False
        self.memory_controller = None
        self._notify_connection_observers(self.connected)
        time.sleep(self.check_interval)

    def sync_write_eeprom(self, pin: int, address: int, data: bytes) -> None:
        """
        A synchronous approach to writing. Acquire a lock, do the operation, ensure no one else is messing with the device simultaneously.

        Parameters
        ----------
        pin : int
            The chip select pin number.
        address : int
            The address to write to.
        data : bytes
            The data to write.
        """
        if not self.connected or not self.memory_controller:
            raise RuntimeError("Not connected to MCP2210 device.")

        with self._command_lock:
            try:
                self.memory_controller.write_to_eeprom(pin, address, data)
                self.memory_controller.wait_for_write_completion(pin)
            except (Exception, OSError) as e:
                logger.error(f"Write failed: {e}")
                raise

    def sync_read_eeprom(self, pin: int, address: int, length: int) -> bytes:
        """
        A synchronous approach to reading.

        Parameters
        ----------
        pin : int
            The chip select pin number.
        address : int
            The address to read from.
        length : int
            The number of bytes to read.

        Returns
        -------
        bytes
            The data read from the EEPROM.
        """
        if not self.connected or not self.memory_controller:
            raise RuntimeError("Not connected to MCP2210 device.")

        with self._command_lock:
            try:
                return self.memory_controller.read_from_eeprom(pin, address, length)
            except (Exception, OSError) as e:
                logger.error(f"Read failed: {e}")
                raise
