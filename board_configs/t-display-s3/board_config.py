""" T-Display-S3 170x320 ST7789 display  """

from lcd_bus import I80Bus
from st7789 import ST7789
from machine import Pin


display_rd_pin = Pin(9, Pin.OUT, value=1)

display_bus = I80Bus(
    dc=7,
    wr=8,
    cs=6,
    data0=39,
    data1=40,
    data2=41,
    data3=42,
    data4=45,
    data5=46,
    data6=47,
    data7=48,
    freq=20000000,
    dc_idle_level=0,
    dc_cmd_level=0,
    dc_dummy_level=0,
    dc_data_level=1,
    cmd_bits=8,
    param_bits=8,
    cs_active_high=False,
    reverse_color_bits=False,
    swap_color_bytes=True,
    pclk_active_neg=False,
    pclk_idle_low=False,
)

display_drv = ST7796(
    display_bus,
    width=170,
    height=320,
    colstart=0,
    rowstart=0,
    rotation=-1,  # PORTRAIT
    color_depth=16,
    color_order=0x0,  # RGB
    reverse_bytes_in_word=True,
    invert_colors=True,
    brightness=1.0,
    backlight_pin=38,
    backlight_on_high=True,
    reset_pin=5,
    reset_high=True,
    power_pin=15,
    power_on_high=True,
)
