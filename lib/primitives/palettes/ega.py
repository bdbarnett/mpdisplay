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

        self._define_named_colors()

    def _define_named_colors(self):

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
        # The first comment name is the name in the 12 major color wheel colors.
        # The comment in parenthesis is the name in the Material Design palette.
        self.GREY = self.color565(127, 127, 127)   # (Grey)
        self.ORANGE = self[52]  # Orange (Orange)
        self.LIME = self[34]  # Chartreuse (Lime)
        self.SPRING_GREEN = self[26]  # Spring Green
        self.AZURE = self[25]  # Azure
        self.INDIGO = self[41]  # Violet (Indigo)
        self.ROSE = self[44]  # Rose
        self.TEAL = self[24]  # (Teal)
        self.PURPLE = self[40]  # (Purple)
        self.PINK = self[45]  # (Pink)
        self.LIGHT_YELLOW = self[55]
        self.DARK_RED = self[32]
        self.DARK_BLUE = self[8]
        self.SKY_BLUE = self[11]
        self.AMBER = self[38]  # (Amber)
        self.BLUE_GREY = self[43]  # (Blue Grey)

        # Wheel colors that aren't defined here:
        self.OLIVE = self[48]  # Olive
        self.SALMON = self[39]  # Salmon


