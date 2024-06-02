# SPDX-FileCopyrightText: 2024 Brad Barnett
#
# SPDX-License-Identifier: MIT
"""
A class to read a 16-bit RGB565 BMP file and present it as a sliceable object.

Usage:
    bmp = BMP565('image.bmp')
    print(bmp.width, bmp.height, self.bpp)
    print(bmp[0])  # Get pixel color at 0 as an integer
    print(bmp[0, 0])  # Get pixel color at (0, 0) as an integer
    print(bmp[0:10])  # Get the first 10 pixels as a memoryview object
    print(bmp[0:10, 0:10])  # Get a 10x10 slice of the image as a bytearray object
"""

import struct

class BMP565:
    def __init__(self, filename):
        with open(filename, 'rb') as f:
            self._read_header(f)
            self._read_data(f)

    def _read_header(self, f):
        if f.read(2) != b'BM':
            raise ValueError('Not a BMP file')
        self.file_size = struct.unpack('<I', f.read(4))[0]
        f.seek(10)
        self.data_offset = struct.unpack('<I', f.read(4))[0]
        self.header_size = struct.unpack('<I', f.read(4))[0]
        self.width, self.height = struct.unpack('<II', f.read(8))
        planes = struct.unpack('<H', f.read(2))[0]
        if planes != 1:
            raise ValueError('Invalid BMP file')
        self.bpp = struct.unpack('<H', f.read(2))[0]
        if self.bpp != 16:
            raise ValueError('Invalid color depth')
        
    def _read_data(self, f):
        # BMP files are stored from bottom up
        # We need to reverse the data without reversing the color byte pairs
        # by reading one row at a time and adding that row to the beginning of the data
        self._buffer = bytearray()
        for i in range(self.height):
            f.seek(self.data_offset + (self.height - i - 1) * self.width * 2)
            self._buffer += f.read(self.width * 2)
        self._mv = memoryview(self._buffer)
        
    def __getitem__(self, key):
        if isinstance(key, tuple):
            x, y = key
            if isinstance(x, slice) and isinstance(y, slice):
                data = bytearray()
                for i in range(y.start, y.stop):
                    data += self._mv[(i * self.width + x.start) * 2:(i * self.width + x.stop) * 2]
                return data
            else:
                return struct.unpack('<H', self._mv[(y * self.width + x) * 2:(y * self.width + x) * 2 + 2])[0]
        elif isinstance(key, int):
            return struct.unpack('<H', self._mv[key * 2:key * 2 + 2])[0]
        elif isinstance(key, slice):
            if key.start is None and key.stop is None:
                return self._mv[:]
            return self._mv[key.start * 2:key.stop * 2]
        else:
            raise ValueError('Invalid key')
