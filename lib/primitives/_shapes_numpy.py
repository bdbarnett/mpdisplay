"""
Shapes primitives for writing to buffers using numpy.

The canvas is a framebuffer object.
It won't be a numpy array until the function converts it to one.

Includes:
    pixel
    fill_rect
    blit_rect
    fill
    hline
    vline
    line
    rect
    ellipse
    poly
    arc
    circle
    round_rect
    polygon
"""

from ulab import numpy as np
import math
from . import Area

def _to_map(canvas):
    """Convert a framebuffer object to a numpy array."""
    return np.memmap(canvas, np.uint16, "w+", shape=(canvas.height, canvas.width))

def pixel(canvas, x, y, color):
    """Draw a single pixel."""
    arr = _to_map(canvas)
    arr[y, x] = color
    return Area(x, y, 1, 1)

def fill_rect(canvas, x, y, width, height, color):
    """Fill a rectangle with a color."""
    arr = _to_map(canvas)
    arr[y:y+height, x:x+width] = color
    return Area(x, y, width, height)

def blit_rect(canvas, buf, x, y, width, height):
    """Blit a rectangle from a buffer to the canvas."""
    arr = _to_map(canvas)
    arr[y:y+height, x:x+width] = buf
    return Area(x, y, width, height)

def fill(canvas, color):
    """Fill the canvas with a color."""
    arr = _to_map(canvas)
    arr[:, :] = color
    return Area(0, 0, canvas.width, canvas.height)

def hline(canvas, x, y, width, color):
    """Draw a horizontal line."""
    arr = _to_map(canvas)
    arr[y, x:x+width] = color
    return Area(x, y, width, 1)

def vline(canvas, x, y, height, color):
    """Draw a vertical line."""
    arr = _to_map(canvas)
    arr[y:y+height, x] = color
    return Area(x, y, 1, height)

def line(canvas, x0, y0, x1, y1, color):
    """Draw a line."""
    arr = _to_map(canvas)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        arr[y0, x0] = color
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return Area(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))

def rect(canvas, x, y, width, height, color, fill=False):
    """Draw a rectangle."""
    if fill:
        fill_rect(canvas, x, y, width, height, color)
    else:
        hline(canvas, x, y, width, color)
        hline(canvas, x, y+height-1, width, color)
        vline(canvas, x, y, height, color)
        vline(canvas, x+width-1, y, height, color)
    return Area(x, y, width, height)

def ellipse(canvas, x, y, r, r2, color, fill=False, mask=0b1111, width=None, height=None):
    """Draw an ellipse."""
    arr = _to_map(canvas)
    if width is None:
        width = r
    if height is None:
        height = r2
    if fill:
        for i in range(-r, r):
            for j in range(-r2, r2):
                if i**2/r**2 + j**2/r2**2 <= 1:
                    arr[y+j, x+i] = color
    else:
        for i in range(-r, r):
            for j in range(-r2, r2):
                if i**2/r**2 + j**2/r2**2 <= 1:
                    for m in range(4):
                        if mask & (1 << m):
                            arr[y+j+m, x+i] = color
    return Area(x-r, y-r2, 2*r, 2*r2)

def poly(canvas, x, y, coords, color, fill=False):
    """Draw a polygon."""
    arr = _to_map(canvas)
    if fill:
        for i in range(len(coords)):
            line(canvas, x+coords[i][0], y+coords[i][1], x+coords[(i+1)%len(coords)][0], y+coords[(i+1)%len(coords)][1], color)
    else:
        for i in range(len(coords)):
            line(canvas, x+coords[i][0], y+coords[i][1], x+coords[(i+1)%len(coords)][0], y+coords[(i+1)%len(coords)][1], color)
    return Area(x, y, 0, 0)

def arc(canvas, x, y, r, a1, a2, c, f=False, m=0b1111, w=1):
    """Draw an arc."""
    resolution = 60
    a1 = math.radians(a1)
    a2 = math.radians(a2)
    x0 = x + int(r * math.cos(a1))
    y0 = y + int(r * math.sin(a1))
    if a2 > a1:
        arc_range = range(int(a1 * resolution), int(a2 * resolution))
    else:
        arc_range = range(int(a1 * resolution), int(a2 * resolution), -1)

    for a in arc_range:
        ar = a / resolution
        x1 = x + int(r * math.cos(ar))
        y1 = y + int(r * math.sin(ar))
        line(canvas, x0, y0, x1, y1, c)
        x0 = x1
        y0 = y1
    return Area(x - r, y - r, r * 2, r * 2)  # Marks the whole 360 degrees of the circle

def circle(canvas, x, y, r, c, f=False, m=0b1111):
    """Draw a circle."""
    ellipse(canvas, x, y, r, r, c, f, m)
    return Area(x - r, y - r, r * 2, r * 2)

def round_rect(canvas, x, y, w, h, r, c, f=False, m=0b1111):
    """Draw a rounded rectangle."""
    if w < 2 * r:
        r = w // 2
    if h < 2 * r:
        r = h // 2
    ellipse(canvas, x + w // 2, y + h // 2, r, r, c, f, m, w, h)
    return Area(x, y, w, h)

def polygon(canvas, points, x, y, color, angle=0, center_x=0, center_y=0):
    """Draw a polygon on the display."""
    arr = _to_map(canvas)
    for i in range(len(points)):
        x0 = x + points[i][0]
        y0 = y + points[i][1]
        x1 = x + points[(i + 1) % len(points)][0]
        y1 = y + points[(i + 1) % len(points)][1]
        arr[y0, x0] = color
        line(canvas, x0, y0, x1, y1, color)
    return Area(x, y, 0, 0)

