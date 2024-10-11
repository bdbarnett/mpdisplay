
import board_config
import widgets as w
try:
    from gc import collect, mem_free
except ImportError:
    mem_free = None


w.DEBUG = False
w.MARK_UPDATES = False
w.init_timer(10)  # Remove this line to use polled mode in a while loop


REVERSE = False  # for troubleshooting progressbar, sliders, scrollbars

display = w.Display(board_config.display_drv, board_config.broker)
screen = w.Screen(display, visible=True)

status = w.TextBox(screen, w=screen.width, align=w.ALIGN.BOTTOM, scale=1)

icon = w.Icon(screen, value=w.ICONS+"home_filled_36dp.png")  # noqa: F841

label1 = w.Label(screen, align=w.ALIGN.TOP, value="Inverted", bg=screen.bg, scale=2, inverted=True)  # noqa: F841
toggle_button = w.ToggleButton(screen, align_to=icon, align=w.ALIGN.OUTER_RIGHT, value=False)
def flip_label(sender):
    label1._inverted = not label1._inverted
    label1.changed()
toggle_button.set_on_change(flip_label)

checkbox = w.CheckBox(screen, align=w.ALIGN.OUTER_BOTTOM, align_to=icon, value=False)
checkbox.set_on_change(lambda sender: status.set_value(f"{'checked' if sender.value else 'unchecked'}"))
cb_label = w.Label(checkbox, value="Check Me", align=w.ALIGN.OUTER_RIGHT)

button1 = w.Button(screen, w=96, align=w.ALIGN.CENTER, value="button1", label="Mem_free")
if mem_free:
    mem_free_label = w.Label(screen, y=6, align_to=button1, align=w.ALIGN.OUTER_BOTTOM, value=f"Free mem: {mem_free()}")
    def mem_free_action(sender):
        collect()
        mem_free_label.set_value(f"Free mem: {mem_free()}")
    button1.set_on_press(mem_free_action)

hide_button = w.Button(screen, align=w.ALIGN.OUTER_LEFT, align_to=button1, value="Hide", label="Hide",)
hide_button.set_on_release(lambda sender: hide_button.hide(True))

jmp_button = w.Button(screen, align=w.ALIGN.OUTER_RIGHT, align_to=button1, value="Jump", label="Jump")
def jump(sender):
    if jmp_button.align == w.ALIGN.OUTER_RIGHT:
        jmp_button.set_position(align = w.ALIGN.OUTER_LEFT)
    else:
        jmp_button.set_position(align = w.ALIGN.OUTER_RIGHT)
jmp_button.set_on_release(jump)

radio_group = w.RadioGroup()
radio1 = w.RadioButton(screen, group=radio_group, y=10, align_to=checkbox, align=w.ALIGN.OUTER_BOTTOM, value=False)
r1_label = w.Label(radio1, value="Radio 1", align=w.ALIGN.OUTER_RIGHT, scale=2)
radio2 = w.RadioButton(screen, group=radio_group, align_to=radio1, align=w.ALIGN.OUTER_BOTTOM, value=True)
r2_label = w.Label(radio2, value="Radio 2", align=w.ALIGN.OUTER_RIGHT, scale=2)
radio1.set_on_change(lambda sender: status.set_value(f"RadioButton 1 is now {'checked' if sender.value else 'unchecked'}"))
radio2.set_on_change(lambda sender: status.set_value(f"RadioButton 2 is now {'checked' if sender.value else 'unchecked'}"))

scrollbar2 = w.ScrollBar(screen, w=screen.width, align_to=status, align=w.ALIGN.OUTER_TOP, vertical=False, value=0.5, reverse=REVERSE)
scrollbar2.slider.set_on_change(lambda sender: status.set_value(f"ScrollBar value: {sender.value:.2f}"))

slider1 = w.Slider(screen, w=screen.width, align_to=scrollbar2, align=w.ALIGN.OUTER_TOP, value=0.5, step=0.05, reverse=REVERSE)
slider1.set_on_change(lambda sender: status.set_value(f"Slider value: {sender.value:.2f}"))

# # Simulate a scroll bar. Shows how to add an Icon to a Button. Also shows how to use an IconButton.
pbar = w.ProgressBar(screen, y=slider1.y-screen.height, w=display.width//2, align=w.ALIGN.BOTTOM, value=0.5, reverse=REVERSE)
pbar.set_on_change(lambda sender: status.set_value(f"Progress: {sender.value:.0%}"))
pbtn1 = w.Button(pbar, align=w.ALIGN.OUTER_LEFT)
pbtn1_icon = w.Icon(pbtn1, align=w.ALIGN.CENTER, value=w.ICONS+"keyboard_arrow_left_36dp.png")  # noqa: F841
pbtn2 = w.IconButton(pbar, align=w.ALIGN.OUTER_RIGHT, icon=w.ICONS+"keyboard_arrow_right_36dp.png")
pbtn1.set_on_press(lambda sender: pbar.set_value(pbar.value-0.1))
pbtn2.set_on_press(lambda sender: pbar.set_value(pbar.value+0.1))


clock = w.DigitalClock(screen, align=w.ALIGN.TOP_RIGHT)

screen.visible = True


polling = not display.timer
print("Polling" if polling else "Timer running")
while polling:
    w.tick()
