# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
FBDisplay class for MPDisplay.
"""

from . import _BaseDisplay
from area import Area

try:
    from ulab import numpy as np
except ImportError:
    import numpy as np


class FBDisplay(_BaseDisplay):
    '''
    A class to interface with CircuitPython FrameBuffer objects.
    '''
    def __init__(self, buffer, width=None, height=None, stride=None, reverse_bytes_in_word=False,):
        """
        Initializes the display instance with the given parameters.

        :param fb: The CircuitPython FrameBuffer object.
        :type width: FrameBuffer
        """
        super().__init__()
        self._raw_buffer = buffer
        self._buffer = memoryview(buffer)
        self._width = width if width else buffer.width
        self._height = height if height else buffer.height
#        self._stride = stride if stride else buffer.row_stride // 2
        self.requires_byte_swap = reverse_bytes_in_word
        self._rotation = 0
        self.color_depth = 16

        self.init()

    ############### Required API Methods ################

    def init(self):
        """
        Initializes the display instance.  Called by __init__ and rotation setter.
        """
        pass


    def fill_rect(self, x, y, w, h, c):
        BPP = self.color_depth // 8
        x2 = x + w
        y2 = y + h
        top = min(y, y2)
        left = min(x, x2)
        bottom = max(y, y2)
        right = max(x, x2)
        color = c & 0xFFFF
        arr = np.frombuffer(self._buffer, dtype=np.uint16)
        for _y in range(y, y + h):
            begin = (_y * self.width + left)
            end = begin + w
            arr[begin : end] = color
        return Area(left, top, right - left, bottom - top)

    def blit_rect(self, buf, x, y, width, height):
        BPP = self.color_depth // 8
        if x < 0 or y < 0 or x + width > self.width or y + height > self.height:
            raise ValueError("The provided x, y, w, h values are out of range")
        if len(buf) != width * height * BPP:
            raise ValueError("The source buffer is not the correct size")
        arr = np.frombuffer(self._buffer, dtype=np.uint8)
        for row in range(height):
            source_begin = row * width * BPP
            source_end = source_begin + width * BPP
            dest_begin = ((y + row) * self.width + x) * BPP
            dest_end = dest_begin + width * BPP
            arr[dest_begin : dest_end] = buf[source_begin : source_end]
        return Area(x, y, width, height)
