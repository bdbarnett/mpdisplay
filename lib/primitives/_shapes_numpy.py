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
import math
from . import Area
from sys import implementation
if implementation.name == 'cpython':
    import numpy as np
else:
    from ulab import numpy as np


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

def poly(canvas, x, y, coords, c, f=False):
    """
    Given a list of coordinates, draw an arbitrary (convex or concave) closed polygon at the given x, y location
    using the given color.

    The coords must be specified as an array of integers, e.g. array('h', [x0, y0, x1, y1, ... xn, yn]) or a
    list or tuple of points, e.g. [(x0, y0), (x1, y1), ... (xn, yn)].

    The optional f parameter can be set to True to fill the polygon. Otherwise, just a one-pixel outline is drawn.
    """

    # Convert the coords to a list of x, y tuples if it is not already
    if isinstance(coords, list):
        vertices = coords
    elif isinstance(coords, tuple):
        vertices = list(coords)
    else:
        # Check that the coords array has an even number of elements
        if len(coords) % 2 != 0:
            raise ValueError("coords must have an even number of elements")
        vertices = [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]

    # Check that the polygon has at least 3 vertices
    if len(vertices) < 3:
        raise ValueError("polygon must have at least 3 vertices")

    # Close the polygon if it is not already closed
    if vertices[0] != vertices[-1]:
        vertices.append(vertices[0])

    # Offset vertices by (x, y)
    vertices = [(x + vertex[0], y + vertex[1]) for vertex in vertices]

    # Find the rectangle bounding box of the polygon
    left = min(vertex[0] for vertex in vertices)
    right = max(vertex[0] for vertex in vertices)
    top = min(vertex[1] for vertex in vertices)
    bottom = max(vertex[1] for vertex in vertices)

    for i in range(len(vertices) - 1):
        line(
            canvas,
            vertices[i][0],
            vertices[i][1],
            vertices[i + 1][0],
            vertices[i + 1][1],
            c,
        )
    if f:
        for y in range(top, bottom + 1):
            intersections = []
            for i in range(len(vertices) - 1):
                x0, y0 = vertices[i]
                x1, y1 = vertices[i + 1]
                if y0 <= y < y1 or y1 <= y < y0:
                    intersections.append(x0 + (x1 - x0) * (y - y0) // (y1 - y0))
            intersections.sort()
            for i in range(0, len(intersections), 2):
                line(canvas, intersections[i], y, intersections[i + 1], y, c)
    return Area(left, top, right - left, bottom - top)

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
