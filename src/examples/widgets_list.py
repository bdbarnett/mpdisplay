"""
Test ListView widget
"""
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


def add_item(to_list):
    item = pw.ListItem(to_list, value="Item")
    return item

def remove_item(from_list):
    from_list.remove(from_list.children[-1])

list_view = pw.ListView(main, w=main.width//2, h=main.height//2, align=pw.ALIGN.CENTER)

remove = pw.Button(top, label="Remove Item", align=pw.ALIGN.TOP_RIGHT)
add = pw.Button(top, label="Add Item", align_to=remove, align=pw.ALIGN.OUTER_LEFT)
add.add_event_cb(pw.Events.MOUSEBUTTONUP, lambda sender, e: add_item(list_view))
remove.add_event_cb(pw.Events.MOUSEBUTTONUP, lambda sender, e: remove_item(list_view))

screen.visible = True


if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        pw.tick()
