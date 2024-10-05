import board_config
import widgets as w
from widgets.console import Console


display = w.Display(board_config.display_drv, board_config.broker, start_timer=True)
pal = display.pal
screen = w.Screen(display, pal.SILVER, visible=True)
display.set_vscroll(40, 40)
# clock = w.DigitalClock(screen, h=8, y=2, fg=pal.BLACK, bg=pal.SILVER)
console = Console(screen)
console.clear()
display.framebuf.fill_rect(*display.tfa_area, pal.RED)

i=1
while i<60:
    console.write(f"{i}:  vscroll={display.vscroll}, y_rel={console._cursor_y_rel}, y_pos={console._cursor_y_pos}\n")
    if not w.timer:
        w.tick()
    console.by_char = not console.by_char
    i += 1
