'''
color_setup.py - color setup using the GUI framework
Usage:
    from color_setup import ssd
    <your code here>
'''
from gui_framework import SSD
import framebuf
import board_config

mode = framebuf.GS4_HMSB  # 4-bit (16 item) lookup table of 16-bit RGB565 colors; w*h/2 buffer
# mode = framebuf.GS8  # 256 8-bit RGB332 colors; w*h buffer
# mode = framebuf.RGB565  # all 65,536 16-bit RGB565 colors; w*h*2 buffer

ssd = SSD(board_config.display_drv, mode)
