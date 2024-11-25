# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Tyler Crumpton
#
# SPDX-License-Identifier: MIT
"""
`gc9a01`
================================================================================

displayio driver for GC9A01 TFT LCD displays


* Author(s): Tyler Crumpton

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/tylercrumpton/CircuitPython_GC9A01.git"

try:
    from displaysys.busdisplay import BusDisplay
except ImportError:
    from busdisplay import BusDisplay

_INIT_SEQUENCE = bytearray(
    b"\xfe\x00"  # Inter Register Enable1 (FEh)
    b"\xef\x00"  # Inter Register Enable2 (EFh)
    b"\xb6\x02\x00\x00"  # Display Function Control (B6h) [S1→S360 source, G1→G32 gate]
    b"\x36\x01\x48"  # Memory Access Control(36h) [Invert Row order, invert vertical scan order]
    b"\x3a\x01\x05"  # COLMOD: Pixel Format Set (3Ah) [16 bits / pixel]
    b"\xc3\x01\x13"  # Power Control 2 (C3h) [VREG1A = 5.06, VREG1B = 0.68]
    b"\xc4\x01\x13"  # Power Control 3 (C4h) [VREG2A = -3.7, VREG2B = 0.68]
    b"\xc9\x01\x22"  # Power Control 4 (C9h)
    b"\xf0\x06\x45\x09\x08\x08\x26\x2a"  # SET_GAMMA1 (F0h)
    b"\xf1\x06\x43\x70\x72\x36\x37\x6f"  # SET_GAMMA2 (F1h)
    b"\xf2\x06\x45\x09\x08\x08\x26\x2a"  # SET_GAMMA3 (F2h)
    b"\xf3\x06\x43\x70\x72\x36\x37\x6f"  # SET_GAMMA4 (F3h)
    b"\x66\x0a\x3c\x00\xcd\x67\x45\x45\x10\x00\x00\x00"
    b"\x67\x0a\x00\x3c\x00\x00\x00\x01\x54\x10\x32\x98"
    b"\x74\x07\x10\x85\x80\x00\x00\x4e\x00"
    b"\x98\x02\x3e\x07"
    b"\x35\x00"  # Tearing Effect Line ON (35h) [both V-blanking and H-blanking]
    b"\x21\x00"  # Display Inversion ON (21h)
    b"\x11\x80\x78"  # Sleep Out Mode (11h) and delay(120)
    b"\x29\x80\x14"  # Display ON (29h) and delay(20)
    b"\x2a\x04\x00\x00\x00\xef"  # Column Address Set (2Ah) [Start col = 0, end col = 239]
    b"\x2b\x04\x00\x00\x00\xef"  # Row Address Set (2Bh) [Start row = 0, end row = 239]
)


# pylint: disable=too-few-public-methods
class GC9A01(BusDisplay):
    """GC9A01 display driver"""

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)
