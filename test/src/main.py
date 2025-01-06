from mcp2210 import Mcp2210, Mcp2210GpioDesignation, Mcp2210GpioDirection

mcp = Mcp2210(serial_number="0001757257")

# this only needs to happen once
# if you don't call this, the device will use the existing settings
mcp.configure_spi_timing(chip_select_to_data_delay=0,
                         last_data_byte_to_cs=0,
                         delay_between_bytes=0)

cs_pin_number = 0
mcp.set_gpio_designation(cs_pin_number, Mcp2210GpioDesignation.CHIP_SELECT)

# set all pins as GPIO
for i in range(1,9):
    mcp.set_gpio_designation(i, Mcp2210GpioDesignation.GPIO)

# set lower GPIOs to output
for i in range(1,9):
    mcp.set_gpio_direction(i, Mcp2210GpioDirection.OUTPUT)

def eeprom_write(mcp, cs_pin_number, address, data):
    write_enable_command = b'\x06'  # Write enable opcode
    mcp.spi_exchange(write_enable_command, cs_pin_number)
    
    write_command = b'\x02'  # Write opcode
    address_bytes = address.to_bytes(2, 'big')  # Convert address to 2 bytes
    payload = write_command + address_bytes + data
    mcp.spi_exchange(payload, cs_pin_number)

def eeprom_read(mcp, cs_pin_number, address, length):
    read_command = b'\x03'  # Read opcode
    address_bytes = address.to_bytes(2, 'big')  # Convert address to 2 bytes
    payload = read_command + address_bytes + b'\x00' * length
    response = mcp.spi_exchange(payload, cs_pin_number)
    return response[-length:]

number = (99).to_bytes(1, 'big')  # Convert 26 to a single byte


# Write 2 bytes to address 0x0010
eeprom_write(mcp, cs_pin_number, address=0x0010, data=number)

# Read 2 bytes from address 0x0010
data = eeprom_read(mcp, cs_pin_number, address=0x0010, length=1)
print("Read data:", data)


