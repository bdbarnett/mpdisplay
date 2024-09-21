# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
PyDevices touch_keypad

Matrix keypad helper for touch displays on PyDevices

Divides the display into a grid of rows and columns.
Returns the key number of the associated cell pressed.

Also passes through the key from any KEYDOWN events from the display.

Usage:
from touch_keypad import Keypad
from board_config import display_drv, broker

keys = [1, 2, 3, "A", "B", "C", "play", "pause", "esc"]
keypad = Keypad(broker.poll, 0, 0, display_drv.width, display_drv.height, cols=3, rows=3, keys=keys)
while True:
    if key := keypad.read():
        print(key)
"""

from .events import Events
try:
    from basedisplay import Area
except ImportError:
    print("basedisplay module not found.  Keypad.areas attribut will not be available.")
    Area = None


class Keypad:
    def __init__(self, poll, x, y, w, h, cols=3, rows=3, keys=None):
        self._keys = keys if keys else [i for i in range(cols * rows)]
        self._poll = poll
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cols = cols
        self.rows = rows
        self.key_width = kw = w / cols
        self.key_height = kh = h / rows
        if Area:
            self.areas = [Area(x + kw * i, y + kh * j, kw, kh) for j in range(rows) for i in range(cols)]


    def read(self):
        event = self._poll()
        if event and event.type == Events.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            if x < self.x or x > self.x + self.w or y < self.y or y > self.y + self.h:
                return None
            col = int((x - self.x) / self.key_width)
            row = int((y - self.y) / self.key_height)
            # BUG:  Sometimes throws an IndexError in Wokwi if the touch is on the last line
            # Instead of doing a bounds check we just catch the exception.
            try:
                key = self._keys[row * self.cols + col]
                return key
            except IndexError:
                pass

        if event and event.type == Events.KEYDOWN:
            key = event.key
            return key

        return None
