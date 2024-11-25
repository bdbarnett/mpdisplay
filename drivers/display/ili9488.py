# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`bagaloozy_ili9488`
====================================================

Display driver for ILI9488

* Author(s): Mark Winney

Implementation Notes
--------------------

**Hardware:**

* Buy Display LCD 3.5" 320x480 TFT Display Module,OPTL Touch Screen w/Breakout Board
  <https://www.buydisplay.com/lcd-3-5-inch-320x480-tft-display-module-optl-touch-screen-w-breakout-board>

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

try:
    from displaysys.busdisplay import BusDisplay
except ImportError:
    from busdisplay import BusDisplay

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ILI9488.git"

_INIT_SEQUENCE = (
    b"\xe0\x0f\x00\x03\x09\x08\x16\x0a\x3f\x78\x4c\x09\x0a\x08\x16\x1a\x0f"
    b"\xe1\x0f\x00\x16\x19\x03\x0f\x05\x32\x45\x46\x04\x0e\x0d\x35\x37\x0f"
    b"\xc0\x02\x17\x15"  # Power Control 1 Vreg1out Verg2out
    b"\xc1\x01\x41"  # Power Control 2 VGH,VGL
    b"\xc5\x03\x00\x12\x80"  # Power Control 3 Vcom
    b"\x36\x01\x48"  # Memory Access
    b"\x3a\x01\x55"  # Interface Pixel Format 16 bit
    b"\xb0\x01\x00"  # Interface Mode Control
    b"\xb1\x01\xa0"  # Frame rate 60Hz
    b"\xb4\x01\x02"  # Display Inversion Control 2-dot
    b"\xb6\x00"  # Display Function Control  RGB/MCU Interface Control
    b"\x02\x01\x02"  # MCU Source,Gate scan direction
    b"\xe9\x01\x00"  # Set Image Function Disable 24 bit data
    b"\xf7\x04\xa9\x51\x2c\x82"  # Adjust Control D7 stream, loose
    b"\x11\x80\x78"  # Sleep out delay 120ms
    b"\x29\x00"
)


# pylint: disable=too-few-public-methods
class ILI9488(BusDisplay):
    """ILI9488 display driver"""

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)
