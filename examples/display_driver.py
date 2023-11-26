""" WT32-SC01 Plus 320x480 ST7796 display """
# Example display_driver.py for lv_micropython using lvmp_devices.
# Name it anything you like.  That file name is used here because
# most lv_micropython examples use that name.
#
# Usage:
#   import display_driver
# or
#   from display_driver import devices

import mpdisplay                            # https://github.com/bdbarnett/mpdisplay
from backlight import Backlight             # https://github.com/bdbarnett/mpdisplay/blob/main/backlight.py
from st7796 import init_sequence, rotations # https://github.com/bdbarnett/mpdisplay/blob/main/drivers
from ft6x36 import FT6x36                   # https://github.com/lbuque/micropython-ft6x36
from rotary import RotaryIRQ                # https://github.com/miketeachman/micropython-rotary
from lvmp_devices import Devices            # https://github.com/bdbarnett/lvmp_devices
from machine import Pin, I2C

###############################################################################
# Setup Display Driver & Backlight
###############################################################################

# The WT32-SC01 Plus has the reset pins of the display IC and the touch IC both
# tied to pin 4.  Controlling this pin with the display driver can lead to an
# unresponsive touchscreen.  This case is not common.  If they aren't tied 
# together on your board, define reset in mpdisplay.Display instead, like:
#    mpdisplay.Display(reset=4)
# Also do this for the display power pin if your board has one.  Most don't.
reset=Pin(4, Pin.OUT, value=1)

# Create the bus
bus = mpdisplay.I80_bus(
    (9, 46, 3, 8, 18, 17, 16, 15),
    dc=0,
    wr=47,
    cs=6,
    pclk=20_000_000,
    swap_color_bytes=True,
    reverse_color_bits=False,
)

# Create the display
display_drv = mpdisplay.Display(
    bus,
    width=320,
    height=480,
    bpp=16,
    reset=-1,  # See note above.
    rotation=1,
    bgr=True,
    invert_color=True,
    init_sequence=init_sequence,
    rotations=rotations,
)

# Create the backlight.  Not all screens have a user controllable backlight.
backlight=Backlight(Pin(45, Pin.OUT), on_high=True)

###############################################################################
# Setup Touch and other I2C devices
###############################################################################

i2c = I2C(0, sda=Pin(6), scl=Pin(5))
touch_drv = FT6x36(i2c)

###############################################################################
# Setup Rotary Encoder(s)
###############################################################################
# This is just an example.  This board doesn't have an encoder.  In this 
# example, `enc1_btn.value() returns 0 if pressed, 1 if not pressed.  We can
# flip the value in a lambda function.

enc1 = RotaryIRQ(1, 2, pull_up=True, half_step=True)
enc1_btn = Pin(0, Pin.IN, Pin.PULL_UP)
enc1_funcs = (enc1.value, lammbda : not enc1_btn.value())

###############################################################################
# Create devices for LVGL
###############################################################################

devices = Devices(
    display_drv = display_drv,
    bgr = True,
    factor = 10,
    blit_func = display_drv.blit,
    alloc_buf_func = mpdisplay.allocate_buffer,
    reg_ready_cb_func = display_drv.register_cb,
    touch_read_func = touch_drv.get_positions,
    touch_rotation = 5,
    enc_funcs = [enc1_funcs],
    )

###############################################################################
# Attach any other devices you want to access from your main.py to `devices`
###############################################################################

devices.backlight = backlight
