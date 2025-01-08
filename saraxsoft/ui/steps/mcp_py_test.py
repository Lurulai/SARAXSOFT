from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection

class MemoryController:
    def __init__(self, serial_number: str, cs_pin_number: int):
        self.mcp = Mcp2210(serial_number=serial_number)
        self.cs_pin_number = cs_pin_number
        self._configure_mcp_chip()

    def _configure_mcp_chip(self):
        # this only needs to happen once
        # if you don't call this, the device will use the existing settings
        self.mcp.configure_spi_timing(chip_select_to_data_delay=0,
                         last_data_byte_to_cs=0,
                         delay_between_bytes=0)
        
        self.mcp.set_gpio_designation(self.cs_pin_number, Mcp2210GpioDesignation.CHIP_SELECT)
        # set all pins as GPIO
        for i in range(1,9):
            self.mcp.set_gpio_designation(i, Mcp2210GpioDesignation.GPIO)
            self.mcp.set_gpio_direction(i, Mcp2210GpioDirection.OUTPUT)
        # self.mcp.set_gpio_output_value(1, False)
                
    def write_to_eeprom(self, address: int, data: bytes):
        write_enable_command = b'\x06'  # Write enable opcode
        self.mcp.spi_exchange(write_enable_command, self.cs_pin_number)
    
        write_command = b'\x02'  # Write opcode
        address_bytes = address.to_bytes(2, 'big')  # Convert address to 2 bytes
        payload = write_command + address_bytes + data
        self.mcp.spi_exchange(payload, self.cs_pin_number)

    def read_from_eeprom(self, address: int, length: int):
        read_command = b'\x03'  # Read opcode
        address_bytes = address.to_bytes(2, 'big')  # Convert address to 2 bytes
        payload = read_command + address_bytes + b'\x00' * length
        response = self.mcp.spi_exchange(payload, self.cs_pin_number)
        return response[-length:]
