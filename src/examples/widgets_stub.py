
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

home = w.IconButton(top, align=w.ALIGN.TOP_LEFT, icon_file=w.ICONS+"home_filled_36dp.png")
clock = w.DigitalClock(bottom, y=-8, align=w.ALIGN.BOTTOM_RIGHT, visible=False)
clock_toggle = w.ToggleButton(bottom, align_to=clock, align=w.ALIGN.OUTER_LEFT, value=False)
status = w.TextBox(bottom, y=-8, w=clock_toggle.x, align=w.ALIGN.BOTTOM_LEFT, scale=1, value="Status: loaded.")
clock_toggle.add_event_cb(w.Events.MOUSEBUTTONDOWN, lambda sender, e: clock.hide(not sender.value))
button = w.Button(main, label="Button")
button.add_event_cb(w.Events.MOUSEBUTTONDOWN, lambda sender, e: status.set_value("Button clicked!"))
button.add_event_cb(w.Events.MOUSEBUTTONUP, lambda sender, e: status.set_value("Button released."))
screen.visible = True


if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        w.tick()
