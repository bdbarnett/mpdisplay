""" LilyGo T-Dongle-S3 80x160 ST7735 display """

from lcd_bus import SPIBus
from st7735 import ST7735
from machine import Pin, I2C


display_bus = SPIBus(
    dc=2,
    cs=4,
    mosi=3,
    sclk=5,
    host=2,
    tx_only=True,
    freq=60_000_000,
    spi_mode=0,
    cmd_bits=8,
    param_bits=8,
    lsb_first=False,
    dc_low_on_data=False,
    cs_high_active=False,
)

display_drv = ST7735(
    display_bus,
    width=80,
    height=160,
    colstart=0,
    rowstart=0,
    rotation=180,
    mirrored=False,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=False,
    invert=True,
    brightness=1.0,
    backlight_pin=38,
    backlight_on_high=True,
    reset_pin=1,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

touch_read_func = lambda : None
touch_rotation_table = None
