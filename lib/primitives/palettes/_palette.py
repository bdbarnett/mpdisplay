
# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT


NAMES = {
    0x000000: "Black",
    0x000040: "Navy Blue",
    0x000080: "Dark Blue",
    0x0000C0: "Cobalt Blue",
    0x0000FF: "Blue",
    0x004000: "Dark Green",
    0x004040: "Teal",
    0x004080: "Steel Blue",
    0x0040C0: "Deep Sky Blue",
    0x0040FF: "Dodger Blue",
    0x008000: "Green",
    0x008040: "Medium Sea Green",
    0x008080: "Dark Cyan",
    0x0080C0: "Light Sea Green",
    0x0080FF: "Deep Sky Blue",
    0x00C000: "Lime Green",
    0x00C040: "Spring Green",
    0x00C080: "Medium Spring Green",
    0x00C0C0: "Aquamarine",
    0x00C0FF: "Turquoise",
    0x00FF00: "Lime",
    0x00FF40: "Lawn Green",
    0x00FF80: "Chartreuse",
    0x00FFC0: "Pale Green",
    0x00FFFF: "Cyan",
    0x400000: "Maroon",
    0x400040: "Purple",
    0x400080: "Indigo",
    0x4000C0: "Blue Violet",
    0x4000FF: "Medium Slate Blue",
    0x404000: "Olive",
    0x404040: "Dim Gray",
    0x404080: "Slate Blue",
    0x4040C0: "Royal Blue",
    0x4040FF: "Medium Blue",
    0x408000: "Dark Olive Green",
    0x408040: "Sea Green",
    0x408080: "Cadet Blue",
    0x4080C0: "Cornflower Blue",
    0x4080FF: "Steel Blue",
    0x40C000: "Yellow Green",
    0x40C040: "Medium Aquamarine",
    0x40C080: "Medium Sea Green",
    0x40C0C0: "Light Blue",
    0x40C0FF: "Sky Blue",
    0x40FF00: "Lime",
    0x40FF40: "Lawn Green",
    0x40FF80: "Spring Green",
    0x40FFC0: "Pale Green",
    0x40FFFF: "Aquamarine",
    0x800000: "Red",
    0x800040: "Deep Pink",
    0x800080: "Purple",
    0x8000C0: "Dark Violet",
    0x8000FF: "Dark Orchid",
    0x804000: "Saddle Brown",
    0x804040: "Rosy Brown",
    0x804080: "Medium Orchid",
    0x8040C0: "Medium Purple",
    0x8040FF: "Slate Blue",
    0x808000: "Olive",
    0x808040: "Dark Khaki",
    0x808080: "Gray",
    0x8080C0: "Light Slate Gray",
    0x8080FF: "Light Steel Blue",
    0x80C000: "Yellow Green",
    0x80C040: "Chartreuse",
    0x80C080: "Pale Green",
    0x80C0C0: "Light Green",
    0x80C0FF: "Pale Turquoise",
    0x80FF00: "Lime",
    0x80FF40: "Spring Green",
    0x80FF80: "Light Green",
    0x80FFC0: "Medium Spring Green",
    0x80FFFF: "Pale Turquoise",
    0xC00000: "Dark Red",
    0xC00040: "Medium Violet Red",
    0xC00080: "Crimson",
    0xC000C0: "Magenta",
    0xC000FF: "Deep Pink",
    0xC04000: "Orange Red",
    0xC04040: "Tomato",
    0xC04080: "Hot Pink",
    0xC040C0: "Deep Pink",
    0xC040FF: "Orchid",
    0xC08000: "Dark Orange",
    0xC08040: "Peru",
    0xC08080: "Sandy Brown",
    0xC080C0: "Light Coral",
    0xC080FF: "Medium Orchid",
    0xC0C000: "Gold",
    0xC0C040: "Khaki",
    0xC0C080: "Dark Khaki",
    0xC0C0C0: "Silver",
    0xC0C0FF: "Light Steel Blue",
    0xC0FF00: "Chartreuse",
    0xC0FF40: "Lawn Green",
    0xC0FF80: "Green Yellow",
    0xC0FFC0: "Pale Green",
    0xC0FFFF: "Pale Turquoise",
    0xFF0000: "Red",
    0xFF0040: "Deep Pink",
    0xFF0080: "Hot Pink",
    0xFF00C0: "Magenta",
    0xFF00FF: "Fuchsia",
    0xFF4000: "Orange Red",
    0xFF4040: "Tomato",
    0xFF4080: "Violet Red",
    0xFF40C0: "Orchid",
    0xFF40FF: "Fuchsia",
    0xFF8000: "Dark Orange",
    0xFF8040: "Coral",
    0xFF8080: "Light Coral",
    0xFF80C0: "Medium Orchid",
    0xFF80FF: "Pink",
    0xFFC000: "Gold",
    0xFFC040: "Light Goldenrod",
    0xFFC080: "Peach Puff",
    0xFFC0C0: "Light Pink",
    0xFFC0FF: "Lavender Blush",
    0xFFFF00: "Yellow",
    0xFFFF40: "Light Yellow",
    0xFFFF80: "Pale Goldenrod",
    0xFFFFC0: "Lemon Chiffon",
    0xFFFFFF: "White",
}


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
        for color, name in NAMES.items():
            setattr(self, name.replace(" ", "_").upper(), color)

    @property
    def name(self):
        return self._name

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        return self._length  # must be implemented by subclasses
    
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
        return NAMES.get(r << 16 | g << 8 | b, f"#{r:02X}{g:02X}{b:02X}")

    def _get_rgb(self, index):
        raise NotImplementedError("Subclasses must implement this method")


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

