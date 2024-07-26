# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
A Draw class to draw shapes onto a specified canvas.  Shapes include:
['arc', 'blit', 'blit_rect', 'circle', 'ellipse', 'fill', 'fill_rect', 'hline', 
'line', 'pixel', 'poly', 'polygon', 'rect', 'round_rect', 'triangle', 'vline', 
text, bitmap, pbitmap, write]
"""

from . import shapes
from .pytext import pytext
from . import bitmap as _bitmap
from . import write as _write


class Draw:
    def __init__(self, canvas):
        self.canvas = canvas

    def arc(self, x, y, r, a0, a1, c):
        return shapes.arc(self.canvas, x, y, r, a0, a1, c)

    def blit(self, source, x, y, key=-1, palette=None):
        return shapes.blit(self.canvas, source, x, y, key, palette)

    def blit_rect(self, buf, x, y, w, h):
        return shapes.blit_rect(self.canvas, buf, x, y, w, h)

    def blit_tranparent(self, buf, x, y, w, h, key=None):
        return shapes.blit_transparent(self.canvas, buf, x, y, w, h, key)

    def circle(self, x, y, r, c, f=False):
        return shapes.circle(self.canvas, x, y, r, c, f)

    def ellipse(self, x, y, r1, r2, c, f=False, m=0b1111, w=None, h=None):
        return shapes.ellipse(self.canvas, x, y, r1, r2, c, f, m, w, h)

    def fill(self, c):
        return shapes.fill(self.canvas, c)

    def fill_rect(self, x, y, w, h, c):
        return shapes.fill_rect(self.canvas, x, y, w, h, c)

    def hline(self, x, y, w, c):
        return shapes.hline(self.canvas, x, y, w, c)

    def line(self, x1, y1, x2, y2, c):
        return shapes.line(self.canvas, x1, y1, x2, y2, c)

    def pixel(self, x, y, c):
        return shapes.pixel(self.canvas, x, y, c)

    def poly(self, x, y, coords, c, f=False):
        return shapes.poly(self.canvas, x, y, coords, c, f)

    def polygon(self, points, x, y, c, angle=0, center_x=0, center_y=0):
        return shapes.polygon(self.canvas, points, x, y, c, angle, center_x, center_y)

    def rect(self, x, y, w, h, c, f=False):
        return shapes.rect(self.canvas, x, y, w, h, c, f)

    def round_rect(self, x, y, w, h, r, c, f=False):
        return shapes.round_rect(self.canvas, x, y, w, h, r, c, f)

    def triangle(self, x1, y1, x2, y2, x3, y3, c, f=False):
        return shapes.triangle(self.canvas, x1, y1, x2, y2, x3, y3, c, f)

    def vline(self, x, y, h, c):
        return shapes.vline(self.canvas, x, y, h, c)

    def text(self, font, text, x0, y0, color=-1, background=0):
        return pytext(self.canvas, font, text, x0, y0, color, background)

    def bitmap(self, bitmap, x, y, index=0):
        return _bitmap.bitmap(self.canvas, bitmap, x, y, index)

    def pbitmap(self, bitmap, x, y, index=0):
        return _bitmap.pbitmap(self.canvas, bitmap, x, y, index)

    def write(self, font, string, x, y, fg=-1, bg=0):
        return _write.write(self.canvas, font, string, x, y, fg, bg)
    
    def write_width(self, font, string):
        return _write.write_width(self.canvas, font, string)