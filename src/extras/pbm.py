"""
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
"""

from array import array
from framebuf import FrameBuffer, MONO_HLSB


class PBM(FrameBuffer):
    def __init__(self, filename):
        self._filename = filename
        with open(self._filename, "rb") as f:
            # Read the header
            header = f.read(3)[:2]
            if header != b"P1" and header != b"P4":
                raise ValueError("Invalid PBM header")
            # Read the data
            if header == b"P1":
                # ASCII
                print("ASCII")
                raise NotImplementedError("ASCII PBM files are not supported yet")
            elif header == b"P4":
                # Binary
                next_line = f.readline().strip()
                while next_line[0] == 35:  # 35 is the ASCII code for #
                    next_line = f.readline().strip()
                dimensions = next_line.split()
                self.width = int(dimensions[0])
                self.height = int(dimensions[1])
                self._buffer = array("B", f.read())
                self._mv = memoryview(self._buffer)
        super().__init__(self._mv, self.width, self.height, MONO_HLSB)

    def render(self, canvas, x, y, fg=0, bg=None):
        col = row = 0
        for i in range(len(self._buffer)):
            for bit in self._bitgen(self._buffer[i]):
                if bit:
                    canvas.pixel(x + col, y + row, fg)
                elif bg is not None:
                    canvas.pixel(x + col, y + row, bg)
                col += 1
                if col >= self.width:
                    col = 0
                    row += 1

    @staticmethod
    def _bitgen(b):
        """
        generator to iterate over the bits in a byte (character)
        """
        # reverse bit order
        b = (b & 0xF0) >> 4 | (b & 0x0F) << 4
        b = (b & 0xCC) >> 2 | (b & 0x33) << 2
        b = (b & 0xAA) >> 1 | (b & 0x55) << 1
        for i in range(8):
            yield (b >> i) & 1

    def __str__(self):
        return f"PBM: {self.width}x{self.height}"
    
    def __repr__(self):
        return f"PBM: {self.width}x{self.height}"

