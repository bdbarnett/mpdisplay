""" T-Embed ST7789 display with encoder"""

from lcd_bus import SPIBus
from st7789 import ST7789
from machine import Pin, I2C
from rotary_irq_esp import RotaryIRQ


display_bus = SPIBus(
    dc=13,
    cs=10,
    mosi=11,
    miso=-1,
    sclk=12,
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

display_drv = ST7789(
    display_bus,
    width=170,
    height=320,
    colstart=0,
    rowstart=0,
    rotation=0,
    mirrored=False,
    color_depth=16,
    bgr=False,
    reverse_bytes_in_word=True,
    invert=False,
    brightness=1.0,
    backlight_pin=15,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

encoder_drv = RotaryIRQ(1, 2, pull_up=True, half_step=True)
encoder_read_func = encoder_drv.value
encoder_button = Pin(0, Pin.IN, Pin.PULL_UP)
encoder_button_func = lambda : not encoder_button.value()
