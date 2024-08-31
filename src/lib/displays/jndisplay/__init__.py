# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
JNDisplay class for MPDisplay on Jupyter Notebook
"""

from basedisplay import BaseDisplay, Area, color_rgb
from IPython.display import display, update_display # type: ignore
from PIL import Image, ImageDraw # type: ignore


class JNDisplay(BaseDisplay):
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
        self._requires_byte_swap = False
        self._auto_byte_swap_enabled = self._requires_byte_swap
        self._rotation = 0
        self.color_depth = 16
        self._buffer = Image.new("RGB", (self.width, self.height))
        self._draw = ImageDraw.Draw(self._buffer)

        self.init()

    ############### Required API Methods ################

    def init(self):
        """
        Initializes the display instance.  Called by __init__ and rotation setter.
        """
        display(self._buffer, display_id=self._display_id)

    def fill_rect(self, x, y, w, h, c):
        color = c & 0xFFFF
        r, g, b = color_rgb(color)
        x2 = x + w
        y2 = y + h
        top = min(y, y2)
        left = min(x, x2)
        bottom = max(y, y2)
        right = max(x, x2)
        self._draw.rectangle([(left, top), (right, bottom)], fill=(r, g, b))
        return Area(left, top, right - left, bottom - top)

    def blit_rect(self, buf, x, y, w, h):
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
        r, g, b = color_rgb(c)
        self._draw.point((x, y), fill=(r, g, b))
        return Area(x, y, 1, 1)

    ############### Optional API Methods ################

    def show(self):
        update_display(self._buffer, display_id=self._display_id)
