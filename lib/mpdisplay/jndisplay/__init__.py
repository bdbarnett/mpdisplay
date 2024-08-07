# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
JNDisplay class for MPDisplay on Jupyter Notebook
"""

from .. import _BaseDisplay, Area
from IPython.display import display, update_display
from PIL import Image, ImageDraw


class JNDisplay(_BaseDisplay):
    '''
    A class to interface with CircuitPython FrameBuffer objects.
    '''
    _next_display_id = 0


    def __init__(self, width, height):
        """
        Initializes the display instance with the given parameters.
        """
        super().__init__()
        self._display_id = f"JNDisplay_{JNDisplay._next_display_id}"
        JNDisplay._next_display_id += 1
        self._width = width
        self._height = height
        self.requires_byte_swap = False
        self._rotation = 0
        self.color_depth = 16
        self._buffer = Image.new("RGB", (self.width, self.height))
        self._draw = ImageDraw.Draw(self._buffer)

        self.init()

    def show(self):
        update_display(self._buffer, display_id=self._display_id)

    ############### Required API Methods ################

    def init(self):
        """
        Initializes the display instance.  Called by __init__ and rotation setter.
        """
        display(self._buffer, display_id=self._display_id)

    def fill_rect(self, x, y, w, h, c):
        if self.requires_byte_swap:
            c = ((c & 0xFF00) >> 8) | ((c & 0x00FF) << 8)
        color = c & 0xFFFF
        r, g, b = self.color_rgb(color)
        x2 = x + w
        y2 = y + h
        top = min(y, y2)
        left = min(x, x2)
        bottom = max(y, y2)
        right = max(x, x2)
        self._draw.rectangle([(left, top), (right, bottom)], fill=(r, g, b))
        return Area(left, top, right - left, bottom - top)

    def blit_rect(self, buf, x, y, w, h):
        if self.requires_byte_swap:
            self._swap_bytes(buf, w * h)

        BPP = self.color_depth // 8
        if x < 0 or y < 0 or x + w > self.width or y + h > self.height:
            raise ValueError("The provided x, y, w, h values are out of range")
        if len(buf) != w * h * BPP:
            raise ValueError("The source buffer is not the correct size")

        for j in range(h):
            for i in range(w):
                color = buf[(j * w + i) * BPP:(j * w + i) * BPP + BPP]
                self.pixel(x + i, y + j, color)
        
        return Area(x, y, w, h)

    def pixel(self, x, y, c):
        if self.requires_byte_swap:
            c = ((c & 0xFF00) >> 8) | ((c & 0x00FF) << 8)
        r, g, b = self.color_rgb(c)
        self._draw.point((x, y), fill=(r, g, b))
        return Area(x, y, 1, 1)