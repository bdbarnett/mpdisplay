from ._area import Area
from ._binfont import BinFont, text, btext, bfont_width, bfont_height
from . import _shapes as shapes


class BasicShapes:
    # Used by framebuf.py
    # Does not include fill_rect, fill, pixel
    hline = shapes.hline
    vline = shapes.vline
    line = shapes.line
    rect = shapes.rect
    ellipse = shapes.ellipse
    poly = shapes.poly
    text = text

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

class DisplayShapes(BasicShapes, ExtendedShapes):
    # Used by MPDisplay
    # Does not include fill_rect, fill, pixel
    pass # This class is just a collection of methods, no need to instantiate it

class Shapes(BasicShapes, ExtendedShapes):
    # Can be used by the end-user
    # Includes fill_rect, fill, pixel
    fill_rect = shapes.fill_rect
    fill = shapes.fill
    pixel = shapes.pixel