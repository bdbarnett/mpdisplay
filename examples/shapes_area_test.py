"""
Test the Area return type of the shapes functions.

Shape functions return an Area object that represents the bounding box of the shape drawn.
This object can be used to optimize the display by redrawing only the area that has changed.

Area objects have the attributes x, y, w and h.  They may be added together, such as:
    area3 = area1 + area2

and may be unpacked, such as:
    x, y, w, h = area3
or as a function argument:
    shapes.rect(display_drv, *area3, display_drv.color565(0, 0, 255))

"""

from board_config import display_drv
from shapes import shapes


dirty = shapes.circle(display_drv, 120, 120, 50, display_drv.color565(255, 0, 0), True)
dirty += shapes.ellipse(display_drv, 100, 85, 50, 30, display_drv.color565(0, 255, 0), True, 0b1111)
shapes.rect(display_drv, *dirty, display_drv.color565(0, 0, 255))
