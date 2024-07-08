# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
from . import Area

from ._basic_shapes import (
    fill_rect,
    fill,
    pixel,
    hline,
    vline,
    line,
    rect,
    ellipse,
    poly,
)
import math


def arc(canvas, x, y, r, a0, a1, c, f=False):
    resolution = 60
    a0 = math.radians(a0)
    a1 = math.radians(a1)
    x0 = x + int(r * math.cos(a0))
    y0 = y + int(r * math.sin(a0))
    if a1 > a0:
        arc_range = range(int(a0 * resolution), int(a1 * resolution))
    else:
        arc_range = range(int(a0 * resolution), int(a1 * resolution), -1)

    for a in arc_range:
        ar = a / resolution
        x1 = x + int(r * math.cos(ar))
        y1 = y + int(r * math.sin(ar))
        line(canvas, x0, y0, x1, y1, c)
        x0 = x1
        y0 = y1
    return Area(x - r, y - r, r * 2, r * 2)  # Marks the whole 360 degrees of the circle

def circle(canvas, x, y, r, c, f=False, m=0b1111):
    ellipse(canvas, x, y, r, r, c, f, m)
    return Area(x - r, y - r, r * 2, r * 2)

def round_rect(canvas, x, y, w, h, r, c, f=False, m=0b1111):
    if w < 2 * r:
        r = w // 2
    if h < 2 * r:
        r = h // 2
    ellipse(canvas, x + w // 2, y + h // 2, r, r, c, f, m, w, h)
    return Area(x, y, w, h)

def blit_rect(canvas, buf, x, y, w, h):
    """
    Blit a rectangular area from a buffer to the canvas.
    :param buf: Buffer containing the data to blit
    :param x: X coordinate of the top-left corner of the area
    :param y: Y coordinate of the top-left corner of the area
    :param w: Width of the area
    :param h: Height of the area
    """
    # copy bytes from buf to canvas.buffer, one row at a time

    BPP = canvas.color_depth // 8

    if x < 0 or y < 0 or x + w > canvas.width or y + h > canvas.height:
        raise ValueError("The provided x, y, w, h values are out of range")

    if len(buf) != w * h * BPP:
        print(f"len(buf)={len(buf)} w={w} h={h} self.color_depth={canvas.color_depth}")
        raise ValueError("The source buffer is not the correct size")

    for row in range(h):
        source_begin = row * w * BPP
        source_end = source_begin + w * BPP
        dest_begin = ((y + row) * canvas.width + x) * BPP
        dest_end = dest_begin + w * BPP
        print(f"{source_begin=}, {source_end=}, source_len={source_end-source_begin}, {dest_begin=}, {dest_end=}, dest_len={dest_end-dest_begin}")
        canvas.buffer[dest_begin : dest_end] = buf[source_begin : source_end]
    return Area(x, y, w, h)


def blit(canvas, source, x, y, key=-1, palette=None):
    print(f"{dir(canvas)=}\n{dir(source)=}\n\n")
    if (
        (-x >= source.width) or
        (-y >= source.height) or
        (x >= canvas.width) or
        (y >= canvas.height)
    ):
        # Out of bounds, no-op.
        return

    # Clip.
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = max(0, -x)
    y1 = max(0, -y)
    x0end = min(canvas.width, x + source.width)
    y0end = min(canvas.height, y + source.height)

    for y0 in range(y0, y0end):
        cx1 = x1
        for cx0 in range(x0, x0end):
            col = source.pixel(cx1, y1)
            if palette:
                col = palette.pixel(col, 0)
            if col != key:
                pixel(canvas, cx0, y0, col)
            cx1 += 1
        y1 += 1
    return Area(x0, y0, x0end - x0, y0end - y0)
