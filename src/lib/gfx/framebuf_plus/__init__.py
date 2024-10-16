# SPDX-FileCopyrightText: <text> 2018 Kattni Rembor, Melissa LeBlanc-Williams
# and Tony DiCola, for Adafruit Industries.
# Copyright 2024 Brad Barnett
# Original file created by Damien P. George
# SPDX-License-Identifier: MIT

"""
PyDevices gfx.framebuf_plus

A subclass of FrameBuffer that adds some useful methods for drawing shapes and text.
Each method returns a bounding box (x, y, w, h) of the drawn shape to indicate
the area of the display that was modified.  This can be used to update only the
modified area of the display.
"""

# Inherits from frambuf.Framebuffer, which may be compiled into MicroPython
# or may be from framebuf.py.  This module should return an Area object, but
# the MicroPython framebuf module returns None, so the methods inherited from
# framebuf.FrameBuffer are overridden to return an Area object.
# The methods inherited from ExtendedShapes are not overridden, as they already
# return an Area object.
from framebuf import FrameBuffer as _FrameBuffer
from framebuf import (
    MVLSB,  # noqa: F401
    MONO_VLSB,
    MONO_HLSB,
    MONO_HMSB,
    RGB565,
    GS2_HMSB,
    GS4_HMSB,
    GS8,
)
from .. import Area
from .. import shapes
from .. import binfont
import struct

class ExtendedShapes:
    """
    All the methods from shapes.py except for
    those implemented in framebuf.FrameBuffer.
    """

    arc = shapes.arc
    blit_rect = shapes.blit_rect
    blit_transparent = shapes.blit_transparent
    circle = shapes.circle
    ellipse = shapes.ellipse
    polygon = shapes.polygon
    round_rect = shapes.round_rect
    triangle = shapes.triangle
    text8 = binfont.text8
    text14 = binfont.text14
    text16 = binfont.text16


