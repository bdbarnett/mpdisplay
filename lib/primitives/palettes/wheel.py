"""
This module contains the cool wheel color palette as a class object.


Usage:
    from primitives.palettes import get_palette
    palette = get_palette(name="wheel", color_depth=16, swapped=False, length=256)

    # OR
    from board_config import display_drv
    palette = display_drv.get_palette(name="wheel", color_depth=16, swapped=False, length=256)
    # OR
    palette = display_drv.get_palette()

    # to access the 32 named colors directly:
    x = palette.RED
    x = palette.BLACK

    # to iterate over all available colors:
        for x in palette:
            pass

"""
from ._palette import Palette as _Palette


class CWPalette(_Palette):
    """
    A class to represent a color wheel as a palette.
    """

    def __init__(self, name="", color_depth=16, swapped=False, length=256):
        super().__init__(name, color_depth, swapped)

        self._length = length
        self._bounds = self._length - 1
        self._one_third = self._length // 3
        self._two_thirds = 2 * self._length // 3
        self._spacing = 256 * 3 / self._length

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
            index += self._length

        index = self._bounds - index
        if index < self._one_third:
            r, g, b = (255 - int(index * self._spacing), 0, int(index * self._spacing))
        elif index < self._two_thirds:
            index -= self._one_third
            r, g, b = (0, int(index * self._spacing), 255 - int(index * self._spacing))
        else:
            index -= self._two_thirds
            r, g, b = (int(index * self._spacing), 255 - int(index * self._spacing), 0)

        if self._color_depth == 24:
            return r << 16 | g << 8 | b
        elif self._color_depth == 16:
            return self.color565(r, g, b)
        else:
            raise ValueError("Invalid color depth")

    def __len__(self):
        return self._length