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

clock = pw.DigitalClock(bottom, y=-8, align=pw.ALIGN.BOTTOM_RIGHT, visible=False)
clock_toggle = pw.ToggleButton(bottom, align_to=clock, align=pw.ALIGN.OUTER_LEFT, value=False)
status = pw.TextBox(bottom, y=-8, w=clock_toggle.x, align=pw.ALIGN.BOTTOM_LEFT, scale=1, value="Status: loaded.")
clock_toggle.add_event_cb(pw.Events.MOUSEBUTTONDOWN, lambda sender, e: clock.hide(not sender.value))

item_no = 1
def add_item(to_list: pw.ListView):
    global item_no
    item = pw.Button(to_list, label=f"Item {item_no}", icon_file=pw.icon_theme.home(pw.ICON_SIZE.LARGE))
    item.add_event_cb(pw.Events.MOUSEBUTTONDOWN, lambda sender, e: status.set_value(f"{sender.label.value} clicked."))
    item_no += 1

def remove_item(from_list: pw.ListView):
    if from_list.children:
        from_list.children[0].parent = None
    else:
        status.value = "ListView is empty."

list_view = pw.ListView(main, w=main.width//2, h=main.height//2, align=pw.ALIGN.CENTER)

add = pw.Button(top, label="+ Item")
remove = pw.Button(top, label="- Item", align_to=add, align=pw.ALIGN.OUTER_RIGHT)
down = pw.IconButton(top, align=pw.ALIGN.TOP_RIGHT, icon_file=pw.icon_theme.down_arrow(pw.ICON_SIZE.LARGE))
up = pw.IconButton(top, align_to=down, align=pw.ALIGN.OUTER_LEFT, icon_file=pw.icon_theme.up_arrow(pw.ICON_SIZE.LARGE))

add.add_event_cb(pw.Events.MOUSEBUTTONUP, lambda sender, e: add_item(list_view))
remove.add_event_cb(pw.Events.MOUSEBUTTONUP, lambda sender, e: remove_item(list_view))
down.add_event_cb(pw.Events.MOUSEBUTTONDOWN, lambda sender, e: list_view.scroll_down())
up.add_event_cb(pw.Events.MOUSEBUTTONDOWN, lambda sender, e: list_view.scroll_up())
list_view.set_change_cb(lambda sender: status.set_value(f"Item {sender.value+1} of {len(sender.children)}"))


screen.visible = True

if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        pw.tick()