class FrameBuffer(_FrameBuffer, ExtendedShapes):
    def __init__(self, buffer, width, height, format, *args, **kwargs):
        super().__init__(buffer, width, height, format, *args, **kwargs)
        self._width = width
        self._height = height
        self._fb_format = format
        if format == MONO_VLSB:
            self._color_depth = 1
        elif format == MONO_HLSB:
            self._color_depth = 1
        elif format == MONO_HMSB:
            self._color_depth = 1
        elif format == RGB565:
            self._color_depth = 16
        elif format == GS2_HMSB:
            self._color_depth = 2
        elif format == GS4_HMSB:
            self._color_depth = 4
        elif format == GS8:
            self._color_depth = 8
        else:
            raise ValueError("invalid format")

    @property
    def color_depth(self):
        return self._color_depth

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def buffer(self):
        return self._buffer
    
    @property
    def format(self):
        return self._fb_format

    def fill_rect(self, x, y, w, h, c):
        """
        Fill the given rectangle with the given color.

        Args:
            x (int): x coordinate
            y (int): y coordinate
            w (int): Width in pixels
            h (int): Height in pixels
            c (int): 565 encoded color
        """
        super().fill_rect(x, y, w, h, c)
        return Area(x, y, w, h)

    def pixel(self, x, y, c=None):
        """
        Draw a single pixel at the given location and color.

        Args:
            x (int): x coordinate
            y (int): y coordinate
            c (int): 565 encoded color (default: None)
        """
        if c is None:
            return super().pixel(x, y)
        super().pixel(x, y, c)
        return Area(x, y, 1, 1)

    def fill(self, c):
        """
        Fill the entire display with the given color.

        Args:
            c (int): 565 encoded color
        """
        super().fill(c)
        return Area(0, 0, self.width, self.height)

    def ellipse(self, x, y, rx, ry, c, f=False, m=0b1111):
        """
        Draw an ellipse at the given location, radii and color.

        Args:
            x (int): Center x coordinate
            y (int): Center y coordinate
            rx (int): X radius
            ry (int): Y radius
            c (int): 565 encoded color
            f (bool): Fill the ellipse (default: False)
            m (int): Bitmask to determine which quadrants to draw (default: 0b1111)
        """
        super().ellipse(x, y, rx, ry, c, f, m)
        return Area(x - rx, y - ry, 2 * rx, 2 * ry)

    def hline(self, x, y, w, c):
        """
        Draw a horizontal line at the given location, width and color.

        Args:
            x (int): x coordinate
            y (int): y coordinate
            w (int): Width in pixels
            c (int): 565 encoded color
        """
        super().hline(x, y, w, c)
        return Area(x, y, w, 1)

    def line(self, x1, y1, x2, y2, c):
        """
        Draw a line between the given start and end points and color.

        Args:
            x1 (int): Start x coordinate
            y1 (int): Start y coordinate
            x2 (int): End x coordinate
            y2 (int): End y coordinate
            c (int): 565 encoded color
        """
        super().line(x1, y1, x2, y2, c)
        return Area(min(x1, x2), min(y1, y2), abs(x2 - x1) + 1, abs(y2 - y1) + 1)

    def poly(self, x, y, coords, c, f=False):
        """
        Draw a polygon at the given location, coordinates and color.

        Args:
            x (int): x coordinate
            y (int): y coordinate
            coords (array): Array of x, y coordinate tuples
            c (int): 565 encoded color
            f (bool): Fill the polygon (default: False)
        """
        super().poly(x, y, coords, c, f)
        # Calculate the bounding box of the polygon
        # Convert the coords to a list of x, y tuples if it is not already
        if isinstance(coords, list):
            vertices = coords
        elif isinstance(coords, tuple):
            vertices = list(coords)
        else:
            # Check that the coords array has an even number of elements
            if len(coords) % 2 != 0:
                raise ValueError("coords must have an even number of elements")
            vertices = [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]
        # Find the min and max x and y values
        min_x = min([v[0] for v in vertices])
        min_y = min([v[1] for v in vertices])
        max_x = max([v[0] for v in vertices])
        max_y = max([v[1] for v in vertices])
        return Area(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def rect(self, x, y, w, h, c, f=False):
        """
        Draw a rectangle at the given location, size and color.

        Args:
            x (int): Top left corner x coordinate
            y (int): Top left corner y coordinate
            w (int): Width in pixels
            h (int): Height in pixels
            c (int): 565 encoded color
            f (bool): Fill the rectangle (default: False)
        """
        super().rect(x, y, w, h, c, f)
        return Area(x, y, w, h)

    def vline(self, x, y, h, c):
        """
        Draw a vertical line at the given location, height and color.

        Args:
            x (int): x coordinate
            y (int): y coordinate
            h (int): Height in pixels
            c (int): 565 encoded color
        """
        super().vline(x, y, h, c)
        return Area(x, y, 1, h)

    def text(self, s, x, y, c=1, scale=1, inverted=False, font_file=None, height=8):
        """
        Draw text at the given location, using the given font and color.

        Args:
            s (str): Text to draw
            x (int): x coordinate
            y (int): y coordinate
            c (int): 565 encoded color
            scale (int): Font scale (default: 1)
            inverted (bool): Invert the text (default: False)
            font_file (str): Font file (default: None)
            height (int): Font height in pixels (default: 8)
        """
        return binfont.text(self, s, x, y, c, scale, inverted, font_file, height=height)

    def blit(self, buf, x, y, key=-1, palette=None):
        """
        Blit the given buffer at the given location.

        Args:
            buf (FrameBuffer): FrameBuffer to blit
            x (int): x coordinate
            y (int): y coordinate
            key (int): Color key (default: -1)
            palette (list): Palette (default: None)
        """
        super().blit(buf, x, y, key, palette)
        return

    def save(self, filename=None):
        """
        Save the framebuffer to a file.  The file extension must match the format.

        Args:
            filename (str): Filename to save to
        """
        if filename is None:
            filename = "screenshot"
        file_ext = filename.split(".")[-1]
        if self.format == MONO_HLSB:
            if file_ext != "pbm":
                filename += ".pbm"
            with open(filename, "wb") as f:
                f.write(b"P4\n")
                f.write(f"{self.width} {self.height}\n".encode())
                f.write(self.buffer)
        elif self.format == GS2_HMSB:
            if file_ext != "pgm":
                filename += ".pgm"
            with open(filename, "wb") as f:
                f.write(b"P5\n")
                f.write(f"{self.width} {self.height}\n".encode())
                f.write(b"3\n")
                f.write(self.buffer)
        elif self.format == GS4_HMSB:
            if file_ext != "pgm":
                filename += ".pgm"
            with open(filename, "wb") as f:
                f.write(b"P5\n")
                f.write(f"{self.width} {self.height}\n".encode())
                f.write(b"15\n")
                f.write(self.buffer)
        elif self.format == GS8:
            if file_ext != "pgm":
                filename += ".pgm"
            with open(filename, "wb") as f:
                f.write(b"P5\n")
                f.write(f"{self.width} {self.height}\n".encode())
                f.write(b"255\n")
                f.write(self.buffer)
        elif self.format == RGB565:
            if file_ext != "bmp":
                filename += ".bmp"
            with open(filename, "wb") as f:
                f.write(b"BM")  # Offset 0: Signature
                f.write((54 + len(self.buffer)).to_bytes(4, "little"))  # Offset 2: File size
                f.write(b"\x00\x00\x00\x00")  # Offset 6: Unused
                f.write(b"\x36\x00\x00\x00")  # Offset 10: Offset to image data
                f.write(b"\x28\x00\x00\x00")  # Offset 14: DIB header size
                f.write(self.width.to_bytes(4, "little"))  # Offset 18: Width
                f.write(self.height.to_bytes(4, "little"))  # Offset 22: Height
                f.write(b"\x01\x00")  # Offset 26: Planes
                f.write(b"\x10\x00")  # Offset 28: Bits per pixel
                f.write(b"\x00\x00\x00\x00")  # Offset 30: Compression
                f.write(len(self.buffer).to_bytes(4, "little"))  # Offset 34: Image size
                f.write(b"\x00\x00\x00\x00\x00\x00\x00\x00")  # Offset 38: Horizontal and vertical resolution
                f.write(b"\x00\x00\x00\x00")  # Offset 46: Colors in palette
                f.write(b"\x00\x00\x00\x00")  # Offset 50: Important colors
                # The order of the lines is reversed.  We need to reverse them back.
                for i in range(self.height):
                    f.write(self.buffer[(self.height - i - 1) * self.width * 2 : (self.height - i) * self.width * 2])
        else:
            raise ValueError(f"Save method not implemented for format {self.format}")

    @staticmethod
    def from_file(filename):
        """
        Load a framebuffer from a file.

        Args:
            filename (str): Filename to load from
        """
        # Read the first two bytes to determine the file type
        with open(filename, "rb") as f:
            header = f.read(2)
            f.seek(0)
        if header == b"P4":
            return pbm_to_framebuffer(filename)
        elif header == b"P5":
            return pgm_to_framebuffer(filename)
        elif header == b"BM":
            return bmp_to_framebuffer(filename)
        else:
            raise ValueError(f"Unsupported file type {header}")

def pbm_to_framebuffer(filename):
    """
    Convert a PBM file to a MONO_HLSB FrameBuffer
    """
    with open(filename, "rb") as f:
        lines = f.readlines()
    if lines[0] != b"P4\n":
        raise ValueError(f"Invalid PBM file {filename}")
    width, height = map(int, lines[1].split())
    buffer = memoryview(bytearray((width + 7) // 8 * height))
    buffer[:] = b"".join(lines[2:])
    return FrameBuffer(buffer, width, height, MONO_HLSB)

def pgm_to_framebuffer(filename):
    """
    Convert a PGM file to a GS2_HMSB, GS4_HMSB or GS8 FrameBuffer
    """
    with open(filename, "rb") as f:
        lines = f.readlines()
    if lines[0] != b"P5\n":
        raise ValueError(f"Invalid PGM file {filename}")
    width, height = map(int, lines[1].split())
    max_value = int(lines[2])
    if max_value == 3:
        format = GS2_HMSB
        array_size = (width + 3) // 4 * height
    elif max_value == 15:
        format = GS4_HMSB
        array_size = (width + 1) // 2 * height
    elif max_value == 255:
        format = GS8
        array_size = width * height
    else:
        raise ValueError(f"Unsupported max value {max_value}")
    buffer = memoryview(bytearray(array_size))
    buffer[:] = b"".join(lines[3:])
    return FrameBuffer(buffer, width, height, format)

def bmp_to_framebuffer(filename):
    """
    Convert a BMP file to a RGB565 FrameBuffer
    First ensures planes is 1, bits per pixel is 16, and compression is 0.
    """
    with open(filename, "rb") as f:
        if f.read(2) != b"BM":
            raise ValueError("Not a BMP file")
        f.seek(10)
        data_offset = struct.unpack("<I", f.read(4))[0]
        f.seek(14)
        width, height = struct.unpack("<II", f.read(8))
        planes = struct.unpack("<H", f.read(2))[0]
        if planes != 1:
            raise ValueError("Invalid BMP file")
        bpp = struct.unpack("<H", f.read(2))[0]
        if bpp != 16:
            raise ValueError("Invalid color depth")
        f.seek(data_offset)
        buffer = memoryview(bytearray(width * height * 2))
        f.seek(54)
        for i in range(height):
            buffer[(height - i - 1) * width * 2 : (height - i) * width * 2] = f.read(width * 2)
    return FrameBuffer(buffer, width, height, RGB565)
