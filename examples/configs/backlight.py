# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#
# Backlight - adapted from displayio.Display at:
# https://github.com/adafruit/Adafruit_Blinka_Displayio/blob/main/displayio/_display.py

BACKLIGHT_IN_OUT = 1
BACKLIGHT_PWM = 2


class Backlight:
    """
    Backlight controller
    :param pin: Pin object
    :param on_high: True if .brightness() value of 1 is full on, False if value of 0 is full on
    """

    def __init__(self, pin=None, on_high=True, brightness=1.0):
        self._on_high = on_high
        self._brightness = brightness
        self._type = None
        self._backlight = None
        
        if pin is not None:
            try:
                from machine import PWM
                # 100Hz looks decent and doesn't keep the CPU too busy
                self._backlight = PWM(pin, freq=100, duty_u16=0, invert=(not self._on_high))
                self._type = BACKLIGHT_PWM
            except ImportError:
                # PWM not implemented on this platform or Pin
                self._backlight = pin
                self._type = BACKLIGHT_IN_OUT
        self.brightness(brightness)

    def __call__(self, value=None):
        if value is None:
            return self.brightness
        else:
            return self.brightness(value)

    @property
    def brightness(self):
        """The brightness of the display as a float. 0.0 is off and 1.0 is full `brightness`."""
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if self._backlight is None: return
        if 0 <= float(value) <= 1.0:
            if self._type == BACKLIGHT_PWM:
                self._backlight.duty_u16 = value * 0xFFFF
            elif self._type == BACKLIGHT_IN_OUT:
                self._backlight.value = (value > 0.0) == self._on_high
            self._brightness = value
