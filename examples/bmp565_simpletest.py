from board_config import display_drv
from bmp565 import BMP565
from draw import shapes


bmp = BMP565("examples/assets/guy.bmp")
print(f"{bmp.width=}, {bmp.height=}, {bmp.bpp=}")
display_drv.blit_rect(bmp[0:bmp.width, 0:bmp.height], 0, 0, bmp.width, bmp.height)

shapes.hline(bmp, 0, bmp.height//2, bmp.width, 0xFFFF)
display_drv.blit_rect(bmp[:], bmp.width, 0, bmp.width, bmp.height)
