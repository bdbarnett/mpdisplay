# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

from ._palette import Palette as _Palette
from ._ega import COLORS

class EGAPalette(_Palette):
    """
    A class to represent the EGA color palette.
    """

    def __init__(self, name="", color_depth=16, swapped=False, colors=COLORS):
        super().__init__(name, color_depth, swapped, colors)

        # EGA 16 colors
        self.BLACK = self[0]
        self.BLUE = self[1]
        self.GREEN = self[2]
        self.CYAN = self[3]
        self.RED = self[4]
        self.MAGENTA = self[5]
        self.BROWN = self[20]
        self.LIGHT_GREY = self[7]
        self.DARK_GREY = self[56]
        self.LIGHT_BLUE = self[57]
        self.LIGHT_GREEN = self[58]
        self.LIGHT_CYAN = self[59]
        self.LIGHT_RED = self[60]
        self.LIGHT_MAGENTA = self[61]
        self.YELLOW = self[62]
        self.WHITE = self[63]

        # Custom colors
        self.PINK = self[47]
        self.PURPLE = self[41]
        self.DEEP_PURPLE = self[40]
        self.INDIGO = self[29]
        self.TEAL = self[24]
        self.LIME = self[34]
        self.AMBER = self[46]
        self.ORANGE = self[38]
        self.DEEP_ORANGE = self[52]
        self.GREY = self[48]  # closer to olive
        self.BLUE_GREY = self[17]

        self.MAROON = self[32]
        self.DEEP_PINK = self[45]
        self.DARK_BLUE = self[8]
        self.DARK_GREEN = self[16]
        self.SALMON = self[39]
