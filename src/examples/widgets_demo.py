
import board_config
import widgets as w


w.DEBUG = False
w.MARK_UPDATES = False
w.init_timer(10)  # Remove this line to use polled mode in a while loop


display = w.Display(board_config.display_drv, board_config.broker, 38, 38)
pal = display.pal
screen = w.Screen(display, None, visible=False)

if screen.partitioned:
    top, bottom, main = screen.top, screen.bottom, screen.main
else:
    top = bottom = main = screen

color_wheel = w.get_palette(name="wheel", swapped=display.needs_swap, length=display.vsa, saturation=1.0)
if screen.partitioned:
    def main_area_draw(area=None):
        area = area or display.vsa_area
        # print(f"draw_bg: {area}")
        for i in range(area.y, area.y+area.h):
            display.framebuf.fill_rect(area.x, i, area.w, 1, color_wheel[i-display.tfa])
    main.draw = main_area_draw
    main_area_draw()

aligns = [w.ALIGN.TOP_LEFT, w.ALIGN.TOP, w.ALIGN.TOP_RIGHT,
          w.ALIGN.LEFT, w.ALIGN.CENTER, w.ALIGN.RIGHT,
          w.ALIGN.BOTTOM_LEFT, w.ALIGN.BOTTOM, w.ALIGN.BOTTOM_RIGHT,
          w.ALIGN.OUTER_TOP_LEFT, w.ALIGN.OUTER_TOP, w.ALIGN.OUTER_TOP_RIGHT,
          w.ALIGN.OUTER_LEFT, w.ALIGN.OUTER_RIGHT,
          w.ALIGN.OUTER_BOTTOM_LEFT, w.ALIGN.OUTER_BOTTOM, w.ALIGN.OUTER_BOTTOM_RIGHT]

align_names = ["TL", "TOP", "TR",
                "LEFT", "CTR", "RIGHT",
                "BL", "BOT", "BR",
                "OTL", "OT", "OTR",
                "OL", "OR",
                "OBL", "OB", "OBR"]

def demo_alignments(parent, align_to=None):
    for name, align in zip(align_names, aligns):
        w.Label(parent, align=align, align_to=align_to, value=name)

def scroll_by(value):
    display.vscroll += value

def scroll_to(value):
    display.vscroll = value

auto_scroll_task = None
def toggle_auto_scroll(sender):
    global auto_scroll_task
    if not auto_scroll_task:
        auto_scroll_task = display.add_task(lambda: scroll_by(1), 1)
    else:
        display.remove_task(auto_scroll_task)
        auto_scroll_task = None


home = w.IconButton(top, x=2, align=w.ALIGN.TOP_LEFT, icon=w.ICONS+"home_filled_36dp.png")
toggle = w.ToggleButton(top, x=2, align_to=home, align=w.ALIGN.OUTER_RIGHT, value=False)
down = w.IconButton(top, x=-2, align=w.ALIGN.TOP_RIGHT, icon=w.ICONS+"keyboard_arrow_down_36dp.png")
up = w.IconButton(top, x=-2, align_to=down, align=w.ALIGN.OUTER_LEFT, icon=w.ICONS+"keyboard_arrow_up_36dp.png")
slider1 = w.Slider(top, y=9, w=up.x-toggle.x-toggle.width-16, h=18, align=w.ALIGN.TOP, value=0, step=0.05)

clock = w.DigitalClock(bottom, x=-3, y=-9, align=w.ALIGN.BOTTOM_RIGHT, visible=False)
clock_toggle = w.ToggleButton(bottom, x=-3, align_to=clock, align=w.ALIGN.OUTER_LEFT, value=False)
status = w.TextBox(bottom, x=3, y=-9, w=clock_toggle.x-6, align=w.ALIGN.BOTTOM_LEFT, scale=1, value="Status: loaded.")

button = w.Button(main, w=main.width//2, h=64, align=w.ALIGN.CENTER, label="test", radius=10, pressed_offset=5)
demo_alignments(button)

scroll_jump = 5
home.set_on_press(lambda sender: scroll_to(0))
toggle.set_on_change(toggle_auto_scroll)
down.set_on_press(lambda sender: scroll_by(-scroll_jump))
up.set_on_press(lambda sender: scroll_by(scroll_jump))
slider1.set_on_change(lambda sender: scroll_to(int(sender.value * display.vsa)))
button.set_on_press(lambda sender: status.set_value("Button pressed"))
button.set_on_release(lambda sender: status.set_value("Button released"))
clock_toggle.set_on_change(lambda sender: clock.hide(not sender.value))

screen.visible = True


if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        w.tick()
