'''
color_setup.py - color setup using the GUI framework
Usage:
    from color_setup import ssd
    <your code here>
'''
from gui_framework import SSD
import framebuf
import board_config

# mode = framebuf.GS4_HMSB
# mode = framebuf.GS8
mode = framebuf.RGB565

ssd = SSD(board_config.display_drv, mode)
