from ._area import Area
from ._binfont import BinFont, text as atext, btext, bfont_width, bfont_height
from .tools import bitmap, pbitmap, write, write_width, polygon, text as ttext
from .palettes import get_palette

try:
    from . import _shapes_numpy as shapes
    print("Using _shapes_numpy.")
except Exception as e:
    print(f"Error importing _shapes_numpy: {e}.  \nFalling back to _shapes.")
    from . import _shapes as shapes


def text(canvas, first_arg, *args, **kwargs):
    if isinstance(first_arg, (str, bytes)):
        return atext(canvas, first_arg, *args, **kwargs)
    else:
        return ttext(canvas, first_arg, *args, **kwargs)


class BasicShapes:
    # Used by framebuf.py
    # Do not include fill_rect or pixel because they need to be
    # specific to the object that uses them
    fill = shapes.fill
    hline = shapes.hline
    vline = shapes.vline
    line = shapes.line
    rect = shapes.rect
    ellipse = shapes.ellipse
    poly = shapes.poly
    text = text


class ExtendedShapes:
    # Used by framebuf_plus.py
    # Does not include shapes from BasicShapes
    arc = shapes.arc
    circle = shapes.circle
    round_rect = shapes.round_rect
    polygon = polygon
    blit_rect = shapes.blit_rect
    atext = atext
    btext = btext
    ttext = ttext
    bfont_width = bfont_width
    bfont_height = bfont_height
    bitmap = bitmap
    pbitmap = pbitmap
    write = write
    write_width = write_width


class Shapes(BasicShapes, ExtendedShapes):
    # Can be used by the end-user
    pass


class DisplayPrimitives(Shapes):
    # Used by MPDisplay
    get_palette = get_palette
