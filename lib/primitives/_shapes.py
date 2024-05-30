# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
from ._area import Area
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


def arc(canvas, x, y, r, a1, a2, c, f=False, m=0b1111, w=1):
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

def blit_rect(canvas, buf, x, y, w, h):
    """
    Blit a rectangular area from a buffer to the canvas.
    :param buf: Buffer containing the data to blit
    :param x: X coordinate of the top-left corner of the area
    :param y: Y coordinate of the top-left corner of the area
    :param w: Width of the area
    :param h: Height of the area
    """
    # copy bytes from buf to self._buffer, one row at a time

    BPP = canvas.color_depth // 8

    if x < 0 or y < 0 or x + w > canvas.width or y + h > canvas.height:
        raise ValueError("The provided x, y, w, h values are out of range")

    if len(buf) != w * h * BPP:
        print(f"len(buf)={len(buf)} w={w} h={h} self.color_depth={canvas.color_depth}")
        raise ValueError("The source buffer is not the correct size")

    for row in range(h):
        start = row * w * BPP
        dest = ((y + row) * canvas.width + x) * BPP
        canvas._buffer[dest : dest + w * BPP] = buf[start : start + w * BPP]
    return Area(x, y, w, h)