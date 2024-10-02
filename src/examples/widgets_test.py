
import board_config
import widgets as w


display = w.Display(board_config.display_drv, board_config.broker, use_timer=True)
pal = display.pal
screen = w.Screen(display, pal.SILVER, visible=False)

icon = w.Icon(screen, x=0, y=0, fg=pal.RED, value="icons/36dp/keyboard_arrow_down_36dp.png")  # noqa: F841
label1 = w.Label(screen, y=2, value="Testing", fg=pal.BLACK)  # noqa: F841

status = w.TextBox(screen, x=0, y=display.height-38, w=display.width-20)

button1 = w.Button(screen, w=96, fg=pal.BLUE, value="button1", label="Click Me", label_color=pal.WHITE)
button1.set_on_press(lambda sender: status.set_value(f"{sender.value} pressed!"))
button1.set_on_release(lambda sender: status.set_value(f"{sender.value} released!"))

# Simulate a scroll bar. Shows how to add an Icon to a Button. Also shows how to use an IconButton.
pbar = w.ProgressBar(screen, y=display.height-100, w=display.width//2, value=0.5)
pbar.set_on_change(lambda sender: status.set_value(f"Progress: {sender.value:.0%}"))
pbtn1 = w.Button(screen, x=pbar.x-w.default_icon_size, y=pbar.y, fg=pal.GREEN)
pbtn1_icon = w.Icon(pbtn1, fg=pal.BLACK, value="icons/36dp/keyboard_arrow_left_36dp.png")  # noqa: F841
pbtn2 = w.IconButton(screen, x=pbar.x+pbar.width, y=pbar.y, fg=pal.BLACK, bg=pal.GREEN, icon="icons/36dp/keyboard_arrow_right_36dp.png")
pbtn1.set_on_press(lambda sender: pbar.set_value(pbar.value-0.1))
pbtn2.set_on_press(lambda sender: pbar.set_value(pbar.value+0.1))

# Create a CheckBox widget
checkbox = w.CheckBox(screen, y=100, fg=pal.BLACK, bg=pal.WHITE, value=False)

# Add a callback to print the state when the checkbox is toggled
checkbox.set_on_change(lambda sender: status.set_value(f"{'checked' if sender.value else 'unchecked'}"))


# Create a RadioGroup to manage the radio buttons
radio_group = w.RadioGroup()

# Create a couple of RadioButtons and add them to the RadioGroup
radio1 = w.RadioButton(screen, group=radio_group, x=50, y=50, fg=pal.BLACK, bg=pal.WHITE, value=False)
radio2 = w.RadioButton(screen, group=radio_group, x=50, y=100, fg=pal.BLACK, bg=pal.WHITE, value=True)

# Set a callback to update the status when a radio button is checked
# radio1.set_on_change(lambda sender: status.set_value(f"RadioButton 1 is now {'checked' if sender.value else 'unchecked'}"))
# radio2.set_on_change(lambda sender: status.set_value(f"RadioButton 2 is now {'checked' if sender.value else 'unchecked'}"))

# Create a ToggleButton
toggle_button = w.ToggleButton(screen, y=150, fg=pal.BLACK, bg=pal.WHITE, value=False)

# Set a callback to update the status when the toggle button changes state
toggle_button.set_on_change(lambda sender: status.set_value(f"Toggle is now {'On' if sender.value else 'Off'}"))


# Create a horizontal slider with a custom knob color
slider = w.Slider(screen, y=380, w=200, fg=pal.BLACK, bg=pal.GREY, knob_color=pal.RED, value=0.5, step=0.05)

# # Set a callback to update the status when the slider changes
# slider.set_on_change(lambda sender: status.set_value(f"Slider value: {sender.value:.2f}"))

screen.visible = True

clock = w.DigitalClock(screen, x=display.width-100, y=2, fg=pal.BLACK, bg=pal.SILVER)

if not display.use_timer:
    while True:
        display.tick()
