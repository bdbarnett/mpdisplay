""" M5Stack CoreS3 with ILI9342 320x240 display """

from lcd_bus import SPIBus
from ili9341 import ILI9341
from machine import I2C, Pin
from ft6x36 import FT6x36
from eventsys.devices import Devices


display_bus = SPIBus(
    dc=35,
    cs=3,
    mosi=37,
    sck=36,
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

display_drv = ILI9341(
    display_bus,
    width=240,
    height=320,
    colstart=0,
    rowstart=0,
    rotation=180,
    mirrored=False,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=True,
    invert=True,
    brightness=1.0,
    backlight_pin=None,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

i2c = I2C(0, sda=Pin(12), scl=Pin(11), freq=100000)
touch_drv = FT6x36(i2c)
touch_read_func=touch_drv.get_positions
touch_rotation_table=None

touch_dev = broker.create_device(
    type=Devices.TOUCH,
    read=touch_read_func,
    data=touch_rotation_table,
)
