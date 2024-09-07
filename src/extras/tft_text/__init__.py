"""
MIT License

Copyright (c) 2024 Brad Barnett

Copyright (c) 2020-2023 Russ Hughes

Copyright (c) 2019 Ivan Belokobylskiy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The file is based on Russ Hughes's st7789_mpy driver from
https://github.com/russhughes/st7789_mpy

which is based on devbis' st7789py_mpy module from
https://github.com/devbis/st7789py_mpy.

"""

from micropython import const
from sys import implementation
from basedisplay import Area

if implementation.name == "micropython":
    try:
        from ._viper import _pack8, _pack16
    except Exception:
        from ._python import _pack8, _pack16
else:
        from ._python import _pack8, _pack16


WHITE = const(0xFFFF)
BLACK = const(0x0000)


def text(canvas, font, text, x0, y0, color=WHITE, background=BLACK):
    """
    Draw text on display in specified font and colors. 8 and 16 bit wide
    fonts are supported.

    Args:
        font (module): font module to use.
        text (str): text to write
        x0 (int): column to start drawing at
        y0 (int): row to start drawing at
        color (int): 565 encoded color to use for characters
        background (int): 565 encoded color to use for background
    """
    if font.WIDTH == 8:
        return _text8(canvas, font, text, x0, y0, color, background)
    else:
        return _text16(canvas, font, text, x0, y0, color, background)

def _text8(canvas, font, text, x0, y0, fg_color=WHITE, bg_color=BLACK):
    """
    Internal method to write characters with width of 8 and
    heights of 8 or 16.

    Args:
        font (module): font module to use
        text (str): text to write
        x0 (int): column to start drawing at
        y0 (int): row to start drawing at
        color (int): 565 encoded color to use for characters
        background (int): 565 encoded color to use for background
    """

    x_pos = x0
    for char in text:
        ch = ord(char)
        if (
            font.FIRST <= ch < font.LAST
            and x_pos + font.WIDTH <= canvas.width
            and y0 + font.HEIGHT <= canvas.height
        ):
            if font.HEIGHT == 8:
                passes = 1
                size = 8
                each = 0
            else:
                passes = 2
                size = 16
                each = 8

            for line in range(passes):
                idx = (ch - font.FIRST) * size + (each * line)
                buffer = _pack8(font.FONT, idx, fg_color, bg_color)
                canvas.blit_rect(buffer, x_pos, y0 + 8 * line, 8, 8)

            x_pos += 8
    return Area(x0, y0, x_pos - x0, font.HEIGHT)

def _text16(canvas, font, text, x0, y0, fg_color=WHITE, bg_color=BLACK):
    """
    Internal method to draw characters with width of 16 and heights of 16
    or 32.

    Args:
        font (module): font module to use
        text (str): text to write
        x0 (int): column to start drawing at
        y0 (int): row to start drawing at
        color (int): 565 encoded color to use for characters
        background (int): 565 encoded color to use for background
    """

    x_pos = x0
    for char in text:
        ch = ord(char)
        if (
            font.FIRST <= ch < font.LAST
            and x_pos + font.WIDTH <= canvas.width
            and y0 + font.HEIGHT <= canvas.height
        ):
            each = 16
            if font.HEIGHT == 16:
                passes = 2
                size = 32
            else:
                passes = 4
                size = 64

            for line in range(passes):
                idx = (ch - font.FIRST) * size + (each * line)
                buffer = _pack16(font.FONT, idx, fg_color, bg_color)
                canvas.blit_rect(buffer, x_pos, y0 + 8 * line, 16, 8)
        x_pos += 16
    return Area(x0, y0, x_pos - x0, font.HEIGHT)
