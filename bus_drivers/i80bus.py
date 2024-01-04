import micropython
import machine
import struct
import sys
from lib.lcd_bus import _BaseBus, Optional
from time import sleep_us


class I80Bus(_BaseBus):
    """
    Represents an I80 bus interface for controlling GPIO pins.

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
        
        # Create the data pins as outputs
        data_pins = [data0, data1, data2, data3, data4, data5, data6, data7]
        for pin in data_pins:
            machine.Pin(pin, machine.Pin.OUT)

        # Create the control pins as outputs
        self._pin_dc = machine.Pin(dc, machine.Pin.OUT)
        self._pin_cs = machine.Pin(cs, machine.Pin.OUT)
        self._pin_wr = machine.Pin(wr, machine.Pin.OUT)
        
        self.swap_enabled = swap_color_bytes
        
        
        # Create the out registers for _write method
        self._out_a_reg: int = self._GPIO_BASE_0 + self._GPIO_OUT_OFFSET
        self._out_b_reg: int = self._GPIO_BASE_1 + self._GPIO_OUT_OFFSET
        if self._pins_per_port == 16:
            self._out_c_reg: int = self._GPIO_BASE_C + self._GPIO_OUT_OFFSET
            self._out_d_reg: int = self._GPIO_BASE_D + self._GPIO_OUT_OFFSET

        # Create the cs and dc masks as an int
        mask_cs: int = 1 << (cs % self._pins_per_port)
        mask_dc: int = 1 << (dc % self._pins_per_port)
        mask_wr: int = 1 << (wr % self._pins_per_port)

        # Create register locations for cs active and inactive, dc data and command
        if self._pins_per_port == 32:  # Most platforms
            self._write = self._write32
            self._mask_cs_active = self._mask_cs_inactive = mask_cs
            self._mask_dc_data = self._mask_dc_cmd = mask_dc
            self._mask_wr_active = self._mask_wr_inactive = mask_wr

            if cs < 32:
                cs_reg_base = self._GPIO_BASE_0
            else:
                cs_reg_base = self._GPIO_BASE_1

            if dc < 32:
                dc_reg_base = self._GPIO_BASE_0
            else:
                dc_reg_base = self._GPIO_BASE_1

            if wr < 32:
                wr_reg_base = self._GPIO_BASE_0
            else:
                wr_reg_base = self._GPIO_BASE_1

            if cs_active_high:
                self._cs_active_reg = cs_reg_base + self._GPIO_SET_OFFSET
                self._cs_inactive_reg = cs_reg_base + self._GPIO_CLR_OFFSET
            else:
                self._cs_active_reg = cs_reg_base + self._GPIO_CLR_OFFSET
                self._cs_inactive_reg = cs_reg_base + self._GPIO_SET_OFFSET

            if dc_data_level:
                self._dc_data_reg = dc_reg_base + self._GPIO_SET_OFFSET
                self._dc_cmd_reg = dc_reg_base + self._GPIO_CLR_OFFSET
            else:
                self._dc_data_reg = dc_reg_base + self._GPIO_CLR_OFFSET
                self._dc_cmd_reg = dc_reg_base + self._GPIO_SET_OFFSET

            if pclk_active_neg:
                self._wr_active_reg = wr_reg_base + self._GPIO_CLR_OFFSET
                self._wr_inactive_reg = wr_reg_base + self._GPIO_SET_OFFSET
            else:
                self._wr_active_reg = wr_reg_base + self._GPIO_SET_OFFSET
                self._wr_inactive_reg = wr_reg_base + self._GPIO_CLR_OFFSET

        else:  # stm32
            self._write = self._write16
            if cs_active_high:
                self._mask_cs_active = mask_cs
                self._mask_cs_inactive = mask_cs << 16
            else:
                self._mask_cs_active = mask_cs << 16
                self._mask_cs_inactive = mask_cs

            if dc_data_level:
                self._mask_dc_data = mask_dc
                self._mask_dc_cmd = mask_dc << 16
            else:
                self._mask_dc_data = mask_dc << 16
                self._mask_dc_cmd = mask_dc

            if pclk_active_neg:
                self._mask_wr_active = mask_wr << 16
                self._mask_wr_inactive = mask_wr
            else:
                self._mask_wr_active = mask_wr
                self._mask_wr_inactive = mask_wr << 16

            if cs < 16:
                cs_reg_base = self._GPIO_BASE_0
            elif cs < 32:
                cs_reg_base = self._GPIO_BASE_1
            elif cs < 48:
                cs_reg_base = self._GPIO_BASE_C
            else:
                cs_reg_base = self._GPIO_BASE_D

            if dc < 16:
                dc_reg_base = self._GPIO_BASE_0
            elif dc < 32:
                dc_reg_base = self._GPIO_BASE_1
            elif dc < 48:
                dc_reg_base = self._GPIO_BASE_C
            else:
                dc_reg_base = self._GPIO_BASE_D

            if wr < 16:
                wr_reg_base = self._GPIO_BASE_0
            elif wr < 32:
                wr_reg_base = self._GPIO_BASE_1
            elif wr < 48:
                wr_reg_base = self._GPIO_BASE_C
            else:
                wr_reg_base = self._GPIO_BASE_D

            self._cs_active_reg = self._cs_inactive_reg = cs_reg_base + self._GPIO_SET_RESET_OFFSET
            self._dc_data_reg = self._dc_cmd_reg = dc_reg_base + self._GPIO_SET_RESET_OFFSET
            self._wr_active_reg = self._wr_inactive_reg = wr_reg_base + self._GPIO_SET_RESET_OFFSET

        # Create the lookup tables as a list
        self._lookup_table_1 = [None] * 256
        self._lookup_table_2 = [None] * 256

        # Create the pin mask as an int
        self._pin_mask_1: int = 0
        self._pin_mask_2: int = 0

        # Populate lookup table and pin_mask
        self._create_lookup_tables(data_pins)

        # Integers used in _write method
        self._tx_value_1: int = 0
        self._tx_value_2: int = 0
        self._last = None
        
    def _create_lookup_tables(self, pins: list[int]) -> None:
        """
        Creates a lookup table for a group of 8 pins.

        Args:
            pins (list): A list of 8 pin numbers.

        Returns:
            None
        """
        # Calculate the pin masks
        for pin in pins:
            if pin < 32:
                self._pin_mask_1 |= (1 << pin)
            elif pin < 64:
                self._pin_mask_2 |= (1 << (pin - 32))
            else:
                raise ValueError("Pin number must be less than 64")

        # Iterate through all possible 8-bit values (0 to 255)
        for i in range(256):
            mapped_value_a = 0
            mapped_value_b = 0

            # Iterate through each pin and set corresponding pin bits in mapped_value
            for j, pin in enumerate(pins):
                if i & (1 << j):
                    if pin < 32:
                        mapped_value_a |= (1 << pin)
                    else:
                        mapped_value_b |= (1 << (pin - 32))
                    
            # Add the mapping to the lookup table
            self._lookup_table_1[i] = mapped_value_a
            self._lookup_table_2[i] = mapped_value_b

        print(self._lookup_table_1)
        print(self._lookup_table_2)
        print(f"0b{self._pin_mask_1:032b}")
        print(f"0b{self._pin_mask_2:032b}")

    @micropython.native
    def tx_param(
        self,
        cmd: Optional[int] = None,
        data: Optional[memoryview] = None,
    ) -> None:
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
    def _write32(self, data: memoryview) -> None:
        """
        Writes data to the I80 bus interface for devices with 32-bit GPIO registers.

        Args:
            data (memoryview): The data to be written.

        Returns:
            None
        """
        for i in range(len(data)):
            value = data[i] & 0xFF
#            machine.mem32[self._wr_inactive_reg] = self._mask_wr_inactive  # WR Inactive
            self._pin_wr(0)
            if value != self._last:
                self._tx_value_1 = self._lookup_table_1[value] & 0xFFFFFFFF
                machine.mem32[self._out_a_reg] = (self._tx_value_1 | (machine.mem32[self._out_a_reg] & ~self._pin_mask_1)) & 0xFFFFFFFF

                self._tx_value_2 = self._lookup_table_2[value] & 0xFFFFFFFF
                machine.mem32[self._out_b_reg] = (self._tx_value_2 | (machine.mem32[self._out_b_reg] & ~self._pin_mask_2)) & 0xFFFFFFFF

                self._last = value
#            machine.mem32[self._wr_active_reg] = self._mask_wr_active  # WR Active
            self._pin_wr(1)
            sleep_us(1)

    @micropython.native
    def _write16(self, data: memoryview) -> None:
        """
        Writes data to the I80 bus interface for devices with 16-bit GPIO registers.

        Args:
            data (memoryview): The data to be written.

        Returns:
            None
        """
        for i in range(len(data)):
            value = data[i] & 0xFF
            machine.mem32[self._wr_inactive_reg] = self._mask_wr_inactive  # WR Inactive
            if value != self._last:
                self._tx_value_1 = self._lookup_table_1[value] & 0xFFFFFFFF
                machine.mem16[self._out_a_reg] = ((self._tx_value_1 & 0xFFFF) | (machine.mem16[self._out_a_reg] & (~self._pin_mask_1 & 0xFFFF))) & 0xFFFF
                machine.mem16[self._out_b_reg] = ((self._tx_value_1 >> 16) | (machine.mem16[self._out_b_reg] & (~self._pin_mask_1 >> 16))) & 0xFFFF

                self._tx_value_2 = self._lookup_table_2[value] & 0xFFFFFFFF
                machine.mem16[self._out_c_reg] = ((self._tx_value_2 & 0xFFFF) | (machine.mem16[self._out_c_reg] & (~self._pin_mask_2 & 0xFFFF))) & 0xFFFF
                machine.mem16[self._out_d_reg] = ((self._tx_value_2 >> 16) | (machine.mem16[self._out_d_reg] & (~self._pin_mask_2 >> 16))) & 0xFFFF

                self._last = value
            machine.mem32[self._wr_active_reg] = self._mask_wr_active  # WR Active


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