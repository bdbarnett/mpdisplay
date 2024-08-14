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

from displays.busdisplay import BusDisplay

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ILI9488.git"

_INIT_SEQUENCE = (
    b"\xE0\x0F\x00\x03\x09\x08\x16\x0A\x3F\x78\x4C\x09\x0A\x08\x16\x1A\x0F"
    b"\xE1\x0F\x00\x16\x19\x03\x0F\x05\x32\x45\x46\x04\x0E\x0D\x35\x37\x0F"
    b"\xC0\x02\x17\x15"  # Power Control 1 Vreg1out Verg2out 
    b"\xC1\x01\x41"  # Power Control 2 VGH,VGL
    b"\xC5\x03\x00\x12\x80"  # Power Control 3 Vcom 
    b"\x36\x01\x48"  # Memory Access 
    b"\x3A\x01\x55"  # Interface Pixel Format 16 bit    
    b"\xB0\x01\x00"  # Interface Mode Control
    b"\xB1\x01\xA0"  # Frame rate 60Hz 
    b"\xB4\x01\x02"  # Display Inversion Control 2-dot 
    b"\xB6\x00"  # Display Function Control  RGB/MCU Interface Control 
    b"\x02\x01\x02"  # MCU Source,Gate scan direction 
    b"\xE9\x01\x00"  # Set Image Function Disable 24 bit data
    b"\xF7\x04\xA9\x51\x2C\x82"  # Adjust Control D7 stream, loose 
    b"\x11\x80\x78"  # Sleep out delay 120ms
    b"\x29\x00"
)

# pylint: disable=too-few-public-methods
class ILI9488(BusDisplay):
    """ ILI9488 display driver """

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)
