# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
FBDisplay class for PyDevices.
"""

from pyd_basedisplay import BaseDisplay, np, Area, swap_bytes
if not np:
    raise ImportError("This module depends on the numpy module. Please install it.")


class FBDisplay(BaseDisplay):
    '''
    A class to interface with CircuitPython FrameBuffer objects.
    '''
    def __init__(self, buffer, width=None, height=None, reverse_bytes_in_word=False):
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
        self._requires_byte_swap = reverse_bytes_in_word
        self._auto_byte_swap_enabled = self._requires_byte_swap
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
        """
        Fills a rectangle with the given color.
               
        :param x: The x-coordinate of the top-left corner of the rectangle.
        :type x: int
        :param y: The y-coordinate of the top-left corner of the rectangle.
        :type y: int
        :param w: The width of the rectangle.
        :type w: int
        :param h: The height of the rectangle.
        :type h: int
        :param c: The color of the rectangle.
        :type c: int
        
        :return: The Area object representing the rectangle.
        :rtype: Area
        """
        if self._auto_byte_swap_enabled:
            c = ((c & 0xFF00) >> 8) | ((c & 0x00FF) << 8)

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

    def blit_rect(self, buf, x, y, w, h):
        """
        Blits a buffer to the display at the given coordinates.

        :param buf: The buffer to blit.
        :type buf: bytearray
        :param x: The x-coordinate of the top-left corner of the blit.
        :type x: int
        :param y: The y-coordinate of the top-left corner of the blit.
        :type y: int
        :param w: The width of the blit.
        :type w: int
        :param h: The height of the blit.
        :type h: int

        :return: The Area object representing the blit.
        :rtype: Area
        """
        if self._auto_byte_swap_enabled:
            swap_bytes(buf, w * h)

        BPP = self.color_depth // 8
        if x < 0 or y < 0 or x + w > self.width or y + h > self.height:
            raise ValueError("The provided x, y, w, h values are out of range")
        if len(buf) != w * h * BPP:
            raise ValueError("The source buffer is not the correct size")
        arr = np.frombuffer(self._buffer, dtype=np.uint8)
        for row in range(h):
            source_begin = row * w * BPP
            source_end = source_begin + w * BPP
            dest_begin = ((y + row) * self.width + x) * BPP
            dest_end = dest_begin + w * BPP
            arr[dest_begin : dest_end] = buf[source_begin : source_end]
        return Area(x, y, w, h)

    def pixel(self, x, y, c):
        """
        Gets the color of the pixel at the given coordinates.

        :param x: The x-coordinate of the pixel.
        :type x: int
        :param y: The y-coordinate of the pixel.
        :type y: int
        :param c: The color to set the pixel to.
        :type c: int
        """
        self.fill_rect(x, y, 1, 1, c)

    ############### Optional API Methods ################

    def show(self):
        self._raw_buffer.refresh()
