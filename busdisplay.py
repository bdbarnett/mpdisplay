# SPDX-FileCopyrightText: 2023 Kevin Schlosser and Brad Barnett
#
# SPDX-License-Identifier: MIT

from micropython import const, alloc_emergency_exception_buf
from machine import Pin
from time import sleep_ms
import lcd_bus
# import gc


# gc.threshold(0x10000) # leave enough room for SPI master TX DMA buffers
alloc_emergency_exception_buf(256)

# Constants
_INVOFF = const(0x20)
_INVON = const(0x21)
_CASET = const(0x2A)
_RASET = const(0x2B)
_RAMWR = const(0x2C)
_MADCTL = const(0x36)

COLOR_ORDER_RGB = const(0x00)
COLOR_ORDER_BGR = const(0x08)

_MADCTL_MH = const(0x04)  # Refresh 0=Left to Right, 1=Right to Left
_MADCTL_ML = const(0x10)  # Refresh 0=Top to Bottom, 1=Bottom to Top
_MADCTL_MV = const(0x20)  # 0=Normal, 1=Row/column exchange
_MADCTL_MX = const(0x40)  # 0=Left to Right, 1=Right to Left
_MADCTL_MY = const(0x80)  # 0=Top to Bottom, 1=Bottom to Top

# MADCTL values for each of the rotation constants for non-st7789 displays.
ROTATION_TABLE = (
    _MADCTL_MX,
    _MADCTL_MV,
    _MADCTL_MY,
    _MADCTL_MY | _MADCTL_MX | _MADCTL_MV
)

# Negative rotation constants indicate the MADCTL value will come from
# the ROTATION_TABLE, otherwise the rotation value is used as the MADCTL value.
PORTRAIT = const(-1)
LANDSCAPE = const(-2)
REVERSE_PORTRAIT = const(-3)
REVERSE_LANDSCAPE = const(-4)


class BusDisplay():

    display_name = 'BusDisplay'
    MAX_TRANSFER_BYTES = 1024*1024

    # Default values of "power" and "backlight" are reversed logic! 0 means ON.
    # You can change this by setting backlight_on and power_on arguments.

    def __init__(
        self,
        display_bus,
        width,
        height,
        colstart=0,
        rowstart=0,
        rotation=PORTRAIT,
        color_depth=16,
        color_order=COLOR_ORDER_BGR,
        reverse_bytes_in_word=False,
        invert_colors=False,
        brightness=1.0,
        backlight_pin=None,
        backlight_on_high=True,
        reset_pin=None,
        reset_high=True,
        power_pin=None,
        power_on_high=True,
#        data_as_commands=False,  # not implemented
        set_column_command=_CASET,
        set_row_command=_RASET,
        write_ram_command=_RAMWR,
    ):

        
        max_trans = width * height * color_depth
            
        display_bus.init(width, height, color_depth, max_trans, rgb565_byte_swap=reverse_bytes_in_word)

        self.display_bus = display_bus
        self.width = width
        self.height = height
        self._colstart = colstart
        self._rowstart = rowstart
        self._rotation = rotation
        self._color_depth = color_depth
        self._color_order = color_order
