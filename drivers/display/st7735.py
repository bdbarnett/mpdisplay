# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_st7735`
====================================================

Displayio driver for ST7735 based displays.

* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

try:
    from displaysys.busdisplay import BusDisplay
except ImportError:
    from busdisplay import BusDisplay

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ST7735.git"

_INIT_SEQUENCE = (
    b"\x01\x80\x32"  # _SWRESET and Delay 50ms
    b"\x11\x80\xff"  # _SLPOUT
    b"\x3a\x81\x05\x0a"  # _COLMOD
    b"\xb1\x83\x00\x06\x03\x0a"  # _FRMCTR1
    b"\x36\x01\x08"  # _MADCTL
    b"\xb6\x02\x15\x02"  # _DISSET5
    # 1 clk cycle nonoverlap, 2 cycle gate, rise, 3 cycle osc equalize, Fix on VTL
    b"\xb4\x01\x00"  # _INVCTR line inversion
    b"\xc0\x82\x02\x70\x0a"  # _PWCTR1 GVDD = 4.7V, 1.0uA, 10 ms delay
    b"\xc1\x01\x05"  # _PWCTR2 VGH = 14.7V, VGL = -7.35V
    b"\xc2\x02\x01\x02"  # _PWCTR3 Opamp current small, Boost frequency
    b"\xc5\x82\x3c\x38\x0a"  # _VMCTR1
    b"\xfc\x02\x11\x15"  # _PWCTR6
    b"\xe0\x10\x09\x16\x09\x20\x21\x1b\x13\x19\x17\x15\x1e\x2b\x04\x05\x02\x0e"  # _GMCTRP1 Gamma
    b"\xe1\x90\x0b\x14\x08\x1e\x22\x1d\x18\x1e\x1b\x1a\x24\x2b\x06\x06\x02\x0f\x0a"  # _GMCTRN1
    b"\x13\x80\x0a"  # _NORON
    b"\x29\x80\xff"  # _DISPON
)


# pylint: disable=too-few-public-methods
class ST7735(BusDisplay):
    """ST7735 driver"""

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)
