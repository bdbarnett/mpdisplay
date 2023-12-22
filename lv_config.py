"""
    lv_config.py - LVGL configuration file
    Save this file as `display_driver.py` to use with LVGL examples
"""

# Allocate buffers as early as possible to ensure they are in SRAM if desired
# Note: other imports are out of the suggested order to allow for this
import heap_caps

# Change these 3 lines to your needs
buf_size = 320*480*2 // 10  # TODO: add note about buffer sizes
fbuf1 = heap_caps.malloc(buf_size, heap_caps.CAP_DMA)  # TODO: add note malloc and CAPS
fbuf2 = heap_caps.malloc(buf_size, heap_caps.CAP_DMA)


import lvgl as lv
import lv_driver_framework
import board_config

# Change lv.COLOR_FORMAT to match your display
display = lv_driver_framework.DisplayDriver(
    board_config.display_drv, lv.COLOR_FORMAT.RGB565, fbuf1, fbuf2)

# Change touch_rotation to match your display
touch = lv_driver_framework.TouchDriver(
    board_config.touch_drv_read, touch_rotation=5)

# Uncomment if your board has an encoder
# encoder = lv_driver_framework.EncoderDriver(
#     board_config.encoder_drv_read, board_config.encoder_button_read)
