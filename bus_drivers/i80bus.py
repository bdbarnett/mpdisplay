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
from lib.lcd_bus import _BaseBus, Optional
from gpio_registers import GPIO_SET_CLR_REGISTERS
from uctypes import addressof
from array import array


class I80Bus(_BaseBus):
    """
    Represents an I80 bus interface for controlling GPIO pins.
    Currently only supports 8-bit data bus width and requires pin numbers instead of pin names.
    ESP32, RP2, SAMD and NRF use pin numbers and should work with this driver.
    MIMXRT and STM use pin names and will not work with this driver until pin names are supported.

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
    ) -> None:
        super().__init__()

        # Save the swap enabled setting for the base class
        self.swap_enabled = swap_color_bytes

        # Use the GPIO_SET_CLR_REGISTERS class to get the register addresses and masks
        # for the control pins and to determine the number of pins per port for
        # _setup_data_pins() and _write()
        self.gpio = GPIO_SET_CLR_REGISTERS()

        # Define the _write method
        self._use_set_clr_regs = True if self.gpio.pins_per_port == 32 else False

        # Get the masks for the control pins
        self._cs_active_mask, self._cs_inactive_mask = self.gpio.get_set_clr_masks(
            cs, cs_active_high
        )
        self._dc_data_mask, self._dc_cmd_mask = self.gpio.get_set_clr_masks(
            dc, dc_data_level
        )
        self._wr_inactive_mask, self._wr_active_mask = self.gpio.get_set_clr_masks(
            wr, pclk_active_neg
        )

        # Get the register addresses for the control pins
        self._cs_active_reg, self._cs_inactive_reg = self.gpio.get_set_clr_regs(
            cs, cs_active_high
        )
        self._dc_data_reg, self._dc_cmd_reg = self.gpio.get_set_clr_regs(
            dc, dc_data_level
        )
        self._wr_inactive_reg, self._wr_active_reg = self.gpio.get_set_clr_regs(
            wr, pclk_active_neg
        )

        # Set the control pins as outputs
        machine.Pin(dc, machine.Pin.OUT, value=not dc_data_level)
        machine.Pin(cs, machine.Pin.OUT, value=not cs_active_high)
        machine.Pin(wr, machine.Pin.OUT, value=pclk_active_neg)

        # Configure data pins as outputs, populate lookup tables and pin_masks
        self._setup_data_pins([data0, data1, data2, data3, data4, data5, data6, data7])

    def _setup_data_pins(self, pins: list[int]) -> None:
        """
        Sets output mode and creates lookup_tables and pin_masks for a list pins.
        Must be called after self.gpio is initialized.
        """
        bus_width = len(pins)
        if bus_width != 8:
            raise ValueError("bus_width must be 8")

        lut_len = 2**bus_width  # 256 for 8-bit bus width

        # Set the data pins as outputs
        for pin in pins:
            machine.Pin(pin, machine.Pin.OUT)

        pin_masks = []  # list of 32-bit pin masks, 1 per lookup table
        if self._use_set_clr_regs:
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
            if self._use_set_clr_regs:
                set_regs.append(self.gpio.set_reg(start_pin))
                clr_regs.append(self.gpio.clr_reg(start_pin))
            else:
                set_reset_regs_A.append(self.gpio.set_reset_reg(start_pin))
                set_reset_regs_B.append(self.gpio.set_reset_reg(start_pin + 16))
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
        _pin_data = array("I", [0] * 4 * self._num_luts)
        for i in range(self._num_luts):
            _pin_data[i * 4 + 0] = pin_masks[i]
            _pin_data[i * 4 + 1] = (
                set_regs[i]
                if self._use_set_clr_regs
                else set_reset_regs_A[i]
            )
            _pin_data[i * 4 + 2] = (
                clr_regs[i]
                if self._use_set_clr_regs
                else set_reset_regs_B[i]
            )
            _pin_data[i * 4 + 3] = addressof(self._lookup_tables[i])
        self._pin_data = memoryview(_pin_data)

    @micropython.native
    def tx_param(
        self, cmd: Optional[int] = None, data: Optional[memoryview] = None
    ) -> None:
        """Write to the display: command and/or data."""
        machine.mem32[self._cs_active_reg] = self._cs_active_mask  # CS Active

        if cmd is not None:
            struct.pack_into("B", self.buf1, 0, cmd)
            machine.mem32[self._dc_cmd_reg] = self._dc_cmd_mask  # DC Command
            self._write(self.buf1, 1)
        if data is not None:
            machine.mem32[self._dc_data_reg] = self._dc_data_mask  # DC Data
            self._write(data, len(data))

        machine.mem32[self._cs_inactive_reg] = self._cs_inactive_mask  # CS Inactive

    @micropython.viper
    def _write(self, data: ptr8, length: int):
        _wr_inactive_reg = ptr32(self._wr_inactive_reg)
        _wr_inactive_mask = int(self._wr_inactive_mask)
        _wr_active_reg = ptr32(self._wr_active_reg)
        _wr_active_mask = int(self._wr_active_mask)
        _use_set_clr_regs = bool(self._use_set_clr_regs)
        _pin_data = ptr32(self._pin_data)
        _num_luts = int(self._num_luts)

        last: int = -1
        for i in range(length):
            _wr_inactive_reg[0] = _wr_inactive_mask  # WR Inactive
            val = data[i]
            if val != last:
                for n in range(_num_luts):
                    pin_mask = _pin_data[n * 4 + 0]
                    if pin_mask != 0:
                        set_reg = ptr32(_pin_data[n * 4 + 1])
                        clr_reg = ptr32(_pin_data[n * 4 + 2])
                        lut = ptr32(_pin_data[n * 4 + 3])
                        tx_value: int = lut[val]
                        # if _use_set_clr_regs:
                        if True:
                            set_reg[0] = tx_value
                            clr_reg[0] = tx_value ^ pin_mask
                        else:
                            set_reg[0] = (tx_value & 0xFFFF) | ((tx_value ^ pin_mask) << 16)
                            clr_reg[0] = (tx_value >> 16) | ((tx_value ^ pin_mask) & 0xFFFF0000)
                last = val
            _wr_active_reg[0] = _wr_active_mask  # WR Active


# Example usage
# display_bus = I80Bus(
#     dc=0,
#     wr=47,
#     cs=6,
#     data0=9,
#     data1=46,
#     data2=3,
#     data3=8,
#     data4=18,
#     data5=17,
#     data6=16,
#     data7=15,
#     # freq=20000000,
#     # cmd_bits=8,
#     # param_bits=8,
#     # reverse_color_bits=False,
#     swap_color_bytes=True,
#     cs_active_high=False,
#     pclk_active_neg=False,
#     # pclk_idle_low=False,
#     # dc_idle_level=0,
#     # dc_cmd_level=0,
#     # dc_dummy_level=0,
#     dc_data_level=1,
# )
#
# display_bus.tx_param(0x36, memoryview(b'\x00\x01\x02\x03'))
