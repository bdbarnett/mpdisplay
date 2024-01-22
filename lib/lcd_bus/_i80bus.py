# SPDX-FileCopyrightText: 2023 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
An example implementation of an I80 bus driver written in MicroPython.
This driver is VERY slow and is only intended as an example to be rewritten in C
or have the _write method rewritten to use DMA transfers.
"""

import machine
import struct
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
        freq=20_000_000,  # Not used; maintained for compatibility with lcd_bus C driver
        cmd_bits=8,  # ditto
        param_bits=8,  # ditto
        reverse_color_bits=False,  # ditto
        pclk_idle_low=False,  # ditto
        dc_idle_level=0,  # ditto
        dc_cmd_level=0,  # ditto
        dc_dummy_level=0,  # ditto
        ) -> None:

        super().__init__()
        from ._gpio_registers import GPIO_SET_CLR_REGISTERS

        # Save the swap enabled setting for the base class
        self._swap_enabled = swap_color_bytes

        # Use the GPIO_SET_CLR_REGISTERS class to get the register addresses and masks
        # for the control pins and to determine the number of pins per port for
        # _setup_data_pins() and _write().  Implemented as a local variable to allow
        # the instance to be garbage collected after initialization.
        gpio = GPIO_SET_CLR_REGISTERS()

        # Define the _write method
        # If self._is_32bit is True, then the _write method will use a 32-bit set and 
        # a 32-bit clear register.  Otherwise, the _write method will use set_reset registers
        # which use the lower 16 bits for set and the upper 16 bits for clear.
        self._is_32bit = True if gpio.pins_per_port == 32 else False

        # Get the masks for the control pins
        self._cs_mask, self._cs_not_mask = gpio.get_set_clr_masks(cs, cs_active_high)
        self._dc_data_mask, self._dc_cmd_mask = gpio.get_set_clr_masks(dc, dc_data_level)
        self._wr_not_mask, self._wr_mask = gpio.get_set_clr_masks(wr, pclk_active_neg)

        # Get the register addresses for the control pins
        self._cs_reg, self._cs_not_reg = gpio.get_set_clr_regs(cs, cs_active_high)
        self._dc_data_reg, self._dc_cmd_reg = gpio.get_set_clr_regs(dc, dc_data_level)
        self._wr_not_reg, self._wr_reg = gpio.get_set_clr_regs(wr, pclk_active_neg)

        # Set the control pins as outputs
        machine.Pin(dc, machine.Pin.OUT, value=not dc_data_level)
        machine.Pin(cs, machine.Pin.OUT, value=not cs_active_high)
        machine.Pin(wr, machine.Pin.OUT, value=pclk_active_neg)

        # Configure data pins as outputs, populate lookup tables and pin_masks
        pins = [data0, data1, data2, data3, data4, data5, data6, data7]

        # Check that the bus width is 8
        if len(pins) != 8:
            raise ValueError("bus width must be 8")
        lut_len = 2**len(pins)  # 256 for 8-bit bus width

        # Set the data pins as outputs
        for pin in pins:
            machine.Pin(pin, machine.Pin.OUT)

        pin_masks = []  # list of 32-bit pin masks, 1 per lookup table
        if self._is_32bit:
            set_regs = []  # list of 32-bit set registers, 1 per lookup table
            clr_regs = []  # list of 32-bit clear registers, 1 per lookup table
        else:
            set_reset_regs_A = []  # list of 32-bit set/reset registers, 1 per lookup table
            set_reset_regs_B = []  # list of 32-bit set/reset registers, 1 per lookup table
        self._lookup_tables = []  # list of memoryview lookup tables

        # Create the pin_masks and initialize the lookup_tables
        # LUT values are 32-bit, so iterate through each set of 32 pins regardless of pins_per_port
        for start_pin in range(0, max(pins), 32):
            lut_pins = [p for p in pins if p >= start_pin and p < start_pin + 32]
            pin_mask = sum([1 << (p - start_pin) for p in lut_pins]) if lut_pins else 0
            # print(f"lut pins = {lut_pins}; pin_mask = 0b{pin_mask:032b}")
            pin_masks.append(pin_mask)
            if self._is_32bit:
                set_regs.append(gpio.set_reg(start_pin))
                clr_regs.append(gpio.clr_reg(start_pin))
            else:
                set_reset_regs_A.append(gpio.set_reset_reg(start_pin))
                set_reset_regs_B.append(gpio.set_reset_reg(start_pin + 16))
            self._lookup_tables.append(array("I", [0] * lut_len) if pin_mask else None)

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

        self._num_luts = len(self._lookup_tables)

        # for i, lut in enumerate(self._lookup_tables):
        #     print(f"Lookup table {i}:")
        #     for j in range(0, lut_len):
        #         print(f"{j:03d}: 0b{lut[j]:032b}")

        # save all settings in an array for use in viper
        pin_data = array("I", [0] * 4 * self._num_luts)
        for i in range(self._num_luts):
            pin_data[i * 4 + 0] = pin_masks[i]
            pin_data[i * 4 + 1] = (
                set_regs[i]
                if self._is_32bit
                else set_reset_regs_A[i]
            )
            pin_data[i * 4 + 2] = (
                clr_regs[i]
                if self._is_32bit
                else set_reset_regs_B[i]
            )
            pin_data[i * 4 + 3] = addressof(self._lookup_tables[i])
        self._pin_data = memoryview(pin_data)

    @micropython.native
    def tx_param(
        self, cmd: Optional[int] = None, data: Optional[memoryview] = None
        ) -> None:
        """Write to the display: command and/or data."""
        machine.mem32[self._cs_reg] = self._cs_mask  # CS Active

        if cmd is not None:
            struct.pack_into("B", self.buf1, 0, cmd)
            machine.mem32[self._dc_cmd_reg] = self._dc_cmd_mask  # DC Command
            self._write(self.buf1, 1)
        if data is not None:
            machine.mem32[self._dc_data_reg] = self._dc_data_mask  # DC Data
            self._write(data, len(data))

        machine.mem32[self._cs_not_reg] = self._cs_not_mask  # CS Inactive

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
