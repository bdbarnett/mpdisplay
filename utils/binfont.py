# SPDX-FileCopyrightText: Tony DiCola, 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""
A module to draw text to a canvas using fonts from 
https://github.com/spacerace/romfont
"""

import os
import struct
from area import Area

# Default font file to use if none is specified.
# Should be 8x8 to keep framebuf.py compatible with MicroPython framebuf module
_FONTS = {
    8: "fonts/binfont_8x8.bin",
    14: "fonts/binfont_8x14.bin",
    16: "fonts/binfont_8x16.bin",
}
_DEFAULT_FONT = _FONTS[8]


def text8(canvas, s, x, y, c=1, scale=1, inverted=False, font_file=None, font_height=8):
    """Place text on the canvas.  Breaks on \n to next line.

    Does not break on line going off canvas.
    """
    if (
        not hasattr(canvas, "_text8font")
        or (font_file is not None and canvas._text8font.font_file != font_file)
        or (font_height is not None and canvas._text8font.font_height != font_height)
    ):
        # load the font!
        canvas._text8font = BinFont(font_file, font_height)

    return canvas._text8font.text(canvas, s, x, y, c, scale, inverted)


def text14(canvas, s, x, y, c=1, scale=1, inverted=False, font_file=None, font_height=14):
    """Place text on the screen.  Breaks on \n to next line.

    Does not break on line going off screen.
    """
    if (
        not hasattr(canvas, "_text14font")
        or (font_file is not None and canvas._text14font.font_file != font_file)
        or (font_height is not None and canvas._text14font.font_height != font_height)
    ):
        # load the font!
        canvas._text14font = BinFont(font_file, font_height)

    return canvas._text14font.text(canvas, s, x, y, c, scale, inverted)

def text16(canvas, s, x, y, c=1, scale=1, inverted=False, font_file=None, font_height=16):
    """Place text on the screen.  Breaks on \n to next line.

    Does not break on line going off screen.
    """
    if (
        not hasattr(canvas, "_text16font")
        or (font_file is not None and canvas._text16font.font_file != font_file)
        or (font_height is not None and canvas._text16font.font_height != font_height)
    ):
        # load the font!
        canvas._text16font = BinFont(font_file, font_height)

    return canvas._text16font.text(canvas, s, x, y, c, scale, inverted)


class BinFont:
    """A helper class to read binary font tiles and 'seek' through them as a
    file to display in a canvas or directly on screen. We use file access
    so we dont waste 1KB of RAM on a font!"""

    def __init__(self, font_file=None, font_height=None):
        # Specify the drawing area width and height, and the pixel function to
        # call when drawing pixels (should take an x and y param at least).
        # Optionally specify font_file to override the font file to use (default
        # is vga_8x8.bin).  The font format is a binary file with the following
        # format:
        # - x bytes: font data, in ASCII order covering 128 or all 256 characters.
        #            Each character should have a byte for each pixel row of
        #            data (i.e. a 8x8 font has 8 bytes per character).
        self.font_file = (
            font_file if font_file else _FONTS.get(font_height, _DEFAULT_FONT)
        )
        self.font_name = self.font_file.split("/")[-1].split(".bin")[0]
        self._font_height = (
            font_height
            if font_height is not None
            else int(self.font_name.split("x")[-1])
        )
        self._font_width = 8

        # Open the font file.
        # Note that only fonts up to 8 pixels wide are currently supported.
        try:
            self._font = open(self.font_file, "rb")
            # simple font file validation check based on expected file size
            filesize = os.stat(self.font_file)[6]
            if (
                filesize != 256 * self.font_height
                and filesize != 128 * self.font_height
            ):
                raise RuntimeError(
                    f"Invalid font file: {self.font_file} is {filesize} bytes, expected {256 * self.font_height}"
                )
        except OSError:
            print("Could not find font file", self.font_file)
            raise
        except OverflowError:
            # os.stat can throw this on boards without long int support
            # just hope the font file is valid and press on
            pass

    @property
    def font_width(self):
        """Return the width of the font in pixels."""
        return self._font_width

    @property
    def font_height(self):
        """Return the height of the font in pixels."""
        return self._font_height

    def deinit(self):
        """Close the font file as cleanup."""
        self._font.close()

    def __enter__(self):
        """Initialize/open the font file"""
        self.__init__()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """cleanup on exit"""
        self.deinit()

    def draw_char(self, char, x, y, canvas, color, scale=1, inverted=False):
        """Draw one character at position (x,y) to a canvas in a given color"""
        scale = max(scale, 1)
        # Don't draw the character if it will be clipped off the visible area.
        # if x < -self.font_width or x >= canvas.width or \
        #   y < -self.font_height or y >= canvas.height:
        #    return
        # Go through each row of the character.
        for char_y in range(self._font_height):
            # Grab the byte for the current row of font data.
            self._font.seek((ord(char) * self._font_height) + char_y)
            try:
                line = struct.unpack("B", self._font.read(1))[0]
            except RuntimeError:
                continue  # maybe character isnt there? go to next
            # Go through each column in the row byte.
            for char_x in range(self.font_width):
                # Draw a pixel for each bit that's flipped on.
                if (line >> (self.font_width - char_x - 1)) & 0x1:
                    canvas.fill_rect(
                        (
                            x + char_x * scale
                            if not inverted
                            else x + (self._font_width - char_x - 1) * scale
                        ),
                        (
                            y + char_y * scale
                            if not inverted
                            else y + (self._font_height - char_y - 1) * scale
                        ),
                        scale,
                        scale,
                        color,
                    )
        return Area(x, y, self._font_width * scale, self._font_height * scale)

    def text(self, canvas, string, x, y, color, scale=1, inverted=False):
        """Write text to the canvas at the specified position in the specified color."""
        if inverted:
            string = "".join(reversed(string))

        char_y = y
        largest_x = 0  # the last x position reached on the longest line
        for chunk in string.split("\n"):
            last_x = x  # the last x position reached on the current line
            for i, char in enumerate(chunk):
                char_x = x + (i * self.font_width * scale)
                if char_x < canvas.width if hasattr(canvas, "width") else True:
                    if char_y < canvas.height if hasattr(canvas, "height") else True:
                        if char_x + (self.font_width * scale) > 0:
                            if char_y + (self.font_height * scale) > 0:
                                self.draw_char(
                                    char,
                                    char_x,
                                    char_y,
                                    canvas,
                                    color,
                                    scale=scale,
                                    inverted=inverted,
                                )
                                last_x = char_x + (self.font_width * scale)
            largest_x = max([largest_x, last_x])  # update the largest x position
            char_y += self.font_height * scale
        return Area(x, y, largest_x - x, char_y - y)

    def text_width(self, text, scale=1):
        """Return the pixel width of the specified text message."""
        return len(text) * self._font_width * scale
