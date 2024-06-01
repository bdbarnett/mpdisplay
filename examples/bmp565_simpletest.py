from board_config import display_drv
from primitives import BMP565, shapes


bmp = BMP565("examples/test.bmp")
print(f"{bmp.width=}, {bmp.height=}, {bmp.bpp=}")
display_drv.blit_rect(bmp[0:16, 0:16], 0, 0, 16, 16)

shapes.line(bmp, 0, 0, bmp.width-1, bmp.height-1, 0xFFFF)
display_drv.blit_rect(bmp[:], 32, 32, bmp.width, bmp.height)
