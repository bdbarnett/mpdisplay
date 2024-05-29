
# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

# 125 colors with only 0x00, 0x40, 0x80, 0xC0, 0xFF as RGB values
NAMES = {
    0x000000: "Black",
    0x000040: "Midnight Express",
    0x000080: "Navy",
    0x0000C0: "Medium Blue",
    0x0000FF: "Blue",
    0x004000: "Myrtle",
    0x004040: "Cyprus",
    0x004080: "Dark Cerulean",
    0x0040C0: "Cobalt",
    0x0040FF: "Vivid Navy",
    0x008000: "Green",
    0x008040: "Dark Spring Green",
    0x008080: "Teal",
    0x0080C0: "Cerulean",
    0x0080FF: "Azure",
    0x00C000: "Islamic Green",
    0x00C040: "Dark Pastel Green",
    0x00C080: "Faux-Green",
    0x00C0C0: "Iris Blue",
    0x00C0FF: "Deep Sky Blue",
    0x00FF00: "Lime",
    0x00FF40: "Malachite",
    0x00FF80: "Spring Green",
    0x00FFC0: "Medium Spring Green",
    0x00FFFF: "Cyan",
    0x400000: "Seal Brown",
    0x400040: "Deep Purple",
    0x400080: "Indigo",
    0x4000C0: "Purple Heart",
    0x4000FF: "Han Purple",
    0x404000: "Turtle Green",
    0x404040: "Dark Gray",
    0x404080: "Jackson's Purple",
    0x4040C0: "Free Speech Blue",
    0x4040FF: "Neon Blue",
    0x408000: "Bilbao",
    0x408040: "Japanese Laurel",
    0x408080: "Paradiso",
    0x4080C0: "Curious Blue",
    0x4080FF: "Royal Blue",
    0x40C000: "Strong Green",
    0x40C040: "Lime Green",
    0x40C080: "Medium Sea Green",
    0x40C0C0: "Medium Turquoise",
    0x40C0FF: "Summer Sky",
    0x40FF00: "Harlequin",
    0x40FF40: "Lime Green",
    0x40FF80: "Screamin' Green",
    0x40FFC0: "Turquoise",
    0x40FFFF: "Baby Blue",
    0x800000: "Maroon",
    0x800040: "Tyrian Purple",
    0x800080: "Purple",
    0x8000C0: "Dark Violet",
    0x8000FF: "Violet",
    0x804000: "Brown",
    0x804040: "Red Robin",
    0x804080: "Eminence",
    0x8040C0: "Dark Orchid",
    0x8040FF: "Blue Violet",
    0x808000: "Olive",
    0x808040: "Wasabi",
    0x808080: "Grey",
    0x8080C0: "Moody Blue",
    0x8080FF: "Light Blue",
    0x80C000: "Citrus",
    0x80C040: "Mantis",
    0x80C080: "De York",
    0x80C0C0: "Glacier",
    0x80C0FF: "Maya Blue",
    0x80FF00: "Chartreuse",
    0x80FF40: "Green Yellow",
    0x80FF80: "Light Green",
    0x80FFC0: "Aquamarine",
    0x80FFFF: "Light Cyan",
    0xC00000: "Free Speech Red",
    0xC00040: "Cardinal",
    0xC00080: "Medium Violet Red",
    0xC000C0: "Deep Magenta",
    0xC000FF: "Electric Purple",
    0xC04000: "Rust",
    0xC04040: "Chestnut",
    0xC04080: "Medium Red Violet",
    0xC040C0: "Fuchsia",
    0xC040FF: "Medium Orchid",
    0xC08000: "Dark Goldenrod",
    0xC08040: "Brandy Punch",
    0xC08080: "Brandy Rose",
    0xC080C0: "London Hue",
    0xC080FF: "Heliotrope",
    0xC0C000: "La Rioja",
    0xC0C040: "Celery",
    0xC0C080: "Pine Glade",
    0xC0C0C0: "Light Grey",
    0xC0C0FF: "Lavender Blue",
    0xC0FF00: "Electric Lime",
    0xC0FF40: "Green Yellow",
    0xC0FF80: "Sulu",
    0xC0FFC0: "Granny Apple",
    0xC0FFFF: "Pale Turquoise",
    0xFF0000: "Red",
    0xFF0040: "Torch Red",
    0xFF0080: "Rose",
    0xFF00C0: "Hot Magenta",
    0xFF00FF: "Magenta",
    0xFF4000: "Deep Orange",
    0xFF4040: "Coral Red",
    0xFF4080: "Violet Red",
    0xFF40C0: "Razzle Dazzle Rose",
    0xFF40FF: "Pink Flamingo",
    0xFF8000: "Orange",
    0xFF8040: "Coral",
    0xFF8080: "Light Coral",
    0xFF80C0: "Persian Pink",
    0xFF80FF: "Pink",
    0xFFC000: "Amber",
    0xFFC040: "Supernova",
    0xFFC080: "Macaroni and Cheese",
    0xFFC0C0: "Your Pink",
    0xFFC0FF: "Snuff",
    0xFFFF00: "Yellow",
    0xFFFF40: "Paris Daisy",
    0xFFFF80: "Light Yellow",
    0xFFFFC0: "Cumulus",
    0xFFFFFF: "White"
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
    
    def luminance(self, index):
        r, g, b = self._get_rgb(index)
        return 0.299 * r + 0.587 * g + 0.114 * b
    
    def brightness(self, index):
        r, g, b = self._get_rgb(index)
        return (r + g + b) / 3 / 255

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
