# SPDX-FileCopyrightText: 2023 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
An example implementation of an I80 bus driver written in MicroPython.
This driver is VERY slow and is only intended as an example to be rewritten in C
or have the _write method rewritten to use DMA transfers.
"""

from machine import Pin
from uctypes import addressof
from array import array
from ._basebus import BaseBus, Optional


class I80Bus(BaseBus):
    """
    Represents an I80 bus interface for controlling GPIO pins.
    Currently only supports 8-bit data bus width and requires pin numbers instead of pin names.
    ESP32, RP2, SAMD and NRF use pin numbers and should work with this driver.
    MIMXRT and STM use pin names and have not been tested.

    Args:
        dc (int): The pin number for the DC pin.
        cs (int): The pin number for the CS pin.
        wr (int): The pin number for the WR pin.
        d0 - d7 (int): The pin numbers for the data pins.
        cs_active_high (bool): True if CS is active high, False if CS is active low.
        dc_data_level (int): The level for the DC pin when sending data (1 or 0).
        pclk_active_neg (bool): True if PCLK is active low, False if PCLK is active high.
        swap_color_bytes (bool): True if the color bytes should be swapped, False otherwise.
    """

    name = "MicroPython I80Bus driver"

    def __init__(
        self,
        dc,
        cs,
        wr,
        data0,
        data1,
        data2,
        data3,
        data4,
        data5,
        data6,
        data7,
        cs_active_high=False,
        dc_data_level=1,
        pclk_active_neg=False,
        swap_color_bytes=False,
        *,
        freq=20_000_000,  # Not used; maintained for compatibility with mp_lcd_bus C driver
        cmd_bits=8,  # ditto
        param_bits=8,  # ditto
        reverse_color_bits=False,  # ditto
        pclk_idle_low=False,  # ditto
        dc_idle_level=0,  # ditto
        dc_cmd_level=0,  # ditto
        dc_dummy_level=0,  # ditto
        ) -> None:

        super().__init__()

        # Save the swap enabled setting for the base class
        self._swap_enabled = swap_color_bytes

        # Save the data pins
        pins = [data0, data1, data2, data3, data4, data5, data6, data7]

        # Check that the bus width is 8
        if len(pins) != 8:
            raise ValueError("bus width must be 8")

        # Set the data pins as outputs
        for pin in pins:
            Pin(pin, Pin.OUT)

        # Setup the control pins
        self._dc_data: bool = bool(dc_data_level)
        self._dc_cmd: bool = not self._dc_data
        self.dc: Pin = Pin(dc, Pin.OUT, value=self._dc_cmd)

        self._cs_active: bool = cs_active_high
        self._cs_inactive: bool = not self._cs_active
        self.cs: Pin = (
            Pin(cs, Pin.OUT, value=self._cs_inactive) if cs != -1 else lambda val: None
            )

        self._wr_active: bool = not pclk_active_neg
        self._wr_inactive: bool = not self._wr_active  # not used in this class, may be used in a subclass
        self.wr: Pin = Pin(wr, Pin.OUT, value=pclk_active_neg)

        self.setup(pins, wr)

    def setup(self, pins: list[int], wr: int) -> None:
        """
        Setup lookup tables and pin data for the _write method.
        """
        from ._gpio_registers import GPIO_SET_CLR_REGISTERS

        # Use the GPIO_SET_CLR_REGISTERS class to get the register addresses and masks
        # for the data pins and wr pin and to determine the number of pins per port for
        # _write().  Implemented as a local variable to allow the instance to be garbage
        # collected after setup function has completed.
        gpio = GPIO_SET_CLR_REGISTERS()

        # If self._is_32bit is True the _write method will use a 32-bit set and a 32-bit
        # clear register.  Otherwise, the _write method will use set_reset registers
        # which use the lower 16 bits for set and the upper 16 bits for clear.
        self._is_32bit = True if gpio.pins_per_port == 32 else False

        # Get the masks for the write pin
        self._wr_mask, self._wr_not_mask = gpio.get_set_clr_masks(wr, self._wr_active)
        # Get the register addresses for the write pin
        self._wr_reg, self._wr_not_reg = gpio.get_set_clr_regs(wr, self._wr_active)

        self._lookup_tables = []  # list of memoryview lookup tables
        pin_masks = []  # list of 32-bit pin masks
        regsA = []  # list of set registers if _is_32bit else set/reset registers for lower 16 pins
        regsB = []  # list of clear registers if _is_32bit else set/reset registers for upper 16 pins
        lut_len = 2**len(pins)  # Number of entries per lut -- 256 for 8-bit bus width

        # Create the pin_masks, initialize the lookup_tables and populate the 2 reg lists
        # LUT values are 32-bit, so iterate through each set of 32 pins regardless of pins_per_port
        for start_pin in range(0, max(pins), 32):
            lut_pins = [p for p in pins if p >= start_pin and p < start_pin + 32]
            pin_mask = sum([1 << (p - start_pin) for p in lut_pins]) if lut_pins else 0
            # print(f"lut pins = {lut_pins}; pin_mask = 0b{pin_mask:032b}")
            pin_masks.append(pin_mask)
            self._lookup_tables.append(array("I", [0] * lut_len) if pin_mask else None)
            if self._is_32bit:
                regsA.append(gpio.set_reg(start_pin) if pin_mask else 0)
                regsB.append(gpio.clr_reg(start_pin) if pin_mask else 0)
            else:
                regsA.append(gpio.set_reset_reg(start_pin) if pin_mask else 0)
                regsB.append(gpio.set_reset_reg(start_pin + 16) if pin_mask else 0)
        self._num_luts = len(self._lookup_tables)

        # Populate the lookup tables
        # Iterate through all possible 8-bit values (0 to 255), assumes 8-bit bus width
        for index in range(lut_len):
            # Iterate through each pin
            for bit_number, pin in enumerate(pins):
                # If the bit is set in the index
                if index & (1 << bit_number):
                    # Set the bit in the lookup table
                    value = self._lookup_tables[pin // 32][index]
                    value |= 1 << (pin % 32)
                    self._lookup_tables[pin // 32][index] = value

        if False:  # Set to True to print the lookup tables
            for i, lut in enumerate(self._lookup_tables):
                print(f"\nLookup table {i}:")
                for j in range(0, lut_len):
                    print(f"{j:03d}: 0b{lut[j]:032b}")

        # save all settings in an array pin_data for use in viper
        pin_data = array("I", [0] * 4 * self._num_luts)
        for i in range(self._num_luts):
            pin_data[i * 4 + 0] = pin_masks[i]
            pin_data[i * 4 + 1] = regsA[i]
            pin_data[i * 4 + 2] = regsB[i]
            pin_data[i * 4 + 3] = addressof(self._lookup_tables[i])
        self._pin_data = memoryview(pin_data)

    @micropython.viper
    def _write(self, data: ptr8, length: int):
        wr_not_reg = ptr32(self._wr_not_reg)
        wr_not_mask = int(self._wr_not_mask)
        wr_reg = ptr32(self._wr_reg)
        wr_mask = int(self._wr_mask)
        is_32bit = bool(self._is_32bit)
        pin_data = ptr32(self._pin_data)
        num_luts = int(self._num_luts)

        last: int = -1
        for i in range(length):
            wr_not_reg[0] = wr_not_mask  # WR Inactive
            val = data[i]
            if val != last:
                for n in range(num_luts):
                    pin_mask = pin_data[n * 4 + 0]
                    if pin_mask != 0:
                        regA = ptr32(pin_data[n * 4 + 1])
                        regB = ptr32(pin_data[n * 4 + 2])
                        lut = ptr32(pin_data[n * 4 + 3])
                        tx_value: int = lut[val]
                        # if _is_32bit:  # TODO:  Not working yet. Assume 32-bit for now.
                        if True:
                            regA[0] = tx_value
                            regB[0] = tx_value ^ pin_mask
                        else:
                            regA[0] = (tx_value & 0xFFFF) | ((tx_value ^ pin_mask) << 16)
                            regB[0] = (tx_value >> 16) | ((tx_value ^ pin_mask) & 0xFFFF0000)
                last = val
            wr_reg[0] = wr_mask  # WR Active
