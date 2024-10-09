
import board_config
import widgets as w


w.DEBUG = True
w.MARK_UPDATES = False
w.init_timer(10)  # Remove this line to use polled mode in a while loop


display = w.Display(board_config.display_drv, board_config.broker, 38, 38)
screen = w.Screen(display, visible=False)

if screen.partitioned:
    top, bottom, main = screen.top, screen.bottom, screen.main
else:
    top = bottom = main = screen

home = w.IconButton(top, x=2, align=w.ALIGN.TOP_LEFT, icon=w.ICONS+"home_filled_36dp.png")
clock = w.DigitalClock(bottom, x=-3, y=-9, align=w.ALIGN.BOTTOM_RIGHT, visible=False)
clock_toggle = w.ToggleButton(bottom, x=-3, align_to=clock, align=w.ALIGN.OUTER_LEFT, value=False)
status = w.TextBox(bottom, x=3, y=-9, w=clock_toggle.x-6, align=w.ALIGN.BOTTOM_LEFT, scale=1, value="Status: loaded.")
clock_toggle.set_on_change(lambda sender: clock.hide(not sender.value))

screen.visible = True


if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        w.tick()
