# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Tyler Crumpton
#
# SPDX-License-Identifier: MIT
"""
`gc9d01`
================================================================================

displayio driver for GC9D01 TFT LCD displays


* Author(s): Tyler Crumpton

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/tylercrumpton/CircuitPython_GC9D01.git"

from busdisplay import BusDisplay

_INIT_SEQUENCE = bytearray(
    b"\xFE\x00"  # Inter Register Enable1 (FEh)
    b"\xEF\x00"  # Inter Register Enable2 (EFh)
    b"\x80\x01\xFF"
    b"\x81\x01\xFF"
    b"\x82\x01\xFF"
    b"\x83\x01\xFF"
    b"\x84\x01\xFF"
    b"\x85\x01\xFF"
    b"\x86\x01\xFF"
    b"\x87\x01\xFF"
    b"\x88\x01\xFF"
    b"\x89\x01\xFF"
    b"\x8A\x01\xFF"
    b"\x8B\x01\xFF"
    b"\x8C\x01\xFF"
    b"\x8D\x01\xFF"
    b"\x8E\x01\xFF"
    b"\x8F\x01\xFF"
    b"\x3A\x01\x05"  # COLMOD: Pixel Format Set (3Ah) MCU interface, 16 bits / pixel
    b"\xEC\x01\x10"  # Inversion (ECh) DINV=1+2 column for Single Gate (BFh=0)
    b"\x7E\x01\x7A"
    b"\x74\x07\x02\x0E\x00\x00\x28\x00\x00"
    b"\x98\x01\x3E"
    b"\x99\x01\x3E"
    b"\xB5\x03\x0E\x0E\x00"  # Blanking Porch Control (B5h) VFP=14 VBP=14 HBP=Off
    b"\x60\x04\x38\x09\x6D\x67"
    b"\x63\x05\x38\xAD\x6D\x67\x05"
    b"\x64\x06\x38\x0B\x70\xAB\x6D\x67"
    b"\x66\x06\x38\x0F\x70\xAF\x6D\x67"
    b"\x6A\x02\x00\x00"
    b"\x68\x07\x3B\x08\x04\x00\x04\x64\x67"
    b"\x6C\x07\x22\x02\x22\x02\x22\x22\x50"
    b"\x6E\x1E\x00\x00\x00\x00\x07\x01\x13\x11\x0B\x09\x16\x15\x1D\x1E\x00\x00\x00\x00\x1E\x1D\x15\x16\x0A\x0C\x12\x14\x02\x08\x00\x00\x00\x00"  # pylint: disable=line-too-long
    b"\xA9\x01\x1B"
    b"\xA8\x01\x6B"
    b"\xA8\x01\x6D"
    b"\xA7\x01\x40"
    b"\xAD\x01\x47"
    b"\xAF\x01\x73"
    b"\xAF\x01\x73"
    b"\xAC\x01\x44"
    b"\xA3\x01\x6C"
    b"\xCB\x01\x00"
    b"\xCD\x01\x22"
    b"\xC2\x01\x10"
    b"\xC5\x01\x00"
    b"\xC6\x01\x0E"
    b"\xC7\x01\x1F"
    b"\xC8\x01\x0E"
    b"\xBF\x01\x00"  # Dual-Single Gate Select (BFh) 0=>Single gate
    b"\xF9\x01\x20"
    b"\x9B\x01\x3B"
    b"\x93\x03\x33\x7F\x00"
    b"\x70\x06\x0E\x0F\x03\x0E\x0F\x03"
    b"\x71\x03\x0E\x16\x03"
    b"\x91\x02\x0E\x09"
    b"\xC3\x01\x2C"  # Vreg1a Voltage Control 2 (C3h) vreg1_vbp_d=0x2C
    b"\xC4\x01\x1A"  # Vreg1b Voltage Control 2 (C4h) vreg1_vbn_d=0x1A
    b"\xF0\x06\x51\x13\x0C\x06\x00\x2F"  # SET_GAMMA1 (F0h)
    b"\xF2\x06\x51\x13\x0C\x06\x00\x33"  # SET_GAMMA3 (F2h)
    b"\xF1\x06\x3C\x94\x4F\x33\x34\xCF"  # SET_GAMMA2 (F1h)
    b"\xF3\x06\x4D\x94\x4F\x33\x34\xCF"  # SET_GAMMA4 (F3h)
    b"\x36\x01\x00"  # Memory Access Control (36h) MY=0, MX=0, MV=0, ML=0, BGR=0, MH=0
    b"\x11\x80\xC8"  # Sleep Out Mode (11h) and delay(200)
    b"\x29\x80\x14"  # Display ON (29h) and delay(20)
    b"\x2C\x00"  # Memory Write (2Ch) D=0
)


# pylint: disable=too-few-public-methods
class GC9D01(BusDisplay):
    """GC9D01 display driver"""

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)
