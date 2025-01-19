"""Memory controller module."""

from __future__ import annotations

from mcp2210 import Mcp2210, Mcp2210GpioDesignation


class MemoryController:
    """Controller for the EEPROM memory on the MCP2210."""

    def __init__(self, serial_number: str, connected_pins: list[int]) -> None:
        """
        Initialize the MemoryController.

        Parameters
        ----------
        serial_number : str
            The serial number of the MCP2210 device.
        connected_pins : list[int]
            The list of connected pins.
        """
        self.mcp = Mcp2210(serial_number=serial_number)
        self.connected_pins = connected_pins
        self._configure_mcp_chip()

    def _configure_mcp_chip(self) -> None:
        """Configure the MCP2210 chip for SPI communication."""
        self.mcp.configure_spi_timing(
            chip_select_to_data_delay=1,
            last_data_byte_to_cs=1,
            delay_between_bytes=0,
        )
        self.mcp.set_spi_mode(3)
        # set all pins as GPIO
        for pin in self.connected_pins:
            self.mcp.set_gpio_designation(pin, Mcp2210GpioDesignation.GPIO)

    def wait_for_write_completion(self, cs_pin: int) -> None:
        """Wait for the write operation to complete."""
        status_command = b"\x05"  # Status register read opcode (commonly used)
        while True:
            status_response = self.mcp.spi_exchange(
                status_command + b"\x00", cs_pin
            )
            if not (status_response[1] & 0x01):  # bit 0 => Write-In-Progress
                break

    def _select_pin(self, cs_pin: int) -> None:
        """
        Select the chip select pin.

        Parameters
        ----------
        cs_pin : int
            The chip select pin number.
        """
        self.mcp.set_gpio_designation(cs_pin, Mcp2210GpioDesignation.CHIP_SELECT)
        for pin in self.connected_pins:
            if pin != cs_pin:
                self.mcp.set_gpio_designation(pin, Mcp2210GpioDesignation.GPIO)

    def write_to_eeprom(self, cs_pin: int, address: int, data: bytes) -> None:
        """
        Write data to the EEPROM.

        Parameters
        ----------
        cs_pin : int
            The chip select pin number.
        address : int
            The address to write to.
        data : bytes
            The data to write.
        """
        self._select_pin(cs_pin)
        write_enable_command = b"\x06"  # Write enable opcode
        self.mcp.spi_exchange(write_enable_command, cs_pin)

        write_command = b"\x02"  # Write opcode
        address_bytes = address.to_bytes(2, "big")  # 2 bytes address
        payload = write_command + address_bytes + data
        self.mcp.spi_exchange(payload, cs_pin)

    def read_from_eeprom(self, cs_pin: int, address: int, length: int) -> bytes:
        """
        Read data from the EEPROM.

        Parameters
        ----------
        cs_pin : int
            The chip select pin number.
        address : int
            The address to read from.
        length : int
            The number of bytes to read.

        Returns
        -------
        bytes
            The read data.
        """
        self._select_pin(cs_pin)
        read_command = b"\x03"  # Read opcode
        address_bytes = address.to_bytes(2, "big")
        payload = read_command + address_bytes + b"\x00" * length
        response = self.mcp.spi_exchange(payload, cs_pin)
        return response[-length:]
