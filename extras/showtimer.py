"""
Create a timer to call display_drv.show() periodically.
"""
from board_config import display_drv

from timer import Timer
from sys import platform

class ShowTimer:
    def __init__(self):
        self._tim = Timer(-1 if platform == "rp2" else 1)

    def start(self, period):
        self._tim.init(mode=Timer.PERIODIC, period=period, callback=self.do_something)

    def do_something(self, t):
        display_drv.show()

    def stop(self, t=None):
        self._tim.deinit()

# Create a timer that calls tt.do_something every 1ms
showtimer = ShowTimer()
showtimer.start(33)  
