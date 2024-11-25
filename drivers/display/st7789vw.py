"""
ST7789VW Driver
Adapted from LCD_Module_RPI_code.zip/LCD_Module_RPI_code/RaspberryPi/python/lib
at https://files.waveshare.com/upload/8/8d/LCD_Module_RPI_code.zip
"""

try:
    from displaysys.busdisplay import BusDisplay
except ImportError:
    from busdisplay import BusDisplay


_INIT_SEQUENCE = [
    (0x36, b"\x00", 0),
    (0x3A, b"\x05", 0),
    (0x21, b"\x00", 0),
    (0x2A, b"\x00\x00\x01\x3f", 0),
    (0x2B, b"\x00\x00\x00\xef", 0),
    (0xB2, b"\x0c\x0c\x00\x33\x33", 0),
    (0xB7, b"\x35", 0),
    (0xBB, b"\x1f", 0),
    (0xC0, b"\x2c", 0),
    (0xC2, b"\x01", 0),
    (0xC3, b"\x12", 0),
    (0xC4, b"\x20", 0),
    (0xC6, b"\x0f", 0),
    (0xD0, b"\xa4\xa1", 0),
    (0xE0, b"\xd0\x08\x11\x08\x0c\x15\x39\x33\x50\x36\x13\x14\x29\x2d", 0),
    (0xE1, b"\xd0\x08\x10\x08\x06\x06\x39\x44\x51\x0b\x16\x14\x2f\x31", 0),
    (0x21, b"\x00", 0),
    (0x11, b"\x00", 0),
    (0x29, b"\x00", 120),
]


class ST7789VW(BusDisplay):
    """ST789VW display driver"""

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)
