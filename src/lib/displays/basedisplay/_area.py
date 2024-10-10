# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
This module defines the Area class, which represents a rectangular area defined by its position and dimensions.
"""


class Area:
    """
    Represents a rectangular area defined by its position and dimensions.
    """

    def __init__(self, x, y, w, h):
        """
        Initializes a new instance of the Area class.

        Args:
            x (int | float): The x-coordinate of the top-left corner of the area.
            y (int | float): The y-coordinate of the top-left corner of the area.
            w (int | float): The width of the area.
            h (int | float): The height of the area.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self, x, y=None):
        """
        Checks if the specified point is contained within the area.

        Args:
            x (int | tuple): The x-coordinate of the point to check
                or a tuple containing the x and y coordinates of the point.
            y (int): The y-coordinate of the point to check.

        Returns:
            bool: True if the point is contained within the area, False otherwise.
        """
        if isinstance(x, tuple):
            x, y = x
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    def contains_area(self, other):
        """
        Checks if the specified area is contained within the area.

        Args:
            other (Area): The other area to check.

        Returns:
            bool: True if the other area is contained within the area, False otherwise.
        """
        return (
            self.x <= other.x
            and self.y <= other.y
            and self.x + self.w >= other.x + other.w
            and self.y + self.h >= other.y + other.h
        )

    def intersects(self, other):
        """
        Checks if the current Area object intersects with another Area object.

        Args:
            other (Area): The other Area object to check for overlap.

        Returns:
            bool: True if the two Area objects intersect, False otherwise.
        """
        # Check if one rectangle is to the left of the other
        if self.x + self.w <= other.x or other.x + other.w <= self.x:
            return False
        # Check if one rectangle is above the other
        if self.y + self.h <= other.y or other.y + other.h <= self.y:
            return False
        return True

    def offset_by(self, dx=0, dy=0):
        """
        Returns a new Area offset by the specified amount in the x and y directions.

        Args:
            dx (int | float): The amount to offset the area in the x direction.
            dy (int | float): The amount to offset the area in the y direction.

        Returns:
            Area: A new Area object offset by the specified amount in the x and y directions.
        """
        return Area(self.x + dx, self.y + dy, self.w, self.h)

    def clip(self, other):
        """
        Clips the current Area object to the specified Area object.

        Args:
            other (Area): The other Area object to clip to.

        Returns:
            Area: A new Area object representing the clipped area.
        """
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        w = min(self.x + self.w, other.x + other.w) - x
        h = min(self.y + self.h, other.y + other.h) - y
        return Area(x, y, w, h)

    def __eq__(self, other):
        """
        Checks if the current Area object is equal to another Area object.

        Args:
            other (Area): The other Area object to compare with.

        Returns:
            bool: True if the two Area objects are equal, False otherwise.
        """
        return (
            self.x == other.x
            and self.y == other.y
            and self.w == other.w
            and self.h == other.h
        )

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
            max(self.y + self.h, other.y + other.h) - min(self.y, other.y),
        )

    def __iter__(self):
        """
        Returns an iterator over the elements of the Area object.

        Returns:
            iterator: An iterator over the elements of the Area object.
        """
        return iter((self.x, self.y, self.w, self.h))

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
