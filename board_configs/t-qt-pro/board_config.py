""" LILYGO T-QT Pro GC9107 128x128 display """

from lcd_bus import SPIBus
from gc9a01 import GC9A01  # same as GC9107
from machine import Pin


display_bus = SPIBus(
    dc=6,
    host=1,
    mosi=2,
    sck=3,
    cs=5,
    pclk=20_000_000,
    tx_only=True,
    wp=-1,
    hd=-1,
    quad_spi=False,
    tx_only=True,
    cmd_bits=8,
    param_bits=8,
    dc_low_on_data=False,
    sio_mode=False,
    lsb_first=False,
    cs_high_active=False,
    spi_mode=0,
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

touch_read_func = lambda : None
touch_rotation_table = None
