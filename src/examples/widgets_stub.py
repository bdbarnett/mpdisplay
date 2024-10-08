
import board_config
import widgets as w


w.DEBUG = False
w.MARK_UPDATES = False
w.init_timer(10)  # Remove this line to use polled mode in a while loop


display = w.Display(board_config.display_drv, board_config.broker)
pal = display.pal
screen = w.Screen(display, None, visible=False)
display.set_vscroll(38, 38)

button_bar = w.Widget(screen, w=display.width, h=display.tfa, align=w.ALIGN.TOP_LEFT, bg=pal.WHITE)
status_bar = w.Widget(screen, w=display.width, h=display.bfa, align=w.ALIGN.BOTTOM_LEFT, bg=pal.WHITE)
main_area = w.Widget(screen, w=display.width, h=display.vsa, align=w.ALIGN.TOP_LEFT, y=display.tfa, bg=pal.BLACK, visible=True)

home = w.IconButton(button_bar, x=2, align=w.ALIGN.TOP_LEFT, icon="icons/home_filled_36dp.png")
clock = w.DigitalClock(status_bar, x=-3, align=w.ALIGN.RIGHT, fg=pal.BLACK, bg=button_bar.bg, visible=False)
clock_toggle = w.ToggleButton(status_bar, x=-3, align_to=clock, align=w.ALIGN.OUTER_LEFT, fg=pal.BLACK, bg=pal.WHITE, value=False)
status = w.TextBox(status_bar, w=clock_toggle.x-3, align=w.ALIGN.LEFT, scale=1, value="Status: loaded.")
clock_toggle.set_on_change(lambda sender: clock.hide(not sender.value))

screen.visible = True


if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        w.tick()
