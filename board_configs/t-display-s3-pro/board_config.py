""" T-Display-S3 Pro 222x480 ST7796 display
https://github.com/Xinyuan-LilyGO/T-Display-S3-Pro/blob/master/schematic/T-Display-Pro.pdf
"""

from spibus import SPIBus
from st7796 import ST7796
from machine import Pin, I2C
from cst8xx import CST8XX
from eventsys.devices import Devices, Broker


display_bus = SPIBus(
    id=1,
    baudrate=40_000_000,
    sck=18,
    mosi=17,
    miso=8,
    dc=9,
    cs=39,  # Marked MTLK on the schematic
)

display_drv = ST7796(
    display_bus,
    width=222,  # Width & height may need to be swapped
    height=480,
    colstart=0,  # Adjust colstart & rowstart to center the image
    rowstart=49,  # Guessing the value here = (320 - 222) // 2
    rotation=0,  # Only change after all other settings are correct
    mirrored=False,
    color_depth=16,
    bgr=True,  # Change if the colors are wrong
    reverse_bytes_in_word=True,  # Change if the colors are wrong
    invert=True,  # Change if black and white are swapped
    brightness=1.0,
    backlight_pin=48,  # Marked SPICLK_N on the schematic
    backlight_on_high=True,  # Guessing the polarity
    reset_pin=47,  # Marked SPILCK_P on the schematic; could be `None`
    reset_high=True,  # Guessing the polarity
    power_pin=None,
    power_on_high=True,
)


i2c = I2C(0, sda=Pin(5), scl=Pin(6), freq=100_000)
touch_drv = CST8XX(i2c, irq_pin=21, rst_pin=13)
touch_read_func = touch_drv.get_point
# Set to (0,0,0,0), reset and run mpdisplay_touch_test.py if touch rotation is wrong
touch_rotation_table = (0, 5, 6, 3)

broker = Broker()

touch_dev = broker.create_device(
    type=Devices.TOUCH,
    read=touch_read_func,
    data=display_drv,
    data2=touch_rotation_table,
)