#        self._data_as_commands = data_as_commands  # not implemented
        self._set_column_command = set_column_command
        self._set_row_command = set_row_command
        self._write_ram_command = write_ram_command

        self._reset_pin = Pin(reset_pin, Pin.OUT, value=not reset_high) if reset_pin else None 
        self._reset_high = reset_high

        self._power_pin = Pin(power_pin, Pin.OUT, value=power_on_high) if power_pin else None
        self._power_on_high = power_on_high

        self._backlight_pin = Pin(backlight_pin, Pin.OUT) if backlight_pin else None
        self._backlight_on_high = backlight_on_high

        if self._backlight_pin is not None:
            try:
                from machine import PWM
                # 1000Hz looks decent and doesn't keep the CPU too busy
                self._backlight_pin = PWM(self._backlight_pin, freq=1000, duty_u16=0)
                self._backlight_is_pwm = True
            except:
                # PWM not implemented on this platform or Pin
                self._backlight_is_pwm = False

        self._param_buf = bytearray(4)
        self._param_mv = memoryview(self._param_buf)
        self._initialized = False

        self.init()
        if not self._initialized:
            raise RuntimeError('Display driver init() must call super().init()')
        self.brightness = brightness
        self.rotation = self._rotation
        if invert_colors:
            self.invert_colors(True)

    def init(self):
        """Post initialization tasks may be added here."""
        self._initialized = True

    def blit(self, x, y, width, height, buf):
        # Column addresses
        x1 = x + self._colstart
        x2 = x + self._colstart + width - 1

        self._param_buf[0] = (x1 >> 8) & 0xFF
        self._param_buf[1] = x1 & 0xFF
        self._param_buf[2] = (x2 >> 8) & 0xFF
        self._param_buf[3] = x2 & 0xFF

        self.display_bus.tx_param(self._set_column_command, self._param_mv[:4])

        # Page addresses
        y1 = y + self._rowstart
        y2 = y + self._rowstart + height - 1

        self._param_buf[0] = (y1 >> 8) & 0xFF
        self._param_buf[1] = y1 & 0xFF
        self._param_buf[2] = (y2 >> 8) & 0xFF
        self._param_buf[3] = y2 & 0xFF

        self.display_bus.tx_param(self._set_row_command, self._param_mv[:4])

        self.display_bus.tx_color(self._write_ram_command, buf, x1, y1, x2, y2)

    def invert_colors(self, value):
        """
        If your white is showing up as black and your black is showing up as white
        try setting this either True or False and see if it corrects the problem.
        """
        if value:
            self.set_params(_INVON)
        else:
            self.set_params(_INVOFF)

    def set_params(self, cmd, params=None):
        self.display_bus.tx_param(cmd, params)

    def get_params(self, cmd, params):
        self.display_bus.rx_param(cmd, params)

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value

        self._param_buf[0] = (
            self._madctl(self._color_order, value, ROTATION_TABLE)
        )
        self.display_bus.tx_param(_MADCTL, self._param_mv[:1])

    @staticmethod
    def _madctl(color_order, rotation, rotations):
        # if rotation is 0 or positive use the value as is.
        if rotation >= 0:
            return rotation | color_order

        # otherwise use abs(rotation)-1 as index to
        # retrieve value from rotations set

        index = abs(rotation) - 1
        if index > len(rotations):
            RuntimeError('Invalid display rotation value specified')

        return rotations[index] | color_order

    def reset(self):
        if self._reset_pin is not None:
            self._reset_pin.value(self._reset_high)
            sleep_ms(120)
            self._reset_pin.value(not self._reset_high)

    @property
    def power(self):
        if self._power_pin is None:
            return -1

        state = self._power_pin.value()
        if self._power_on_high:
            return state

        return not state

    @power.setter
    def power(self, value):
        if self._power_pin is None:
            return

        if self._power_on_high:
            self._power_pin.value(value)
        else:
            self._power_pin.value(not value)

    @property
    def brightness(self):
        if self._backlight_pin is None:
            return -1

        if self._backlight_is_pwm == True:
            value = self._backlight_pin.duty_u16()  # NOQA
            return round(value / 65535)

        value = self._backlight_pin.value()

        if self._power_on_high:
            return value

        return not value

    @brightness.setter
    def brightness(self, value):
        if self._backlight_pin:
            if 0 <= float(value) <= 1.0:
                if self._backlight_is_pwm:
                    if not self._backlight_on_high:
                        value = 1.0 - value
                    self._backlight_pin.duty_u16(int(value * 0xFFFF))
                else:
                    self._backlight.value((value > 0.0) == self._on_high)
                self._brightness = value

