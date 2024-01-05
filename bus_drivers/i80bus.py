import micropython
import machine
import struct
import sys
from lib.lcd_bus import _BaseBus, Optional
from gpio_registers import GPIO_SET_CLR_REGISTERS
from time import sleep_us


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

    Raises:
        NotImplementedError: If the platform is not supported.

    Attributes:

    """

    name = "MicroPython I80Bus driver"

    def __init__(self, dc, cs, wr, data0, data1, data2, data3, data4, data5, data6, data7, cs_active_high=False, dc_data_level=1, pclk_active_neg=False, swap_color_bytes=False) -> None:
        super().__init__()
        
        # Save the swap enabled setting for the base class
        self.swap_enabled = swap_color_bytes

        # Use the GPIO_SET_CLR_REGISTERS class to get the register addresses and masks
        # for the control pins and to determine the number of pins per port for
        # _setup_data_pins() and _write()
        self.gpio=GPIO_SET_CLR_REGISTERS()

        # Configure data pins as outputs, populate lookup tables, pin_masks and tx_values
        self._setup_data_pins([data0, data1, data2, data3, data4, data5, data6, data7])

        # Define the _write method
        self._use_set_clr_regs = True if self.gpio.pins_per_port == 32 else False
        self._last = None  # Integer used in _write method to determine if the value has changed

        # Create the control pins as outputs
        self._pin_dc = machine.Pin(dc, machine.Pin.OUT, value=not dc_data_level)
        self._pin_cs = machine.Pin(cs, machine.Pin.OUT, value=not cs_active_high)
        self._pin_wr = machine.Pin(wr, machine.Pin.OUT, value=pclk_active_neg)

        # Get the masks for the control pins
        self._mask_cs_active, self._mask_cs_inactive = self.gpio.get_set_clr_masks(cs, cs_active_high)
        self._mask_dc_data, self._mask_dc_cmd = self.gpio.get_set_clr_masks(dc, dc_data_level)
        self._mask_wr_active, self._mask_wr_inactive = self.gpio.get_set_clr_masks(wr, pclk_active_neg)

        # Get the register addresses for the control pins
        self._cs_active_reg, self._cs_inactive_reg = self.gpio.get_set_clr_regs(cs, cs_active_high)
        self._dc_data_reg, self._dc_cmd_reg = self.gpio.get_set_clr_regs(dc, dc_data_level)
        self._wr_active_reg, self._wr_inactive_reg = self.gpio.get_set_clr_regs(wr, pclk_active_neg)

    def _setup_data_pins(self, pins: list[int]) -> None:
        """
        Sets output mode and creates lookup_tables, pin_masks and tx_values for a list pins.
        Must be called after self.gpio is initialized.
        """
        bus_width = len(pins)
        if bus_width != 8:
            raise ValueError("bus_width must be 8")
        
        lut_entries = 2 ** bus_width  # 256 for 8-bit bus width

        # Set the data pins as outputs
        for pin in pins:
            machine.Pin(pin, machine.Pin.OUT)

        self._pin_masks = []
        self._lookup_tables = []
        self._tx_values = []
        if self.gpio.pins_per_port == 32:
            self._set_regs = []
            self._clr_regs = []
        else:
            self._set_reset_regs = []

        # Create the pin_masks and tx_values; initialize the lookup_tables
        lut = 0  # Used only in the print statement below.  Can be removed.
        # LUT values are 32-bit, so iterate through each set of 32 pins regardless of pins_per_port
        for start_pin in range(0, max(pins), 32):
            lut_pins = [p for p in pins if p >= start_pin and p < start_pin + 32]
            pin_mask = sum([1 << (pin - start_pin) for pin in lut_pins]) if lut_pins else 0
            self._pin_masks.append(pin_mask)
            print(f"lut {lut}: pins = {lut_pins.sort().reverse()}; pin_mask = 0b{pin_mask:032b}")
            self._lookup_tables.append([0] * lut_entries if pin_mask else None)
            self._tx_values.append(0)  # Used in _write method
            if self.gpio.pins_per_port == 32:
                self._set_regs.append(self.gpio.set_reg(start_pin))
                self._clr_regs.append(self.gpio.clr_reg(start_pin))
            else:
                self._set_reset_regs.append([self.gpio.set_reset_reg(start_pin), self.gpio.set_reset_reg(start_pin+16)])
            lut += 1
        print(f"pins = {pins.sort().reverse()}")
        print(f"pin_masks = {self._pin_masks.reverse()}")

        # Populate the lookup tables
        # Iterate through all possible 8-bit values (0 to 255), assumes 8-bit bus width
        for index in range(lut_entries):
            # Iterate through each pin
            for bit_number, pin in enumerate(pins):
                # If the bit is set in the index
                if index & (1 << bit_number):
                    # Set the bit in the lookup table
                    self._lookup_tables[pin // 32][index] |= (1 << (pin % 32))
        print(f"lookup_tables = {self._lookup_tables}")

    @micropython.native
    def tx_param(self, cmd: Optional[int] = None, data: Optional[memoryview] = None) -> None:
        """Write to the display: command and/or data."""
#        machine.mem32[self._cs_active_reg] = self._mask_cs_active  # CS Active
        self._pin_cs(0)

        if cmd is not None:
            struct.pack_into("B", self.buf1, 0, cmd)
#            machine.mem32[self._dc_cmd_reg] = self._mask_dc_cmd  # DC Command
            self._pin_dc(0)
            self._write(self.buf1)
        if data is not None:
#            machine.mem32[self._dc_data_reg] = self._mask_dc_data  # DC Data
            self._pin_dc(1)
            self._write(data)

#        machine.mem32[self._cs_inactive_reg] = self._mask_cs_inactive  # CS Inactive
        self._pin_cs(1)

    @micropython.native
    def _write(self, data: memoryview) -> None:
        """
        Writes data to the I80 bus interface.

        Args:
            data (memoryview): The data to be written.
        """
        for i in range(len(data)):
            value = data[i]   # 8-bit value (bus_width = 8)
#            machine.mem32[self._wr_inactive_reg] = self._mask_wr_inactive  # WR Inactive
            self._pin_wr(0)
            if value != self._last:  # No need to set the data pins again if the value hasn't changed
                # Iterate through each lookup table
                for i, lut in enumerate(self._lookup_tables):
                    # If the pin_mask is not 0
                    if self._pin_masks[i]:
                        # Lookup the value in the table
                        self._tx_values[i] = lut[value]  # 32-bit value
                        if self._use_set_clr_regs:  # 32-bit ports
                            # Set the appropriate bits for all 32 pins
                            machine.mem32[self._set_regs[i]] = (self._tx_values[i] | (machine.mem32[self._set_regs[i]] & ~self._pin_masks[i])) & 0xFFFFFFFF
                            # Clear the appropriate bits for all 32 pins
                            machine.mem32[self._clr_regs[i]] = ((~self._tx_values[i] & 0xFFFFFFFF) | (machine.mem32[self._clr_regs[i]] & ~self._pin_masks[i])) & 0xFFFFFFFF
                        else:  # 16-bit ports
                            # Set and clear the bits for the first 16 pins
                            machine.mem32[self._set_reset_regs[i][0]] = (self._tx_values[i] & 0xFFFF) | (machine.mem16[self._set_reset_regs[i][0]] & ~self._pin_masks[i] & 0xFFFF)
                            # Set and clear the bits for the second 16 pins
                            machine.mem32[self._set_reset_regs[i][1]] = (self._tx_values[i] >> 16) | (machine.mem16[self._set_reset_regs[i][1]] & ~self._pin_masks[i] >> 16)
                self._last = value
#            machine.mem32[self._wr_active_reg] = self._mask_wr_active  # WR Active
            self._pin_wr(1)
            sleep_us(1)

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