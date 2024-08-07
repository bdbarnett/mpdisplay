""" BPI-Centi-S3 170x320 ST7789 display """

from lcd_bus import I80Bus
from st7789 import ST7789
from machine import Pin
from rotary_irq_esp import RotaryIRQ
from eventsys.devices import Devices

display_rd_pin = Pin(7, Pin.OUT, value=1)

display_bus = I80Bus(
    data0=8,
    data1=9,
    data2=10,
    data3=11,
    data4=12,
    data5=13,
    data6=14,
    data7=15,
    dc=5,
    wr=6,
    cs=4,
    freq=16_000_000,
    dc_idle_level=0,
    dc_cmd_level=0,
    dc_dummy_level=0,
    dc_data_level=1,
    cmd_bits=8,
    param_bits=8,
    cs_active_high=False,
    reverse_color_bits=False,
    pclk_active_neg=False,
    pclk_idle_low=True,
)

display_drv = ST7789(
    display_bus,
    width=170,
    height=320,
    colstart=35,
    rowstart=0,
    rotation=0,
    mirrored=False,
    color_depth=16,
    bgr=False,
    reverse_bytes_in_word=True,
    invert=True,
    brightness=1.0,
    backlight_pin=2,
    backlight_on_high=True,
    reset_pin=3,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

encoder_drv = RotaryIRQ(37, 47, pull_up=True, half_step=True)
encoder_read_func = encoder_drv.value
encoder_button = Pin(35, Pin.IN, Pin.PULL_UP)
encoder_button_func = lambda : not encoder_button.value()

encoder_dev = display_drv.broker.create_device(
    type=Devices.ENCODER,
    read=encoder_read_func,
    read2=encoder_button_func,
)