"""

    def _define_named_colors(self):
        # Comments show the names from the "12 major color wheel colors".
        # The second color name in the comments is the palette family from.
        # Material Design.  An asterisk denote the color name exists in EGA.

        # Monochrome colors with only 0, 127 and 255 as RGB values:
        self.BLACK = self.color565(0, 0, 0)  # *
        self.WHITE = self.color565(255, 255, 255)  # *
        self.GREY = self.color565(127, 127, 127)   # (Grey)

        # The 12 major color wheel colors:
        self.RED = self.color565(255, 0, 0)  # * Red (Red)
        self.ORANGE = self.color565(255, 127, 0)  # Orange (Orange)
        self.YELLOW = self.color565(255, 255, 0)  # * Yellow (Yellow)
        self.LIME = self.color565(127, 255, 0)  # Chartreuse (Lime)
        self.GREEN = self.color565(0, 255, 0)  # * Green (Green)
        self.SPRING_GREEN = self.color565(0, 255, 127)  # Spring Green
        self.CYAN = self.color565(0, 255, 255)  # * Cyan (Cyan)
        self.AZURE = self.color565(0, 127, 255)  # Azure
        self.BLUE = self.color565(0, 0, 255)  # * Blue (Blue)
        self.INDIGO = self.color565(127, 0, 255)  # Violet (Indigo)
        self.MAGENTA = self.color565(255, 0, 255)  # * Magenta
        self.ROSE = self.color565(255, 0, 127)  # Rose

        # The other 12 colors that have only 0, 127 and 255 as RGB values:
        self.TEAL = self.color565(0, 127, 127)  # (Teal)
        self.PURPLE = self.color565(127, 0, 127)  # (Purple)
        self.PINK = self.color565(255, 127, 255)  # (Pink)
        self.LIGHT_GREEN = self.color565(127, 255, 127)  # * (Light Green)
        self.LIGHT_BLUE = self.color565(127, 127, 255)  # * (Light Blue)
        self.LIGHT_CYAN = self.color565(127, 255, 255)  # * Light Cyan
        self.LIGHT_YELLOW = self.color565(255, 255, 127)  # Light Yellow
        self.DARK_RED = self.color565(127, 0, 0)  # Dark Red
        self.DARK_BLUE = self.color565(0, 0, 127)  # Dark Blue
        self.SKY_BLUE = self.color565(0, 127, 255)  # Sky Blue
        self.OLIVE = self.color565(127, 127, 0)  # Olive
        self.SALMON = self.color565(255, 127, 127)  # Salmon

        # Other colors rounding out the 32 named colors:
        self.BROWN = self.color565(127, 63, 0)  # * (Brown)
        self.LIGHT_GREY = self.color565(191, 191, 191) # *
        self.DARK_GREY = self.color565(63, 63, 63) # *
        self.AMBER = self.color565(255, 191, 0)  # (Amber)
        self.BLUE_GREY = self.color565(63, 95, 127)  # (Blue Grey)

        # EGA colors that aren't defined:
        self.LIGHT_RED = self.color565(255, 63, 63)
        self.LIGHT_MAGENTA = self.color565(255, 63, 255)

"""