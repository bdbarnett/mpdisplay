
import board_config
import pywidgets as pw


pw.DEBUG = False
pw.MARK_UPDATES = False
pw.init_timer(10)  # Remove this line to use polled mode in a while loop


display = pw.Display(board_config.display_drv, board_config.broker, 40, 40)
screen = pw.Screen(display, visible=False)

if screen.partitioned:
    top, bottom, main = screen.top, screen.bottom, screen.main
else:
    top = bottom = main = screen

home = pw.IconButton(top, align=pw.ALIGN.TOP_LEFT, icon_file=pw.ICONS+"home_filled_36dp.pbm")
clock = pw.DigitalClock(bottom, y=-8, align=pw.ALIGN.BOTTOM_RIGHT, visible=False)
clock_toggle = pw.ToggleButton(bottom, align_to=clock, align=pw.ALIGN.OUTER_LEFT, value=False)
status = pw.TextBox(bottom, y=-8, w=clock_toggle.x, align=pw.ALIGN.BOTTOM_LEFT, scale=1, value="Status: loaded.")
clock_toggle.add_event_cb(pw.Events.MOUSEBUTTONDOWN, lambda sender, e: clock.hide(not sender.value))


box = pw.Widget(main, align=pw.ALIGN.CENTER, w=100, h=100, bg=display.theme.primary)
button = pw.Button(box, align=pw.ALIGN.CENTER, w=pw.pct.Width(50, box), h=pw.pct.Height(50, box), bg=display.theme.secondary)
def inflate_box():
    box.set_position(w=box.width+10, h=box.height+10)
button.add_event_cb(pw.Events.MOUSEBUTTONUP, lambda sender, e: inflate_box())

screen.visible = True

if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        pw.tick()
