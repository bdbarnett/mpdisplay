""" T-Display-S3 170x320 ST7789 display  """

from lcd_bus import I80Bus
from st7789 import ST7789
from machine import Pin
from time import sleep_ms


display_power_pin=Pin(15, Pin.OUT, value=1)
display_rd_pin = Pin(9, Pin.OUT, value=1)
display_reset_pin=Pin(5, Pin.OUT, value=1)
sleep_ms(100)
display_reset_pin.value(0)
sleep_ms(100)
display_reset_pin.value(1)

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
    pclk_active_neg=False,
    pclk_idle_low=False,
)

display_drv = ST7789(
    display_bus,
    width=170,
    height=320,
    colstart=0,
    rowstart=35,
    rotation=0,
    mirrored=False,
    color_depth=16,
    bgr=False,
    reverse_bytes_in_word=True,,
    invert=True,
    brightness=1.0,
    backlight_pin=38,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

touch_read_func=lambda : None
touch_rotation_table=None
