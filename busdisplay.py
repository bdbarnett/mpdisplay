# SPDX-FileCopyrightText: 2023 Kevin Schlosser and Brad Barnett
#
# SPDX-License-Identifier: MIT

from micropython import const, alloc_emergency_exception_buf
from machine import Pin
from time import sleep_ms

# import gc


# gc.threshold(0x10000) # leave enough room for SPI master TX DMA buffers
alloc_emergency_exception_buf(256)

# Command Constants
_INVOFF = const(0x20)
_INVON = const(0x21)
_CASET = const(0x2A)
_RASET = const(0x2B)
_RAMWR = const(0x2C)
_MADCTL = const(0x36)

# MADCTL bits
_RGB = const(0x00)
_BGR = const(0x08)
_MADCTL_MH = const(0x04)  # Refresh 0=Left to Right, 1=Right to Left (Display Data Latch Order)
_MADCTL_ML = const(0x10)  # Refresh 0=Top to Bottom, 1=Bottom to Top (Line Address Order)
_MADCTL_MV = const(0x20)  # 0=Normal, 1=Row/column exchange (Page/Column Order)
_MADCTL_MX = const(0x40)  # 0=Left to Right, 1=Right to Left (Column Address Order)
_MADCTL_MY = const(0x80)  # 0=Top to Bottom, 1=Bottom to Top (Page Address Order)

# MADCTL values for each of the rotation constants for non-st7789 displays.
_DEFAULT_ROTATION_TABLE = (
    _MADCTL_MX,
    _MADCTL_MV,
    _MADCTL_MY,
    _MADCTL_MY | _MADCTL_MX | _MADCTL_MV,
)

_MIRRORED_ROTATION_TABLE = (
    0,
    _MADCTL_MV | _MADCTL_MX,
    _MADCTL_MX | _MADCTL_MY,
    _MADCTL_MV | _MADCTL_MY,
)
# Negative rotation constants indicate the MADCTL value will come from
# the self.rotation_table, otherwise the rotation value is used as the MADCTL value.
# Reset self.rotation_table in the display driver .init() to change the rotation values.
PORTRAIT = const(-1)
LANDSCAPE = const(-2)
REVERSE_PORTRAIT = const(-3)
REVERSE_LANDSCAPE = const(-4)


