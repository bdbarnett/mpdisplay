from ulab import numpy as np

full_framebuffer = np.zeros((480, 320), dtype=np.uint16)

# creat a buffer for a spritesheet with 16 16x16 sprites
sprite_sheet = np.zeros((16, 16, 16), dtype=np.uint16)

# write to some pixels on each of the 16 sprites just to show they are different for testing purposes
for i in range(16):
    sprite_sheet[i, 0, 0] = i

# how to draw a sprite to the framebuffer
def draw_sprite(sprite, x, y):
    full_framebuffer[y:y+16, x:x+16] = sprite_sheet[sprite]

# draw sprite 0 at 0,0
draw_sprite(0, 0, 0)

# draw sprite 1 at 16,0
draw_sprite(1, 16, 0)


