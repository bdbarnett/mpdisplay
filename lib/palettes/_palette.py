
# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT


class Palette:
    """
    A class to represent a color palette.
    """
    def __init__(self, name="", color_depth=16, swapped=False, cached=False):
        self._name = name
        self._color_depth = color_depth
        self._swapped = swapped
        self._cache = dict() if cached else None

        self._define_named_colors()

    def _define_named_colors(self):
        if not hasattr(self, "_names"):
            from ._win16 import WIN16 as NAMES
            self._names = NAMES
            self._length = len(self._names)
        for color, name in self._names.items():
            if self._color_depth == 16:
                color = self.color565(color)
            setattr(self, name.replace(" ", "_").upper(), color)

    @property
    def name(self):
        return self._name

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        return self._length
    
    def __getitem__(self, index):
        index = self._normalize(index)

        if self._cache is not None:
            if index in self._cache:
                return self._cache[index]
    
        r, g, b = self._get_rgb(index)
        if self._color_depth == 24:
            return r << 16 | g << 8 | b
        elif self._color_depth == 16:
            return self.color565(r, g, b)
        raise ValueError("Invalid color depth")

    def _normalize(self, index):
        while index < 0:
            index += len(self)
        if index >= len(self):
            index %= len(self)
        return index

    def color565(self, r, g=None, b=None):
        if isinstance(r, (tuple, list)):
            # r is a tuple or list
            r, g, b = r
        elif g is None:
            # r is a 24-bit color
            r, g, b = r >> 16 & 0xFF, r >> 8 & 0xFF, r & 0xFF

        color = (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3
        if self._swapped:
            return (color & 0xFF) << 8 | (color & 0xFF00) >> 8 
        else:
            return color

    def color_name(self, index):
        return self.rgb_name(self._get_rgb(self._normalize(index)))

    def rgb_name(self, r, g=None, b=None):
        if isinstance(r, (tuple, list)):
            r, g, b = r
        return self._names.get(r << 16 | g << 8 | b, f"#{r:02X}{g:02X}{b:02X}")
    
    def luminance(self, index):
        r, g, b = self._get_rgb(index)
        return 0.299 * r + 0.587 * g + 0.114 * b
    
    def brightness(self, index):
        r, g, b = self._get_rgb(index)
        return (r + g + b) / 3 / 255

    def _get_rgb(self, index):
        color = list(self._names.keys())[index]
        return color >> 16 & 0xFF, color >> 8 & 0xFF, color & 0xFF


class MappedPalette(Palette):
    """
    A class to represent a color palette with a color map.
    """
    def __init__(self, name, color_depth, swapped, color_map):
        self._color_map = color_map
        self._length = len(color_map) // 3
        super().__init__(name, color_depth, swapped)

    def _get_rgb(self, index):
        r, g, b = self._color_map[index*3:index*3+3]
        return r, g, b
