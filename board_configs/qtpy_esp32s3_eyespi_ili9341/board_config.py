""" QTPy ESP32S3 with EyeSPI and ILI9341 2.8" display """

from lcd_bus import SPIBus
from ili9341 import ILI9341
from machine import Pin, I2C
from ft6x36 import FT6x36


display_bus = SPIBus(
    dc=16,
    host=1,
    mosi=35,
    miso=37,
    sclk=36,
    cs=5,
    freq=20_000_000,
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

display_drv = ILI9341(
    display_bus,
    width=240,
    height=320,
    colstart=0,
    rowstart=0,
    rotation=-1,  # PORTRAIT
    color_depth=16,
    color_order=0x08,  # COLOR_ORDER_BGR
    reverse_bytes_in_word=False,
    brightness=1.0,
    backlight_pin=None,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

i2c = I2C(0, sda=Pin(7), scl=Pin(6), freq=400000)
touch_drv = FT6x36(i2c)
touch_drv_read = touch_drv.get_positions