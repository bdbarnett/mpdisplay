# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
from ._area import Area


def fill_rect(canvas, x, y, w, h, c):
    BPP = 2
    if hasattr(canvas, "fill_rect"):
        canvas.fill_rect(x, y, w, h, c)
    else:
        for i in range(h):
            for j in range(w):
                pixel(canvas, x + j, y + i, c)
    x2 = x + w
    y2 = y + h
    top = min(y, y2)
    left = min(x, x2)
    bottom = max(y, y2)
    right = max(x, x2)
    return Area(left, top, right - left, bottom - top)

def pixel(canvas, x, y, c):
    if hasattr(canvas, "pixel"):
        canvas.pixel(x, y, c)
    else:
        rgb565_color = (c & 0xFFFF).to_bytes(2, "little")
        canvas._buffer[(y * canvas.width + x) * 2:(y * canvas.width + x) * 2 + 2] = rgb565_color
    return Area(x, y, 1, 1)

def fill(canvas, c):
    fill_rect(canvas, 0, 0, canvas.width, canvas.height, c)
    return Area(0, 0, canvas.width, canvas.height)

def hline(canvas, x, y, w, c):
    fill_rect(canvas, x, y, w, 1, c)
    if w < 0:
        return Area(x + w, y, -w, 1)
    return Area(x, y, w, 1)

def vline(canvas, x, y, h, c):
    fill_rect(canvas, x, y, 1, h, c)
    if h < 0:
        return Area(x, y + h, 1, -h)
    return Area(x, y, 1, h)

def line(canvas, x, y, x2, y2, c):
    """
    Bresenham's line algorithm
    """
    dx = abs(x2 - x)
    dy = abs(y2 - y)
    sx = -1 if x > x2 else 1
    sy = -1 if y > y2 else 1
    err = dx - dy
    while True:
        pixel(canvas, x, y, c)
        if x == x2 and y == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    top = min(y, y2)
    left = min(x, x2)
    bottom = max(y, y2)
    right = max(x, x2)
    return Area(left, top, right - left, bottom - top)

def rect(canvas, x, y, w, h, c, f=False):
    if f:
        return fill_rect(canvas, x, y, w, h, c)
    top = y
    left = x
    bottom = y + h
    right = x + w
    hline(canvas, left, top, w, c)
    hline(canvas, left, bottom, w, c)
    vline(canvas, left, top, h, c)
    vline(canvas, right, top, h, c)
    return Area(left, top, w, h)

