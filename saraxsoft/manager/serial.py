"""Manages the Arduino serial connection in separate threads using a publish-subscribe pattern."""
from __future__ import annotations

import threading
import time
from queue import Empty, Queue
from typing import TYPE_CHECKING

import serial
import serial.tools.list_ports
from loguru import logger

from saraxsoft.manager.base import ICommManager

if TYPE_CHECKING:
    from collections.abc import Callable


class SerialManager(ICommManager):
    """Manages the Arduino serial connection in separate threads using a publish-subscribe pattern."""

    def __init__(self, serial_port: str | None = None, baudrate: int = 9600, check_interval: float = 1.0) -> None:
        """
        Initialize the SerialManager.

        Parameters
        ----------
        serial_port : str or None, optional
            The port to connect to, by default None
        baudrate : int, optional
            The baudrate of the connection, by default 9600
        check_interval : float, optional
            Interval (in seconds) between connection checks, by default 1.0
        """
        self.port: str | None = serial_port
        self.baudrate: int = baudrate
        self.serial_connection: serial.Serial | None = None
        self.connected: bool = False
        self.running: bool = False
        self.check_interval: float = check_interval

        self._connection_observers: list[Callable[[bool], None]] = []
        self._command_handlers: list[Callable[[str], None]] = []

        # Thread-safe queue for incoming commands
        self._command_queue: Queue[str] = Queue()
        # Event to signal when a PONG response is received
        self._ping_pong_event = threading.Event()
        # Unique identifier for ping commands
        self._ping_id: str | None = None

        # For sending commands and receiving responses
        self._command_response_queue: Queue[str] = Queue()
        self._command_event = threading.Event()
        self._command_lock = threading.Lock()

        # Threads
        self.monitor_thread: threading.Thread | None = None
        self.read_thread: threading.Thread | None = None
        self.dispatch_thread: threading.Thread | None = None

    def add_connection_observer(self, callback: Callable[[bool], None]) -> None:
        """
        Register a callback to be notified on connection changes.

        Parameters
        ----------
        callback : Callable[[bool], None]
            The callback to be notified.
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

    def _notify_connection_observers(self, connected: bool) -> None:
        """Notify all observers of the connection status."""
        for callback in self._connection_observers:
            callback(connected)

    def start(self) -> None:
        """Start the serial manager."""
        self.running = True

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_connection, name="MonitorThread")
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        # Start reading thread
        self.read_thread = threading.Thread(target=self._read_serial_port, name="ReadThread")
        self.read_thread.daemon = True
        self.read_thread.start()

        # Start dispatching thread
        self.dispatch_thread = threading.Thread(target=self._dispatch_commands, name="DispatchThread")
        self.dispatch_thread.daemon = True
        self.dispatch_thread.start()

    def stop(self) -> None:
        """Stop the serial manager."""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)
        if self.dispatch_thread and self.dispatch_thread.is_alive():
            self.dispatch_thread.join(timeout=2.0)

        # Close the serial connection
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

    def _monitor_connection(self) -> None:
        """Monitor the serial connection and handle connection logic."""
        while self.running:
            if not self.connected:
                self._attempt_connection()
            else:
                self._check_connection()
            time.sleep(self.check_interval)

    def _attempt_connection(self) -> None:
        """Attempt to establish a serial connection."""
        logger.info("Attempting to connect to Arduino...")

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
            self.serial_connection = serial.Serial(port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for the Arduino to reset
            self.port = port
            self.connected = True
            self._notify_connection_observers(self.connected)
            logger.info(f"Connected to Arduino on {port}.")
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino on {port}: {e}")
            return False
        return True

    def _check_connection(self) -> None:
        """Check the connection status by sending a ping and waiting for a pong."""
        if not self.serial_connection or not self.serial_connection.is_open:
            self.connected = False
            self._notify_connection_observers(self.connected)
            return

        try:
            self._ping_id = "PING_CHECK"
            self._ping_pong_event.clear()
            self.serial_connection.write(f"PING {self._ping_id}\n".encode())
            self.serial_connection.flush()

            # Wait for PONG response
            pong_received = self._ping_pong_event.wait(timeout=3)
            if not pong_received:
                logger.warning("No PONG received. Connection lost.")
                self.connected = False
                self._notify_connection_observers(self.connected)
                self.serial_connection.close()
        except (serial.SerialException, OSError) as e:
            logger.error(f"Error during connection check: {e}")
            self.connected = False
            self._notify_connection_observers(self.connected)
            self.serial_connection.close()

    def _read_serial_port(self) -> None:
        """Continuously read from the serial port and enqueue commands."""
        while self.running:
            try:
                if self.connected and self.serial_connection and self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode("utf-8").strip()
                    self._command_queue.put(line)
                else:
                    time.sleep(0.01)
            except (serial.SerialException, OSError):
                logger.error("Error reading from serial port, device not configured or disconnected.")
                self.connected = False
                self._notify_connection_observers(self.connected)

    def _dispatch_commands(self) -> None:
        """Dispatch commands from the queue to registered handlers."""
        while self.running:
            try:
                command = self._command_queue.get(timeout=0.1)
                # Handle ping/pong responses
                if command.startswith("PONG"):
                    self._ping_pong_event.set()
                    self._ping_id = None
                # Handle command responses
                elif self._command_event.is_set():
                    pass  # Command already completed
                elif self._command_lock.locked():
                    self._command_response_queue.put(command)
                    if command.startswith(("OK", "ERROR", "INPUT_STATE")):
                        self._command_event.set()
                # Dispatch command to handlers
                for handler in self._command_handlers:
                    handler(command)
            except Empty:
                continue

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

        with self._command_lock:
            self._command_event.clear()
            self._command_response_queue = Queue()
            self.serial_connection.write((command + "\n").encode("utf-8"))
            self.serial_connection.flush()

            # Collect responses until command is completed
            response_lines: list[str] = []
            command_completed = self._command_event.wait(timeout=3)
            while not self._command_response_queue.empty():
                response_lines.append(self._command_response_queue.get())

            if command_completed:
                return "\n".join(response_lines)
            logger.warning("Command timed out without a response.")
            return ""

    def _handle_disconnection(self) -> None:
        """Handle the disconnection of the serial connection."""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        self.connected = False
        self._notify_connection_observers(self.connected)
        time.sleep(self.check_interval)
