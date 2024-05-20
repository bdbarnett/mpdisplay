from ._area import Area
from ._binfont import BinFont, text, btext, bfont_width, bfont_height
from . import _shapes as shapes
from .tools import bitmap, pbitmap, write, write_width, text as ttext



class BasicShapes:
    # Used by framebuf.py
    # Does not include fill_rect, fill, pixel
    hline = shapes.hline
    vline = shapes.vline
    line = shapes.line
    rect = shapes.rect
    ellipse = shapes.ellipse
    poly = shapes.poly

    def text(self, first_arg, *args, **kwargs):
        if isinstance(first_arg, (str, bytes)):
            return text(self, first_arg, *args, **kwargs)
        else:
            return ttext(self, first_arg, *args, **kwargs)

class ExtendedShapes():
    # Used by framebuf_plus.py
    # Does not include hline, vline, line, rect, ellipse, poly
    arc = shapes.arc
    circle = shapes.circle
    roundrect = shapes.roundrect
    polygon = shapes.polygon
    btext = btext
    bfont_width = bfont_width
    bfont_height = bfont_height
    bitmap = bitmap
    pbitmap = pbitmap
    write = write
    write_width = write_width

class DisplayShapes(BasicShapes, ExtendedShapes):
    # Used by MPDisplay
    # Does not include fill_rect, fill, pixel
    pass

class Shapes(BasicShapes, ExtendedShapes):
    # Can be used by the end-user
    # Includes fill_rect, fill, pixel
    fill_rect = shapes.fill_rect
    fill = shapes.fill
    pixel = shapes.pixel