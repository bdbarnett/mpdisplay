# SPDX-FileCopyrightText: 2020 Peter Hinch, 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT

'''
gui_framework.py
FrameBuffer wrapper for using the MicroPython Nano-GUI or other
framebuf based GUIs with MPDisplay.
Usage:
    'color_setup.py'
        from gui_framework import SSD
        import framebuf
        import board_config

        mode = framebuf.RGB565

        ssd = SSD(board_config.display_drv, mode)

    'main.py'
        from color_setup import ssd
        <your code here>

    OR if not using Nano-GUI or Micro-GUI
        from color_setup import ssd, get_color, registered_colors  # Use registered_colors to test if 16 colors have already been registered when using a LUT.
        <your code here>
'''

import framebuf
import gc
from sys import platform


# Determine how line buffers are allocated
alloc_buffer = lambda size: bytearray(size)
# If heap_caps is available, use it to allocate in internal DMA-capable memory
if platform == "esp32":
    try:
        from heap_caps import malloc, CAP_DMA, CAP_INTERNAL
        alloc_buffer = lambda size: malloc(size, CAP_DMA | CAP_INTERNAL)
    except ImportError:
        pass

# Number of colors that have been registered with get_color using idx=None
registered_colors = 0

def get_color(r, g, b, idx=None):
    """
    Get an RGB565 or RGB332 value for a color and optionally register it in the display's LUT.
    This is a convenience function for using gui_framework WITHOUT Nano-GUI or Micro-GUI.
    Those packages have their own methods of registering colors.

    :param r: Red component (0-255)
    :param g: Green component (0-255)
    :param b: Blue component (0-255)
    :param idx: Optional index to register the color in the display's LUT (0-15)
    :return: RGB565 or RGB332 color value, or the index of the registered color
    """
    global registered_colors  # Index of the next color to register
    c = SSD.rgb(r, g, b)  # Convert the color to RGB565 or RGB332
    if not hasattr(SSD, 'lut'):  # If the ssd doesn't use a LUT in its current mode
        return c  # Return the color as-is
    if idx == None:  # If no index was provided
        if registered_colors < 16:  # If there are fewer than 16 colors already registered
            idx = registered_colors  # Set the index to the next available index
            registered_colors += 1  # Increment the index for the next color
        else:  # If there are already 16 colors registered
            raise ValueError("16 colors have already been registered")
    if not 0 <= idx <= 15:  # If the index is out of range
        raise ValueError('Color numbers must be 0..15')
    offset = idx << 1  # Multiply by 2 (2 bytes per 16-bit color)
    SSD.lut[offset] = c & 0xff  # Set the lower 8 bits of the color
    SSD.lut[offset + 1] = c >> 8  # Set the upper 8 bits of the color
    return idx  # Return the index of the registered color

@micropython.viper
def _lcopy8(dest:ptr8, source:ptr8, length:int, swapped:bool, bgr:bool):
    # Convert a line in 8 bit RGB332 format to 16 bit RGB565 format.
    # Each byte becomes 2 in destination. Source format:
    # <R2 R1 R0 G2 G1 G0 B1 B0>
    # dest:
    # swapped==False, bgr==False: <R2 R1 R0 00 00 G2 G1 G0> <00 00 00 B1 B0 00 00 00>
    # swapped==True,  bgr==False: <00 00 00 B1 B0 00 00 00> <R2 R1 R0 00 00 G2 G1 G0>
    # swapped==False, bgr==True:  <B1 B0 00 00 00 G2 G1 G1> <00 00 00 R2 R1 R0 00 00>
    # swapped==True,  bgr==True:  <00 00 00 R2 R1 R0 00 00> <B1 B0 00 00 00 G2 G1 G0>
    if swapped:
        lsb = 0
        msb = 1
    else:
        lsb = 1
        msb = 0
    n = 0
    for x in range(length):
        c = source[x]
        if bgr:
            dest[n + lsb] = (c & 0xe0) | ((c & 0x1c) >> 2)  # Red Green
            dest[n + msb] = (c & 0x03) << 3  # Blue
        else:
            dest[n + lsb] = ((c & 0x3) << 6) | ((c & 0x1c) >> 2)  # Blue Green
            dest[n + msb] = (c & 0xe0) >> 3  # Red
        n += 2

@micropython.viper
def _lcopy4(dest:ptr16, source:ptr8, lut:ptr16, length:int):
    # Convert a line in 4+4 bit index format to two * 16 bit RGB565 format
    # using a color lookup table. Each byte becomes 4 in destination.
    # Source format:  <C03 C02 C01 C00 C13 C12 C11 C10>
    # Dest format: the same as self.rgb * 2
    n = 0
    for x in range(length):
        c = source[x]  # Get the indices of the 2 pixels
        dest[n] = lut[c >> 4]  # lookup top 4 bits for even pixels
        n += 1
        dest[n] = lut[c & 0x0f]  # lookup bottom 4 bits for odd pixels
        n += 1


