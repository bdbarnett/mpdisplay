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

try:
    from displaysys.busdisplay import BusDisplay
except ImportError:
    from busdisplay import BusDisplay

_INIT_SEQUENCE = bytearray(
    b"\xfe\x00"  # Inter Register Enable1 (FEh)
    b"\xef\x00"  # Inter Register Enable2 (EFh)
    b"\x80\x01\xff"
    b"\x81\x01\xff"
    b"\x82\x01\xff"
    b"\x83\x01\xff"
    b"\x84\x01\xff"
    b"\x85\x01\xff"
    b"\x86\x01\xff"
    b"\x87\x01\xff"
    b"\x88\x01\xff"
    b"\x89\x01\xff"
    b"\x8a\x01\xff"
    b"\x8b\x01\xff"
    b"\x8c\x01\xff"
    b"\x8d\x01\xff"
    b"\x8e\x01\xff"
    b"\x8f\x01\xff"
    b"\x3a\x01\x05"  # COLMOD: Pixel Format Set (3Ah) MCU interface, 16 bits / pixel
    b"\xec\x01\x10"  # Inversion (ECh) DINV=1+2 column for Single Gate (BFh=0)
    b"\x7e\x01\x7a"
    b"\x74\x07\x02\x0e\x00\x00\x28\x00\x00"
    b"\x98\x01\x3e"
    b"\x99\x01\x3e"
    b"\xb5\x03\x0e\x0e\x00"  # Blanking Porch Control (B5h) VFP=14 VBP=14 HBP=Off
    b"\x60\x04\x38\x09\x6d\x67"
    b"\x63\x05\x38\xad\x6d\x67\x05"
    b"\x64\x06\x38\x0b\x70\xab\x6d\x67"
    b"\x66\x06\x38\x0f\x70\xaf\x6d\x67"
    b"\x6a\x02\x00\x00"
    b"\x68\x07\x3b\x08\x04\x00\x04\x64\x67"
    b"\x6c\x07\x22\x02\x22\x02\x22\x22\x50"
    b"\x6e\x1e\x00\x00\x00\x00\x07\x01\x13\x11\x0b\x09\x16\x15\x1d\x1e\x00\x00\x00\x00\x1e\x1d\x15\x16\x0a\x0c\x12\x14\x02\x08\x00\x00\x00\x00"  # pylint: disable=line-too-long
    b"\xa9\x01\x1b"
    b"\xa8\x01\x6b"
    b"\xa8\x01\x6d"
    b"\xa7\x01\x40"
    b"\xad\x01\x47"
    b"\xaf\x01\x73"
    b"\xaf\x01\x73"
    b"\xac\x01\x44"
    b"\xa3\x01\x6c"
    b"\xcb\x01\x00"
    b"\xcd\x01\x22"
    b"\xc2\x01\x10"
    b"\xc5\x01\x00"
    b"\xc6\x01\x0e"
    b"\xc7\x01\x1f"
    b"\xc8\x01\x0e"
    b"\xbf\x01\x00"  # Dual-Single Gate Select (BFh) 0=>Single gate
    b"\xf9\x01\x20"
    b"\x9b\x01\x3b"
    b"\x93\x03\x33\x7f\x00"
    b"\x70\x06\x0e\x0f\x03\x0e\x0f\x03"
    b"\x71\x03\x0e\x16\x03"
    b"\x91\x02\x0e\x09"
    b"\xc3\x01\x2c"  # Vreg1a Voltage Control 2 (C3h) vreg1_vbp_d=0x2C
    b"\xc4\x01\x1a"  # Vreg1b Voltage Control 2 (C4h) vreg1_vbn_d=0x1A
    b"\xf0\x06\x51\x13\x0c\x06\x00\x2f"  # SET_GAMMA1 (F0h)
    b"\xf2\x06\x51\x13\x0c\x06\x00\x33"  # SET_GAMMA3 (F2h)
    b"\xf1\x06\x3c\x94\x4f\x33\x34\xcf"  # SET_GAMMA2 (F1h)
    b"\xf3\x06\x4d\x94\x4f\x33\x34\xcf"  # SET_GAMMA4 (F3h)
    b"\x36\x01\x00"  # Memory Access Control (36h) MY=0, MX=0, MV=0, ML=0, BGR=0, MH=0
    b"\x11\x80\xc8"  # Sleep Out Mode (11h) and delay(200)
    b"\x29\x80\x14"  # Display ON (29h) and delay(20)
    b"\x2c\x00"  # Memory Write (2Ch) D=0
)


# pylint: disable=too-few-public-methods
class GC9D01(BusDisplay):
    """GC9D01 display driver"""

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)
