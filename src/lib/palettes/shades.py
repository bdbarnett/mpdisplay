"""
Creates a palette with a range of shades of a single color.

Usage:
    from palettes.shades import ShadesPalette

    pal = ShadesOfRGBPalette(color_depth=16, swapped=False, cached=True, length=256, rgb=(255, 0, 255))
    for i in range(len(pal)):
        print(f"{i}: {pal[i]:#08X}")
"""

from . import Palette as _Palette


class ShadesPalette(_Palette):
    def __init__(self, name="", color_depth=16, swapped=False, cached=True, length=256, rgb=(0, 0, 0)):
        self._length = length
        self._h, self._s, self._v = self._rgb_to_hsv(*rgb)
        super().__init__(name + str(self._length), color_depth, swapped, cached)

    def _get_rgb(self, index):
        return self._hsv_to_rgb(self._h, self._s, self._v * (index / (self._length - 1)))

    def _rgb_to_hsv(self, r, g, b):
        # incoming values are in the range of 0-255
        # returns h, s, v values in the range of 0-1
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = df / mx
        v = mx
        return h / 360, s, v
    
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

        
