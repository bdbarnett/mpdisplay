
import board_config
import widgets as w

w.DEBUG = True


digits = "0123456789."
operands = "+-*/"
button_labels = [["CE", "C", "BS", "/"],
                 ["7", "8", "9", "*"],
                 ["4", "5", "6", "-"],
                 ["1", "2", "3", "+"],
                 ["+/-", "0", ".", "="]]

w.init_timer(10)  # Remove this line to use polled mode in a while loop

display = w.Display(board_config.display_drv, board_config.broker)
theme = display.theme
screen = w.Screen(display, visible=False)
top_box = w.Widget(screen, h=60, bg=theme.secondary)
readout = w.Widget(top_box, fg=theme.on_background, bg=theme.background, w=top_box.width-6, h=top_box.height-6, align=w.ALIGN.CENTER)
clock = w.DigitalClock(readout, align=w.ALIGN.CENTER, scale=3, visible=False)
clock_toggle = w.ToggleButton(readout, size=18, value=False)
history = w.TextBox(readout, w=readout.width-clock_toggle.width, h=clock_toggle.height, align=w.ALIGN.OUTER_TOP_RIGHT, align_to=clock_toggle, scale=1, visible=False)
history.set_position(y=history.height)
history.visible = True
max_history_chars = (history.width // history.char_width) - 1
history.format = f">{max_history_chars}"
entry = w.TextBox(readout, align=w.ALIGN.BOTTOM, scale=2)
max_entry_chars = (entry.width // entry.char_width) - 1
entry.format = f">{max_entry_chars+1}"

def clock_toggle_callback(sender):
    clock.hide(not sender.value)
    history.hide(sender.value)
    entry.hide(sender.value)
clock_toggle.set_on_change(clock_toggle_callback)

button_box = w.Widget(screen, h=display.height-top_box.height, align=w.ALIGN.BOTTOM)
cols, rows = len(button_labels[0]), len(button_labels)
buttons = [[w.Button(button_box, label=button_labels[j][i], value=button_labels[j][i], radius=4,
    x=w.pct.Width(i*100/cols, button_box), y=w.pct.Height(j*100/rows, button_box),
    w=w.pct.Width(100/cols, button_box), h=w.pct.Height(100/rows, button_box),
    ) for i in range(cols)] for j in range(rows)]


def clear_everything():
    global showing_result, result, last_op, last_entry, calculation_str
    showing_result = False
    entry.value = history.value = result = last_op = last_entry = calculation_str = ""

def format(value):
    if value == "":
        return ""
    val = f"{float(value):.8f}".rstrip("0").rstrip(".")
    if len(val) > max_entry_chars:
        val = f"{float(val):.8e}"
    return val

def calculate(calculation_str) -> str:
    try:
        return format(eval(calculation_str))
    except Exception as e:
        print(f"Error: {e} in {calculation_str}")
        return "Error"

def handle_key_input(key):
    global showing_result, result, last_op, last_entry, calculation_str
    if result == "Error" and key != "CE":
        return
    if key == "=":
        if showing_result: # Repeat the last operation
            calculation_str = f"{result} {last_op} {last_entry}"
        else:  # Perform the operation with the entry, reusing the last entry if entry value is empty
            if entry.value:
                last_entry = format(entry.value)
            calculation_str += " " + last_entry
        result = calculate(calculation_str)
        history.value = calculation_str + " = " + result
        entry.value = result
        showing_result = True
    elif key in operands:
        last_op = key
        if showing_result:  # Start new operation with the result
            calculation_str = f"{result} {last_op}"
        else:
            if entry.value:  # Continue the operation with the entry
                last_entry = format(entry.value)
                calculation_str += f" {last_entry} {last_op}"
            else:  # Change the operator
                if calculation_str:
                    calculation_str = calculation_str[:-1] + key
        history.value = calculation_str
        entry.value = ""
        showing_result = False
    elif key == "+/-":
        if entry.value[0] == "-":
            entry.value = entry.value[1:]
        else:
            entry.value = "-" + entry.value
        if showing_result:
            result = entry.value
    elif key == "C":
        if showing_result:
            clear_everything()
        else:
            entry.value = ""
    elif key == "CE":
        clear_everything()
    elif key == "BS":
        if not showing_result:
            entry.value = entry.value[:-1]
    elif key in digits:
        if showing_result:
            clear_everything()
        if key == ".":
            if entry.value.find(".") == -1 and len(entry.value) < max_entry_chars:
                entry.value += "."
        elif len(entry.value) < max_entry_chars:
            entry.value += key
    else:
        print(f"Unknown key: {key}")

clear_everything()

for row in buttons:
    for button in row:
        button.set_on_press(lambda sender: handle_key_input(sender.value))

screen.visible = True

if not display.timer:
    print("Starting main loop")
    running = True
    while running:
        w.tick()
