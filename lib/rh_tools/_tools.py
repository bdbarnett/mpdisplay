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
from area import Area
import math

if implementation.name == "micropython":
    from ._viper import _pack8, _pack16
else:
    from ._python import _pack8, _pack16


WHITE = const(0xFFFF)
BLACK = const(0x0000)

_default_font = None


def bitmap(canvas, bitmap, x, y, index=0):
    """
    Draw a bitmap on display at the specified column and row

    Args:
        bitmap (bitmap_module): The module containing the bitmap to draw
        x (int): column to start drawing at
        y (int): row to start drawing at
        index (int): Optional index of bitmap to draw from multiple bitmap
            module
    """
    width = bitmap.WIDTH
    height = bitmap.HEIGHT
    to_col = x + width - 1
    to_row = y + height - 1
    if canvas.width <= to_col or canvas.height <= to_row:
        return

    bitmap_size = height * width
    buffer_len = bitmap_size * 2
    bpp = bitmap.BPP
    bs_bit = bpp * bitmap_size * index  # if index > 0 else 0
    palette = bitmap.PALETTE
    needs_swap = canvas.needs_swap if hasattr(canvas, "needs_swap") else False
    buffer = bytearray(buffer_len)

    for i in range(0, buffer_len, 2):
        color_index = 0
        for _ in range(bpp):
            color_index = (color_index << 1) | (
                (bitmap.BITMAP[bs_bit >> 3] >> (7 - (bs_bit & 7))) & 1
            )
            bs_bit += 1

        color = palette[color_index]
        if needs_swap:
            buffer[i] = color >> 8
            buffer[i + 1] = color & 0xFF
        else:
            buffer[i] = color & 0xFF
            buffer[i + 1] = color >> 8

    canvas.blit_rect(buffer, x, y, width, height)
    return Area(x, y, width, height)


