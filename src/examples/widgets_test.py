
import board_config
import widgets as w


display = w.Display(board_config.display_drv, board_config.broker, start_timer=True)
pal = display.pal
screen = w.Screen(display, pal.SILVER, visible=False)
label1 = w.Label(screen, y=2, align=w.ALIGN.TOP, value="Inverted", fg=pal.BLACK, scale=2, inverted=True)  # noqa: F841

icon = w.Icon(screen, x=0, y=0, fg=pal.RED, value="icons/36dp/home_filled_36dp.png")  # noqa: F841

checkbox = w.CheckBox(screen, y=2, align=w.ALIGN.OUTER_BOTTOM, align_to=icon, value=False)
checkbox.set_on_change(lambda sender: status.set_value(f"{'checked' if sender.value else 'unchecked'}"))
cb_label = w.Label(checkbox, x=2, fg=pal.BLACK, value="Check Me", align=w.ALIGN.OUTER_RIGHT)

status = w.TextBox(screen, y=-34, w=screen.width, align=w.ALIGN.BOTTOM, scale=1)

button1 = w.Button(screen, w=96, align=w.ALIGN.CENTER, fg=pal.BLUE, value="button1", label="Click Me", label_color=pal.WHITE)
button1.set_on_press(lambda sender: status.set_value(f"{sender.value} pressed!"))
button1.set_on_release(lambda sender: status.set_value(f"{sender.value} released!"))

# # Simulate a scroll bar. Shows how to add an Icon to a Button. Also shows how to use an IconButton.
pbar = w.ProgressBar(screen, y=-80, w=display.width//2, align=w.ALIGN.BOTTOM, value=0.5)
pbar.set_on_change(lambda sender: status.set_value(f"Progress: {sender.value:.0%}"))
pbtn1 = w.Button(pbar, x=-1, align=w.ALIGN.OUTER_LEFT, fg=pal.GREEN)
pbtn1_icon = w.Icon(pbtn1, align=w.ALIGN.CENTER, value="icons/36dp/keyboard_arrow_left_36dp.png")  # noqa: F841
pbtn2 = w.IconButton(pbar, x=1, align=w.ALIGN.OUTER_RIGHT, bg=pal.GREEN, icon="icons/36dp/keyboard_arrow_right_36dp.png")
pbtn1.set_on_press(lambda sender: pbar.set_value(pbar.value-0.1))
pbtn2.set_on_press(lambda sender: pbar.set_value(pbar.value+0.1))

# Create a RadioGroup to manage the radio buttons
radio_group = w.RadioGroup()

# Create a couple of RadioButtons and add them to the RadioGroup
radio1 = w.RadioButton(screen, group=radio_group, y=10, fg=pal.BLACK, bg=pal.WHITE, align_to=checkbox, align=w.ALIGN.OUTER_BOTTOM, value=False)
r1_label = w.Label(radio1, x=2, fg=pal.BLACK, value="Radio 1", align=w.ALIGN.OUTER_RIGHT, scale=2)
radio2 = w.RadioButton(screen, group=radio_group, y=2, fg=pal.BLACK, bg=pal.WHITE, align_to=radio1, align=w.ALIGN.OUTER_BOTTOM, value=True)
r2_label = w.Label(radio2, x=2, fg=pal.BLACK, value="Radio 2", align=w.ALIGN.OUTER_RIGHT, scale=2)

# Set a callback to update the status when a radio button is checked
radio1.set_on_change(lambda sender: status.set_value(f"RadioButton 1 is now {'checked' if sender.value else 'unchecked'}"))
radio2.set_on_change(lambda sender: status.set_value(f"RadioButton 2 is now {'checked' if sender.value else 'unchecked'}"))

# Create a ToggleButton
toggle_button = w.ToggleButton(screen, y=10, fg=pal.BLACK, bg=pal.WHITE, align_to=radio2, align=w.ALIGN.OUTER_BOTTOM, value=False)

# # Set a callback to update the status when the toggle button changes state
toggle_button.set_on_change(lambda sender: status.set_value(f"Toggle is now {'On' if sender.value else 'Off'}"))


# Create a horizontal slider with a custom knob color
slider = w.Slider(screen, y=50, w=screen.width*3//4, fg=pal.BLACK, bg=pal.GREY, align=w.ALIGN.CENTER, knob_color=pal.RED, value=0.5, step=0.05)

# Set a callback to update the status when the slider changes
slider.set_on_change(lambda sender: status.set_value(f"Slider value: {sender.value:.2f}"))

screen.visible = True

clock = w.DigitalClock(screen, x=-2, y=2, align=w.ALIGN.TOP_RIGHT, fg=pal.BLACK, bg=pal.SILVER)

if not w.timer:
    print("Starting main loop")
    running = True
    while running:
        w.tick()
