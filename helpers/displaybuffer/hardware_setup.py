'''
hardware_setup.py - hardware setup for MicroPython-GUI with DisplayBuffer on MPDisplay
Usage:
    from hardware_setup import display
    <your code here>
'''
from displaybuf import DisplayBuffer as SSD
from board_config import display_drv
from mpdisplay import Events

# format = SSD.GS4_HMSB  # 4-bit (16 item) lookup table of 16-bit RGB565 colors; w*h/2 buffer
# format = SSD.GS8  # 256 8-bit RGB332 colors; w*h buffer
format = SSD.RGB565  # all 65,536 16-bit RGB565 colors; w*h*2 buffer

ssd = SSD(display_drv, format)


class TPad:
    def __init__(self, read_func):
        self._read_func = read_func
        self.col = None
        self.row = None

    def poll(self):
        event = self._read_func()
        if event and event.type == Events.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            self.col = x
            self.row = y
            return True
        else:
            return False

tpad = TPad(display_drv.poll_event)

from gui.core.tgui import Display
display = Display(ssd, tpad)
