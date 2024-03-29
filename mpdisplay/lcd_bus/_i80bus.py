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

    If pins are sequential and on the same port, the driver will write data directly to the
    GPIO registers.  If the pins are not sequential or are on different ports, the driver will
    use lookup tables to write data to the GPIO registers.

    :param dc: The pin number for the DC pin.
    :type dc: int
    :param cs: The pin number for the CS pin.
    :type cs: int
    :param wr: The pin number for the WR pin.
    :type wr: int
    :param d0: The pin number for the data pin 0.
    :type d0: int
    :param d1: The pin number for the data pin 1.
    :type d1: int
    :param d2: The pin number for the data pin 2.
    :type d2: int
    :param d3: The pin number for the data pin 3.
    :type d3: int
    :param d4: The pin number for the data pin 4.
    :type d4: int
    :param d5: The pin number for the data pin 5.
    :type d5: int
    :param d6: The pin number for the data pin 6.
    :type d6: int
    :param d7: The pin number for the data pin 7.
    :type d7: int
    :param cs_active_high: True if CS is active high, False if CS is active low.
    :type cs_active_high: bool
    :param dc_data_level: The level for the DC pin when sending data (1 or 0).
    :type dc_data_level: int
    :param pclk_active_neg: True if PCLK is active low, False if PCLK is active high.
    :type pclk_active_neg: bool
    :param swap_color_bytes: True if the color bytes should be swapped, False otherwise.
    :type swap_color_bytes: bool
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
        freq=20_000_000,  # Not used in this class; passed as an argument to _setup() for subclasses like _i80bus_rp2.py
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

        # Check to see if pins are sequential and all on the same port:
#         if all(pins[i] + 1 == pins[i + 1] for i in range(len(pins) - 1)) and \
#                 pins[0] // 32 == pins[-1] // 32:
#             # Use sequential mode
#             self._setup_seq(pins, wr, freq)
#         else:
            # Use LUT mode
        self._setup_lut(pins, wr, freq)

    def _setup_lut(self, pins: list[int], wr: int, freq: int) -> None:
        """
        Setup lookup tables and pin data for the _write method.
        """
        print("Using LUT mode")
        self._write = self._write_lut
        from ._gpio_registers import GPIO_SET_CLR_REGISTERS

        # Use the GPIO_SET_CLR_REGISTERS class to get the register addresses and masks
        # for the data pins and wr pin and to determine the number of pins per port for
        # _write().  Implemented as a local variable to allow the instance to be garbage
        # collected after _setup function has completed.
        gpio = GPIO_SET_CLR_REGISTERS()

        # If self._is_32bit is True the _write method will use a 32-bit set and a 32-bit
        # clear register.  Otherwise, the _write method will use set_reset registers
        # which use the lower 16 bits for set and the upper 16 bits for clear.
        self._is_32bit = True if gpio.pins_per_port == 32 else False

        # Get the masks for the write pin
        self._wr_mask, self._wr_not_mask = gpio.get_set_clr_masks(wr, self._wr_active)
        # Get the register addresses for the write pin
        self._wr_reg, self._wr_not_reg = gpio.get_set_clr_regs(wr, self._wr_active)
        if False:  # Set to True to print the write pin registers and masks
            print(f"Write pin\n {self._wr_reg=:#08x}, {self._wr_mask=:#032b}\n {self._wr_not_reg=:#08x}, {self._wr_not_mask=:#032b}\n")

        # Setup the data for pin_data and the lookup tables
        self._lookup_tables = []  # list of bytearray lookup tables
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

        # save all settings in an array pin_data for use in viper
        pin_data = array("I", [0] * 4 * self._num_luts)
        for i in range(self._num_luts):
            pin_data[i * 4 + 0] = pin_masks[i]
            pin_data[i * 4 + 1] = regsA[i]
            pin_data[i * 4 + 2] = regsB[i]
            pin_data[i * 4 + 3] = addressof(self._lookup_tables[i])
            if False:  # Set to True to print the lookup tables
                print(f"\nLUT {i}: mask={pin_masks[i]:#032b}, {regsA[i]=:#08x}, {regsB[i]=:#08x}")
                for j in range(0, lut_len):
                    print(f"       {j:3d}: {self._lookup_tables[i][j]:#032b}")
        self._pin_data = memoryview(pin_data)

    def _setup_seq(self, pins: list[int], wr: int, freq: int) -> None:
        """
        Setup pin data for the _write method.
        """
        print("Using sequential mode")
        self._write = self._write_seq
        from ._gpio_registers import GPIO_SET_CLR_REGISTERS

        # Use the GPIO_SET_CLR_REGISTERS class to get the register addresses and masks
        # for the data pins and wr pin and to determine the number of pins per port for
        # _write().  Implemented as a local variable to allow the instance to be garbage
        # collected after this function has completed.
        gpio = GPIO_SET_CLR_REGISTERS()

        # If self._is_32bit is True the _write method will use a 32-bit set and a 32-bit
        # clear register.  Otherwise, the _write method will use set_reset registers
        # which use the lower 16 bits for set and the upper 16 bits for clear.
        self._is_32bit = True if gpio.pins_per_port == 32 else False

        # Get the masks for the write pin
        self._wr_mask, self._wr_not_mask = gpio.get_set_clr_masks(wr, self._wr_active)
        # Get the register addresses for the write pin
        self._wr_reg, self._wr_not_reg = gpio.get_set_clr_regs(wr, self._wr_active)

        # Setup the data for pin_data
        start_pin = pins[0]
        pin_mask = sum([1 << (p - start_pin) for p in pins]) << (start_pin % 32)
        if self._is_32bit:
            regA = gpio.set_reg(start_pin)
            regB = gpio.clr_reg(start_pin)
        else:
            regA = gpio.set_reset_reg(start_pin)
            regB = gpio.set_reset_reg(start_pin + 16)
        shift = start_pin % 32

        # save all settings in an array pin_data for use in viper
        pin_data = array("I", [0] * 4)
        pin_data[0] = pin_mask
        pin_data[1] = regA
        pin_data[2] = regB
        pin_data[3] = shift
        self._pin_data = memoryview(pin_data)

    @micropython.viper
    def _write_lut(self, data: ptr8, length: int):
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

    @micropython.viper
    def _write_seq(self, data: ptr8, length: int):
        wr_not_reg = ptr32(self._wr_not_reg)
        wr_not_mask = int(self._wr_not_mask)
        wr_reg = ptr32(self._wr_reg)
        wr_mask = int(self._wr_mask)
        is_32bit = bool(self._is_32bit)
        pin_data = ptr32(self._pin_data)

        pin_mask = pin_data[0]
        regA = ptr32(pin_data[1])
        regB = ptr32(pin_data[2])
        shift = pin_data[3]

        last: int = -1
        for i in range(length):
            wr_not_reg[0] = wr_not_mask  # WR Inactive
            val = data[i]
            if val != last:
                tx_value: int = val << shift
                # if _is_32bit:  # TODO:  Not working yet. Assume 32-bit for now.
                if True:
                    regA[0] = tx_value
                    regB[0] = tx_value ^ pin_mask
                else:
                    regA[0] = (tx_value & 0xFFFF) | ((tx_value ^ pin_mask) << 16)
                    regB[0] = (tx_value >> 16) | ((tx_value ^ pin_mask) & 0xFFFF0000)
                last = val
            wr_reg[0] = wr_mask  # WR Active