class BusDisplay:
    display_name = "BusDisplay"

    def __init__(
        self,
        display_bus,
        *,
        width,
        height,
        colstart=0,
        rowstart=0,
        rotation=PORTRAIT,
        color_depth=16,
        bgr=False,
        invert=False,
        reverse_bytes_in_word=False,
        brightness=1.0,
        backlight_pin=None,
        backlight_on_high=True,
        reset_pin=None,
        reset_high=True,
        power_pin=None,
        power_on_high=True,
        mirrored=False,
        set_column_command=_CASET,
        set_row_command=_RASET,
        write_ram_command=_RAMWR,
        # Required for the 16-bit SSD1351 128x128 OLED
        #        single_byte_bounds=False,
        # Required for the 16-bit SSD1331 96x64 OLED in addition to the line above
        #        data_as_commands=False,
        # Required for the 4-bit SSD1325 128x64 & SSD1327 128x128 OLEDs in addition to the 2 lines above
        #        grayscale=False,
        #        brightness_command=None,
        # Required for 1-bit OLEDs like the SSD1305, SSD1306, and SH1106 in addition to the 4 lines above
        #        pixels_in_byte_share_row=True,
    ):
        self.display_bus = display_bus
        self._width = width
        self._height = height
        self._colstart = colstart
        self._rowstart = rowstart
        self._rotation = rotation
        self._color_depth = color_depth
        self._bgr = bgr
        self._set_column_command = set_column_command
        self._set_row_command = set_row_command
        self._write_ram_command = write_ram_command
        #        self._single_byte_bounds = single_byte_bounds  # not implemented
        #        self._data_as_commands = data_as_commands  # not implemented
        #        self._grayscale = grayscale  # not implemented
        #        self._brightness_command = brightness_command  # not implemented
        #        self._pixels_in_byte_share_row = pixels_in_byte_share_row  # not implemented

        self._reset_pin = (
            Pin(reset_pin, Pin.OUT, value=not reset_high) if reset_pin else None
        )
        self._reset_high = reset_high

        self._power_pin = (
            Pin(power_pin, Pin.OUT, value=power_on_high) if power_pin else None
        )
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

        self.rotation_table = _DEFAULT_ROTATION_TABLE if not mirrored else _MIRRORED_ROTATION_TABLE
        self._param_buf = bytearray(4)
        self._param_mv = memoryview(self._param_buf)
        self._initialized = False

        display_bus.init(
            width,
            height,
            color_depth,
            self.width * self.height * self._color_depth // 8,
            rgb565_byte_swap=reverse_bytes_in_word,
        )

        self.init()
        if not self._initialized:
            raise RuntimeError(
                "Display driver init() must call super().init() or set self._initialized = True"
            )
        self.brightness = brightness
        if invert:
            self.invert_colors(True)

    def init(self, render_mode_full=False):
        """Post initialization tasks may be added here."""
        self._initialized = True
        self.rotation = self._rotation
        self.set_render_mode_full(render_mode_full)

    def set_render_mode_full(self, render_mode_full=False):
        # If rendering the full screen, set the window once
        # and pass each time .blit() is called.
        if render_mode_full:
            self._set_window(0, 0, self.width, self.height)
            self.set_window = self._pass
        # Otherwise, set the window each time .blit() is called.
        else:
            self.set_window = self._set_window

    def invert_colors(self, value):
        """
        If your white is showing up as black and your black is showing up as white
        try setting this either True or False and see if it corrects the problem.
        """
        if value:
            self.set_params(_INVON)
        else:
            self.set_params(_INVOFF)

    @property
    def width(self):
        if abs(self._rotation) & 1:
            return self._width
        return self._height

    @property
    def height(self):
        if abs(self._rotation) & 1:
            return self._height
        return self._width

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value

        self._param_buf[0] = self._madctl(self._bgr, value, self.rotation_table)
        self.set_params(_MADCTL, self._param_mv[:1])

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

    def reset(self):
        if self._reset_pin is not None:
            self._reset_pin.value(self._reset_high)
            sleep_ms(120)
            self._reset_pin.value(not self._reset_high)

    def blit(self, x, y, width, height, buf):
        x1 = x + self._colstart
        x2 = x + self._colstart + width - 1
        y1 = y + self._rowstart
        y2 = y + self._rowstart + height - 1

        self.set_window(x1, y1, x2, y2)
        self.display_bus.tx_color(self._write_ram_command, buf, x1, y1, x2, y2)

    def _pass(*_, **__):
        pass

    def _set_window(self, x1, y1, x2, y2):
        # See https://github.com/adafruit/Adafruit_Blinka_Displayio/blob/main/displayio/_displaycore.py#L271-L363
        # TODO:  Add `if self._single_byte_bounds is True:` for Column and Row _param_buf packing

        # Column addresses
        self._param_buf[0] = (x1 >> 8) & 0xFF
        self._param_buf[1] = x1 & 0xFF
        self._param_buf[2] = (x2 >> 8) & 0xFF
        self._param_buf[3] = x2 & 0xFF
        self.set_params(self._set_column_command, self._param_mv[:4])

        # Row addresses
        self._param_buf[0] = (y1 >> 8) & 0xFF
        self._param_buf[1] = y1 & 0xFF
        self._param_buf[2] = (y2 >> 8) & 0xFF
        self._param_buf[3] = y2 & 0xFF
        self.set_params(self._set_row_command, self._param_mv[:4])

    def set_params(self, cmd, params=None):
        # See https://github.com/adafruit/Adafruit_Blinka_Displayio/blob/main/displayio/_display.py#L165-L200
        # TODO:  Add `if self._data_as_commands is True:` for tx_param
        self.display_bus.tx_param(cmd, params)

    def get_params(self, cmd, params):
        self.display_bus.rx_param(cmd, params)

    @staticmethod
    def _madctl(bgr, rotation, rotations):
        color_order = _BGR if bgr else _RGB
        # if rotation is 0 or positive use the value as is.
        if rotation >= 0:
            return rotation | color_order

        # otherwise use abs(rotation)-1 as index to
        # retrieve value from rotations set

        index = abs(rotation) - 1
        if index > len(rotations):
            RuntimeError("Invalid display rotation value specified")

        return rotations[index] | color_order

    def _init_bytes(self, init_sequence):
        """
        init_sequence is a CircuitPython displayIO compatible bytes object.
        The ``init_sequence`` is bitpacked to minimize the ram impact. Every command begins
        with a command byte followed by a byte to determine the parameter count and if a
        delay is need after. When the top bit of the second byte is 1, the next byte will be
        the delay time in milliseconds. The remaining 7 bits are the parameter count
        excluding any delay byte. The third through final bytes are the remaining command
        parameters. The next byte will begin a new command definition.
        """
        DELAY = 0x80

        i = 0
        while i < len(init_sequence):
            command = init_sequence[i]
            data_size = init_sequence[i + 1]
            delay = (data_size & DELAY) != 0
            data_size &= ~DELAY

            self.set_params(command, init_sequence[i + 2 : i + 2 + data_size])

            delay_time_ms = 10
            if delay:
                data_size += 1
                delay_time_ms = init_sequence[i + 1 + data_size]
                if delay_time_ms == 255:
                    delay_time_ms = 500

            sleep_ms(delay_time_ms)
            i += 2 + data_size

    def _init_list(self, init_sequence):
        """
        The `_INIT_SEQUENCE` is a list of tuples. As a list, it can be modified in .init(), for example:
            self._INIT_SEQUENCE[-1] = (0x29, b"\x00", 100)
        Each tuple contains the following:
            - The first element is the register address (command)
            - The second element is the register value (data)
            - The third element is the delay in milliseconds after the register is set
        """
        for line in init_sequence:
            self.set_params(line[0], line[1])
            if line[2] != 0:
                sleep_ms(line[2])
