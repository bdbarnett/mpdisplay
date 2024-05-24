from ._area import Area
from ._binfont import BinFont, text as atext, btext, bfont_width, bfont_height
from . import _shapes as shapes
from .tools import bitmap, pbitmap, write, write_width, text as ttext
from .palettes import get_palette

def text(canvas, first_arg, *args, **kwargs):
    if isinstance(first_arg, (str, bytes)):
        return atext(canvas, first_arg, *args, **kwargs)
    else:
        return ttext(canvas, first_arg, *args, **kwargs)


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


class ExtendedShapes:
    # Used by framebuf_plus.py
    # Does not include hline, vline, line, rect, ellipse, poly
    arc = shapes.arc
    circle = shapes.circle
    round_rect = shapes.round_rect
    polygon = shapes.polygon
    atext = atext
    btext = btext
    ttext = ttext
    bfont_width = bfont_width
    bfont_height = bfont_height
    bitmap = bitmap
    pbitmap = pbitmap
    write = write
    write_width = write_width


class DisplayPrimitives(BasicShapes, ExtendedShapes):
    # Used by MPDisplay
    # Does not include fill_rect, fill, pixel
    get_palette = get_palette


class Shapes(BasicShapes, ExtendedShapes):
    # Can be used by the end-user
    # Includes fill_rect, fill, pixel
    fill_rect = shapes.fill_rect
    fill = shapes.fill
    pixel = shapes.pixel
