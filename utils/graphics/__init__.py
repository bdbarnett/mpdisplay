from area import Area
from binfont import text8, text14, text16
from rh_tools import bitmap, pbitmap, write, write_width, polygon, text as rh_text
from . import _shapes as shapes


def text(canvas, first_arg, *args, **kwargs):
    if isinstance(first_arg, (str, bytes)):
        return text8(canvas, first_arg, *args, **kwargs)
    else:
        return rh_text(canvas, first_arg, *args, **kwargs)


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
    blit_rect = shapes.blit_rect
    polygon = polygon
    bitmap = bitmap
    pbitmap = pbitmap
    write = write
    write_width = write_width
    text14 = text14
    text16 = text16


class Shapes(BasicShapes, ExtendedShapes):
    # Used by MPDisplay
    # Can be used by the end-user
    pass
