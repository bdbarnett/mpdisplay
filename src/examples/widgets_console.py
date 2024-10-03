import board_config
import widgets as w
from widgets.console import Console
from time import sleep


display = w.Display(board_config.display_drv, board_config.broker, use_timer=True)
pal = display.pal
screen = w.Screen(display, pal.SILVER, visible=True)
display.set_vscroll(40, 40)
clock = w.DigitalClock(screen, y=2, fg=pal.BLACK, bg=pal.SILVER)
console = Console(screen)
console.clear()
display.framebuf.fill_rect(*display.tfa_area, pal.RED)

i=1
while True:
    console.write(f"{i}!\n")
    sleep(.5)
    i += 1