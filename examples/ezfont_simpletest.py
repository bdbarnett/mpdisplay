"""
Test the EZFont class.  EZFont is a wrapper for ezFBfont that allows rendering to non-framebuffer objects.
It can use fonts from https://github.com/easytarget/microPyEZfonts or
https://github.com/peterhinch/micropython-font-to-py
"""
from board_config import display_drv
from ezfont import EZFont
import gui.fonts.freesans20 as Font1


font1 = EZFont(display_drv, Font1, fg=0xF000, bg=0x0000, tkey=0x0000)
font1.write("Testing", 0, 0, fg=1, bg=0, tkey=None, halign=None, valign=None)

