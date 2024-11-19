"""
color_setup.py - color setup for DisplayBuffer with pydisplay
Usage:
    from color_setup import ssd
    <your code here>
"""

from displaybuf import DisplayBuffer as SSD
from board_config import display_drv
import sys

# SSD.RGB565 is supported by all implementations, so set it as the default format
# Micropython also supports SSD.GS4_HMSB and SSD.GS8

if sys.implementation.name == "micropython":
    # format = SSD.GS4_HMSB  # 4-bit (16 item) lookup table of 16-bit RGB565 colors; w*h/2 buffer
    # format = SSD.GS8  # 256 8-bit RGB332 colors; w*h buffer
    format = SSD.RGB565  # all 65,536 16-bit RGB565 colors; w*h*2 buffer
else:
    format = SSD.RGB565

ssd = SSD(display_drv, format)
