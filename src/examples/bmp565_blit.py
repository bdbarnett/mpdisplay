from color_setup import ssd
from bmp565 import BMP565
from framebuf import FrameBuffer, RGB565
from time import sleep

ssd.fill(0x0)
ssd.show()
bmp = BMP565("examples/assets/warrior.bmp")
fb = FrameBuffer(bmp.buffer, bmp.width, bmp.height, RGB565)

while True:
    ssd.blit(fb, 0, 0)
    ssd.show()
    sleep(1)

    ssd.blit_rect(bmp[:], 0, 0, bmp.width, bmp.height)
    ssd.show()
    sleep(1)