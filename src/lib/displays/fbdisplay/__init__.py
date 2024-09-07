# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
PyDevices fbdisplay
"""

from basedisplay import BaseDisplay, np, Area, swap_bytes

if not np:
    raise ImportError("This module depends on the numpy module. Please install it.")


class FBDisplay(BaseDisplay):
    """
    A class to interface with CircuitPython FrameBuffer objects.

    Args:
        buffer (FrameBuffer): The CircuitPython FrameBuffer object.
        width (int, optional): The width of the display. Defaults to None.
        height (int, optional): The height of the display. Defaults to None.
        reverse_bytes_in_word (bool, optional): Whether to reverse the bytes in a word. Defaults to False.

    Attributes:
        color_depth (int): The color depth of the display
    """

    def __init__(self, buffer, width=None, height=None, reverse_bytes_in_word=False):
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

        Args:
            x (int): The x-coordinate of the top-left corner of the rectangle.
            y (int): The y-coordinate of the top-left corner of the rectangle.
            w (int): The width of the rectangle.
            h (int): The height of the rectangle.
            c (int): The color to fill the rectangle with.

        Returns:
            Area: The Area object representing the filled rectangle.
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
            begin = _y * self.width + left
            end = begin + w
            arr[begin:end] = color
        return Area(left, top, right - left, bottom - top)

    def blit_rect(self, buf, x, y, w, h):
        """
        Blits a buffer to the display at the given coordinates.

        Args:
            buf (memoryview): The buffer to blit.
            x (int): The x-coordinate of the buffer.
            y (int): The y-coordinate of the buffer.
            w (int): The width of the buffer.
            h (int): The height of the buffer.

        Returns:
            Area: The Area object representing the blitted buffer.
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
            arr[dest_begin:dest_end] = buf[source_begin:source_end]
        return Area(x, y, w, h)

    def pixel(self, x, y, c):
        """
        Sets the color of the pixel at the given coordinates.

        Args:
            x (int): The x-coordinate of the pixel.
            y (int): The y-coordinate of the pixel.
            c (int): The color of the pixel.

        Returns:
            Area: The Area object representing the pixel.
        """
        return self.fill_rect(x, y, 1, 1, c)

    ############### Optional API Methods ################

    def show(self):
        """
        Refreshes the display.
        """
        self._raw_buffer.refresh()
