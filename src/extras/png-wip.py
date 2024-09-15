# WORK IN PROGRESS - not working yet!


import zlib
import struct


class PNG:
    def __init__(self, filename):
        self.bitmap = None
        self.palette = None
        self.transparency = None
        self.color_depth = None
        self.width = None
        self.height = None
        self.mode = None
        self.load(filename)

    def load(self, filename):
        with open(filename, 'rb') as file:
            # Read and validate PNG header
            header = file.read(8)
            if header[:8] != b'\x89PNG\r\n\x1a\n':
                raise ValueError('Invalid PNG file')

            # Read chunks
            while True:
                length = int.from_bytes(file.read(4), 'big')
                chunk_type = file.read(4)

                if chunk_type == b'IHDR':
                    # Read image header
                    (
                        self.width,
                        self.height,
                        self.color_depth,
                        self.mode,
                        compression,
                        filters,
                        interlaced,
                    ) = struct.unpack('>IIBBBBB', file.read(13))
                    assert interlaced == 0, 'Interlaced images are not supported'
                    assert compression == 0, 'Unsupported compression method'
                    assert filters == 0, 'Unsupported filter method'
                elif chunk_type == b'PLTE':
                    # Read palette (3 bytes per color)
                    self.palette = file.read(length)
                elif chunk_type == b'IDAT':
                    # Read image data
                    decompressed_data = zlib.decompress(file.read(length))
                elif chunk_type == b'tRNS':
                    # Read transparency data
                    self.transparency = file.read(length)
                elif chunk_type == b'IEND':
                    # End of file
                    break
                else:
                    file.seek(length, 1)  # Skip unknown chunk_type
                # Skip CRC
                file.seek(4, 1)

        # Finished reading file, now process image data
        print(f"Width: {self.width}, Height: {self.height}")
        print(f"Color depth: {self.color_depth}")
        print(f"Palette size: {len(self.palette) if self.palette else 0} bytes")
        print(f"Transparency size: {len(self.transparency) if self.transparency else 0} bytes")
        print(f"Data size: {len(decompressed_data)} bytes")
        print(f"Mode: {self.mode}")
        self.process_data(decompressed_data)

    def process_data(self, decompressed_data):
        # Process decompressed_data to get bitmap
        unit = (1, 0, 3, 1, 2, 0, 4)[self.mode]
        print(f"Unit: {unit}")
        scanline_length = (self.width * self.color_depth * unit + 7) // 8
        print(f"Scanline length: {scanline_length}")
        colors = 1 << (self.color_depth * unit)
        print(f"Colors: {colors}")
        if self.mode == 3:  # indexed color
            self.bitmap = bytearray(self.width * self.height * colors)
            self.mv = memoryview(self.bitmap)
            for y in range(self.height):
                filter_type = decompressed_data[y * (scanline_length + 1)]
                scanline = decompressed_data[y * (scanline_length + 1) + 1 : (y + 1) * (scanline_length + 1)]
                self.decode_scanline(filter_type, scanline, y)
        elif self.mode in (0, 4):  # grayscale
            # Implement grayscale decoding
            raise ValueError(f'Unsupported color mode: {self.mode}')
        elif self.mode in (2, 6):  # truecolor
            raise ValueError(f'Unsupported color mode: {self.mode}')
        else:
            raise ValueError(f'Unsupported color mode: {self.mode}')

        # Process palette if available
        # ...

    def decode_scanline(self, filter_type, scanline, y):
        if filter_type == 0:
            self.mv[y * self.width : (y + 1) * self.width] = scanline
        elif filter_type == 1:
            for x in range(self.width):
                self.mv[y * self.width + x] = scanline[x] + self.mv[y * self.width + x - 1]
        elif filter_type == 2:
            for x in range(self.width):
                self.mv[y * self.width + x] = scanline[x] + self.mv[(y - 1) * self.width + x]
        elif filter_type == 3:
            for x in range(self.width):
                self.mv[y * self.width + x] = scanline[x] + (self.mv[(y - 1) * self.width + x] + self.mv[y * self.width + x - 1]) // 2
        elif filter_type == 4:
            for x in range(self.width):
                self.mv[y * self.width + x] = scanline[x] + self.paeth_predictor(self.mv[(y - 1) * self.width + x], self.mv[y * self.width + x - 1], self.mv[(y - 1) * self.width + x - 1])
        else:
            raise ValueError('Unsupported filter type')

# Usage example
png = PNG('examples/assets/mdtesticon.png')

