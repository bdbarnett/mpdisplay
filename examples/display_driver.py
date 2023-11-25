""" WT32-SC01 Plus 320x480 ST7796 display """
# Example display_driver.py for lv_micropython
# Usage:
#   import display_driver
# or
#   from display_driver import devices

import mpdisplay
from st7796 import init_sequence, rotations
from backlight import Backlight
from machine import Pin, I2C
from lvmp_devices import Devices
from ft6x36 import FT6x36

##########################################
# Setup Display Driver & Backlight
##########################################

reset=Pin(4, Pin.OUT, value=1)

bus = mpdisplay.I80_bus(
    (9, 46, 3, 8, 18, 17, 16, 15),
    dc=0,
    wr=47,
    cs=6,
    pclk=20_000_000,
    swap_color_bytes=True,
    reverse_color_bits=False,
)

display_drv = mpdisplay.Display(
    bus,
    width=320,
    height=480,
    bpp=16,
    reset=-1,  # Reset pin 4 is shared with touch.  Should be controlled outside the driver.
    rotation=1,
    bgr=True,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
)

backlight=Backlight(Pin(45, Pin.OUT), on_high=True)

##########################################
# Setup Touch and other I2C devices
##########################################

i2c = I2C(0, sda=Pin(6), scl=Pin(5))
touch_drv = FT6x36(i2c)

##########################################
# Create devices for LVGL
##########################################

devices = Devices(
    display_drv = display_drv,
    bgr = True,
    factor = 6,
    blit_func = display_drv.blit,
    alloc_buf_func = mpdisplay.allocate_buffer,
    register_ready_cb_func = display_drv.register_cb,
    touch_read_func = touch_drv.get_positions,
    touch_rotation = 5,
    )

##########################################
# Attach any other devices you want to
# access from your main.py to `devices`
##########################################

devices.backlight = backlight
