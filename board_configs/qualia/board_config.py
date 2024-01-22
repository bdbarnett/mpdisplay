""" Qualia with 4.0" 720x720 display """

from lcd_bus import RGBBus
from busdisplay import BusDisplay
from machine import I2C, Pin
from cst8xx import CST8XX

display_bus = RGBBus(
    hsync=41,
    vsync=42,
    de=2,
    disp=-1,
    pclk=1,
    data0=11,  #r0
    data1=10,  #r1
    data2=9,  #r2
    data3=46,  #r3
    data4=3,  #r4
    data5=48,  #g0
    data6=47,  #g1
    data7=21,  #g2
    data8=14,  #g3
    data9=13,  #g4
    data10=12,  #g5
    data11=40,  #b0
    data12=39,  #b1
    data13=38,  #b2
    data14=0,  #b3
    data15=45,  #b4
    freq=25000000,
    bb_size_px=0,
    hsync_pulse_width=2,
    hsync_front_porch=46,
    hsync_back_porch=44,
    hsync_idle_low=False,
    vsync_pulse_width=2,
    vsync_front_porch=16,
    vsync_back_porch=18,
    vsync_idle_low=False,
    de_idle_high=False,
    pclk_idle_high=False,
    pclk_active_neg=False,
    disp_active_low=False,
    refresh_on_demand=False,
    bb_inval_cache=False,
)

display_drv = BusDisplay(
    display_bus,
    width=720,
    height=720,
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

i2c = I2C(0)
touch_drv = CST8XX(i2c)
touch_read_func = touch_drv.touches
touch_rotation_table=None
