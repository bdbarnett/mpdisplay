"""
    lv_config.py - LVGL configuration file
    Save this file as `display_driver.py` to use with LVGL examples
"""

# Allocate buffers as early as possible to ensure they are in SRAM if desired
# Note: other imports are out of the suggested order to allow for this
import heap_caps

# Change these 3 lines to your needs
buf_size = 320*480*2 // 10  # TODO: add note about buffer sizes
fbuf1 = heap_caps.malloc(buf_size, heap_caps.CAP_DMA | heap_caps.CAP_INTERNAL)  # TODO: add note malloc and CAPS
fbuf2 = heap_caps.malloc(buf_size, heap_caps.CAP_DMA | heap_caps.CAP_INTERNAL)


import lvgl as lv
import lv_utils
import lv_driver_framework
import board_config

if not lv_utils.event_loop.is_running():
    eventloop = lv_utils.event_loop(asynchronous=False, exception_sink=None)

# Change color_format to match your display
display = lv_driver_framework.DisplayDriver(
    board_config.display_drv, fbuf1, fbuf2, color_format=lv.COLOR_FORMAT.NATIVE, blocking=True)

# Change touch_rotation to match your display
touch = lv_driver_framework.TouchDriver(
    board_config.touch_drv_read, touch_rotation=0)

# Uncomment if your board has an encoder
# encoder = lv_driver_framework.EncoderDriver(
#     board_config.encoder_drv_read, board_config.encoder_button_read)
