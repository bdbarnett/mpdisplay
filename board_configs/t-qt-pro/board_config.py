""" LILYGO T-QT Pro GC9107 128x128 display """

from lcd_bus import SPIBus
from gc9a01 import GC9A01  # same as GC9107


display_bus = SPIBus(
    dc=6,
    cs=5,
    mosi=2,
    sclk=3,
    host=1,
    tx_only=True,
    freq=60_000_000,
    spi_mode=0,
    cmd_bits=8,
    param_bits=8,
    lsb_first=False,
    dc_low_on_data=False,
    cs_high_active=False,
)

display_drv = GC9A01(
    display_bus,
    width=128,
    height=128,
    colstart=0,
    rowstart=0,
    rotation=180,
    mirrored=False,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=True,
    invert=True,
    brightness=1.0,
    backlight_pin=10,
    backlight_on_high=True,
    reset_pin=1,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)
