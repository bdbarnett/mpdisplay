# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
PyDevices gfx
"""

from basedisplay import Area  # noqa: F401
from .shapes import arc, blit, blit_rect, blit_transparent, circle, ellipse, fill, fill_rect, hline, line, pixel, poly, polygon, rect, round_rect, triangle, vline  # noqa: F401
from .binfont import text, text8, text14, text16


def color888(r, g, b):
    """
    Convert RGB values to a 24-bit color value.

    :param r: The red value.
    :type r: int
    :param g: The green value.
    :type g: int
    :param b: The blue value.
    :type b: int
    :return: The 24-bit color value.
    :rtype: int
    """
    return (r << 16) | (g << 8) | b

def color565(r, g=0, b=0):
    """
    Convert RGB values to a 16-bit color value.

    :param r: The red value.
    :type r: int
    :param g: The green value.
    :type g: int
    :param b: The blue value.
    :type b: int
    :return: The 16-bit color value.
    :rtype: int
    """
    if isinstance(r, (tuple, list)):
        r, g, b = r[:3]
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def color565_swapped(r, g=0, b=0):
    # Convert r, g, b in range 0-255 to a 16 bit color value RGB565
    # ggbbbbbb rrrrrggg
    if isinstance(r, (tuple, list)):
        r, g, b = r[:3]
    color = color565(r, g, b)
    return (color & 0xFF) << 8 | (color & 0xFF00) >> 8

def color332(r, g, b):
    # Convert r, g, b in range 0-255 to an 8 bit color value RGB332
    # rrrgggbb
    return (r & 0xE0) | ((g >> 3) & 0x1C) | (b >> 6)

def color_rgb(color):
    """
    color can be an 16-bit integer or a tuple, list or bytearray of length 2 or 3.
    """
    if isinstance(color, int):
        # convert 16-bit int color to 2 bytes
        color = (color & 0xFF, color >> 8)
    if len(color) == 2:
        r = color[1] & 0xF8 | (color[1] >> 5) & 0x7  # 5 bit to 8 bit red
        g = color[1] << 5 & 0xE0 | (color[0] >> 3) & 0x1F  # 6 bit to 8 bit green
        b = color[0] << 3 & 0xF8 | (color[0] >> 2) & 0x7  # 5 bit to 8 bit blue
    else:
        r, g, b = color
    return (r, g, b)


class Draw:
    """
    A Draw class to draw shapes onto a specified canvas.
    """

    def __init__(self, canvas):
        self.canvas = canvas

    def arc(self, x, y, r, a0, a1, c):
        return arc(self.canvas, x, y, r, a0, a1, c)

    def blit(self, source, x, y, key=-1, palette=None):
        return blit(self.canvas, source, x, y, key, palette)

    def blit_rect(self, buf, x, y, w, h):
        if hasattr(self.canvas, "blit_rect"):
            return self.canvas.blit_rect(buf, x, y, w, h)
        return blit_rect(self.canvas, buf, x, y, w, h)

    def blit_tranparent(self, buf, x, y, w, h, key=None):
        return blit_transparent(self.canvas, buf, x, y, w, h, key)

    def circle(self, x, y, r, c, f=False):
        return circle(self.canvas, x, y, r, c, f)

    def ellipse(self, x, y, r1, r2, c, f=False, m=0b1111, w=None, h=None):
        return ellipse(self.canvas, x, y, r1, r2, c, f, m, w, h)

    def fill(self, c):
        return fill(self.canvas, c)

    def fill_rect(self, x, y, w, h, c):
        return fill_rect(self.canvas, x, y, w, h, c)

    def hline(self, x, y, w, c):
        return hline(self.canvas, x, y, w, c)

    def line(self, x1, y1, x2, y2, c):
        return line(self.canvas, x1, y1, x2, y2, c)

    def pixel(self, x, y, c):
        return pixel(self.canvas, x, y, c)

    def poly(self, x, y, coords, c, f=False):
        return poly(self.canvas, x, y, coords, c, f)

    def polygon(self, points, x, y, c, angle=0, center_x=0, center_y=0):
        return polygon(self.canvas, points, x, y, c, angle, center_x, center_y)

    def rect(self, x, y, w, h, c, f=False):
        return rect(self.canvas, x, y, w, h, c, f)

    def round_rect(self, x, y, w, h, r, c, f=False):
        return round_rect(self.canvas, x, y, w, h, r, c, f)

    def triangle(self, x1, y1, x2, y2, x3, y3, c, f=False):
        return triangle(self.canvas, x1, y1, x2, y2, x3, y3, c, f)

    def vline(self, x, y, h, c):
        return vline(self.canvas, x, y, h, c)

    def text(self, *args, **kwargs):
        return text(self.canvas, *args, **kwargs)

    def text8(self, *args, **kwargs):
        return text8(self.canvas, *args, **kwargs)

    def text14(self, *args, **kwargs):
        return text14(self.canvas, *args, **kwargs)

    def text16(self, *args, **kwargs):
        return text16(self.canvas, *args, **kwargs)
