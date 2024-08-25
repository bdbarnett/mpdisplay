from board_config import display_drv
from framebuf import FrameBuffer, RGB565
from pbm import PBM


display_drv.fill(0xF800)
logo = PBM("examples/assets/micropython.pbm")

# render direct to the display with fg and bg colors
logo.render(display_drv, 0, 0, 0xFFFF, 0x0000)

# render direct to the display with fg and transparent bg
logo.render(display_drv, display_drv.width//2, 0, 0xFFFF)


# render to a frame buffer
buf = bytearray(logo.width * logo.height * 2)
fb = FrameBuffer(buf, logo.width, logo.height, RGB565)
logo.render(fb, 0, 0, 0xFFFF)  # add a bg color if needed

# blit the frame buffer to the display
display_drv.blit_rect(buf, 0, display_drv.height//2, logo.width, logo.height)

# blit the frame buffer to the display with transparent bg
display_drv.blit_transparent(buf, display_drv.width//2, display_drv.height//2, logo.width, logo.height, 0x0)
