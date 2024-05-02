""" Waveshare ESP32-S3-Touch-LCD-4.3 800x480 ST7701 display """

from lcd_bus import RGBBus
from busdisplay import BusDisplay
from machine import I2C, Pin
from gt911 import GT911
from mpdisplay import Devices


display_bus = RGBBus(
    hsync=46,
    vsync=3,
    de=5,
    disp=-1,
    pclk=7,
    data0=14,
    data1=38,
    data2=18,
    data3=17,
    data4=10,
    data5=39,
    data6=0,
    data7=45,
    data8=48,
    data9=47,
    data10=21,
    data11=1,
    data12=2,
    data13=42,
    data14=41,
    data15=40,
    freq=21_000_000,
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

display_drv = BusDisplay(
    display_bus,
    width=800,
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
    backlight_pin=None,
    backlight_on_high=True,
    reset_pin=None,
    reset_high=True,
    power_pin=None,
    power_on_high=True,
)

i2c = I2C(0, scl=Pin(9), sda=Pin(8))
touch_drv = GT911(i2c)
touch_read_func = lambda : touch_drv.read_points()[1][0]
touch_rotation_table = None

touch_dev = display_drv.create_device(
    type=Devices.TOUCH,
    read=touch_read_func,
    data=touch_rotation_table,
)
