""" DIY Raspberry Pi Pico with ILI9341 2.8" display """

from lcd_bus import I80Bus
from ili9341 import ILI9341
from machine import I2C, Pin, freq  # See the note about reset below
from ft6x36 import FT6x36
from mpdisplay import Device_types


# The ILI9341 2.8" display has the reset pins of the display IC and the touch
# tied together.  Controlling this pin with the display driver can lead to an
# unresponsive touchscreen.  This case is uncommon.  If they aren't tied 
# together on your board, define reset in ST7796 instead, like:
#    ILI9341(reset=12)
reset=Pin(12, Pin.OUT, value=1)

display_bus = I80Bus(
    dc=14,
    wr=13,
    cs=15,
    data0=0,
    data1=1,
    data2=2,
    data3=3,
    data4=4,
    data5=5,
    data6=6,
    data7=7,
    freq=10_000_000,
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

i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)  #IRQ = 11
touch_drv = FT6x36(i2c)
touch_read_func=touch_drv.get_positions
touch_rotation_table=None

display_drv.register_device(
    type=Device_types.TOUCH,
    callback=touch_read_func,
    user_data=touch_rotation_table,
)
