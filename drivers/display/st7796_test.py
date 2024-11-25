try:
    from displaysys.busdisplay import BusDisplay
except ImportError:
    from busdisplay import BusDisplay
from micropython import const

_SWRESET = const(0x01)
_SLPOUT = const(0x11)
_CSCON = const(0xF0)
_MADCTL = const(0x36)
_COLMOD = const(0x3A)
_DIC = const(0xB4)
_DFC = const(0xB6)
_DOCA = const(0xE8)
_PWR2 = const(0xC1)
_PWR3 = const(0xC2)
_VCMPCTL = const(0xC5)
_PGC = const(0xE0)
_NGC = const(0xE1)
_DISPON = const(0x29)

_INIT_SEQUENCE = [
    (_SWRESET, None, 120),  # Software reset
    (_SLPOUT, None, 120),  # Sleep out
    (_CSCON, b"\xc3", 0),  # Enable extension command 2 partI
    (_CSCON, b"\x96", 0),  # Enable extension command 2 partII
    (_MADCTL, b"\x48", 0),  # Memory data access control
    (_COLMOD, b"\x55", 0),  # Interface pixel format set to 16
    (_DIC, b"\x01", 0),  # Column inversion
    (_DFC, b"\x80\x02\x3b", 0),  # Display function control
    (_DOCA, b"\x40\x8a\x00\x00\x29\x19\xa5\x33", 0),  # Display output control adjust
    (_PWR2, b"\x06", 0),  # Power control2
    (_PWR3, b"\xa7", 0),  # Power control3
    (_VCMPCTL, b"\x18", 120),  # VCOM control
    (_PGC, b"\xf0\x09\x0b\x06\x04\x15\x2f\x54\x42\x3c\x17\x14\x18\x1b", 0),  # Gamma positive
    # Should first byte be 0xF0 or 0xE0?
    (_NGC, b"\xe0\x09\x0b\x06\x04\x03\x2b\x43\x42\x3b\x16\x14\x17\x1b", 120),  # Gamma negative
    (_CSCON, b"\x3c", 0),  # Command Set control
    (_CSCON, b"\x69", 120),  # Command Set control
    (_DISPON, None, 120),  # Display on
]


class ST7796(BusDisplay):
    """
    ST7796 display driver
    """

    def __init__(self, bus, **kwargs):
        super().__init__(bus, _INIT_SEQUENCE, **kwargs)
