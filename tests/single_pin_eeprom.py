"""test_single_eeprom.py.

Write a known byte to one SPI EEPROM on a single chip-select pin, then read it back.
Ensures basic SPI read/write is functioning.
"""

import time

from loguru import logger
from mcp2210 import Mcp2210, Mcp2210GpioDesignation

SERIAL_NUMBER = "0001757257"
CS_PIN = 0
GPIO_PINS = range(1, 9)
TEST_ADDRESS = 0x0010
TEST_BYTE_TO_WRITE = 0xA5  # Arbitrary test value


def main():
    logger.info("Connecting to MCP2210...")
    mcp = Mcp2210(serial_number=SERIAL_NUMBER)

    # 1) Configure SPI (mode, timing, etc.)
    #    Some libraries have separate calls; adapt if needed.
    mcp.configure_spi_timing(
        chip_select_to_data_delay=1,
        last_data_byte_to_cs=1,
        delay_between_bytes=0
        # Possibly set SPI mode if your library supports it:
        # spi_mode=0 for CPOL=0, CPHA=0
    )

    # 2) Mark the chosen pin as hardware chip-select
    mcp.set_gpio_designation(0, Mcp2210GpioDesignation.CHIP_SELECT)
    for pin in GPIO_PINS:
        if pin != CS_PIN:
            mcp.set_gpio_designation(pin, Mcp2210GpioDesignation.GPIO)

    # 3) Test writing & reading
    try:
        # Write Enable
        # write_enable_cmd = b"\x06"
        # mcp.spi_exchange(write_enable_cmd, CS_PIN)

        # # Write operation
        # write_cmd = b"\x02"
        # addr_bytes = TEST_ADDRESS.to_bytes(2, "big")
        # payload = write_cmd + addr_bytes + TEST_BYTE_TO_WRITE.to_bytes(1, "big")
        # mcp.spi_exchange(payload, CS_PIN)

        # # Wait for write completion
        # wait_for_write_completion(mcp, CS_PIN)

        # Now read back
        for pin in GPIO_PINS:
            read_cmd = b"\x03" + TEST_ADDRESS.to_bytes(2, "big") + b"\x00"
            response = mcp.spi_exchange(read_cmd, CS_PIN)
            read_val = response[-1]
            logger.info(f"Response: {response}")
            logger.info(f"READ BACK => 0x{read_val:02X}")

        # if read_val == TEST_BYTE_TO_WRITE:
        #     logger.info("SUCCESS: Read value matches written value.")
        # else:
        #     print("ERROR: Mismatch. Wrote 0x%02X, got 0x%02X" % (TEST_BYTE_TO_WRITE, read_val))

    finally:
        logger.info("Done. You can re-run or test another pin.")


def wait_for_write_completion(mcp: Mcp2210, cs_pin: int):
    """Poll the status register (0x05) until WIP=0."""
    status_cmd = b"\x05\x00"  # Read status + dummy
    while True:
        resp = mcp.spi_exchange(status_cmd, cs_pin)
        # resp[1] should be status register
        if not (resp[1] & 0x01):
            break
        time.sleep(0.01)


if __name__ == "__main__":
    main()