def ellipse(canvas, x, y, r, r2, c, f=False, m=0b1111, w=None, h=None):
    """
    Midpoint ellipse algorithm
    Draw an ellipse at the given location. Radii r and r2 define the geometry; equal values cause a
    circle to be drawn. The c parameter defines the color.

    The optional f parameter can be set to True to fill the ellipse. Otherwise just a one pixel outline
    is drawn.

    The optional m parameter enables drawing to be restricted to certain quadrants of the ellipse.
    The LS four bits determine which quadrants are to be drawn, with bit 0 specifying Q1, b1 Q2,
    b2 Q3 and b3 Q4. Quadrants are numbered counterclockwise with Q1 being top right.

    Args:
        x (int): Center x coordinate
        y (int): Center y coordinate
        r (int): x radius
        r2 (int): y radius
        c (int): 565 encoded color
        filled (bool): Fill the ellipse (default: False)
        mask (int): Bitmask to determine which quadrants to draw (default: 0b1111)
        w (int): Width of the ellipse (default: 0)
        h (int): Height of the ellipse (default: 0)
    """
    if r < 1 or r2 < 1:
        return

    x_side = w - 2 * r if w else 0
    y_side = h - 2 * r2 if h else 0
    x_offset = x_side // 2 if w else 0
    y_offset = y_side // 2 if h else 0

    if f:
        if y_offset > 0:
            fill_rect(canvas, x - w // 2, y - y_offset, w, y_side, c)
        if x_offset > 0:
            fill_rect(canvas, x - x_offset, y - h // 2, x_side, r, c)
            fill_rect(canvas, x - x_offset, y + h // 2 - r, x_side, r, c)

    if x_offset > 0:
        hline(canvas, x - x_offset, y - h // 2, x_side, c)
        hline(canvas, x - x_offset, y + h // 2, x_side, c)
    if y_offset > 0:
        vline(canvas, x - w // 2, y - y_offset, y_side, c)
        vline(canvas, x + w // 2, y - y_offset, y_side, c)

    a2 = r * r
    b2 = r2 * r2
    fa2 = 4 * a2
    fb2 = 4 * b2

    x1 = r
    y1 = 0
    sigma = 2 * a2 + b2 * (1 - 2 * r)
    while a2 * y1 <= b2 * x1:
        if f:
            if m & 0x1:
                hline(canvas, x + x_offset, y - y1 - y_offset, x1, c)
            if m & 0x2:
                hline(canvas, x - x1 - x_offset, y - y1 - y_offset, x1, c)
            if m & 0x4:
                hline(canvas, x - x1 - x_offset, y + y1 + y_offset, x1, c)
            if m & 0x8:
                hline(canvas, x + x_offset, y + y1 + y_offset, x1, c)
        else:
            if m & 0x1:
                pixel(canvas, x + x1 + x_offset, y - y1 - y_offset, c)
            if m & 0x2:
                pixel(canvas, x - x1 - x_offset, y - y1 - y_offset, c)
            if m & 0x4:
                pixel(canvas, x - x1 - x_offset, y + y1 + y_offset, c)
            if m & 0x8:
                pixel(canvas, x + x1 + x_offset, y + y1 + y_offset, c)
        if sigma >= 0:
            sigma += fb2 * (1 - x1)
            x1 -= 1
        sigma += a2 * ((4 * y1) + 6)
        y1 += 1

    x1 = 0
    y1 = r2
    sigma = 2 * b2 + a2 * (1 - 2 * r2)
    while b2 * x1 <= a2 * y1:
        if f:
            if m & 0x1:
                hline(canvas, x + x_offset, y - y1 - y_offset, x1, c)
            if m & 0x2:
                hline(canvas, x - x1 - x_offset, y - y1 - y_offset, x1, c)
            if m & 0x4:
                hline(canvas, x - x1 - x_offset, y + y1 + y_offset, x1, c)
            if m & 0x8:
                hline(canvas, x + x_offset, y + y1 + y_offset, x1, c)
        else:
            if m & 0x1:
                pixel(canvas, x + x1 + x_offset, y - y1 - y_offset, c)
            if m & 0x2:
                pixel(canvas, x - x1 - x_offset, y - y1 - y_offset, c)
            if m & 0x4:
                pixel(canvas, x - x1 - x_offset, y + y1 + y_offset, c)
            if m & 0x8:
                pixel(canvas, x + x1 + x_offset, y + y1 + y_offset, c)
        if sigma >= 0:
            sigma += fa2 * (1 - y1)
            y1 -= 1
        sigma += b2 * ((4 * x1) + 6)
        x1 += 1

    return Area(
        x - r - x_offset, y - r2 - y_offset, 2 * (r + x_offset), 2 * (r2 + y_offset)
    )

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
        # Fill the polygon using scanline algorithm
        # Calculate the minimum and maximum y-coordinates in the polygon
        y_min = min(vertex[1] for vertex in vertices)
        y_max = max(vertex[1] for vertex in vertices)

        # Iterate through each y-coordinate within the bounding box
        for y_scan in range(y_min, y_max + 1):
            # Determine intersections with the polygon edges
            intersections = []
            for i in range(len(vertices) - 1):
                x1, y1 = vertices[i]
                x2, y2 = vertices[i + 1]
                # Check if the scanline intersects the edge
                if y1 <= y_scan < y2 or y2 <= y_scan < y1:
                    # Calculate the intersection point using linear interpolation
                    x_intersection = x1 + ((y_scan - y1) / (y2 - y1)) * (x2 - x1)
                    intersections.append(x_intersection)

            # Sort intersections in increasing order
            intersections.sort()

            # Draw horizontal lines between pairs of intersection points
            for i in range(0, len(intersections), 2):
                x_start = int(intersections[i])
                x_end = int(intersections[i + 1])
                hline(canvas, x_start, y_scan, x_end - x_start, c)
    return Area(left, top, right - left, bottom - top)
