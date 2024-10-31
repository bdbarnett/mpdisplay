# SPDX-FileCopyrightText: <text> 2018 Kattni Rembor, Melissa LeBlanc-Williams
# and Tony DiCola, for Adafruit Industries.
# Copyright 2024 Brad Barnett
# Original file created by Damien P. George
# SPDX-License-Identifier: MIT

"""
`framebuf`
====================================================

*Python framebuf module, based on the micropython framebuf module.
Will not be imported on MicroPython boards since framebuf is included
in the compiled firmware.

framebuf on MicroPython does not return an Area object for methods that
write to the buffer, but BasicShapes does, so the native shape methods
here return an Area object in order to keep it consistent within this
library.  It is recommended to use framebuf_plus.py instead of this if
you need to use the returned Areas so your code will be transferable.

"""

import pygraphics

try:
    from ulab import numpy as np 
except ImportError:
    try:
        import numpy as np 
    except ImportError:
        np = None


# Framebuf format constants:
MVLSB = 0  # Single bit displays (like SSD1306 OLED)
MONO_VLSB = 0  # Single bit displays (like SSD1306 OLED)
MONO_HLSB = 3  # Single bit files like PBM (Portable BitMap)
MONO_HMSB = 4  # Single bit displays where the bits in a byte are horizontally mapped. Each byte occupies 8 horizontal pixels with bit 0 being the leftmost.
RGB565 = 1  # 16-bit color displays
GS2_HMSB = 5  # 2-bit color displays like the HT16K33 8x8 Matrix
GS4_HMSB = 2  # Unimplemented!
GS8 = 6  # Unimplemented!

# Font file constants:
# To maintain compatibility with MicroPython framebuf, the font should be 8x8, scale 1.
_FONT_FILE = None  # Use the default font
_FONT_WIDTH = 8
_FONT_HEIGHT = 8
_FONT_SCALE = 1


class BasicShapes:
    # Inherited from the FrameBuffer class
    # Do not include fill, fill_rect or pixel because they need to be
    # specific to the class format that uses them
    blit = pygraphics.blit
    ellipse = pygraphics.ellipse
    hline = pygraphics.hline
    line = pygraphics.line
    poly = pygraphics.poly
    rect = pygraphics.rect
    vline = pygraphics.vline
    text = pygraphics.text


class MVLSBFormat:
    """MVLSBFormat"""

    depth = 1

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y >> 3) * framebuf._stride + x
        offset = y & 0x07
        framebuf._buffer[index] = (framebuf._buffer[index] & ~(0x01 << offset)) | (
            (color != 0) << offset
        )

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        index = (y >> 3) * framebuf._stride + x
        offset = y & 0x07
        return (framebuf._buffer[index] >> offset) & 0x01

    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        if color:
            fill = 0xFF
        else:
            fill = 0x00
        for i in range(len(framebuf._buffer)):  # pylint: disable=consider-using-enumerate
            framebuf._buffer[i] = fill

    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments
        while height > 0:
            index = (y >> 3) * framebuf._stride + x
            offset = y & 0x07
            for w_w in range(width):
                framebuf._buffer[index + w_w] = (
                    framebuf._buffer[index + w_w] & ~(0x01 << offset)
                ) | ((color != 0) << offset)
            y += 1
            height -= 1


class MHLSBFormat:
    depth = 1

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y * framebuf._stride + x) >> 3 
        offset = 7 - (x & 0x07)
        framebuf._buffer[index] = (framebuf._buffer[index] & ~(0x01 << offset)) | ((color != 0) << offset)

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        index = (x + y * framebuf._stride) >> 3
        offset = 7 - (x & 0x07)
        return (framebuf._buffer[index] >> offset) & 0x01
    
    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments
        for _x in range(x, x + width):
            offset = 7 - _x & 0x07
            for _y in range(y, y + height):
                index = (_y * framebuf._stride + _x) >> 3
                framebuf._buffer[index] = (
                    framebuf._buffer[index] & ~(0x01 << offset)
                ) | ((color != 0) << offset)

    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        if color:
            fill = 0xFF
        else:
            fill = 0x00
        for i in range(len(framebuf._buffer)):
            framebuf._buffer[i] = fill


