"""
This module contains the cool wheel color palette as a class object.


Usage:
    from primitives.palettes import get_palette
    palette = get_palette(name="wheel", color_depth=16, swapped=False)

    # OR
    from board_config import display_drv
    palette = display_drv.get_palette(name="wheel", color_depth=16, swapped=False)
    # OR
    palette = display_drv.get_palette()

    # to access the 32 named colors directly:
    x = palette.RED
    x = palette.BLACK

    # to iterate over all 256 colors:
        for x in palette:
            pass

"""
from ._palette import Palette as _Palette


class CWPalette(_Palette):
    """
    A class to represent a color wheel as a palette.
    """

    def __init__(self, name="", color_depth=16, swapped=False):
        super().__init__(name, color_depth, swapped)

        # Define all 27 colors that are combinations of 0, 127, 255
        # plus add dark_grey, light_grey, brown, tan, and gold
        # for a total of 32 colors
        self.BLACK = self.color565(0, 0, 0)
        self.WHITE = self.color565(255, 255, 255)
        self.RED = self.color565(255, 0, 0)
        self.PINK = self.color565(255, 128, 255)
        self.PURPLE = self.color565(128, 0, 128)
        self.DEEP_PURPLE = self.color565(64, 0, 128)
        self.INDIGO = self.color565(128, 0, 255)
        self.BLUE = self.color565(0, 0, 255)
        self.LIGHT_BLUE = self.color565(0, 128, 255)
        self.CYAN = self.color565(0, 255, 255)
        self.TEAL = self.color565(0, 128, 128)
        self.GREEN = self.color565(0, 255, 0)
        self.LIGHT_GREEN = self.color565(128, 255, 128)
        self.LIME = self.color565(128, 255, 0)
        self.YELLOW = self.color565(255, 255, 0)
        self.AMBER = self.color565(255, 192, 64)
        self.ORANGE = self.color565(255, 128, 0)
        self.DEEP_ORANGE = self.color565(255, 128, 64)
        self.BROWN = self.color565(128, 64, 0)
        self.GREY = self.color565(128, 128, 128)
        self.BLUE_GREY = self.color565(64, 96, 128)

        self.LIGHT_GREY = self.color565(192, 192, 192)
        self.DARK_GREY = self.color565(64, 64, 64)
        self.MAROON = self.color565(128, 0, 0)
        self.DEEP_PINK = self.color565(255, 0, 128)
        self.LIGHT_RED = self.color565(255, 64, 64)
        self.DARK_BLUE = self.color565(0, 0, 128)
        self.DARK_GREEN = self.color565(0, 128, 0)
        self.SALMON = self.color565(255, 128, 128)
        self.MAGENTA = self.color565(255, 0, 255)
        self.LIGHT_MAGENTA = self.color565(255, 64, 255)
        self.LIGHT_CYAN = self.color565(128, 255, 255)

    def __getitem__(self, index):
        while index < 0:
            index += 256

        index = 255 - index
        if index < 85:
            r, g, b = (255 - index * 3, 0, index * 3)
        elif index < 170:
            index -= 85
            r, g, b = (0, index * 3, 255 - index * 3)
        else:
            index -= 170
            r, g, b = (index * 3, 255 - index * 3, 0)

        if self._color_depth == 24:
            return r << 16 | g << 8 | b
        elif self._color_depth == 16:
            return self.color565(r, g, b)
        else:
            raise ValueError("Invalid color depth")

    def __len__(self):
        return 256