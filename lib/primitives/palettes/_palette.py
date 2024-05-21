
# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT


class Palette:
    """
    A class to represent a color palette.
    """
    def __init__(self, name="", color_depth=16, swapped=False, colors=None):
        self._name = name
        self._color_depth = color_depth
        self._needs_swap = swapped
        self._colors = colors

    def __getitem__(self, index):
        while index < 0:
            index += 256
        r, g, b = self._colors[index*3:index*3+3]
        if self._color_depth == 24:
            return r << 16 | g << 8 | b
        elif self._color_depth == 16:
            return self.color565(r, g, b)
        else:
            raise ValueError("Invalid color depth")

    def __len__(self):
        return len(self._colors)//3
    
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def color565(self, r, g=None, b=None):
        if isinstance(r, (tuple, list)):
            # r is a tuple or list
            r, g, b = r
        elif g is None:
            # r is a 24-bit color
            r, g, b = r >> 16 & 0xFF, r >> 8 & 0xFF, r & 0xFF

        color = (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3
        if self._needs_swap:
            return (color & 0xFF) << 8 | (color & 0xFF00) >> 8 
        else:
            return color