class MHMSBFormat:
    """MHMSBFormat"""

    depth = 1

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y * framebuf._stride + x) >> 3
        offset = x & 0x07
        framebuf._buffer[index] = (framebuf._buffer[index] & ~(0x01 << offset)) | (
            (color != 0) << offset
        )

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        index = (y * framebuf._stride + x) // 8
        offset = 7 - x & 0x07
        return (framebuf._buffer[index] >> offset) & 0x01

    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        if color:
            fill = 0xFF
        else:
            fill = 0x00
        for i in range(len(framebuf._buffer)):  # pylint: disable=consider-using-enumerate
            framebuf._buffer[i] = fill

    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments
        for _x in range(x, x + width):
            offset = 7 - _x & 0x07
            for _y in range(y, y + height):
                index = (_y * framebuf._stride + _x) // 8
                framebuf._buffer[index] = (
                    framebuf._buffer[index] & ~(0x01 << offset)
                ) | ((color != 0) << offset)


class RGB565Format:
    """
    This class implements the RGB565 format
    It assumes a little-endian byte order in the frame buffer
    """

    depth = 16

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y * framebuf._stride + x) * 2
        framebuf._buffer[index : index + 2] = (color & 0xFFFF).to_bytes(2, "little")

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        index = (y * framebuf._stride + x) * 2
        color = framebuf._buffer[index : index + 2]
        color = int.from_bytes(color, "little")
        return color

    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        rgb565_color = (color & 0xFFFF).to_bytes(2, "little")
        if np:
            rgb565_color_int = int.from_bytes(rgb565_color, "little")
            arr = np.frombuffer(framebuf._buffer, dtype=np.uint16)
            arr[:] = rgb565_color_int
        else:
            for i in range(0, len(framebuf._buffer), 2):
                framebuf._buffer[i : i + 2] = rgb565_color

    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments
        rgb565_color = (color & 0xFFFF).to_bytes(2, "little")
        if np:
            rgb565_color_int = int.from_bytes(rgb565_color, "little")
            arr = np.frombuffer(framebuf._buffer, dtype=np.uint16)
            for _y in range(y, y + height):
                arr[_y * framebuf._stride + x : _y * framebuf._stride + x + width] = (
                    rgb565_color_int
                )
        else:
            for _y in range(2 * y, 2 * (y + height), 2):
                offset2 = _y * framebuf._stride
                for _x in range(2 * x, 2 * (x + width), 2):
                    index = offset2 + _x
                    framebuf._buffer[index : index + 2] = rgb565_color


