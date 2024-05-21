# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
This module contains the Material Design color palette as a class object.


Usage:
    from primitives.palettes import get_palette
    palette = get_palette(name="material_design", color_depth=16, swapped=False)

    # OR
    from board_config import display_drv
    palette = display_drv.get_palette(name="material_design", color_depth=16, swapped=False)
    # OR
    palette = display_drv.get_palette()

    # to access the primary variant of a color family by name:
    x = palette.RED
    x = palette.BLACK

    # to access all 256 colors directly:
    x = palette[127]  # color at index 127

    # to access a shade of a color family by index number:
    x = palette.red[0]  # shade 500
    x = palette.red[4]  # shade 900
    x = palette.red[-5]  # shade 50

    # to access a shade by name:
    x = palette.red.S500  # shade 500
    x = palette.red.S900  # shade 900
    x = palette.red.S50  # shade 50

    # to access an accent of a color family by index number:
    x = palette.red.accents[1]  # A100
    x = palette.red.accents[4]  # A700

    # to access an accent of a color family by name:
    x = palette.red.accents.A100
    x = palette.red.accents.A700

    # to iterate over all 256 colors:
        for x in palette:
            pass
            
    # to iterate over all shades in a family:
        for x in palette.red:  # iterate over all 10 shades
            pass
            
    # to iterate over all accents in a family:
        for x in palette.red.accents:  # iterate over all 4 accents
            pass


"""

from ._palette import Palette as _Palette
from ._material_design import COLORS, FAMILIES, LENGTHS


class Accents(_Palette):
    """
    A class to represent the accent colors.
    """

    accents = ["A100", "A200", "A400", "A700"]

    def __init__(self, name, color_depth, swapped, colors, add_names=True):
        super().__init__(name, color_depth, swapped, colors)

        if add_names:
            for i, accent in enumerate(self.accents):
                setattr(self, accent, self[i])


class Family(_Palette):
    """
    A class to represent the color variants.
    """

    shades = ["S50", "S100", "S200", "S300", "S400", "S500", "S600", "S700", "S800", "S900"]

    def __init__(self, name, color_depth, swapped, colors, add_names=True):
        super().__init__(name, color_depth, swapped, colors)

        if add_names:
            if len(self) > 1:
                for i, shade in enumerate(self.shades):
                    setattr(self, shade, self[i - 5])

        if len(self) > 10:
            self.accents = Accents(name + "_accents", color_depth, swapped, colors[-4 * 3 :], add_names)

    def __getitem__(self, index):
        """Return the color variant as an integer with the number of bits specified in the color depth."""
        if len(self) == 1:
            if index != 0:
                raise IndexError("Index out of range")
            else:
                index = 0
        else:
            index += 5
            if not (-1 < index < len(self)):
                raise IndexError("Index out of range")
        return super().__getitem__(index)

    def __iter__(self):
        if len(self) == 1:
            yield self[0]
        else:
            for i in range(-5, 5):
                yield self[i]


class Palette(_Palette):
    """
    A class to represent the Material Design color palette.
    """

    def __init__(self, name="", color_depth=16, swapped=False, colors=COLORS, add_names=True):
        super().__init__(name, color_depth, swapped, colors)

        index = 0
        for name, length in zip(FAMILIES, LENGTHS):
            setattr(
                self,
                name,
                Family(name, color_depth, swapped, colors[index : index + length * 3], add_names),
            )
            setattr(self, name.upper(), getattr(self, name)[0])
            index += length * 3

        self.MAGENTA = 0xFF00FF if color_depth == 24 else 0x1FF8 if self._needs_swap else 0xF81F
