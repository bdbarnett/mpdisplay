
import board_config
import widgets as w
# from gc import collect, mem_free

REVERSE = False  # for troubhleshooting progressbar, sliders, scrollbars
w.MARK_UPDATES = True

display = w.Display(board_config.display_drv, board_config.broker, timer_period=0)
pal = display.pal
screen = w.Screen(display, pal.SILVER, visible=False)

status = w.TextBox(screen, w=screen.width, align=w.ALIGN.BOTTOM, scale=1)

icon = w.Icon(screen, x=0, y=0, fg=pal.RED, value="icons/36dp/home_filled_36dp.png")  # noqa: F841

label1 = w.Label(screen, y=2, align=w.ALIGN.TOP, value="Inverted", fg=pal.BLACK, bg=screen.bg, scale=2, inverted=True)  # noqa: F841
toggle_button = w.ToggleButton(screen, x=2, fg=pal.BLACK, bg=pal.WHITE, align_to=icon, align=w.ALIGN.OUTER_RIGHT, value=False)
def flip_label(sender):
    label1._inverted = not label1._inverted
    label1.changed()
toggle_button.set_on_change(flip_label)

checkbox = w.CheckBox(screen, y=2, align=w.ALIGN.OUTER_BOTTOM, align_to=icon, value=False)
checkbox.set_on_change(lambda sender: status.set_value(f"{'checked' if sender.value else 'unchecked'}"))
cb_label = w.Label(checkbox, x=2, fg=pal.BLACK, value="Check Me", align=w.ALIGN.OUTER_RIGHT)

button1 = w.Button(screen, w=96, align=w.ALIGN.CENTER, fg=pal.BLUE, value="button1", label="Mem_free", label_color=pal.WHITE)
# mem_free_label = w.Label(screen, y=6, align_to=button1, align=w.ALIGN.OUTER_BOTTOM, fg=pal.BLACK, bg=screen.bg, value=f"Free mem: {mem_free()}")
# button1.set_on_press(lambda sender: mem_free_label.set_value(f"Free mem: {mem_free()}"))

hide_button = w.Button(screen, x=-2, align=w.ALIGN.OUTER_LEFT, align_to=button1, fg=pal.BLACK, bg=screen.bg, value="Hide", label="Hide", label_color=pal.YELLOW)
hide_button.set_on_release(lambda sender: hide_button.hide(True))

jmp_button = w.Button(screen, x=2, align=w.ALIGN.OUTER_RIGHT, align_to=button1, fg=pal.BLACK, bg=screen.bg, value="Jump", label="Jump", label_color=pal.BLACK)
def jump(sender):
    old_area = jmp_button.area
    if jmp_button.align == w.ALIGN.OUTER_RIGHT:
        jmp_button.x = -2
        jmp_button.align = w.ALIGN.OUTER_LEFT
    else:
        jmp_button.x = 2
        jmp_button.align = w.ALIGN.OUTER_RIGHT
    screen.draw(old_area)
    display.update(old_area)
    jmp_button.render()
jmp_button.set_on_release(jump)

radio_group = w.RadioGroup()
radio1 = w.RadioButton(screen, group=radio_group, y=10, fg=pal.BLACK, bg=pal.WHITE, align_to=checkbox, align=w.ALIGN.OUTER_BOTTOM, value=False)
r1_label = w.Label(radio1, x=2, fg=pal.BLACK, value="Radio 1", align=w.ALIGN.OUTER_RIGHT, scale=2)
radio2 = w.RadioButton(screen, group=radio_group, y=2, fg=pal.BLACK, bg=pal.WHITE, align_to=radio1, align=w.ALIGN.OUTER_BOTTOM, value=True)
r2_label = w.Label(radio2, x=2, fg=pal.BLACK, value="Radio 2", align=w.ALIGN.OUTER_RIGHT, scale=2)
radio1.set_on_change(lambda sender: status.set_value(f"RadioButton 1 is now {'checked' if sender.value else 'unchecked'}"))
radio2.set_on_change(lambda sender: status.set_value(f"RadioButton 2 is now {'checked' if sender.value else 'unchecked'}"))

scrollbar2 = w.ScrollBar(screen, w=screen.width, align_to=status, align=w.ALIGN.OUTER_TOP, fg=pal.BLACK, bg=pal.GREY, knob_color=pal.BLUE, vertical=False, value=0.5, reverse=REVERSE)
scrollbar2.slider.set_on_change(lambda sender: status.set_value(f"ScrollBar value: {sender.value:.2f}"))

slider1 = w.Slider(screen, y=-2, w=screen.width, fg=pal.BLACK, bg=pal.GREY, align_to=scrollbar2, align=w.ALIGN.OUTER_TOP, knob_color=pal.RED, value=0.5, step=0.05, reverse=REVERSE)
slider1.set_on_change(lambda sender: status.set_value(f"Slider value: {sender.value:.2f}"))

# # Simulate a scroll bar. Shows how to add an Icon to a Button. Also shows how to use an IconButton.
pbar = w.ProgressBar(screen, y=slider1.y-screen.height-2, w=display.width//2, align=w.ALIGN.BOTTOM, value=0.5, reverse=REVERSE)
pbar.set_on_change(lambda sender: status.set_value(f"Progress: {sender.value:.0%}"))
pbtn1 = w.Button(pbar, x=-1, align=w.ALIGN.OUTER_LEFT, fg=pal.GREEN)
pbtn1_icon = w.Icon(pbtn1, align=w.ALIGN.CENTER, value="icons/36dp/keyboard_arrow_left_36dp.png")  # noqa: F841
pbtn2 = w.IconButton(pbar, x=1, align=w.ALIGN.OUTER_RIGHT, bg=pal.GREEN, icon="icons/36dp/keyboard_arrow_right_36dp.png")
pbtn1.set_on_press(lambda sender: pbar.set_value(pbar.value-0.1))
pbtn2.set_on_press(lambda sender: pbar.set_value(pbar.value+0.1))


clock = w.DigitalClock(screen, x=-4, y=4, align=w.ALIGN.TOP_RIGHT, fg=pal.BLACK, bg=pal.SILVER)

screen.visible = True


if not w.timer:
    print("Starting main loop")
    running = True
    while running:
        w.tick()
