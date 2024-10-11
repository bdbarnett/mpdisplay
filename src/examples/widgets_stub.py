
import board_config
import widgets as w


w.DEBUG = False
w.MARK_UPDATES = False
w.init_timer(10)  # Remove this line to use polled mode in a while loop


display = w.Display(board_config.display_drv, board_config.broker, 40, 40)
screen = w.Screen(display, visible=False)

if screen.partitioned:
    top, bottom, main = screen.top, screen.bottom, screen.main
else:
    top = bottom = main = screen

home = w.IconButton(top, align=w.ALIGN.TOP_LEFT, icon=w.ICONS+"home_filled_36dp.png")
clock = w.DigitalClock(bottom, y=-8, align=w.ALIGN.BOTTOM_RIGHT, visible=False)
clock_toggle = w.ToggleButton(bottom, align_to=clock, align=w.ALIGN.OUTER_LEFT, value=False)
status = w.TextBox(bottom, y=-8, w=clock_toggle.x, align=w.ALIGN.BOTTOM_LEFT, scale=1, value="Status: loaded.")
clock_toggle.set_on_change(lambda sender: clock.hide(not sender.value))

screen.visible = True


if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        w.tick()