class GS2HMSBFormat:
    """GS2HMSBFormat"""

    depth = 2

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y * framebuf._stride + x) >> 2
        pixel = framebuf._buffer[index]

        shift = (x & 0b11) << 1
        mask = 0b11 << shift
        color = (color & 0b11) << shift

        framebuf._buffer[index] = color | (pixel & (~mask))

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        index = (y * framebuf._stride + x) >> 2
        pixel = framebuf._buffer[index]

        shift = (x & 0b11) << 1
        return (pixel >> shift) & 0b11

    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        if color:
            bits = color & 0b11
            fill = (bits << 6) | (bits << 4) | (bits << 2) | (bits << 0)
        else:
            fill = 0x00

        framebuf._buffer = [fill for i in range(len(framebuf._buffer))]

    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw the outline and interior of a rectangle at the given location, size and color."""
        # pylint: disable=too-many-arguments
        for _x in range(x, x + width):
            for _y in range(y, y + height):
                GS2HMSBFormat.set_pixel(framebuf, _x, _y, color)


class GS4HMSBFormat:
    depth = 4


class GS8Format:
    depth = 8


class FrameBuffer(BasicShapes):
    """
    FrameBuffer object.

    Args:
        buffer (bytearray): The buffer to use for the frame buffer.
        width (int): The width of the frame buffer in pixels.
        height (int): The height of the frame buffer in pixels.
        format (int): The format of the frame buffer. One of:
            - ``MONO_VLSB``: Single bit displays (like SSD1306 OLED)
            - ``MONO_HLSB``: Single bit files like PBM (Portable BitMap)
            - ``MONO_HMSB``: Single bit displays where the bits in a byte are horizontally mapped
                Each byte occupies 8 horizontal pixels with bit 0 being the leftmost.
            - ``RGB565``: 16-bit color displays
            - ``GS2_HMSB``: 2-bit color displays like the HT16K33 8x8 Matrix
            - ``GS4_HMSB``: Unimplemented!
            - ``GS8``: Unimplemented!
        stride (int): The number of bytes between each horizontal line of the frame buffer
            If not given, it is assumed to be equal to the width.
    """

    def __init__(self, buffer, width, height, format, stride=None):
        self._buffer = buffer
        self._width = width
        self._height = height
        self._stride = stride if stride is not None else width
        self._font = None
        if format == MONO_VLSB:
            self._stride = (self._stride + 7) & ~7
            self._format = MVLSBFormat()
        elif format == MONO_HLSB:
            self._stride = (self._stride + 7) & ~7
            self._format = MHLSBFormat()
        elif format == MONO_HMSB:
            self._format = MHMSBFormat()
        elif format == RGB565:
            self._format = RGB565Format()
        elif format == GS2_HMSB:
            self._stride = (self._stride + 3) & ~3
            self._format = GS2HMSBFormat()
        elif format == GS4_HMSB:
            self._stride = (self._stride + 1) & ~1
            self._format = GS4HMSBFormat()
        elif format == GS8:
            self._format = GS8Format()
        else:
            raise ValueError("invalid format")

    @property
    def width(self):
        """
        The width of the FrameBuffer in pixels.
        """
        return self._width

    @property
    def height(self):
        """
        The height of the FrameBuffer in pixels.
        """
        return self._height

    def fill_rect(self, x, y, w, h, c):
        """
        Draw a rectangle at the given location, size and color.

        Args:
            x (int): The x-coordinate of the top left corner of the rectangle.
            y (int): The y-coordinate of the top left corner of the rectangle.
            w (int): The width of the rectangle.
            h (int): The height of the rectangle.
            c (int): The color of the rectangle.

        Returns:
            tuple: A tuple containing the x, y, width, and height of the rectangle
        """
        self._format.fill_rect(self, x, y, w, h, c)
        return (x, y, w, h)

    def pixel(self, x, y, c=None):
        """
        Set or get the color of a given pixel.

        Args:
            x (int): The x-coordinate of the pixel.
            y (int): The y-coordinate of the pixel.
            c (int): The color of the pixel. If not given, the color of the pixel is returned.

        Returns:
            int, tuple or None:  If c is not given, the color of the pixel is returned.
                If c is given and x and y are within the bounds of the FrameBuffer,
                the x, y, width, and height of the pixel are returned.
                If x and y are not within the bounds of the FrameBuffer, None is returned.
        """
        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            return None
        if c is None:
            return self._format.get_pixel(self, x, y)
        self._format.set_pixel(self, x, y, c)
        return (x, y, 1, 1)

    def fill(self, c):
        """
        Fill the entire FrameBuffer with the specified color.
        
        Args:
            c (int): The color to fill the FrameBuffer with.

        Returns:
            tuple: A tuple containing the x, y, width, and height of the FrameBuffer.
        """
        self._format.fill(self, c)
        return (0, 0, self._width, self._height)

    def scroll(self, xstep, ystep):
        """
        Shift the contents of the FrameBuffer by the given vector (xstep, ystep).
        This may leave a footprint of the previous colors in the FrameBuffer.

        Args:
            xstep (int): The number of pixels to shift the FrameBuffer in the x direction.
            ystep (int): The number of pixels to shift the FrameBuffer in the y direction.

        Raises:
            ValueError: If the FrameBuffer format depth is not a multiple of 8

        Returns:
            None
        """
        # Check to make sure self._format.depth is a multiple of 8
        if self._format.depth % 8 != 0:
            raise ValueError(
                "Scrolling is only implemented for depths that are multiples of 8"
            )

        BPP = self._format.depth // 8  # Bytes per pixel

        # Determine the width and height of the FrameBuffer
        width = self._width
        height = self._height

        # Calculate the number of bytes per row
        bytes_per_row = width * BPP

        # Iterate over each row in the appropriate order (top to bottom for ystep > 0, bottom to top for ystep < 0)
        if ystep > 0:
            y_range = range(height - 1, -1, -1)
        else:
            y_range = range(height)

        # Iterate over each row in the appropriate order
        for y in y_range:
            # Calculate the new row index
            new_y = y + ystep

            # Skip rows that go out of bounds
            if new_y < 0 or new_y >= height:
                continue

            # Calculate the byte offset for the current and new rows
            offset = y * bytes_per_row
            new_offset = new_y * bytes_per_row

            # Iterate over each column in the appropriate order (right to left for xstep > 0, left to right for xstep < 0)
            if xstep > 0:
                for i in range(bytes_per_row - 1, (xstep * BPP) - 1, -1):
                    self._buffer[new_offset + i] = self._buffer[
                        offset + i - (xstep * BPP)
                    ]
            elif xstep < 0:
                for i in range(-xstep * BPP, bytes_per_row):
                    self._buffer[new_offset + i] = self._buffer[
                        offset + i + (xstep * BPP)
                    ]
            else:
                # If there is no x shift, copy the row as is
                self._buffer[new_offset : new_offset + bytes_per_row] = self._buffer[
                    offset : offset + bytes_per_row
                ]


def FrameBuffer1(buffer, width, height, format, stride=None):
    """
    Create a new FrameBuffer object.  Here only for historical reasons.
    """
    return FrameBuffer(buffer, width, height, format, stride)
