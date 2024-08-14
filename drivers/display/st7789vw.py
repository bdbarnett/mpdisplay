""" st7789vw driver
Aapted from: https://files.waveshare.com/upload/8/8d/LCD_Module_RPI_code.zip

LCD_Module_RPI_code.zip\LCD_Module_RPI_code\RaspberryPi\python\lib
"""

from displays.busdisplay import BusDisplay


_INIT_SEQUENCE = [
        (0x36, b"\x00", 0),
        (0x3A, b"\x05", 0),
        (0x21, b"\x00", 0),
        (0x2A, b"\x00\x00\x01\x3F", 0),
        (0x2B, b"\x00\x00\x00\xEF", 0),
        (0xB2, b"\x0C\x0C\x00\x33\x33", 0),
        (0xB7, b"\x35", 0),
        (0xBB, b"\x1F", 0),
        (0xC0, b"\x2C", 0),
        (0xC2, b"\x01", 0),
        (0xC3, b"\x12", 0),
        (0xC4, b"\x20", 0),
        (0xC6, b"\x0F", 0),
        (0xD0, b"\xA4\xA1", 0),
        (0xE0, b"\xD0\x08\x11\x08\x0C\x15\x39\x33\x50\x36\x13\x14\x29\x2D", 0),
        (0xE1, b"\xD0\x08\x10\x08\x06\x06\x39\x44\x51\x0B\x16\x14\x2F\x31", 0),
        (0x21, b"\x00", 0),
        (0x11, b"\x00", 0),
        (0x29, b"\x00", 120),
]


class ST7789VW(BusDisplay):
    """ST789VW display driver"""

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)