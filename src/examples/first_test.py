from board_config import display_drv, broker
from random import getrandbits
from graphics import Area

button_area = Area(display_drv.fill_rect(10, 10, 100, 100, 0xF800))
while True:
    if evt := broker.poll():
        if evt.type == broker.Events.MOUSEBUTTONDOWN:
            if button_area.contains(evt.pos):
                display_drv.fill_rect(*button_area, getrandbits(16))
                print(f"Button pressed at {evt.pos}")
