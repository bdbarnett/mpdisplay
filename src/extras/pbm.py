"""
A class to handle PBM files - WIP - Not working yet

Example:
    from board_config import display_drv
    from framebuf import FrameBuffer, RGB565
    from pbm import PBM

    logo = PBM("examples/assets/micropython.pbm")

    # render direct to the display with fg and bg colors
    logo.render(display_drv, 0, 0, 0xFFFF, 0x0000)

    # render direct to the display with fg and transparent bg
    logo.render(display_drv, 0, display_drv.height//2, 0xFFFF)

    # blit to a frame buffer
    buf = bytearray(logo.width * logo.height * 2)
    fb = FrameBuffer(buf, logo.width, logo.height, RGB565)
    palette = FrameBuffer(memoryview(bytearray(2 * 2)), 2, 1, RGB565)
    palette.pixel(0, 0, 0x0FF0)
    palette.pixel(1, 0, 0xFFFF)
    fb.blit(logo, 0, 0, palette.pixel(0, 0), palette)

    # blit the frame buffer to the display
    display_drv.blit_rect(buf, display_drv.width * 2 // 3, 0, logo.width, logo.height)

    # blit the frame buffer to the display with transparent bg
    display_drv.blit_transparent(buf, display_drv.width * 2 // 3, display_drv.height//2, logo.width, logo.height, 0x000F)

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

