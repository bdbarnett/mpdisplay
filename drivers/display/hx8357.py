# SPDX-FileCopyrightText: 2019 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_hx8357`
================================================================================

displayio driver for HX8357 Displays such as the 3.5-inch TFT FeatherWing and Breakout

* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Hardware:**

* 3.5" PiTFT Plus 480x320 3.5" TFT+Touchscreen for Raspberry Pi:
  <https://www.adafruit.com/product/2441>
* 3.5" TFT 320x480 + Touchscreen Breakout Board w/MicroSD Socket:
  <https://www.adafruit.com/product/2050>
* Adafruit TFT FeatherWing - 3.5" 480x320 Touchscreen for Feathers:
  <https://www.adafruit.com/product/3651>

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
"""

try:
    from displaysys.busdisplay import BusDisplay
except ImportError:
    from busdisplay import BusDisplay

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_HX8357.git"

_INIT_SEQUENCE = (
    b"\x01\x80\x64"  # _SWRESET and Delay 100ms
    b"\xb9\x83\xff\x83\x57\xff"  # _SETC and delay 500ms
    b"\xb3\x04\x80\x00\x06\x06"  # _SETRGB 0x80 enables SDO pin (0x00 disables)
    b"\xb6\x01\x25"  # _SETCOM -1.52V
    b"\xb0\x01\x68"  # _SETOSC Normal mode 70Hz, Idle mode 55 Hz
    b"\xcc\x01\x05"  # _SETPANEL BGR, Gate direction swapped
    b"\xb1\x06\x00\x15\x1c\x1c\x83\xaa"  # _SETPWR1 Not deep standby BT VSPR VSNR AP
    b"\xc0\x06\x50\x50\x01\x3c\x1e\x08"  # _SETSTBA OPON normal OPON idle STBA GEN
    b"\xb4\x07\x02\x40\x00\x2a\x2a\x0d\x78"  # _SETCYC NW 0x02 RTN DIV DUM DUM GDON GDOFF
    b"\xe0\x22\x02\x0a\x11\x1d\x23\x35\x41\x4b\x4b\x42\x3a\x27\x1b\x08\x09\x03\x02\x0a"
    b"\x11\x1d\x23\x35\x41\x4b\x4b\x42\x3a\x27\x1b\x08\x09\x03\x00\x01"  # _SETGAMMA
    b"\x3a\x01\x55"  # _COLMOD 16 bit
    b"\x36\x01\xc0"  # _MADCTL
    b"\x35\x01\x00"  # _TEON TW off
    b"\x44\x02\x00\x02"  # _TEARLINE
    b"\x11\x80\x96"  # _SLPOUT and delay 150 ms
    b"\x36\x01\xa0"
    b"\x29\x80\x32"  # _DISPON and delay 50 ms
)


# pylint: disable=too-few-public-methods
class HX8357(BusDisplay):
    """HX8357D driver"""

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)
