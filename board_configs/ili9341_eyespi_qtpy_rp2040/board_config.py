""" QT Py RP2040 with EyeSPI and ILI9341 2.8" display """

from lcd_bus import SPIBus
from ili9341 import ILI9341
from machine import Pin, I2C
from ft6x36 import FT6x36
from mpdisplay import Devices


display_bus = SPIBus(
    dc=5,
    cs=20,
    mosi=3,
    miso=4, 
    sclk=6,
    host=0,
    tx_only=True,
    freq=60_000_000,
    spi_mode=0,
    cmd_bits=8,
    param_bits=8,
    lsb_first=False,
    dc_low_on_data=False,
    cs_high_active=False,
)

display_drv = ILI9341(
    display_bus,
    width=240,
    height=320,
    colstart=0,
    rowstart=0,
    rotation=0,
    mirrored=False,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=True,
    invert=False,
    brightness=1.0,
    backlight_pin=None,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

i2c = I2C(0, sda=Pin(24), scl=Pin(25), freq=100000)
touch_drv = FT6x36(i2c)
touch_read_func=touch_drv.get_positions
touch_rotation_table=(6, 3, 0, 5)

touch_dev = display_drv.create_device(
    type=Devices.TOUCH,
    read=touch_read_func,
    data=touch_rotation_table,
)
