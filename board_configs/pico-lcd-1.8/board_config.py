""" Waveshare Pico-LCD-1.8 128x160 ST7735S display """

from spibus import SPIBus
from st7735r_1 import ST7735R


display_bus = SPIBus(
    dc=8,
    cs=9,
    mosi=11,
    sclk=10,
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

display_drv = ST7735R(
    display_bus,
    width=160,
    height=128,
    colstart=1,
    rowstart=2,
    rotation=0,
    mirrored=False,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=True,
    invert=False,
    brightness=1.0,
    backlight_pin=13,
    backlight_on_high=True,
    reset_pin=12,
    reset_high=False,
    power_pin=None,
    power_on_high=True,
)