class SSD(framebuf.FrameBuffer):
    '''
    SSD: A class to wrap an MPDisplay driver and provide a framebuf compatible
    interface to it.  It provides a show() method to copy the framebuf to the
    display.  The show() method is optimized for the mode.
    The mode must be one of the following:
        framebuf.RGB565
        framebuf.GS8
        framebuf.GS4_HMSB
    '''

    rgb = None  # Function to convert r, g, b to a color value

    def __init__(self, display_drv, mode):
        self.palette = BoolPalette(mode)  # a 2-value color palette for rendering monochrome glyphs
        self.display_drv = display_drv
        self.height = display_drv.height
        self.width = display_drv.width
        self.bgr = display_drv.bgr

        # If the display bus is a MicroPython bus (not C) and it has byte swapping enabled,
        # disable it and set a flag so we can swap the bytes as they are put into the buffers
        self.swap_color_bytes = False
        if hasattr(display_drv.display_bus, "name") and "MicroPython" in display_drv.display_bus.name:
            if display_drv.display_bus.enable_swap():
                print("Disabling display_drv byte swap and populating colors with bytes swapped instead.")
                display_drv.display_bus.enable_swap(False)
                self.swap_color_bytes = True

        # Set the SSD.rgb function to the appropriate one for the mode, BGR, and byte swapping
        if mode == framebuf.GS8:
            SSD.rgb = self._rgb8
        elif self.bgr == True:
            if self.swap_color_bytes:
                SSD.rgb = self._bgr16_swapped
            else:
                SSD.rgb = self._bgr16
        else:
            if self.swap_color_bytes:
                SSD.rgb = self._rgb16_swapped
            else:
                SSD.rgb = self._rgb16

        # Set the show function to the appropriate one for the mode and
        # allocate the buffer.  Also create the line buffer and lut if needed.
        gc.collect()
        if mode == framebuf.RGB565:
            self._buffer = bytearray(self.width * self.height * 2)
            self.show = self._show16
        elif mode == framebuf.GS8:
            self._linebuf = alloc_buffer(self.width * 2)
            self._buffer = bytearray(self.width * self.height)
            self.show = self._show8
        elif mode == framebuf.GS4_HMSB:
            SSD.lut = bytearray(0x00 for _ in range(32))
            self._linebuf = alloc_buffer(self.width * 2)
            self._buffer = bytearray(self.width * self.height // 2)
            self.show = self._show4
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        super().__init__(self._buffer, self.width, self.height, mode)
        self._mvb = memoryview(self._buffer)
        self.show()  # Clear the display
        gc.collect()

    @micropython.native
    def _show16(self):
        # Copyt the buffer to the display in one go
        self.display_drv.blit(0, 0, self.width, self.height, self._mvb)

    @micropython.native
    def _show8(self):
        # Convert the 8 bit RGB332 values to 16 bit RGB565 values and then copy the line
        # to the display, line by line.
        swapped = self.swap_color_bytes
        bgr = self.bgr
        wd = self.width
        ht = self.height
        lb = self._linebuf
        buf = self._mvb
        for row in range(0, ht):  # For each line
            start = row * wd
            _lcopy8(lb, buf[start :], wd, swapped, bgr)
            self.display_drv.blit(0, row, wd, 1, lb)

    @micropython.native
    def _show4(self):
        # Convert the 4 bit index values to 16 bit RGB565 values using a lookup table
        # and then copy the line to the display, line by line.
        clut = SSD.lut
        width = self.width
        wd = self.width // 2  # 2 pixels per byte
        ht = self.height
        lb = self._linebuf
        buf = self._mvb
        for row in range(0, ht):  # For each line
            start = row * wd
            _lcopy4(lb, buf[start :], clut, wd)  # Copy and map colors
            self.display_drv.blit(0, row, width, 1, lb)

    @staticmethod
    def _rgb8(r, g, b):
        # Convert r, g, b in range 0-255 to an 8 bit color value RGB332
        # rrrgggbb
        return (r & 0xe0) | ((g >> 3) & 0x1c) | (b >> 6)

    @staticmethod
    def _rgb16(r, g, b):
        # Convert r, g, b in range 0-255 to a 16 bit color value RGB565
        # rrrrrggg gggbbbbb
        return ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)
    
    @staticmethod
    def _rgb16_swapped(r, g, b):
        # Convert r, g, b in range 0-255 to a 16 bit color value RGB565
        # ggbbbbbb rrrrrggg
        color = SSD._rgb16(r, g, b)
        return (color & 0xff) << 8 | (color & 0xff00) >> 8
    
    @staticmethod
    def _bgr16(r, g, b):
        # Convert r, g, b in range 0-255 to a 16 bit color value RGB565
        # bbbbbggg gggrrrrr
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    
    @staticmethod
    def _bgr16_swapped(r, g, b):
        # Convert r, g, b in range 0-255 to a 16 bit color value RGB565
        # gggrrrrr bbbbbggg
        color = SSD._bgr16(r, g, b)
        return (color & 0xff) << 8 | (color & 0xff00) >> 8


class BoolPalette(framebuf.FrameBuffer):
    # This is a 2-value color palette for rendering monochrome glyphs to color
    # FrameBuffer instances. Supports destinations with up to 16 bit color.

    # Copyright (c) Peter Hinch 2021
    # Released under the MIT license see LICENSE
    def __init__(self, mode):
        buf = bytearray(4)  # OK for <= 16 bit color
        super().__init__(buf, 2, 1, mode)
    
    def fg(self, color):  # Set foreground color
        self.pixel(1, 0, color)

    def bg(self, color):
        self.pixel(0, 0, color)
