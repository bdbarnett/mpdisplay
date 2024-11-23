"""
`graphics`
====================================================
Graphics library extending MicroPython's framebuf module.
"""

from ._area import Area
from ._draw import Draw
from ._font import Font, text, text8, text14, text16
from ._files import pbm_to_framebuffer, pgm_to_framebuffer, bmp_to_framebuffer
from ._framebuf_plus import (
    FrameBuffer,
    MONO_VLSB,
    MONO_HLSB,
    MONO_HMSB,
    GS2_HMSB,
    GS4_HMSB,
    GS8,
    RGB565,
)
from ._shapes import (
    arc,
    blit,
    blit_rect,
    blit_transparent,
    circle,
    ellipse,
    fill,
    fill_rect,
    gradient_rect,
    hline,
    line,
    pixel,
    poly,
    polygon,
    rect,
    round_rect,
    triangle,
    vline,
)

__all__ = [
    "Area",
    "Draw",
    "Font",
    "text",
    "text8",
    "text14",
    "text16",
    "pbm_to_framebuffer",
    "pgm_to_framebuffer",
    "bmp_to_framebuffer",
    "FrameBuffer",
    "MONO_VLSB",
    "MONO_HLSB",
    "MONO_HMSB",
    "GS2_HMSB",
    "GS4_HMSB",
    "GS8",
    "RGB565",
    "arc",
    "blit",
    "blit_rect",
    "blit_transparent",
    "circle",
    "ellipse",
    "fill",
    "fill_rect",
    "gradient_rect",
    "hline",
    "line",
    "pixel",
    "poly",
    "polygon",
    "rect",
    "round_rect",
    "triangle",
    "vline",
]
