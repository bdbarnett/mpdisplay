
import board_config
import pywidgets as pw


pw.DEBUG = False
pw.MARK_UPDATES = False
# pw.init_timer(10)  # Remove this line to use polled mode in a while loop


display = pw.Display(board_config.display_drv, board_config.broker, 40, 40)
pal = display.pal
screen = pw.Screen(display, None, visible=False)

if screen.partitioned:
    top, bottom, main = screen.top, screen.bottom, screen.main
else:
    top = bottom = main = screen

color_wheel = pw.get_palette(name="wheel", swapped=display.needs_swap, length=display.vsa, saturation=1.0)
if screen.partitioned:
    def main_area_draw(area=None):
        area = area or pw.Area(display.vsa_area)
        # print(f"draw_bg: {area}")
        for i in range(area.y, area.y+area.h):
            display.framebuf.fill_rect(area.x, i, area.w, 1, color_wheel[i-display.tfa])
    main.draw = main_area_draw
    main_area_draw()

aligns = [pw.ALIGN.TOP_LEFT, pw.ALIGN.TOP, pw.ALIGN.TOP_RIGHT,
          pw.ALIGN.LEFT, pw.ALIGN.CENTER, pw.ALIGN.RIGHT,
          pw.ALIGN.BOTTOM_LEFT, pw.ALIGN.BOTTOM, pw.ALIGN.BOTTOM_RIGHT,
          pw.ALIGN.OUTER_TOP_LEFT, pw.ALIGN.OUTER_TOP, pw.ALIGN.OUTER_TOP_RIGHT,
          pw.ALIGN.OUTER_LEFT, pw.ALIGN.OUTER_RIGHT,
          pw.ALIGN.OUTER_BOTTOM_LEFT, pw.ALIGN.OUTER_BOTTOM, pw.ALIGN.OUTER_BOTTOM_RIGHT]

align_names = ["TL", "TOP", "TR",
                "LEFT", "CTR", "RIGHT",
                "BL", "BOT", "BR",
                "OTL", "OT", "OTR",
                "OL", "OR",
                "OBL", "OB", "OBR"]

def demo_alignments(parent, align_to=None):
    for name, align in zip(align_names, aligns):
        pw.Label(parent, align=align, align_to=align_to, value=name)

def scroll_by(value):
    display.vscroll += value

def scroll_to(value):
    display.vscroll = value

auto_scroll_task = None
def toggle_auto_scroll(sender, event=None):
    global auto_scroll_task
    if not auto_scroll_task:
        auto_scroll_task = display.add_task(lambda: scroll_by(1), 1)
    else:
        display.remove_task(auto_scroll_task)
        auto_scroll_task = None


home = pw.IconButton(top, align=pw.ALIGN.TOP_LEFT, icon_file=pw.icon_theme.home(pw.ICON_SIZE.LARGE))
toggle = pw.ToggleButton(top, align_to=home, align=pw.ALIGN.OUTER_RIGHT, value=False)
down = pw.IconButton(top, align=pw.ALIGN.TOP_RIGHT, icon_file=pw.icon_theme.down_arrow(pw.ICON_SIZE.LARGE))
up = pw.IconButton(top, align_to=down, align=pw.ALIGN.OUTER_LEFT, icon_file=pw.icon_theme.up_arrow(pw.ICON_SIZE.LARGE))
slider1 = pw.Slider(top, y=9, w=up.x-toggle.x-toggle.width-16, h=18, align=pw.ALIGN.TOP, value=0, step=0.05)

clock = pw.DigitalClock(bottom, y=-8, align=pw.ALIGN.BOTTOM_RIGHT, visible=False)
clock_toggle = pw.ToggleButton(bottom, align_to=clock, align=pw.ALIGN.OUTER_LEFT, value=False)
status = pw.TextBox(bottom, y=-8, w=clock_toggle.x, align=pw.ALIGN.BOTTOM_LEFT, scale=1, value="Status: loaded.")

button = pw.Button(main, w=main.width//2, h=64, align=pw.ALIGN.CENTER, label="test", radius=10, pressed_offset=5)
# demo_alignments(button)

scroll_jump = 5
home.add_event_cb(pw.Events.MOUSEBUTTONDOWN, lambda sender, e: scroll_to(0))
toggle.add_event_cb(pw.Events.MOUSEBUTTONDOWN, toggle_auto_scroll)
down.add_event_cb(pw.Events.MOUSEBUTTONDOWN, lambda sender, e: scroll_by(-scroll_jump))
up.add_event_cb(pw.Events.MOUSEBUTTONDOWN, lambda sender, e: scroll_by(scroll_jump))
slider1.set_change_cb(lambda sender: scroll_to(int(sender.value * display.vsa)))
button.add_event_cb(pw.Events.MOUSEBUTTONDOWN, lambda sender, e: status.set_value("Button pressed"))
button.add_event_cb(pw.Events.MOUSEBUTTONUP, lambda sender, e: status.set_value("Button released"))
clock_toggle.add_event_cb(pw.Events.MOUSEBUTTONDOWN, lambda sender, e: clock.hide(not sender.value))
screen.add_event_cb(pw.Events.MOUSEWHEEL, lambda sender, e: scroll_by(-e.y))

screen.visible = True


if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        pw.tick()
