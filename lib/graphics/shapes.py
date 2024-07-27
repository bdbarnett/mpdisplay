# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries, 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
`graphics`
====================================================
Graphics primitives for drawing on a canvas.

Heavily modified from the original gfx.py library at:
https://github.com/adafruit/Adafruit_CircuitPython_GFX.git
* Author(s): Kattni Rembor, Tony DiCola, Jonah Yolles-Murphy, based on code by Phil Burgess

Implementation Notes
--------------------
.pixel(), .fill_rect() and .blit_rect() will be called from the canvas object if the canvas
object has these methods.

.pixel() and .blit_rect() assume 16-bit color depth.

"""

from . import Area
import math


def pixel(canvas, x, y, c):
    """A function to pass through in input pixel functionality."""
    # This was added to mainitatn the abstraction between gfx and the dislay library
    if hasattr(canvas, "pixel"):
        canvas.pixel(x, y, c)
    else:
        rgb565_color = (c & 0xFFFF).to_bytes(2, "little")
        canvas.buffer[(y * canvas.width + x) * 2:(y * canvas.width + x) * 2 + 2] = rgb565_color
    return Area(x, y, 1, 1)

def fill_rect(canvas, x, y, w, h, c):
    """Filled rectangle drawing function.  Will draw a filled
    rectangle starting in the upper left x0, y0 position and w, h
    pixels in size."""
    if y < -h or y > canvas.height or x < -w or x > canvas.width:
        return
    if hasattr(canvas, "fill_rect"):
        canvas.fill_rect(x, y, w, h, c)
    else:
        for j in range(y, y + h):
            for i in range(x, x + w):
                pixel(canvas, i, j, c)
    return Area(x, y, w, h)

def fill(canvas, c):
    """Fill the entire canvas with a color."""
    return fill_rect(canvas, 0, 0, canvas.width, canvas.height, c)

def hline(canvas, x0, y0, w, c):
    """Horizontal line drawing function.  Will draw a single pixel wide line."""
    if y0 < 0 or y0 > canvas.height or x0 < -w or x0 > canvas.width:
        return
    fill_rect(canvas, x0, y0, w, 1, c)
    return Area(x0, y0, w, 1)

def vline(canvas, x0, y0, h, c):
    """Vertical line drawing function.  Will draw a single pixel wide line."""
    if y0 < -h or y0 > canvas.height or x0 < 0 or x0 > canvas.width:
        return
    fill_rect(canvas, x0, y0, 1, h, c)
    return Area(x0, y0, 1, h)

def line(canvas, x0, y0, x1, y1, c):
    """Line drawing function.  Will draw a single pixel wide line starting at
    x0, y0 and ending at x1, y1."""
    if x0 == x1:
        return vline(canvas, x0, y0, abs(y1 - y0) + 1, c)
    if y0 == y1:
        return hline(canvas, x0, y0, abs(x1 - x0) + 1, c)
    
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
    dx = x1 - x0
    dy = abs(y1 - y0)
    err = dx // 2
    ystep = 0
    if y0 < y1:
        ystep = 1
    else:
        ystep = -1
    while x0 <= x1:
        if steep:
            pixel(canvas, y0, x0, c)
        else:
            pixel(canvas, x0, y0, c)
        err -= dy
        if err < 0:
            y0 += ystep
            err += dx
        x0 += 1
    return Area(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))

def rect(canvas, x0, y0, w, h, c, f=False):
    """Rectangle drawing function.  Will draw a single pixel wide rectangle
    starting in the upper left x0, y0 position and w, h pixels in
    size."""
    if f:
        return fill_rect(canvas, x0, y0, w, h, c)
    if y0 < -h or y0 > canvas.height or x0 < -w or x0 > canvas.width:
        return
    hline(canvas, x0, y0, w, c)
    hline(canvas, x0, y0 + h - 1, w, c)
    vline(canvas, x0, y0, h, c)
    vline(canvas, x0 + w - 1, y0, h, c)
    return Area(x0, y0, w, h)

def ellipse(canvas, x0, y0, r1, r2, c, f=False, m=0b1111, w=None, h=None):
    """
    Midpoint ellipse algorithm
    Draw an ellipse at the given location. Radii r1 and r2 define the geometry; equal values cause a
    circle to be drawn. The c parameter defines the color.

    The optional f parameter can be set to True to fill the ellipse. Otherwise just a one pixel outline
    is drawn.

    The optional m parameter enables drawing to be restricted to certain quadrants of the ellipse.
    The LS four bits determine which quadrants are to be drawn, with bit 0 specifying Q1, b1 Q2,
    b2 Q3 and b3 Q4. Quadrants are numbered counterclockwise with Q1 being top right.

    Args:
        x0 (int): Center x coordinate
        y0 (int): Center y coordinate
        r1 (int): x radius
        r2 (int): y radius
        c (int): color
        f (bool): Fill the ellipse (default: False)
        mask (int): Bitmask to determine which quadrants to draw (default: 0b1111)
        w (int): Width of the ellipse (default: None)
        h (int): Height of the ellipse (default: None)
    """
    if r1 < 1 or r2 < 1:
        return

    x_side = w - 2 * r1 if w else 0
    y_side = h - 2 * r2 if h else 0
    x_offset = x_side // 2 if w else 0
    y_offset = y_side // 2 if h else 0

    if f:
        if y_offset > 0:
            fill_rect(canvas, x0 - w // 2, y0 - y_offset, w, y_side, c)
        if x_offset > 0:
            fill_rect(canvas, x0 - x_offset, y0 - h // 2, x_side, r1, c)
            fill_rect(canvas, x0 - x_offset, y0 + h // 2 - r1, x_side, r1, c)

    if x_offset > 0:
        hline(canvas, x0 - x_offset, y0 - h // 2, x_side, c)
        hline(canvas, x0 - x_offset, y0 + h // 2, x_side, c)
    if y_offset > 0:
        vline(canvas, x0 - w // 2, y0 - y_offset, y_side, c)
        vline(canvas, x0 + w // 2, y0 - y_offset, y_side, c)

    a2 = r1 * r1
    b2 = r2 * r2
    fa2 = 4 * a2
    fb2 = 4 * b2

    x1 = r1
    y1 = 0
    sigma = 2 * a2 + b2 * (1 - 2 * r1)
    while a2 * y1 <= b2 * x1:
        if f:
            if m & 0x1:
                hline(canvas, x0 + x_offset, y0 - y1 - y_offset, x1, c)
            if m & 0x2:
                hline(canvas, x0 - x1 - x_offset, y0 - y1 - y_offset, x1, c)
            if m & 0x4:
                hline(canvas, x0 - x1 - x_offset, y0 + y1 + y_offset, x1, c)
            if m & 0x8:
                hline(canvas, x0 + x_offset, y0 + y1 + y_offset, x1, c)
        else:
            if m & 0x1:
                pixel(canvas, x0 + x1 + x_offset, y0 - y1 - y_offset, c)
            if m & 0x2:
                pixel(canvas, x0 - x1 - x_offset, y0 - y1 - y_offset, c)
            if m & 0x4:
                pixel(canvas, x0 - x1 - x_offset, y0 + y1 + y_offset, c)
            if m & 0x8:
                pixel(canvas, x0 + x1 + x_offset, y0 + y1 + y_offset, c)
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
                hline(canvas, x0 + x_offset, y0 - y1 - y_offset, x1, c)
            if m & 0x2:
                hline(canvas, x0 - x1 - x_offset, y0 - y1 - y_offset, x1, c)
            if m & 0x4:
                hline(canvas, x0 - x1 - x_offset, y0 + y1 + y_offset, x1, c)
            if m & 0x8:
                hline(canvas, x0 + x_offset, y0 + y1 + y_offset, x1, c)
        else:
            if m & 0x1:
                pixel(canvas, x0 + x1 + x_offset, y0 - y1 - y_offset, c)
            if m & 0x2:
                pixel(canvas, x0 - x1 - x_offset, y0 - y1 - y_offset, c)
            if m & 0x4:
                pixel(canvas, x0 - x1 - x_offset, y0 + y1 + y_offset, c)
            if m & 0x8:
                pixel(canvas, x0 + x1 + x_offset, y0 + y1 + y_offset, c)
        if sigma >= 0:
            sigma += fa2 * (1 - y1)
            y1 -= 1
        sigma += b2 * ((4 * x1) + 6)
        x1 += 1
    return Area(x0 - r1 - x_offset, y0 - r2 - y_offset, 2 * (r1 + x_offset), 2 * (r2 + y_offset))

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
    else:
        for i in range(len(vertices) - 1):
            line(
                canvas,
                vertices[i][0],
                vertices[i][1],
                vertices[i + 1][0],
                vertices[i + 1][1],
                c,
            )
    return Area(left, top, right - left, bottom - top)

def blit(canvas, source, x, y, key=-1, palette=None):
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

    for cy0 in range(y0, y0end):
        cx1 = x1
        for cx0 in range(x0, x0end):
            col = source.pixel(cx1, y1)
            if palette:
                col = palette.pixel(col, 0)
            if col != key:
                pixel(canvas, cx0, cy0, col)
            cx1 += 1
        y1 += 1
    return Area(x0, y0, x0end - x0, y0end - y0)



def blit_rect(canvas, buf, x, y, w, h):
    """
    Blit a rectangular area from a buffer to the canvas.
    :param buf: Buffer containing the data to blit
    :param x: X coordinate of the top-left corner of the area
    :param y: Y coordinate of the top-left corner of the area
    :param w: Width of the area
    :param h: Height of the area
    :return: Area object representing the blitted area
    """
    if hasattr(canvas, "blit_rect"):
        return canvas.blit_rect(buf, x, y, w, h)

    BPP = 2

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
        canvas.buffer[dest_begin : dest_end] = buf[source_begin : source_end]
    return Area(x, y, w, h)

def blit_transparent(canvas, buf, x, y, w, h, key):
    """
    Blit a buffer with transparency.

    :param buf: Buffer to blit.  Must already be byte-swapped if necessary.
    :type buf: memoryview
    :param x: X-coordinate to blit to
    :type x: int
    :param y: Y-coordinate to blit to
    :type y: int
    :param w: Width of the buffer
    :type w: int
    :param h: Height of the buffer
    :type h: int
    :param key: Key value for transparency
    :type key: int
    """
    BPP = canvas.color_depth // 8
    key_bytes = key.to_bytes(BPP, "little")
    stride = w * BPP
    for j in range(h):
        rowstart = j * stride
        colstart = 0
        # iterate over each pixel looking for the first non-key pixel
        while colstart < stride:
            startoffset = rowstart + colstart
            if buf[startoffset : startoffset + BPP] != key_bytes:
                # found a non-key pixel
                # then iterate over each pixel looking for the next key pixel
                colend = colstart
                while colend < stride:
                    endoffset = rowstart + colend
                    if buf[endoffset : endoffset + BPP] == key_bytes:
                        break
                    colend += BPP
                # blit the non-key pixels
                blit_rect(canvas, buf[rowstart + colstart : rowstart + colend], x + colstart // BPP, y + j, (colend - colstart) // BPP, 1)
                colstart = colend
            else:
                colstart += BPP
    return Area(x, y, w, h)

def circle(canvas, x0, y0, r, c, f=False):
    """Circle drawing function.  Will draw a single pixel wide circle with
    center at x0, y0 and the specified r."""
    if f:
        return _fill_circle(canvas, x0, y0, r, c)
    f = 1 - r
    ddF_x = 1
    ddF_y = -2 * r
    x = 0
    y = r
    pixel(canvas, x0, y0 + r, c)  # bottom
    pixel(canvas, x0, y0 - r, c)  # top
    pixel(canvas, x0 + r, y0, c)  # right
    pixel(canvas, x0 - r, y0, c)  # left
    while x < y:
        if f >= 0:
            y -= 1
            ddF_y += 2
            f += ddF_y
        x += 1
        ddF_x += 2
        f += ddF_x
        # angle notations are based on the unit circle and in diection of being drawn
        pixel(canvas, x0 + x, y0 + y, c)  # 270 to 315
        pixel(canvas, x0 - x, y0 + y, c)  # 270 to 255
        pixel(canvas, x0 + x, y0 - y, c)  # 90 to 45
        pixel(canvas, x0 - x, y0 - y, c)  # 90 to 135
        pixel(canvas, x0 + y, y0 + x, c)  # 0 to 315
        pixel(canvas, x0 - y, y0 + x, c)  # 180 to 225
        pixel(canvas, x0 + y, y0 - x, c)  # 0 to 45
        pixel(canvas, x0 - y, y0 - x, c)  # 180 to 135
    return Area(x0 - r, y0 - r, 2 * r, 2 * r)

def _fill_circle(canvas, x0, y0, r, c):
    """Filled circle drawing function.  Will draw a filled circle with
    center at x0, y0 and the specified r."""
    vline(canvas, x0, y0 - r, 2 * r + 1, c)
    f = 1 - r
    ddF_x = 1
    ddF_y = -2 * r
    x = 0
    y = r
    while x < y:
        if f >= 0:
            y -= 1
            ddF_y += 2
            f += ddF_y
        x += 1
        ddF_x += 2
        f += ddF_x
        vline(canvas, x0 + x, y0 - y, 2 * y + 1, c)
        vline(canvas, x0 + y, y0 - x, 2 * x + 1, c)
        vline(canvas, x0 - x, y0 - y, 2 * y + 1, c)
        vline(canvas, x0 - y, y0 - x, 2 * x + 1, c)
    return Area(x0 - r, y0 - r, 2 * r, 2 * r)

def triangle(canvas, x0, y0, x1, y1, x2, y2, c, f=False):
    # pylint: disable=too-many-arguments
    """Triangle drawing function.  Will draw a single pixel wide triangle
    around the points (x0, y0), (x1, y1), and (x2, y2)."""
    if f:
        return _fill_triangle(canvas, x0, y0, x1, y1, x2, y2, c)
    line(canvas, x0, y0, x1, y1, c)
    line(canvas, x1, y1, x2, y2, c)
    line(canvas, x2, y2, x0, y0, c)
    left = min(x0, x1, x2)
    top = min(y0, y1, y2)
    right = max(x0, x1, x2)
    bottom = max(y0, y1, y2)
    return Area(left, top, right - left, bottom - top)

def _fill_triangle(canvas, x0, y0, x1, y1, x2, y2, c):
    # pylint: disable=too-many-arguments, too-many-locals, too-many-statements, too-many-branches
    """Filled triangle drawing function.  Will draw a filled triangle around
    the points (x0, y0), (x1, y1), and (x2, y2)."""
    if y0 > y1:
        y0, y1 = y1, y0
        x0, x1 = x1, x0
    if y1 > y2:
        y2, y1 = y1, y2
        x2, x1 = x1, x2
    if y0 > y1:
        y0, y1 = y1, y0
        x0, x1 = x1, x0
    a = 0
    b = 0
    last = 0
    if y0 == y2:
        a = x0
        b = x0
        if x1 < a:
            a = x1
        elif x1 > b:
            b = x1
        if x2 < a:
            a = x2
        elif x2 > b:
            b = x2
        hline(canvas, a, y0, b - a + 1, c)
        return
    dx01 = x1 - x0
    dy01 = y1 - y0
    dx02 = x2 - x0
    dy02 = y2 - y0
    dx12 = x2 - x1
    dy12 = y2 - y1
    if dy01 == 0:
        dy01 = 1
    if dy02 == 0:
        dy02 = 1
    if dy12 == 0:
        dy12 = 1
    sa = 0
    sb = 0
    y = y0
    if y0 == y1:
        last = y1 - 1
    else:
        last = y1
    while y <= last:
        a = x0 + sa // dy01
        b = x0 + sb // dy02
        sa += dx01
        sb += dx02
        if a > b:
            a, b = b, a
        hline(canvas, a, y, b - a + 1, c)
        y += 1
    sa = dx12 * (y - y1)
    sb = dx02 * (y - y0)
    while y <= y2:
        a = x1 + sa // dy12
        b = x0 + sb // dy02
        sa += dx12
        sb += dx02
        if a > b:
            a, b = b, a
        hline(canvas, a, y, b - a + 1, c)
        y += 1
    left = min(x0, x1, x2)
    top = min(y0, y1, y2)
    right = max(x0, x1, x2)
    bottom = max(y0, y1, y2)
    return Area(left, top, right - left, bottom - top)

def round_rect(canvas, x0, y0, w, h, r, c, f=False):
    """Rectangle with rounded corners drawing function.
    This works like a regular rect though! if r = 0
    Will draw the outline of a rectangle with rounded corners with (x0,y0) at the top left
    """
    if f:
        return _fill_round_rect(canvas, x0, y0, w, h, r, c)
    # shift to correct for start point location
    x0 += r
    y0 += r

    # ensure that the r will only ever half of the shortest side or less
    r = int(min(r, w / 2, h / 2))

    if r:
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r
        vline(canvas, x0 - r, y0, h - 2 * r + 1, c)  # left
        vline(canvas, x0 + w - r, y0, h - 2 * r + 1, c)  # right
        hline(canvas, x0, y0 + h - r + 1, w - 2 * r + 1, c)  # bottom
        hline(canvas, x0, y0 - r, w - 2 * r + 1, c)  # top
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            # angle notations are based on the unit circle and in diection of being drawn

            # top left
            pixel(canvas, x0 - y, y0 - x, c)  # 180 to 135
            pixel(canvas, x0 - x, y0 - y, c)  # 90 to 135
            # top right
            pixel(canvas, x0 + x + w - 2 * r, y0 - y, c)  # 90 to 45
            pixel(canvas, x0 + y + w - 2 * r, y0 - x, c)  # 0 to 45
            # bottom right
            pixel(canvas, x0 + y + w - 2 * r, y0 + x + h - 2 * r, c) # 0 to 315
            pixel(canvas, x0 + x + w - 2 * r, y0 + y + h - 2 * r, c)  # 270 to 315
            # bottom left
            pixel(canvas, x0 - x, y0 + y + h - 2 * r, c)  # 270 to 255
            pixel(canvas, x0 - y, y0 + x + h - 2 * r, c)  # 180 to 225
    return Area(x0 - r, y0 - r, w - 2 * r, h - 2 * r)

def _fill_round_rect(canvas, x0, y0, w, h, r, c):
    """Filled circle drawing function.  Will draw a filled circle with
    center at x0, y0 and the specified r."""
    # shift to correct for start point location
    x0 += r
    y0 += r

    # ensure that the r will only ever half of the shortest side or less
    r = int(min(r, w / 2, h / 2))

    fill_rect(canvas, x0, y0 - r, w - 2 * r + 2, h + 2, c)

    if r:
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            # part notation starts with 0 on left and 1 on right, and direction is noted
            # top left
            vline(canvas, x0 - y, y0 - x, 2 * x + 1 + h - 2 * r, c)  # 0 to .25
            vline(canvas, x0 - x, y0 - y, 2 * y + 1 + h - 2 * r, c)  # .5 to .25
            # top right
            vline(canvas, x0 + x + w - 2 * r, y0 - y, 2 * y + 1 + h - 2 * r, c)  # .5 to .75
            vline(canvas, x0 + y + w - 2 * r, y0 - x, 2 * x + 1 + h - 2 * r, c)  # 1 to .75
    return Area(x0 - r, y0 - r, w - 2 * r, h - 2 * r)

def arc(canvas, x, y, r, a0, a1, c):
    resolution = 60
    a0 = math.radians(a0)
    a1 = math.radians(a1)
    x0 = x + int(r * math.cos(a0))
    y0 = y + int(r * math.sin(a0))
    if a1 > a0:
        arc_range = range(int(a0 * resolution), int(a1 * resolution))
    else:
        arc_range = range(int(a0 * resolution), int(a1 * resolution), -1)

    x_min = x_max = x0
    y_min = y_max = y0
    for a in arc_range:
        ar = a / resolution
        x1 = x + int(r * math.cos(ar))
        y1 = y + int(r * math.sin(ar))
        line(canvas, x0, y0, x1, y1, c)
        x_min = min(x0, x1, x_min)
        x_max = max(x0, x1, x_max)
        y_min = min(y0, y1, y_min)
        y_max = max(y0, y1, y_max)
        x0 = x1
        y0 = y1
    return Area(x_min, y_min, x_max - x_min, y_max - y_min)

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
    # MIT License
    # Copyright (c) 2024 Brad Barnett
    # Copyright (c) 2020-2023 Russ Hughes
    # Copyright (c) 2019 Ivan Belokobylskiy
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
