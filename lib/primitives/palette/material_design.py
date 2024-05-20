"""This module contains the Material Design color palette as a class object.

The color index goes from -4 to 5, where -4 is the darkest shade and 5 is the lightest.
0 is the primary color.


Usage:
    from lib.primitives.palette import palette

    # Load the Material Design palette in 16-bit color depth
    material_design = palette("material_design", 16)

    # to access the primary colors:
    primary_color_1 = material_design.red.s50  # shade 50

    primary_color_1 = material_design.red[0]  # 500
    primary_color_2 = material_design.red[4]  # 900
    primary_color_3 = material_design.red[-5]  # 50

    # to access the accent colors:
    accent_color_1 = material_design.red.a100

    # to access the accent colors with the index:
    accent_color_1 = material_design.red[5]  # A100
    accent_color_2 = material_design.red[8]  # A700

    # to access the accent colors directly:
    accent_color_1 = material_design.red.accent(1)  # A100

"""
from ._material_design import red, pink, purple, deep_purple, indigo, blue, light_blue, cyan, teal, green, light_green, lime, yellow, amber, orange, deep_orange, brown, grey, blue_grey


class Variants:
    """
    A class to represent the color variants.
    """
    def __init__(self, family, color_depth):
        self._bytes = family
        self._color_depth = color_depth

    def accent(self, index):
        if index not in range(1, 5):
            raise IndexError("Index out of range")
        return self[index+4]

    @property
    def s50(self):
        return self[-5]
    
    @property
    def s100(self):
        return self[-4]
    
    @property
    def s200(self):
        return self[-3]
    
    @property
    def s300(self):
        return self[-2]
    
    @property
    def s400(self):
        return self[-1]
    
    @property
    def s500(self):
        return self[0]
    
    @property
    def s600(self):
        return self[1]
    
    @property
    def s700(self):
        return self[2]
    
    @property
    def s800(self):
        return self[3]
    
    @property
    def s900(self):
        return self[4]
    
    @property
    def a100(self):
        return self[5]
    
    @property
    def a200(self):
        return self[6]
    
    @property
    def a400(self):
        return self[7]
    
    @property
    def a700(self):
        return self[8]
    
    def __getitem__(self, index):
        """Return the color variant as an integer with the number of bits specified in the color depth."""
        if index not in range(-5, 9):
            raise IndexError("Index out of range")
        index += 5  # adjust the index to the list
        color = int.from_bytes(self._bytes[index*3:index*3+3], "big")
        print(f"{color=:06X}")
        if self._color_depth == 24:
            return color
        elif self._color_depth == 16:
            # convert the 24-bit color to 16-bit color
            r, g, b = color.to_bytes(3, "big")
            return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3
        else:
            raise ValueError("Invalid color depth")
    
    def __iter__(self):
        return iter([self.s50, self.s100, self.s200, self.s300, self.s400, self.s500, self.s600, self.s700, self.s800, self.s900, self.a100, self.a200, self.a400, self.a700])
    
    def __len__(self):
        return 14


class Palette:
    """
    A class to represent the Material Design color palette.
    """
    def __init__(self, color_depth=24):
        self.red = Variants(red, color_depth)
        self.pink = Variants(pink, color_depth)
        self.purple = Variants(purple, color_depth)
        self.deep_purple = Variants(deep_purple, color_depth)
        self.indigo = Variants(indigo, color_depth)
        self.blue = Variants(blue, color_depth)
        self.light_blue = Variants(light_blue, color_depth)
        self.cyan = Variants(cyan, color_depth)
        self.teal = Variants(teal, color_depth)
        self.green = Variants(green, color_depth)
        self.light_green = Variants(light_green, color_depth)
        self.lime = Variants(lime, color_depth)
        self.yellow = Variants(yellow, color_depth)
        self.amber = Variants(amber, color_depth)
        self.orange = Variants(orange, color_depth)
        self.deep_orange = Variants(deep_orange, color_depth)
        self.brown = Variants(brown, color_depth)
        self.grey = Variants(grey, color_depth)
        self.blue_grey = Variants(blue_grey, color_depth)
        self.black = 0x0
        self.white = 0xFFFFFF if color_depth == 24 else 0xFFFF
