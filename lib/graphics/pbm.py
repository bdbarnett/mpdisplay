'''
A class to handle PBM files - WIP - Not working yet

Example:
    pbm = PBM('image.pbm')
    print(pbm.width, pbm.height)
    print(pbm[0])  # Get the first byte
    print(pbm[0, 0])  # Get the first bit
    print(pbm[0:10])  # Get the first 10 bytes as a memoryview object
    print(pbm[0:10, 0:10])  # Get a 10x10 slice of the image as a bytearray object
    pbm[0] = 0xFF  # Set the first byte
    pbm[0, 0] = 1  # Set the first bit
    pbm[0:10] = b'\xFF' * 10  # Set the first 10 bytes
    pbm[0:10, 0:10] = b'\xFF' * 10 * 10  # Set a 10x10 slice of the image
    pbm.save('image.pbm')  # Save the image to a file
    pbm.map16((0xFFFF, 0x0000))  # Convert the image to a 16-bit color map
    pbm.map16((0xFFFF, 0x0000), to_buffer)  # Convert the image to a 16-bit color map and store it in the to_buffer array
    pbm.write('image.pbm', binary=False)  # Save the image to a file in ASCII format

    from framebuf import FrameBuffer, MONO_HLSB, MONO_VLSB, MONO_HMSB, MONO_VMSB, RGB565
    fb = FrameBuffer(pbm, pbm.width, pbm.height, MONO_HLSB)
    pal = (0xFFFF, 0x0000)

    # Display buffer for a 320x240 display
    display = bytearray(320 * 240 * 2)
    display_mv = memoryview(display)
    display_fb = FrameBuffer(display_mv, 320, 240, RGB565)

    # Convert the image to a 16-bit color map




'''

import math
from array import array
import sys


class PBM:
    def __init__(self, filename=None, source=None, width=None, height=None):
        self._filename = filename
        if source is not None:
            self.width = width
            self.height = height
            self._buffer = source
            if len(self._buffer) != math.ceil(width * height / 8):
                raise ValueError("Invalid buffer size")
            self._mv = memoryview(self._buffer)
        elif filename is not None:
            self.read()
        else:
            raise ValueError('Invalid arguments')

    def read(self):
        with open(self._filename, "r") as f:

            # Read the header
            header = f.readline().strip()
            if header != "P1" and header != "P4":
                print("Error: Invalid PBM header")
                sys.exit(1)

            # Read the dimensions
            dimensions = f.readline().strip().split()
            self.width = int(dimensions[0])
            self.height = int(dimensions[1])

            # Read the data
            if header == "P1":
                # ASCII
                self._buffer = array("B", [0] * math.ceil(self.width * self.height / 8))
                self._mv = memoryview(self._buffer)
                for i in range(self.height):
                    line = f.readline().strip().split()
                    for j in range(self.width):
                        if line[j] == "1":
                            self._mv[i * self.width + j // 8] |= 1 << (7 - j % 8)
            elif header == "P4":
                # Binary
                self._buffer = array("B", f.read())
                self._mv = memoryview(self._buffer)

    def save(self, filename, binary=True):
        if binary:
            with open(filename, "wb") as f:
                f.write(b"P4\n")
                f.write(f"{self.width} {self.height}\n".encode())
                f.write(self._buffer)
        else:
            with open(filename, "w"):
                f.write("P1\n")
                f.write(f"{self.width} {self.height}\n")
                for i in range(self.height):
                    for j in range(self.width):
                        f.write("1" if self._mv[i * self.width + j // 8] & (1 << (7 - j % 8)) else "0")
                    f.write("\n")

    def map16(self, palette, to_buffer=None, x=0, y=0, stride=0):
        # fg and bg are 16-bit colors
        fg = palette[0]
        bg = palette[1]
        if to_buffer is None:
            # to_buffer is an array of 16-bit colors
            to_buffer = array("H", [0] * self.width * self.height)
        to_mv = memoryview(to_buffer)
        # stride is the number of pixels to skip in the destination buffer to get to the next line
        if stride == 0:
            try:
                stride = to_buffer.width
            except AttributeError:
                stride = self.width

        for i in range(self.height):
            for j in range(self.width):
                if self._mv[i * self.width + j // 8] & (1 << (7 - j % 8)):
                    to_mv[(i + y) * stride + j + x] = fg
                else:
                    to_mv[(i + y) * stride + j + x] = bg
        return to_buffer


    def __getitem__(self, key):
        if isinstance(key, int):
            return self._mv[key]
        elif isinstance(key, tuple):
            if len(key) == 1:
                return self._mv[key[0]]
            elif len(key) == 2:
                return self._mv[key[0] * self.width + key[1] // 8] & (1 << (7 - key[1] % 8))
            elif len(key) == 4:
                return self._mv[key[0]:key[1], key[2]:key[3]]
        else:
            raise ValueError("Invalid key type")
        
    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._mv[key] = value
        elif isinstance(key, tuple):
            if len(key) == 1:
                self._mv[key[0]] = value
            elif len(key) == 2:
                if value:
                    self._mv[key[0] * self.width + key[1] // 8] |= 1 << (7 - key[1] % 8)
                else:
                    self._mv[key[0] * self.width + key[1] // 8] &= ~(1 << (7 - key[1] % 8))
            elif len(key) == 4:
                self._mv[key[0]:key[1], key[2]:key[3]] = value
        else:
            raise ValueError("Invalid key type")
        
    def __str__(self):
        return f"PBM: {self.width}x{self.height}"
    
    def __repr__(self):
        return f"PBM: {self.width}x{self.height}"
    
    def __len__(self):
        return len(self._buffer)
    
    def __iter__(self):
        return iter(self._buffer)
