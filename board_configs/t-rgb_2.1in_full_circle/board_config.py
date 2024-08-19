""" T-RGB 480x480 ST7701 display - 2.1" Full Circle with CST820 touch controller """

from lcd_bus import RGBBus
from st7701 import ST7701, LCDPins
from machine import Pin, I2C
from xl9535 import XL9535
from cst8xx import CST8XX
from eventsys.devices import Devices


display_bus = RGBBus(
    hsync=47,
    vsync=41,
    de=45,
    disp=-1,
    pclk=42,
    data0=7,
    data1=6,
    data2=5,
    data3=3,
    data4=2,
    data5=14,
    data6=13,
    data7=12,
    data8=11,
    data9=10,
    data10=9,
    data11=21,
    data12=18,
    data13=17,
    data14=16,
    data15=15,
    freq=8_000_000,
    num_fbs=2,
    bb_size_px=0,
    hsync_front_porch=50,
    hsync_pulse_width=30,
    hsync_pulse_width=1,
    hsync_idle_low=False,
    vsync_front_porch=20,
    vsync_back_porch=30,
    vsync_pulse_width=1,
    vsync_idle_low=False,
    de_idle_high=False,
    pclk_idle_high=False,
    pclk_active_neg=False,
    disp_active_low=False,
    refresh_on_demand=False,
    fb_in_psram=False,
    no_fb=False,
    bb_inval_cache=False,
)

i2c = I2C(0, scl=Pin(48), sda=Pin(8))
io_expander = XL9535(i2c)
lcd_pins = LCDPins(
    pwr_en=io_expander.Pin(2, io_expander.OUT),
    cs=io_expander.Pin(3, io_expander.OUT),
    sda=io_expander.Pin(4, io_expander.OUT),
    clk=io_expander.Pin(5, io_expander.OUT),
    rst=io_expander.Pin(6, io_expander.OUT),
)
tp_rst=io_expander.Pin(1, io_expander.OUT, value=1)
sd_cs=io_expander.Pin(7, io_expander.OUT, value=1)

display_drv = ST7701(
    lcd_pins,
    display_bus,
    width=480,
    height=480,
    colstart=0,
    rowstart=0,
    rotation=0,
    mirrored=False,
    color_depth=16,
    bgr=True,
    reverse_bytes_in_word=False,
    invert=False,
    brightness=1.0,
    backlight_pin=46,
    backlight_on_high=True,
    rst_pin=None,
    rst_high=True,
    pwr_en_pin=None,
    pwr_en_on_high=True,
)

touch_drv = CST8XX(i2c, rst_pin=tp_rst)
touch_read_func = touch_drv.get_point
touch_rotation_table=None

touch_dev = broker.create_device(
    type=Devices.TOUCH,
    read=touch_read_func,
    data=touch_rotation_table,
)