def pbitmap(canvas, bitmap, x, y, index=0):
    """
    Draw a bitmap on display at the specified column and row one row at a time

    Args:
        bitmap (bitmap_module): The module containing the bitmap to draw
        x (int): column to start drawing at
        y (int): row to start drawing at
        index (int): Optional index of bitmap to draw from multiple bitmap
            module

    """
    width = bitmap.WIDTH
    height = bitmap.HEIGHT
    bitmap_size = height * width
    bpp = bitmap.BPP
    bs_bit = bpp * bitmap_size * index  # if index > 0 else 0
    palette = bitmap.PALETTE
    needs_swap = canvas.needs_swap if hasattr(canvas, "needs_swap") else False
    buffer = bytearray(bitmap.WIDTH * 2)

    for row in range(height):
        for col in range(width):
            color_index = 0
            for _ in range(bpp):
                color_index <<= 1
                color_index |= (
                    bitmap.BITMAP[bs_bit // 8] & 1 << (7 - (bs_bit % 8))
                ) > 0
                bs_bit += 1
            color = palette[color_index]
            if needs_swap:
                buffer[col * 2] = color & 0xFF
                buffer[col * 2 + 1] = color >> 8 & 0xFF
            else:
                buffer[col * 2] = color >> 8 & 0xFF
                buffer[col * 2 + 1] = color & 0xFF

        to_col = x + width - 1
        to_row = y + row
        if canvas.width > to_col and canvas.height > to_row:
            canvas.blit_rect(buffer, x, y + row, width, height)
    return Area(x, y, width, height)


def write(canvas, font, string, x, y, fg=WHITE, bg=BLACK):
    """
    Write a string using a converted true-type font on the display starting
    at the specified column and row

    Args:
        font (font): The module containing the converted true-type font
        s (string): The string to write
        x (int): column to start writing
        y (int): row to start writing
        fg (int): foreground color, optional, defaults to WHITE
        bg (int): background color, optional, defaults to BLACK
    """
    buffer_len = font.HEIGHT * font.MAX_WIDTH * 2
    buffer = bytearray(buffer_len)
    fg_hi = fg & 0xFF
    fg_lo = fg >> 8

    bg_hi = bg & 0xFF
    bg_lo = bg >> 8

    x_pos = x
    for character in string:
        try:
            char_index = font.MAP.index(character)
            offset = char_index * font.OFFSET_WIDTH
            bs_bit = font.OFFSETS[offset]
            if font.OFFSET_WIDTH > 1:
                bs_bit = (bs_bit << 8) + font.OFFSETS[offset + 1]

            if font.OFFSET_WIDTH > 2:
                bs_bit = (bs_bit << 8) + font.OFFSETS[offset + 2]

            char_width = font.WIDTHS[char_index]
            buffer_needed = char_width * font.HEIGHT * 2

            for i in range(0, buffer_needed, 2):
                if font.BITMAPS[bs_bit // 8] & 1 << (7 - (bs_bit % 8)) > 0:
                    buffer[i] = fg_hi
                    buffer[i + 1] = fg_lo
                else:
                    buffer[i] = bg_hi
                    buffer[i + 1] = bg_lo

                bs_bit += 1

            to_col = x_pos + char_width - 1
            to_row = y + font.HEIGHT - 1
            if canvas.width > to_col and canvas.height > to_row:
                canvas.blit_rect(
                    buffer[:buffer_needed], x_pos, y, char_width, font.HEIGHT
                )

            x_pos += char_width

        except ValueError:
            pass
    return Area(x, y, x_pos - x, font.HEIGHT)


def write_width(canvas, font, string):
    """
    Returns the width in pixels of the string if it was written with the
    specified font

    Args:
        font (font): The module containing the converted true-type font
        string (string): The string to measure

    Returns:
        int: The width of the string in pixels

    """
    width = 0
    for character in string:
        try:
            char_index = font.MAP.index(character)
            width += font.WIDTHS[char_index]
        except ValueError:
            pass

    return width


def text(canvas, firstarg, *args, **kwargs):
    global _default_font
    if type(firstarg) == str:
        if _default_font == None:
            import vga1_8x8

            _default_font = vga1_8x8
        return _text(canvas, _default_font, firstarg, *args, **kwargs)
    else:
        return _text(canvas, firstarg, *args, **kwargs)


def _text(canvas, font, text, x0, y0, color=WHITE, background=BLACK):
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


def polygon(canvas, points, x, y, color, angle=0, center_x=0, center_y=0):
    """
    Draw a polygon on the display.

    Args:
        points (list): List of points to draw.
        x (int): X-coordinate of the polygon's position.
        y (int): Y-coordinate of the polygon's position.
        color (int): 565 encoded color.
        angle (float): Rotation angle in radians (default: 0).
        center_x (int): X-coordinate of the rotation center (default: 0).
        center_y (int): Y-coordinate of the rotation center (default: 0).

    Raises:
        ValueError: If the polygon has less than 3 points.
    """
    if len(points) < 3:
        raise ValueError("Polygon must have at least 3 points.")

    # fmt: off
    if angle:
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rotated = [
            (x + center_x + int((point[0] - center_x) * cos_a - (point[1] - center_y) * sin_a),
                y + center_y + int((point[0] - center_x) * sin_a + (point[1] - center_y) * cos_a))
            for point in points
        ]
    else:
        rotated = [(x + int((point[0])), y + int((point[1]))) for point in points]

    # Find the rectangle bounding box of the polygon
    left = min(vertex[0] for vertex in rotated)
    right = max(vertex[0] for vertex in rotated)
    top = min(vertex[1] for vertex in rotated)
    bottom = max(vertex[1] for vertex in rotated)

    for i in range(1, len(rotated)):
        canvas.line(rotated[i - 1][0], rotated[i - 1][1], rotated[i][0], rotated[i][1], color)
    # fmt: on
    return Area(left, top, right - left, bottom - top)
