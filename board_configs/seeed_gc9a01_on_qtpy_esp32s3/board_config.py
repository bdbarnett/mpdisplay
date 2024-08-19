""" Seeed Studio Round Display for XIAO GC9A01 240x240 display on Adafruit QT Py ESP32-S3"""

from lcd_bus import SPIBus
from gc9a01 import GC9A01
from machine import Pin, I2C
from chsc6x import CHSC6X
from eventsys.devices import Devices


display_bus = SPIBus(
    dc=8,
    cs=17,
    mosi=35,
    miso=37,
    sclk=36,
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
    width=240,
    height=240,
    colstart=0,
    rowstart=0,
    rotation=0,
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

i2c = I2C(0, sda=Pin(7), scl=Pin(6), freq=400000)
touch_drv = CHSC6X(i2c, irq_pin=16)
touch_read_func=touch_drv.touch_read
touch_rotation_table=(0, 5, 6, 3)

touch_dev = broker.create_device(
    type=Devices.TOUCH,
    read=touch_read_func,
    data=touch_rotation_table,
)
