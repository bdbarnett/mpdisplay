# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
touch_keypad.py - Matrix keypad helper for touch displays on MPDisplay

Divides the display into a grid of rows and columns.
Returns the key number of the associated cell pressed.

Also passes through the key from any KEYDOWN events from the display.

Usage:
from touch_keypad import Keypad
from board_config import display_drv, broker

keys = [1, 2, 3, "A", "B", "C", "play", "pause", "esc"]
keypad = Keypad(broker.poll, display_drv.width, display_drv.height, cols=3, rows=3, keys=keys)
while True:
    if key := keypad.read():
        print(key)
"""
from .events import Events


class Keypad:
    def __init__(self, poll, width, height, cols=3, rows=3, keys=None):
        self._keys = keys if keys else [i + 1 for i in range(cols * rows)]
        self._poll = poll
        self._width = width
        self._height = height
        self._cols = cols
        self._rows = rows

    def read(self):
        event = self._poll()
        if event and event.type == Events.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            col = x // (self._width // self._cols)
            row = y // (self._height // self._rows)
            key = self._keys[row * self._cols + col]
            return key

        if event and event.type == Events.KEYDOWN:
            key = event.key
            return key

        return None
