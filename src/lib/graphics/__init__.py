# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
Graphics module.
"""


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
 
