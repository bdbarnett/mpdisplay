# The MIT License (MIT)
#
# Copyright (c) 2019 Tavish Naruka <tavish@electronut.in> for Electronut Labs (electronut.in)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`electronutlabs_ili9163`
================================================================================

displayio driver for ILI9163 TFT-LCD displays.


* Author(s): Tavish Naruka <tavish@electronut.in>

Implementation Notes
--------------------

**Hardware:**

    * `Electronut Labs Blip <https://docs.electronut.in/blip/>`_
    * `TFTM018 <https://www.mouser.com/ds/2/239/Lite-On_LTR-329ALS-01%20DS_ver1.1-348647.pdf>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

try:
    from displaysys.busdisplay import BusDisplay
except ImportError:
    from busdisplay import BusDisplay

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/electronut/Electronutlabs_CircuitPython_ILI9163.git"

_INIT_SEQUENCE = (
    b"\x01\x80\x80"
    b"\x11\x80\x05"
    b"\x3a\x01\x05"
    b"\x26\x01\x04"
    b"\xf2\x01\x01"
    b"\xe0\x0f\x3f\x25\x1c\x1e\x20\x12\x2a\x90\x24\x11\x00\x00\x00\x00\x00"
    b"\xe1\x0f\x20\x20\x20\x20\x05\x00\x15\xa7\x3d\x18\x25\x2a\x2b\x2b\x3a"
    b"\xb1\x02\x08\x08"
    b"\xb4\x01\x07"
    b"\xc0\x02\x0a\x02"
    b"\xc1\x01\x02"
    b"\xc5\x02\x50\x5b"
    b"\xc7\x01\x40"
    b"\x2a\x04\x00\x00\x00\x7f"
    b"\x2b\x04\x00\x00\x00\x7f"
    b"\x36\x01\x68"  # rotation
    b"\x29\x80\x78"
    b"\x2c\x80\x78"
)

# pylint: disable=too-few-public-methods


class ILI9163(BusDisplay):
    """ILI9163 display driver"""

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)
