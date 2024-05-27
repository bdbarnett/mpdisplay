# SPDIX:# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
Makes a color cube palette.

Usage:
    from primitives.palettes import get_palette
    palette = get_palette(name="wheel", size=5, color_depth=16, swapped=False)

    # OR
    from board_config import display_drv
    palette = display_drv.get_palette(name="cube", size=5, color_depth=16, swapped=False)
    # OR
    palette = display_drv.get_palette(name="cube")

    # OR
    from primitives.palettes.cube import CubePalette
    palette = CubePalette(size=5, color_depth=24)

    print(f"Palette: {palette.name}, Length: {len(palette)}")
    for i, color in enumerate(palette):
        for i, color in enumerate(palette):  print(f"{i}. {color:#06X} {palette.color_name(i)}")
"""
from ._palette import Palette as _Palette


class CubePalette(_Palette):
    """
    size specifies the number of values per color channel.
    """
    def __init__(self, name="", color_depth=16, swapped=False, cached=True, size=5):
        super().__init__(name, color_depth, swapped, cached)

        self._size = size
        self._length = size ** 3
        self._values = [round(i * (255 / (size - 1)) + .25) for i in range(size)]
        self._name = name if name else f"Cube{len(self)}"

    def _get_rgb(self, index):
        z = index % self._size
        index //= self._size
        y = index % self._size
        index //= self._size
        x = index % self._size
        return self._values[x], self._values[y], self._values[z]
