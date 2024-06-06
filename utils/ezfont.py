"""
A wrapper for ezFBfont that allows rendering to non-framebuffer objects.

See ezFBfont at https://github.com/easytarget/microPyEZfonts
"""
from ezFBfont import ezFBfont, framebuf


class EZFont(ezFBfont):
    def __init__(self, device,
                font,
                fg = None,
                bg = None,
                tkey = None,
                halign = None,
                valign = None,
                colors = None,
                verbose = False):
        super().__init__(device, font, fg, bg, tkey, halign, valign, colors, verbose)
        self.fg = fg
        self.bg = bg

    def _put_char(self, char, x, y, fg, bg, tkey):
        # fetch the glyph
        glyph, char_height, char_width = self._font.get_ch(char)
        if glyph is None:
            return 0, 0  # Nothing to print. skip.
        buf = bytearray(glyph)
        charbuf = framebuf.FrameBuffer(buf, char_width, char_height, self._font_format)

        if (
            (-x >= char_width) or
            (-y >= char_height) or
            (x >= self._device.width) or
            (y >= self._device.height)
        ):
            # Out of bounds, no-op.
            return

        # Clip.
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = max(0, -x)
        y1 = max(0, -y)
        x0end = min(self._device.width, x + char_width)
        y0end = min(self._device.height, y + char_height)

        for y0 in range(y0, y0end):
            cx1 = x1
            for cx0 in range(x0, x0end):
                col = charbuf.pixel(cx1, y1)
                if col > 0:
                    col = self.fg
                else:
                    col = self.bg
                if col != tkey:
                    self._device.pixel(cx0, y0, col)
                cx1 += 1
            y1 += 1
        return char_width, char_height
