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

    def __init__(self, name="", color_depth=16, swapped=False, length=256, cache=True, saturation=1.0, value=None):
        super().__init__(name, color_depth, swapped)

        self._length = length
        self._cache = dict() if cache else None

        if saturation is None and value is None:
            self._mode = "wheel"
            self._one_third = self._length // 3
            self._two_thirds = 2 * self._length // 3
            self._spacing = 256 * 3 / self._length
        
        else:
            self._mode = "hsv"
            self._saturation = saturation if saturation is not None else 1.0
            self._value = value if value is not None else 1.0
            if not 0 <= self._saturation <= 1 or not 0 <= self._value <= 1:
                raise ValueError("Saturation and value must be in the range of 0-1")

        self._define_named_colors()

    def __getitem__(self, index):
        while index < 0:
            index += self._length  # wrap around

        if self._cache is not None:
            if index in self._cache:
                return self._cache[index]

        if self._mode == "wheel":
            r, g, b = self._wheel_to_rgb(index)
        else:
            r, g, b = self._hsv_to_rgb(index / self._length, self._saturation, self._value)

        if self._color_depth == 24:
            color = r << 16 | g << 8 | b
        elif self._color_depth == 16:
            color = self.color565(r, g, b)
        else:
            raise ValueError("Invalid color depth")
        
        if self._cache is not None:
            self._cache[index] = color

        return color

    def __len__(self):
        return self._length
    
    def _wheel_to_rgb(self, index):
        # incoming index is in the range of 0-self._length
        index = self._length - 1 - index  # reverse the order

        if index < self._one_third:
            return (255 - int(index * self._spacing), 0, int(index * self._spacing))
        elif index < self._two_thirds:
            index -= self._one_third
            return (0, int(index * self._spacing), 255 - int(index * self._spacing))
        else:
            index -= self._two_thirds
            return (int(index * self._spacing), 255 - int(index * self._spacing), 0)
    
    def _hsv_to_rgb(self, h, s, v):
        # incoming values are in the range of 0-1
        # returns r, g, b values in the range of 0-255
        if s == 0.0:  # when s=0, all values are shades of gray
            return int(v * 255), int(v * 255), int(v * 255)
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = int(255 * v * (1.0 - s))
        q = int(255 * v * (1.0 - s * f))
        t = int(255 * v * (1.0 - s * (1.0 - f)))
        v = int(255 * v)
        i = i % 6
        if i == 0:  # red
            return v, t, p
        if i == 1:  # yellow
            return q, v, p
        if i == 2:  # green
            return p, v, t
        if i == 3:  # cyan
            return p, q, v
        if i == 4:  # blue
            return t, p, v
        if i == 5:  # magenta
            return v, p, q
        return 0, 0, 0

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
