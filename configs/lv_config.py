"""
    lv_config.py - LVGL configuration file
    Save this file as `display_driver.py` to use with LVGL examples
"""

import board_config
import lvgl as lv
import gc

print("Creating buffers")
gc.collect()
color_format = lv.COLOR_FORMAT.RGB565
draw_buf1 = lv.draw_buf_create(board_config.display_drv.width, 50, color_format, 0)
draw_buf2 = lv.draw_buf_create(board_config.display_drv.width, 50, color_format, 0)
print("Buffers created.")

###################### Load LVGL and continue setting up

import lv_mpdisplay

display = lv_mpdisplay.DisplayDriver(
    board_config.display_drv,
    draw_buf1,
    draw_buf2,
    color_format,
    blocking=True,
)

print("finished loading lv_config.py")
