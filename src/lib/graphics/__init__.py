# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
Graphics module.
"""


def color888(r, g, b):
    """
    Convert RGB values to a 24-bit color value.

    :param r: The red value.
    :type r: int
    :param g: The green value.
    :type g: int
    :param b: The blue value.
    :type b: int
    :return: The 24-bit color value.
    :rtype: int
    """
    return (r << 16) | (g << 8) | b

def color565(r, g=0, b=0):
    """
    Convert RGB values to a 16-bit color value.

    :param r: The red value.
    :type r: int
    :param g: The green value.
    :type g: int
    :param b: The blue value.
    :type b: int
    :return: The 16-bit color value.
    :rtype: int
    """
    if isinstance(r, (tuple, list)):
        r, g, b = r[:3]
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def color565_swapped(r, g=0, b=0):
    # Convert r, g, b in range 0-255 to a 16 bit color value RGB565
    # ggbbbbbb rrrrrggg
    if isinstance(r, (tuple, list)):
        r, g, b = r[:3]
    color = color565(r, g, b)
    return (color & 0xFF) << 8 | (color & 0xFF00) >> 8

def color332(r, g, b):
    # Convert r, g, b in range 0-255 to an 8 bit color value RGB332
    # rrrgggbb
    return (r & 0xE0) | ((g >> 3) & 0x1C) | (b >> 6)

def color_rgb(color):
    """
    color can be an 16-bit integer or a tuple, list or bytearray of length 2 or 3.
    """
    if isinstance(color, int):
        # convert 16-bit int color to 2 bytes
        color = (color & 0xFF, color >> 8)
    if len(color) == 2:
        r = color[1] & 0xF8 | (color[1] >> 5) & 0x7  # 5 bit to 8 bit red
        g = color[1] << 5 & 0xE0 | (color[0] >> 3) & 0x1F  # 6 bit to 8 bit green
        b = color[0] << 3 & 0xF8 | (color[0] >> 2) & 0x7  # 5 bit to 8 bit blue
    else:
        r, g, b = color
    return (r, g, b)


class Area:
    """
    Represents a rectangular area defined by its position and dimensions.
    """

    def __init__(self, x, y, w, h):
        """
        Initializes a new instance of the Area class.

        Args:
            x (int): The x-coordinate of the top-left corner of the area.
            y (int): The y-coordinate of the top-left corner of the area.
            w (int): The width of the area.
            h (int): The height of the area.
        """
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    def __repr__(self):
        """
        Returns a string representation of the Area object.

        Returns:
            str: A string representation of the Area object.
        """
        return f"Area({self.x}, {self.y}, {self.w}, {self.h})"
    
    def __str__(self):
        """
        Returns a string representation of the Area object.

        Returns:
            str: A string representation of the Area object.
        """
        return f"Area({self.x}, {self.y}, {self.w}, {self.h})"
    
    def __eq__(self, other):
        """
        Checks if the current Area object is equal to another Area object.

        Args:
            other (Area): The other Area object to compare with.

        Returns:
            bool: True if the two Area objects are equal, False otherwise.
        """
        return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h
    
    def __ne__(self, other):
        """
        Checks if the current Area object is not equal to another Area object.

        Args:
            other (Area): The other Area object to compare with.

        Returns:
            bool: True if the two Area objects are not equal, False otherwise.
        """
        return not self.__eq__(other)
    
    def __add__(self, other):
        """
        Computes the union of the current Area object and another Area object.

        Args:
            other (Area): The other Area object to compute the union with.

        Returns:
            Area: A new Area object representing the union of the two areas.
        """
        return Area(
            min(self.x, other.x),
            min(self.y, other.y),
            max(self.x + self.w, other.x + other.w) - min(self.x, other.x),
            max(self.y + self.h, other.y + other.h) - min(self.y, other.y)
        )
    
    def __len__(self):
        """
        Returns the number of elements in the Area object.

        Returns:
            int: The number of elements in the Area object.
        """
        return 4

    def __iter__(self):
        """
        Returns an iterator over the elements of the Area object.

        Returns:
            iterator: An iterator over the elements of the Area object.
        """
        return iter((self.x, self.y, self.w, self.h))

    @property
    def x(self):
        """
        Gets the x-coordinate of the top-left corner of the area.

        Returns:
            int: The x-coordinate of the top-left corner of the area.
        """
        return self._x
    
    @property
    def y(self):
        """
        Gets the y-coordinate of the top-left corner of the area.

        Returns:
            int: The y-coordinate of the top-left corner of the area.
        """
        return self._y
    
    @property
    def w(self):
        """
        Gets the width of the area.

        Returns:
            int: The width of the area.
        """
        return self._w
    
    @property
    def h(self):
        """
        Gets the height of the area.

        Returns:
            int: The height of the area.
        """
        return self._h
 
